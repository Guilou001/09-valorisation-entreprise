"""Ligne de commande : télécharger, puis produire tables, figures, classeur et mémo."""

from __future__ import annotations

from pathlib import Path

import typer

app = typer.Typer(help="Valorisation du Canadien National : historique SEC, DCF statué, DCF inversé, "
                       "sensibilités, comparables, classeur Excel, mémo bilingue.")

G_TERMINAL = 0.02          # précepte : cible d'inflation de la Banque du Canada
ERP = 0.05                 # précepte : prime de risque des actions (Damodaran)


@app.callback()
def main() -> None:
    """Sous-commandes nommées."""


@app.command()
def fetch() -> None:
    """Companyfacts SEC + instantané de marché Yahoo + taux 10 ans de la Banque du Canada."""
    import json

    import requests

    from vlab import data

    data.fetch()
    resp = requests.get("https://www.bankofcanada.ca/valet/observations/BD.CDN.10YR.DQ.YLD/json?recent=1",
                        timeout=60)
    resp.raise_for_status()
    obs = resp.json()["observations"][0]
    snapshot = json.loads(data.MARKET.read_text())
    snapshot["taux_10_ans_canada"] = {"date": obs["d"], "valeur_pct": float(obs["BD.CDN.10YR.DQ.YLD"]["v"])}
    data.MARKET.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")
    hist = data.load_history()
    typer.echo(f"SEC : exercices {hist.index.min()} -> {hist.index.max()} ; "
               f"marché du {snapshot['date']} ; taux 10 ans {obs['d']} : {snapshot['taux_10_ans_canada']['valeur_pct']} %")


@app.command()
def build(out: Path = Path("results")) -> None:
    """Toute la chaîne : historique enrichi, WACC, DCF, DCF inversé, sensibilité, comparables, livrables."""
    import numpy as np
    import pandas as pd

    from vlab import data, model, report

    hist = model.enrich_history(data.load_history()).loc[2011:]
    market = data.load_market()
    cn = market["titres"]["CNR.TO"]
    price = float(cn["currentPrice"])
    shares_m = float(cn["sharesOutstanding"]) / 1e6
    last = hist.index.max()

    # composants du WACC, chacun avec son statut (repris dans le README et le mémo)
    rf = market["taux_10_ans_canada"]["valeur_pct"] / 100.0          # rapporté (BdC, daté)
    beta = float(cn["beta"])                                         # rapporté (Yahoo)
    debt = float(hist.loc[last, "dette_long_terme"])                 # mesuré (M$ CAD)
    cash = float(hist.loc[last, "tresorerie"])
    net_debt = debt - cash
    cost_debt = float((hist["interets"].tail(3) / hist["dette_long_terme"].tail(3)).mean())   # mesuré
    tax = float(hist["taux_impot_effectif"].tail(3).mean())          # mesuré
    equity_mv = price * shares_m
    wacc = model.wacc_from_components(rf, ERP, beta, cost_debt, tax, equity_mv, debt)

    rev = hist["revenus"].dropna()
    rev_cagr = float((rev.loc[last] / rev.loc[last - 10]) ** (1 / 10) - 1)   # mesuré, 10 ans d'étiquettes
    fcff = hist["fcff"].dropna()
    # croissance du FCFF lissée 3 ans aux deux bouts, exposant compté sur les ANNÉES (2021 manque)
    span = float(fcff.index[-3:].to_numpy().mean() - fcff.index[:3].to_numpy().mean())
    fcff_cagr = float((fcff.tail(3).mean() / fcff.head(3).mean()) ** (1 / span) - 1)
    fcff_base = float(fcff.tail(3).mean())                           # mesuré

    h = model.Hypotheses(fcff_base=fcff_base, wacc=wacc, g_initial=rev_cagr,
                         g_terminal=G_TERMINAL, dette_nette=net_debt, actions=shares_m)
    base_value = model.value_per_share(h)
    implied = model.implied_growth(price, h)
    waccs = [round(w, 3) for w in np.arange(0.06, 0.0951, 0.005)]
    sens = model.sensitivity(h, waccs, [0.01, 0.015, 0.02, 0.025, 0.03])

    ebitda = float((hist["resultat_exploitation"] + hist["amortissements"]).loc[last])
    eps = float(hist.loc[last, "bpa_dilue"])
    comps = model.comparables_table(market, ebitda, eps, net_debt, shares_m)

    tables = out / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    hist.round(3).to_csv(tables / "historique_enrichi.csv")
    sens.round(1).to_csv(tables / "sensibilite.csv")
    comps.round(2).to_csv(tables / "comparables.csv")
    hyp = pd.DataFrame([
        ("cours (CAD)", price, "rapporté", f"Yahoo, {market['date']}"),
        ("actions en circulation (millions)", shares_m, "rapporté", f"Yahoo, {market['date']}"),
        ("FCFF de départ (M$ CAD)", fcff_base, "mesuré", f"moyenne {last - 2}-{last}, SEC"),
        ("dette nette (M$ CAD)", net_debt, "mesuré", f"exercice {last}, SEC"),
        ("taux sans risque", rf, "rapporté", f"BdC 10 ans, {market['taux_10_ans_canada']['date']}"),
        ("prime de risque actions", ERP, "précepte", "Damodaran"),
        ("beta", beta, "rapporté", "Yahoo"),
        ("coût de la dette avant impôt", cost_debt, "mesuré", f"intérêts/dette, moyenne {last - 2}-{last}"),
        ("taux d'impôt effectif", tax, "mesuré", f"moyenne {last - 2}-{last}"),
        ("WACC", wacc, "modélisé", "composants ci-dessus"),
        ("croissance années 1-5 (scénario de base)", rev_cagr, "modélisé", "ancrée sur le TCAC des revenus 10 ans"),
        ("croissance perpétuelle", G_TERMINAL, "précepte", "cible d'inflation BdC"),
        ("valeur par action DCF (CAD)", base_value, "modélisé", "sortie du modèle"),
        ("croissance implicite dans le cours", implied, "modélisé", "DCF inversé"),
        ("TCAC FCFF réalisé", fcff_cagr, "mesuré", "lissé 3 ans aux deux bouts, période 2011-2025"),
    ], columns=["grandeur", "valeur", "statut", "source"])
    hyp.to_csv(tables / "hypotheses.csv", index=False)

    figs = out / "figures"
    figs.mkdir(parents=True, exist_ok=True)
    report.fig_historique(hist, figs / "historique_cn.png")
    grid = sens.to_numpy()
    report.fig_football(price, (float(np.nanmin(grid)), float(np.nanmax(grid))),
                        float(comps.loc["valeur_cn_implicite_par_action", "ev_ebitda"]),
                        float(comps.loc["valeur_cn_implicite_par_action", "pe"]),
                        base_value, figs / "football_field.png")
    report.fig_croissance_implicite(implied, fcff_cagr, rev_cagr, figs / "croissance_implicite.png")

    report.build_workbook(hist, h, sens, comps, market["date"], Path("reports/classeur_valorisation_cn.xlsx"))
    typer.echo(f"cours {price:.2f} $, DCF de base {base_value:.0f} $, croissance implicite "
               f"{100 * implied:.1f} % (réalisé FCFF {100 * fcff_cagr:.1f} %, revenus {100 * rev_cagr:.1f} %)")
    typer.echo(f"tables -> {tables}, figures -> {figs}, classeur -> reports/classeur_valorisation_cn.xlsx")


if __name__ == "__main__":
    app()
