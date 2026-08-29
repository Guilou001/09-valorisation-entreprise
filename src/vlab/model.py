"""Le modèle : flux de trésorerie disponibles, DCF sous hypothèses statuées, et DCF inversé.

Le DCF, l'actualisation des flux de trésorerie disponibles futurs, répond à « que vaut l'entreprise
si mes hypothèses sont bonnes ». Son inverse, la pièce maîtresse du dépôt, répond à la question la
plus utile : « quelle croissance le prix d'aujourd'hui suppose-t-il », qu'on peut alors comparer à
ce que l'entreprise a réellement fait sur dix ans. Toutes les hypothèses portent leur statut
(mesuré, rapporté, précepte, modélisé), et la sensibilité est systématique.

Définitions employées, en une ligne chacune :
- FCFF (free cash flow to the firm), l'argent que l'exploitation laisse après investissements,
  avant toute rémunération des prêteurs : flux d'exploitation + intérêts x (1 - taux d'impôt) - capex.
- WACC, le coût moyen pondéré du capital, le taux qui mélange ce qu'exigent actionnaires et
  prêteurs, au prorata de leurs poids en valeur de marché.
- Valeur terminale de Gordon : le flux de l'année suivante divisé par (WACC - croissance perpétuelle),
  valable seulement si la croissance perpétuelle reste sous le WACC.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize


def enrich_history(h: pd.DataFrame) -> pd.DataFrame:
    """Les colonnes dérivées : marges, FCF, FCFF, taux d'impôt effectif, BPA."""
    df = h.copy()
    df["marge_exploitation_pct"] = 100.0 * df["resultat_exploitation"] / df["revenus"]
    df["fcf"] = df["flux_exploitation"] - df["capex"]
    df["taux_impot_effectif"] = (df["impots"] / df["resultat_avant_impots"]).clip(0.0, 0.5)
    df["fcff"] = df["flux_exploitation"] + df["interets"] * (1.0 - df["taux_impot_effectif"]) - df["capex"]
    df["bpa_dilue"] = df["benefice_net"] / df["actions_diluees"]
    df["capex_sur_revenus_pct"] = 100.0 * df["capex"] / df["revenus"]
    return df


@dataclass(frozen=True)
class Hypotheses:
    """Chaque champ porte son statut dans le README et le mémo ; rien n'est implicite."""
    fcff_base: float              # M$ CAD, mesuré (moyenne des 3 derniers exercices)
    wacc: float                   # modélisé, composants statués
    g_initial: float              # modélisé : croissance des 5 premières années
    g_terminal: float             # précepte : croissance perpétuelle (PIB nominal de long terme)
    annees: int = 10              # les 5 dernières années glissent de g_initial vers g_terminal
    dette_nette: float = 0.0      # M$ CAD, mesuré (dette long terme - trésorerie)
    actions: float = 1.0          # millions de titres, rapporté (Yahoo, daté)


def fcff_path(h: Hypotheses) -> np.ndarray:
    """Les flux projetés : g_initial cinq ans, puis fondu linéaire vers g_terminal."""
    growths = []
    for t in range(1, h.annees + 1):
        if t <= 5:
            growths.append(h.g_initial)
        else:
            w = (t - 5) / (h.annees - 5)
            growths.append((1 - w) * h.g_initial + w * h.g_terminal)
    return h.fcff_base * np.cumprod(1.0 + np.array(growths))


def enterprise_value(h: Hypotheses) -> float:
    """La somme actualisée des flux projetés plus la valeur terminale de Gordon."""
    if h.g_terminal >= h.wacc:
        raise ValueError("la croissance perpétuelle doit rester sous le WACC (Gordon)")
    flows = fcff_path(h)
    discount = (1.0 + h.wacc) ** np.arange(1, h.annees + 1)
    pv_flows = float((flows / discount).sum())
    terminal = flows[-1] * (1.0 + h.g_terminal) / (h.wacc - h.g_terminal)
    return pv_flows + float(terminal / discount[-1])


def value_per_share(h: Hypotheses) -> float:
    return (enterprise_value(h) - h.dette_nette) / h.actions


def implied_growth(price: float, h: Hypotheses) -> float:
    """Le DCF inversé : la croissance initiale qui rend la valeur par action égale au cours."""
    def gap(g: float) -> float:
        hh = Hypotheses(fcff_base=h.fcff_base, wacc=h.wacc, g_initial=g, g_terminal=h.g_terminal,
                        annees=h.annees, dette_nette=h.dette_nette, actions=h.actions)
        return value_per_share(hh) - price

    return float(optimize.brentq(gap, -0.20, 0.30, xtol=1e-8))


def sensitivity(h: Hypotheses, waccs: list[float], g_terminals: list[float]) -> pd.DataFrame:
    """La valeur par action pour chaque couple (WACC, croissance perpétuelle) admissible."""
    rows = {}
    for w in waccs:
        rows[w] = {g: (np.nan if g >= w else value_per_share(
            Hypotheses(h.fcff_base, w, h.g_initial, g, h.annees, h.dette_nette, h.actions)))
            for g in g_terminals}
    out = pd.DataFrame(rows).T
    out.index.name = "wacc"
    out.columns.name = "g_terminal"
    return out


def wacc_from_components(rf: float, erp: float, beta: float, cost_debt: float, tax: float,
                         equity_mv: float, debt_mv: float) -> float:
    """WACC = poids des fonds propres x (rf + beta x ERP) + poids de la dette x coût x (1 - impôt)."""
    total = equity_mv + debt_mv
    ke = rf + beta * erp
    kd = cost_debt * (1.0 - tax)
    return float((equity_mv / total) * ke + (debt_mv / total) * kd)


def comparables_table(market: dict, cn_ebitda: float, cn_eps: float, cn_net_debt: float,
                      cn_shares: float) -> pd.DataFrame:
    """Les multiples des pairs (Yahoo, datés) et la valeur de CN qu'impliquerait leur médiane."""
    rows = []
    for t, d in market["titres"].items():
        rows.append({"titre": t, "ev_ebitda": d.get("enterpriseToEbitda"), "pe": d.get("trailingPE")})
    df = pd.DataFrame(rows).set_index("titre")
    peers = df.drop(index="CNR.TO")
    med_ev, med_pe = peers["ev_ebitda"].median(), peers["pe"].median()
    df.loc["mediane_pairs"] = [med_ev, med_pe]
    df.loc["valeur_cn_implicite_par_action"] = [
        (med_ev * cn_ebitda - cn_net_debt) / cn_shares,
        med_pe * cn_eps,
    ]
    return df
