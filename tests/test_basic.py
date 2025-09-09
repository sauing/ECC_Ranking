import pandas as pd
from ecc_rankings.batting import BattingScraper


def test_combine_and_score_basic():
    sample = pd.DataFrame([
        {"KNCB Ranking": "1", "Klasse": "1e klasse", "Player": "Alice", "matches": "2", "innings": "2", "not_outs": "0", "Runs": "80", "highest": "80", "average": "40.0", "strike_rate": "80.0", "Season": 2025},
        {"KNCB Ranking": "2", "Klasse": "2e klasse", "Player": "Alice", "matches": "3", "innings": "3", "not_outs": "1", "Runs": "60", "highest": "30", "average": "30.0", "strike_rate": "75.0", "Season": 2025},
        {"KNCB Ranking": "1", "Klasse": "1e klasse", "Player": "Bob",   "matches": "1", "innings": "1", "not_outs": "0", "Runs": "10", "highest": "10", "average": "10.0", "strike_rate": "50.0", "Season": 2025},
    ])

    scraper = BattingScraper(html_path="")
    out = scraper.combine_and_score(sample)

    assert "Player" in out.columns
    assert "Points" in out.columns

    alice = out.loc[out["Player"] == "Alice"].iloc[0]
    bob = out.loc[out["Player"] == "Bob"].iloc[0]
    assert alice["Points"] >= bob["Points"]


def test_generate_html_contains_player():
    sample = pd.DataFrame([
        {"KNCB Ranking": "1", "Klasse": "1e klasse", "Player": "Charlie", "matches": "1", "innings": "1", "not_outs": "0", "Runs": "25", "highest": "25", "average": "25.0", "strike_rate": "60.0", "Season": 2025},
    ])
    scraper = BattingScraper(html_path="")
    html = scraper.generate_html(sample)
    assert "Charlie" in html
