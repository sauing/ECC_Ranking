from ecc_rankings.fantasy_points import FantasyRules, _name_aliases, _points_from_row, _resolve_name


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
    assert _resolve_name("J.K Singh", aliases) == "jk singh"
