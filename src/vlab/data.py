"""Données : les états financiers par l'API XBRL de la SEC, le marché par Yahoo Finance.

Le Canadien National (CN) est coté à Toronto (CNR.TO) et à New York (CNI) : ses états financiers
normalisés (US GAAP, en dollars CANADIENS) sont donc servis par l'API publique companyfacts de la
SEC, sans compte ni clé, à partir de ses dépôts annuels. Chaque concept comptable (revenus,
résultat d'exploitation, flux de trésorerie, capex...) arrive en points datés ; le chargeur garde
les points couvrant un exercice complet et, en cas de re-publication, la valeur déposée en dernier.

Les données de marché (cours, actions en circulation, capitalisation) et les multiples des
comparables viennent de Yahoo Finance (usage personnel). Tout se télécharge par `vlab fetch`, rien
n'est commité ; un instantané daté des chiffres de marché est écrit en JSON pour que le reste de la
chaîne soit rejouable hors ligne.

Trou déclaré : l'exercice 2021 du CN est ABSENT du XBRL de la SEC (aucun point annuel dans
companyfacts ni dans l'API frames, constaté le 2026-08-28). Il reste vide dans les tableaux plutôt
que comblé, et les calculs de croissance comptent les années par leurs étiquettes, pas par leurs
positions.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

CIK = "0000016868"                    # Canadian National Railway Co (SEC)
TICKER = "CNR.TO"
PEERS = ["CP.TO", "UNP", "CSX", "NSC"]
UA = {"User-Agent": "Guillaume Vaudescal vaudescal.guillaumepro@gmail.com"}

RAW = Path("data/raw")
FACTS = RAW / "cn_companyfacts.json"
MARKET = RAW / "marche.json"

# Concepts US GAAP retenus, avec leurs replis (le concept de revenus change de nom en 2018, ASC 606)
CONCEPTS: dict[str, list[str]] = {
    "revenus": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    "resultat_exploitation": ["OperatingIncomeLoss"],
    "amortissements": ["DepreciationDepletionAndAmortization", "Depreciation"],
    "benefice_net": ["NetIncomeLoss"],
    "flux_exploitation": ["NetCashProvidedByUsedInOperatingActivities"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment"],
    "interets": ["InterestExpense", "InterestExpenseNonoperating"],
    "impots": ["IncomeTaxExpenseBenefit"],
    "resultat_avant_impots": ["IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest",
                              "IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments"],
    "dette_long_terme": ["LongTermDebt"],
    "tresorerie": ["CashAndCashEquivalentsAtCarryingValue"],
    "actions_diluees": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
}
FLOW = {"revenus", "resultat_exploitation", "amortissements", "benefice_net", "flux_exploitation",
        "capex", "interets", "impots", "resultat_avant_impots", "actions_diluees"}


def fetch(raw: Path = RAW) -> None:
    """Télécharge companyfacts (SEC) et un instantané de marché daté (Yahoo)."""
    import requests
    import yfinance as yf

    raw.mkdir(parents=True, exist_ok=True)
    resp = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{CIK}.json", headers=UA, timeout=120)
    resp.raise_for_status()
    FACTS.write_bytes(resp.content)

    snapshot: dict = {"date": pd.Timestamp.today().strftime("%Y-%m-%d"), "titres": {}}
    for t in [TICKER, *PEERS]:
        info = yf.Ticker(t).info
        snapshot["titres"][t] = {k: info.get(k) for k in (
            "currentPrice", "marketCap", "sharesOutstanding", "enterpriseValue",
            "trailingPE", "enterpriseToEbitda", "totalDebt", "totalCash", "beta", "currency")}
    MARKET.write_text(json.dumps(snapshot, indent=1), encoding="utf-8")


def _annual_points(fact: dict, flow: bool) -> pd.Series:
    """Les points d'un concept, un par exercice : durée d'un an pour les flux, fin d'exercice pour
    les stocks ; en cas de re-publication, la valeur déposée en dernier gagne."""
    unit = "CAD" if "CAD" in fact["units"] else list(fact["units"].keys())[0]
    rows: dict[int, tuple[str, float]] = {}
    for p in fact["units"][unit]:
        end = pd.Timestamp(p["end"])
        if flow:
            if "start" not in p:
                continue
            days = (end - pd.Timestamp(p["start"])).days
            if not 350 <= days <= 380:
                continue
        elif not (end.month == 12 and end.day == 31):
            continue
        year = end.year
        filed = p.get("filed", "")
        if year not in rows or filed >= rows[year][0]:
            rows[year] = (filed, float(p["val"]))
    return pd.Series({y: v for y, (_, v) in sorted(rows.items())})


def load_history(path: Path = FACTS) -> pd.DataFrame:
    """Le tableau annuel des postes retenus, en millions de CAD (actions en millions de titres)."""
    if not path.exists():
        raise FileNotFoundError(f"{path} absent : lancer d'abord `vlab fetch` (données non commitées)")
    facts = json.loads(path.read_text())["facts"]["us-gaap"]
    out = {}
    for name, concepts in CONCEPTS.items():
        series = [
            _annual_points(facts[c], name in FLOW)
            for c in concepts if c in facts
        ]
        if not series:
            continue
        merged = series[0]
        for s in series[1:]:
            merged = s.combine_first(merged)      # le concept le plus récent gagne sur le recouvrement
        out[name] = merged / 1e6
    df = pd.DataFrame(out)
    df.index.name = "exercice"
    return df


def load_market(path: Path = MARKET) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"{path} absent : lancer d'abord `vlab fetch`")
    return json.loads(path.read_text())
