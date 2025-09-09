import time
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from .config import BOWLING_URLS, KLASSE_WEIGHTS, SEASON, CLUB_NAME
from .driver import get_driver
from .config import CHROME_PATH, HEADLESS, WINDOW_SIZE

class BowlingScraper:
    HTML_PATH: str

    def __init__(self, html_path: str):
        self.HTML_PATH = html_path

    def scrape(self) -> pd.DataFrame:
        driver = get_driver(CHROME_PATH, HEADLESS, WINDOW_SIZE)
        all_data = []
        try:
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
                        # safe int parse for wickets
                        try:
                            wkts = int(str(cols[4]).strip())
                        except Exception:
                            wkts = 0
                        all_data.append({
                            "KNCB Ranking": cols[0].strip(),
                            "Klasse": klasse,
                            "Player": cols[1].strip(),
                            "Matches": cols[3].strip(),
                            "Wickets": wkts,
                            "Best": cols[5].strip(),
                            "Avg": cols[6].strip(),
                            "Eco": cols[7].strip(),
                            "Strike Rate": cols[8].strip(),
                            "Season": SEASON,
                        })
                        counter += 1
        finally:
            driver.quit()
        return pd.DataFrame(all_data)

    def calculate_icc_points(self, df: pd.DataFrame) -> pd.DataFrame:
        def _pick_numeric_series(d: pd.DataFrame, names: list[str], default=0, as_int=True) -> pd.Series:
            for n in names:
                if n in d.columns:
                    s = d[n]
                    if s.dtype == object:
                        s = s.astype(str).str.extract(r"(\d+\.?\d*)", expand=False)
                    s = pd.to_numeric(s, errors="coerce").fillna(default)
                    return s.astype(int) if as_int else s.astype(float)
            return pd.Series(default, index=d.index, dtype=int if as_int else float)

        if df.empty:
            return df.copy()

        d = df.copy()
        d["Wickets"] = _pick_numeric_series(d, ["Wickets"], 0, True)
        d["Avg"] = _pick_numeric_series(d, ["Avg", "Average"], 40.0, False)
        d["Eco"] = _pick_numeric_series(d, ["Eco", "Economy"], 6.5, False)
        d["Strike Rate"] = _pick_numeric_series(d, ["Strike Rate", "SR"], 40.0, False)
        d["matches"] = _pick_numeric_series(d, ["matches", "Matches", "Mat", "M"], 0, True)

        if "Best" in d:
            wkts = d["Best"].astype(str).str.extract(r"^\s*(\d+)\s*/", expand=False)
            d["BestWkts"] = pd.to_numeric(wkts, errors="coerce").fillna(0).astype(int)
        else:
            d["BestWkts"] = pd.Series(0, index=d.index, dtype=int)

        wickets_c = 400.0 * np.tanh(d["Wickets"] / 35.0)
        avg_c = 250.0 * np.tanh(np.maximum(0.0, 40.0 - d["Avg"]) / 25.0)
        eco_c = 200.0 * np.tanh(np.maximum(0.0, 6.5 - d["Eco"]) / 2.5)
        sr_c  = 100.0 * np.tanh(np.maximum(0.0, 40.0 - d["Strike Rate"]) / 20.0)
        best_c = 50.0 * np.tanh(d["BestWkts"] / 6.0)

        raw = wickets_c + avg_c + eco_c + sr_c + best_c
        sf = np.tanh(d["matches"] / 6.0)
        if (sf == 0).all():
            sf = pd.Series(0.6, index=d.index)
        w = d["Klasse"].map(KLASSE_WEIGHTS).fillna(1.0)

        d["Points"] = (raw * sf * w).round(0).astype(int)
        return d

    def generate_html(self, df: pd.DataFrame) -> str:
        d = self.calculate_icc_points(df).sort_values("Points", ascending=False).reset_index(drop=True).copy()
        d.insert(0, "Club Ranking", (d.index + 1).astype(int))
        d.insert(1, "Badge", d["Club Ranking"].map({1:"🥇",2:"🥈",3:"🥉"}).fillna(""))

        html_table = d.to_html(index=False, escape=False)
        for col in ["Club Ranking", "Points", "Wickets", "Matches", "Eco", "Strike Rate"]:
            html_table = html_table.replace(f"<th>{col}</th>", f'<th data-sort-method="number">{col}</th>')

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>KNCB Bowling Stats {SEASON}</title>
  <style>
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background-color: #f2f2f2; cursor: pointer; }}
    tr:nth-child(even) {{ background-color:#fafafa; }}
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }}
  </style>
  <script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
</head>
<body>
  <h2>KNCB Bowling Stats {SEASON} — {CLUB_NAME}</h2>
  {html_table}
  <script>new Tablesort(document.querySelector("table"));</script>
  <br>
  <div style="font-size:0.95em;color:#555;">
    <b>Points Calculation (ECC model):</b><br>
    Multi-factor with diminishing returns: wickets, bowling average, economy, strike rate, best-innings wickets.
    Adjusted by sample size and klasse weights (Eerste 1.15, Tweede 1.07, Vierde 1.00).
  </div>
</body>
</html>"""

    def save_html(self, html_page: str):
        with open(self.HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html_page)
