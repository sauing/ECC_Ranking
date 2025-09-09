import time
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from .config import BOWLING_URLS, KLASSE_WEIGHTS, SEASON, CLUB_NAME
from .driver import get_driver
from .config import CHROME_PATH, HEADLESS, WINDOW_SIZE

class BowlingScraper:
    URLS = {
        "Eerste_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73934&season=19&team=136540",
        "Tweede_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73940&season=19",
        "Vierde_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73942&season=19",
    }
    HTML_PATH:str

    def __init__(self, html_path: str):
        self.HTML_PATH = html_path

    def scrape(self):
        """Scrapes bowling statistics for Eindhoven CC from KNCB website.

        Returns:
            pd.DataFrame: DataFrame containing scraped bowling statistics.
        """
        driver = get_driver(CHROME_PATH, HEADLESS, WINDOW_SIZE)
        all_data = []
        for klasse, url in BOWLING_URLS.items():
            driver.get(url)
            time.sleep(6)
            rows = driver.find_elements(By.XPATH, "//*[@id='page-wrap']/div[4]/div/div[4]/div/div")
            counter = 0
            for row in rows[1:]:
                if counter >= 10:
                    break
                cols = row.text.split("\n")
                if len(cols) > 8 and cols[2].strip() == CLUB_NAME:
                    all_data.append({
                        "KNCB Ranking": cols[0].strip(),
                        "Klasse": klasse,
                        "Player": cols[1].strip(),
                        "Matches": cols[3].strip(),
                        "Wickets": cols[6].strip(),
                        "Best": cols[7].strip(),
                        "Avg": cols[8].strip(),
                        "Eco": cols[9].strip(),
                        "Strike Rate": cols[10].strip(),
                        "Season": SEASON,
                    })
                    counter += 1
        driver.quit()
        return pd.DataFrame(all_data)

    def calculate_icc_points(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        ICC-like bowling score on ~0–1000 scale with klasse difficulty.
        Robust to missing/odd 'matches' so Points never silently zero out.
        """
        def _pick_numeric_series(df: pd.DataFrame, candidates: list[str], default: int | float = 0,
                                 as_int: bool = True) -> pd.Series:
            """
            Return the first existing column from candidates, coerced to numeric.
            Handles strings like '3 (T20)' by extracting the first number.
            If none found, returns a Series filled with default.
            """
            for name in candidates:
                if name in df.columns:
                    s = df[name]
                    # Extract first integer substring if it's string-like
                    if s.dtype == object:
                        s = s.astype(str).str.extract(r"(\d+)", expand=False)
                    s = pd.to_numeric(s, errors="coerce")
                    s = s.fillna(default)
                    return s.astype(int) if as_int else s.astype(float)
            return pd.Series(default, index=df.index, dtype=int if as_int else float)

        if df.empty:
            return df

        d = df.copy()

        # Core numerics (tolerant)
        d["Wickets"] = _pick_numeric_series(d, ["Wickets"], default=0, as_int=True)
        d["Avg"] = _pick_numeric_series(d, ["Avg", "Average"], default=40.0, as_int=False)
        d["Eco"] = _pick_numeric_series(d, ["Eco", "Economy"], default=6.5, as_int=False)
        d["Strike Rate"] = _pick_numeric_series(d, ["Strike Rate", "SR"], default=40.0, as_int=False)

        # Matches: try multiple headings / formats
        matches = _pick_numeric_series(d, ["matches", "Matches", "Mat", "M"], default=0, as_int=True)
        d["matches"] = matches

        # Best wickets (e.g., '5/20' → 5)
        if "BestWkts" in d:
            d["BestWkts"] = _pick_numeric_series(d, ["BestWkts"], default=0, as_int=True)
        else:
            if "Best" in d:
                wkts = d["Best"].astype(str).str.extract(r"^\s*(\d+)\s*/", expand=False)
                d["BestWkts"] = pd.to_numeric(wkts, errors="coerce").fillna(0).astype(int)
            else:
                d["BestWkts"] = pd.Series(0, index=d.index, dtype=int)

        # --- Components (diminishing returns via tanh) ---
        wickets_c = 400.0 * np.tanh(d["Wickets"] / 35.0)

        avg_impr = np.maximum(0.0, 40.0 - d["Avg"])
        avg_c = 250.0 * np.tanh(avg_impr / 25.0)

        eco_impr = np.maximum(0.0, 6.5 - d["Eco"])
        eco_c = 200.0 * np.tanh(eco_impr / 2.5)

        sr_impr = np.maximum(0.0, 40.0 - d["Strike Rate"])
        sr_c = 100.0 * np.tanh(sr_impr / 20.0)

        best_c = 50.0 * np.tanh(d["BestWkts"] / 6.0)

        raw = wickets_c + avg_c + eco_c + sr_c + best_c

        # Sample-size factor: if matches parsed as all zeros, use a safe floor instead of zeroing the table
        sf = np.tanh(d["matches"] / 6.0)
        if (sf == 0).all():
            # Use a conservative floor so short samples don't dominate but scores aren’t wiped out
            sf = pd.Series(0.6, index=d.index)  # tweakable: 0.5–0.7 is reasonable

        # Klasse multiplier
        w = d["Klasse"].map(KLASSE_WEIGHTS).fillna(1.00)

        d["Points"] = raw * sf * w
        d["Points"] = d["Points"].round(0).astype(int)
        return d

    def generate_html(self, df):
        """Generates an HTML table from the bowling statistics DataFrame (with 🥇🥈🥉 badges)."""
        df = self.calculate_icc_points(df)

        # Sort by Points and add Club Ranking + Badge
        df_sorted = df.sort_values("Points", ascending=False).reset_index(drop=True).copy()
        df_sorted.insert(0, "Club Ranking", (df_sorted.index + 1).astype(int))
        badge_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        df_sorted.insert(1, "Badge", df_sorted["Club Ranking"].map(badge_map).fillna(""))

        # Build HTML (escape=False so emoji render)
        html_table = df_sorted.to_html(index=False, escape=False)
        for col in ["Club Ranking", "Points", "Wickets", "matches", "Eco", "strike_rate"]:
            html_table = html_table.replace(f"<th>{col}</th>", f'<th data-sort-method="number">{col}</th>')
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>KNCB Bowling Stats 2025</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; cursor: pointer; }}
            </style>
            <script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
        </head>
        <body>
            <h2>KNCB Batting Stats {SEASON} — {CLUB_NAME}</h2>
            {html_table}
            <script>
                new Tablesort(document.querySelector("table"));
            </script>
            <br>
            <div style="font-size: 0.95em; color: #555;">
                  <b>Points Calculation (ECC model):</b><br>
                  Multi-factor with diminishing returns: wickets, bowling average (lower better), economy (lower better),
                  strike rate (lower better), best-innings wickets. Adjusted by sample size and klasse weights
                  (Eerste 1.15, Tweede 1.07, Vierde 1.00).
        </div>
        </body>
        </html>
        """
