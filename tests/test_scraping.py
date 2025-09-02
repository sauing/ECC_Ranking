import unittest
from ecc_ranking.scraping.bowling import BowlingScraper
from ecc_ranking.scraping.batting import BattingScraper
import pandas as pd

class TestBowlingScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = BowlingScraper()
        # Sample data for testing ICC points calculation
        self.sample_data = pd.DataFrame([
            {
                "KNCB Ranking": "1",
                "Klasse": "Eerste_Klasse",
                "Player": "Test Player",
                "Matches": "5",
                "Wickets": 10,
                "Best": "5/20",
                "Avg": "15.0",
                "Eco": "4.5",
                "Strike Rate": "25.0",
                "Season": "2025",
            }
        ])

    def test_calculate_icc_points(self):
        df = self.scraper.calculate_icc_points(self.sample_data.copy())
        self.assertIn("Points", df.columns)
        # Points = (10*20) + (5*10) + (50-4.5)*5 + (100-25)*2 = 200+50+227.5+150 = 627.5
        self.assertAlmostEqual(df.loc[0, "Points"], 627.5, places=1)

class TestBattingScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = BattingScraper()
        # Sample data for testing ICC points calculation
        self.sample_data = pd.DataFrame([
            {
                "KNCB Ranking": "1",
                "Klasse": "Eerste_Klasse",
                "Player": "Test Player",
                "matches": "5",
                "innings": "5",
                "not_outs": "1",
                "Runs": "200",
                "highest": "100*",
                "average": "50.0",
                "strike_rate": "120.0",
                "Season": "2025",
            }
        ])

    def test_calculate_icc_points(self):
        df = self.scraper.calculate_icc_points(self.sample_data.copy())
        self.assertIn("Points", df.columns)
        # Points = 200 + (50*2) + (120*0.5) = 200+100+60 = 360
        self.assertAlmostEqual(df.loc[0, "Points"], 360.0, places=1)

if __name__ == "__main__":
    unittest.main()
