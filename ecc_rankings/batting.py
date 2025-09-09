import time
import numpy as np
import pandas as pd
from selenium.webdriver.common.by import By
from .config import BATTING_URLS, KLASSE_WEIGHTS, SEASON, CLUB_NAME
from .driver import get_driver
from .config import CHROME_PATH, HEADLESS, WINDOW_SIZE

class BattingScraper:
    HTML_PATH: str

    def __init__(self, html_path: str):
        self.HTML_PATH = html_path

    def scrape(self) -> pd.DataFrame:
        driver = get_driver(CHROME_PATH, HEADLESS, WINDOW_SIZE)
        all_data = []
        try:
            for klasse, url in BATTING_URLS.items():
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
                            "matches": cols[3].strip(),
                            "innings": cols[4].strip(),
                            "not_outs": cols[5].strip(),
                            "Runs": cols[6].strip(),
                            "highest": cols[7].strip(),
                            "average": cols[8].strip(),
                            "strike_rate": cols[9].strip(),
                            "Season": SEASON,
                        })
                        counter += 1
        finally:
            driver.quit()
        return pd.DataFrame(all_data)

    # Merge across klassen and recompute once per player
    def combine_and_score(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df.copy()

        d = df.copy()
        d["Runs"] = pd.to_numeric(d.get("Runs"), errors="coerce").fillna(0).astype(int)
        d["average"] = pd.to_numeric(d.get("average"), errors="coerce").fillna(0.0)
        d["strike_rate"] = pd.to_numeric(d.get("strike_rate"), errors="coerce").fillna(0.0)
        d["innings"] = pd.to_numeric(d.get("innings"), errors="coerce").fillna(0).astype(int)
        d["not_outs"] = pd.to_numeric(d.get("not_outs"), errors="coerce").fillna(0).astype(int)
        matches_col = "matches" if "matches" in d.columns else ("Matches" if "Matches" in d.columns else None)
        d["matches"] = pd.to_numeric(d[matches_col], errors="coerce").fillna(0).astype(int) if matches_col else 0
        if "highest" in d.columns:
            hs = d["highest"].astype(str).str.extract(r"(\d+)", expand=False)
            d["highest_num"] = pd.to_numeric(hs, errors="coerce").fillna(0).astype(int)
        else:
            d["highest_num"] = 0

        valid_sr = d["strike_rate"] > 0
        d["balls_est"] = np.where(valid_sr, d["Runs"] * 100.0 / d["strike_rate"], np.nan)
        d["klasse_w"] = d["Klasse"].map(KLASSE_WEIGHTS).fillna(1.0)

        rows = []
        for player, g in d.groupby("Player", dropna=False):
            runs_total = int(g["Runs"].sum())
            innings_total = int(g["innings"].sum())
            notouts_total = int(g["not_outs"].sum())
            matches_total = int(g["matches"].sum())
            highest_total = int(g["highest_num"].max()) if len(g) else 0

            balls_total = g["balls_est"].sum(skipna=True)
            if pd.isna(balls_total) or balls_total <= 0:
                sr_total = float((g["strike_rate"] * g["Runs"]).sum() / max(1, g["Runs"].sum())) if g["Runs"].sum() > 0 else 0.0
            else:
                sr_total = float(100.0 * runs_total / balls_total)

            outs = max(1, innings_total - notouts_total)
            avg_total = float(runs_total / outs) if runs_total > 0 else 0.0
            w_combined = float((g["matches"] * g["klasse_w"]).sum() / matches_total) if matches_total > 0 else 1.0

            dom_klasse = ""
            if matches_total > 0:
                km = g.groupby("Klasse")["matches"].sum().sort_values(ascending=False)
                dom_klasse = km.index[0] if len(km) else ""

            runs_c = 300.0 * np.tanh(runs_total / 600.0)
            avg_c  = 350.0 * np.tanh(avg_total / 75.0)
            sr_c   = 200.0 * np.tanh(sr_total / 130.0)
            no_rate = (notouts_total / max(1, innings_total)) if innings_total > 0 else 0.0
            cons_c = 100.0 * np.tanh(no_rate / 0.4)
            milestone = 60.0 if highest_total >= 100 else (25.0 if highest_total >= 50 else 0.0)

            raw = runs_c + avg_c + sr_c + cons_c + milestone
            sf  = np.tanh(matches_total / 6.0)
            points = int(round(raw * sf * w_combined))

            rows.append({
                "Player": player,
                "Runs": runs_total,
                "innings": innings_total,
                "not_outs": notouts_total,
                "matches": matches_total,
                "highest": highest_total,
                "average": round(avg_total, 2),
                "strike_rate": round(sr_total, 2),
                "Klasse Mix": dom_klasse,
                "Klasse Weight": round(w_combined, 3),
                "Points": points,
                "Season": SEASON,
            })
        return pd.DataFrame(rows)

    def generate_html(self, df: pd.DataFrame) -> str:
        d = self.combine_and_score(df).sort_values("Points", ascending=False).reset_index(drop=True).copy()
        d.insert(0, "Club Ranking", (d.index + 1).astype(int))
        d.insert(1, "Badge", d["Club Ranking"].map({1:"🥇",2:"🥈",3:"🥉"}).fillna(""))

        html_table = d.to_html(index=False, escape=False)
        for col in ["Club Ranking", "Points", "Runs", "matches", "average", "strike_rate"]:
            html_table = html_table.replace(f"<th>{col}</th>", f'<th data-sort-method="number">{col}</th>')

        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>KNCB Batting Stats {SEASON}</title>
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
  <h2>KNCB Batting Stats {SEASON} — {CLUB_NAME}</h2>
  {html_table}
  <script>new Tablesort(document.querySelector("table"));</script>
  <br>
  <div style="font-size:0.95em;color:#555;">
    <b>Scoring & merging:</b><br>
    Player appears once: stats merged across klassen (runs/inn/not-outs/matches summed; SR/AVG recomputed; highest=max).
    Klasse difficulty = match-weighted average; ICC-style multi-factor (tanh) score with sample-size.
  </div>
</body>
</html>"""

    def save_html(self, html_page: str):
        with open(self.HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html_page)
