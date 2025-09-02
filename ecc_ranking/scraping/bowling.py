import pandas as pd
import time
from selenium.webdriver.common.by import By
from ..utils import get_driver
from ..config import BOWLING_URLS, BOWLING_HTML_PATH, CLUB_NAME, SEASON

class BowlingScraper:
    def scrape(self):
        driver = get_driver()
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
                        "Wickets": int(cols[4].strip()),
                        "Best": cols[5].strip(),
                        "Avg": cols[6].strip(),
                        "Eco": cols[7].strip(),
                        "Strike Rate": cols[8].strip(),
                        "Season": SEASON,
                    })
                    counter += 1
        driver.quit()
        return pd.DataFrame(all_data)

    def calculate_icc_points(self, df):
        df["Wickets"] = pd.to_numeric(df["Wickets"], errors="coerce").fillna(0).astype(int)
        df["BestWkts"] = df["Best"].str.extract(r"(\d+)").fillna(0).astype(int)
        df["Eco"] = pd.to_numeric(df["Eco"], errors="coerce").fillna(0)
        df["Strike Rate"] = pd.to_numeric(df["Strike Rate"], errors="coerce").fillna(0)
        df["Points"] = (
            df["Wickets"] * 20 +
            df["BestWkts"] * 10 +
            (50 - df["Eco"]) * 5 +
            (100 - df["Strike Rate"]) * 2
        )
        return df

    def generate_html(self, df):
        df = self.calculate_icc_points(df)
        df_sorted = df.sort_values("Points", ascending=False).reset_index(drop=True)
        df_sorted.insert(0, "Club Ranking", (df_sorted.index + 1).astype(int))
        html_table = df_sorted.to_html(index=False)
        html_table = html_table.replace('<th>Club Ranking</th>', '<th data-sort-method="number">Club Ranking</th>')
        html_table = html_table.replace('<th>Points</th>', '<th data-sort-method="number">Points</th>')
        html_table = html_table.replace('<th>Wickets</th>', '<th data-sort-method="number">Wickets</th>')
        return html_table

    def save_html(self, html_table):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset=\"UTF-8\">
            <title>KNCB Bowling Stats 2025</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; cursor: pointer; }}
            </style>
            <script src=\"https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js\"></script>
        </head>
        <body>
            <h2>KNCB Bowling Stats 2025</h2>
            {html_table}
            <script>
                new Tablesort(document.querySelector(\"table\"));
            </script>
            <br>
            <div style=\"font-size: 0.95em; color: #555;\">
                <b>Points Calculation Reference:</b><br>
                Points = (Wickets × 20) + (Best wickets × 10) + (50 - Economy) × 5 + (100 - Strike Rate) × 2<br>
                <i>ICC-style points are calculated based on wickets, best bowling, economy rate, and strike rate.</i>
            </div>
        </body>
        </html>
        """
        with open(BOWLING_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html_content)
