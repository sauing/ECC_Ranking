import pandas as pd

from ecc_rankings.fantasy_points import FantasyRules, _choose_col, _name_aliases, _points_from_row, _resolve_name, _safe_read_tables


class _FakeDriver:
    def __init__(self, html: str):
        self.page_source = html

    def get(self, _url: str):
        return None


def test_points_from_row_full_case():
    rules = FantasyRules()
    row = {
        "runs": 102,
        "Four": 10,
        "Sixes": 3,
        "Overs": 4,
        "Maiden": 1,
        "Economy": 2.8,
        "wickets": 5,
        "catches": 1,
        "run_outs_direct": 1,
        "run_outs_shared": 1,
    }
    assert _points_from_row(row, rules) == 262


def test_points_economy_penalty_applies_only_after_4_overs():
    rules = FantasyRules()
    row = {
        "runs": 0,
        "Four": 0,
        "Sixes": 0,
        "Overs": 3.5,
        "Maiden": 0,
        "Economy": 14,
        "wickets": 1,
        "catches": 0,
        "run_outs_direct": 0,
        "run_outs_shared": 0,
    }
    assert _points_from_row(row, rules) == 20


def test_name_mapping_resolves_initials_and_dots():
    aliases = _name_aliases()
    assert _resolve_name("A Manohar", aliases) == "aarav manohar"
    assert _resolve_name("A MANOHAR", aliases) == "aarav manohar"
    assert _resolve_name("J.K Singh", aliases) == "jk singh"


def test_safe_read_tables_falls_back_to_driver_html(monkeypatch):
    original_read_html = pd.read_html

    def _fake_read_html(src):
        if isinstance(src, str) and src.startswith("http"):
            raise ValueError("No tables found")
        return original_read_html(src)

    monkeypatch.setattr("pandas.read_html", _fake_read_html)
    html = "<table><tr><th>Player</th><th>R</th></tr><tr><td>A Manohar</td><td>50</td></tr></table>"
    tables = _safe_read_tables("http://dummy", driver=_FakeDriver(html))
    assert len(tables) == 1
    assert isinstance(tables[0], pd.DataFrame)
    assert list(tables[0].columns) == ["Player", "R"]


def test_name_mapping_fallback_keeps_unmapped_player():
    aliases = _name_aliases()
    assert _resolve_name("New Player", aliases) == "New Player"
    assert _resolve_name("Extras", aliases) is None


def test_choose_col_handles_fuzzy_headers():
    df = pd.DataFrame(columns=["Batting R", "Balls (B)", "4s count", "Wickets W"])
    assert _choose_col(df, ("R", "Runs")) == "Batting R"
    assert _choose_col(df, ("B", "BF")) == "Balls (B)"
    assert _choose_col(df, ("W", "Wkts")) == "Wickets W"
