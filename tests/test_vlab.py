"""Le modèle sur cas fabriqués : actualisation à la main, DCF inversé, Gordon, chargeur SEC."""

import json

import numpy as np
import pandas as pd
import pytest

from vlab.model import (
    Hypotheses,
    enterprise_value,
    fcff_path,
    implied_growth,
    sensitivity,
    value_per_share,
    wacc_from_components,
)


def test_enterprise_value_matches_a_hand_discounting():
    # flux constants (croissances nulles) : EV = somme des VA + Gordon actualisé, refaits à la main
    h = Hypotheses(fcff_base=100.0, wacc=0.08, g_initial=0.0, g_terminal=0.0, annees=3,
                   dette_nette=0.0, actions=1.0)
    hand = sum(100.0 / 1.08**t for t in (1, 2, 3)) + (100.0 / 0.08) / 1.08**3
    assert enterprise_value(h) == pytest.approx(hand, rel=1e-12)


def test_fcff_path_fades_from_initial_to_terminal_growth():
    h = Hypotheses(fcff_base=100.0, wacc=0.08, g_initial=0.10, g_terminal=0.02, annees=10)
    flows = fcff_path(h)
    implied_g_last = flows[-1] / flows[-2] - 1.0
    assert implied_g_last == pytest.approx(0.02, abs=1e-12)      # la dernière année croît au terminal
    assert flows[0] == pytest.approx(110.0)


def test_gordon_requires_growth_below_wacc():
    h = Hypotheses(fcff_base=100.0, wacc=0.05, g_initial=0.02, g_terminal=0.06)
    with pytest.raises(ValueError):
        enterprise_value(h)


def test_implied_growth_inverts_the_dcf():
    h = Hypotheses(fcff_base=100.0, wacc=0.08, g_initial=0.05, g_terminal=0.02,
                   dette_nette=500.0, actions=10.0)
    price = value_per_share(h)
    g = implied_growth(price, h)
    assert g == pytest.approx(0.05, abs=1e-6)                    # on retrouve la croissance de départ


def test_sensitivity_is_monotonic_in_wacc_and_growth():
    h = Hypotheses(fcff_base=100.0, wacc=0.08, g_initial=0.04, g_terminal=0.02, actions=10.0)
    s = sensitivity(h, [0.06, 0.08, 0.10], [0.01, 0.02, 0.03])
    col = s[0.02].dropna()
    assert col.is_monotonic_decreasing                           # plus le WACC monte, moins ça vaut
    row = s.loc[0.08].dropna()
    assert row.is_monotonic_increasing                           # plus g monte, plus ça vaut


def test_wacc_blends_the_two_costs():
    w = wacc_from_components(rf=0.03, erp=0.05, beta=1.0, cost_debt=0.05, tax=0.25,
                             equity_mv=750.0, debt_mv=250.0)
    assert w == pytest.approx(0.75 * 0.08 + 0.25 * 0.05 * 0.75, rel=1e-12)


def test_loader_keeps_full_year_points_and_latest_filing(tmp_path):
    from vlab import data

    facts = {"facts": {"us-gaap": {
        "Revenues": {"units": {"CAD": [
            {"start": "2020-01-01", "end": "2020-12-31", "val": 100e6, "filed": "2021-02-01"},
            {"start": "2020-01-01", "end": "2020-12-31", "val": 101e6, "filed": "2022-02-01"},
            {"start": "2020-10-01", "end": "2020-12-31", "val": 30e6, "filed": "2021-02-01"},
        ]}},
        "OperatingIncomeLoss": {"units": {"CAD": [
            {"start": "2020-01-01", "end": "2020-12-31", "val": 40e6, "filed": "2021-02-01"},
        ]}},
        "CashAndCashEquivalentsAtCarryingValue": {"units": {"CAD": [
            {"end": "2020-12-31", "val": 5e6, "filed": "2021-02-01"},
            {"end": "2020-06-30", "val": 9e6, "filed": "2021-02-01"},
        ]}},
    }}}
    p = tmp_path / "facts.json"
    p.write_text(json.dumps(facts))
    hist = data.load_history(p)
    assert hist.loc[2020, "revenus"] == pytest.approx(101.0)     # la re-publication gagne, T4 écarté
    assert hist.loc[2020, "tresorerie"] == pytest.approx(5.0)    # le stock de fin d'exercice seulement


def test_enrich_history_computes_fcff():
    from vlab.model import enrich_history

    h = pd.DataFrame({"revenus": [100.0], "resultat_exploitation": [40.0], "flux_exploitation": [50.0],
                      "capex": [20.0], "interets": [4.0], "impots": [9.0],
                      "resultat_avant_impots": [36.0], "benefice_net": [27.0],
                      "actions_diluees": [10.0]}, index=[2020])
    e = enrich_history(h)
    assert e.loc[2020, "taux_impot_effectif"] == pytest.approx(0.25)
    assert e.loc[2020, "fcff"] == pytest.approx(50.0 + 4.0 * 0.75 - 20.0)
    assert e.loc[2020, "bpa_dilue"] == pytest.approx(2.7)
    assert not np.isnan(e.loc[2020, "marge_exploitation_pct"])
