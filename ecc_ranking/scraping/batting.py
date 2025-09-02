import pandas as pd
import time
from selenium.webdriver.common.by import By
from ..utils import get_driver
from ..config import BATTING_URLS, BATTING_HTML_PATH, CLUB_NAME, SEASON

class BattingScraper:
    def scrape(self):
        driver = get_driver()
        all_data = []
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
                        "not_outs" : cols[5].strip(),
                        "Runs": cols[6].strip(),
                        "highest" : cols[7].strip(),
                        "average" : cols[8].strip(),
                        "strike_rate" : cols[9].strip(),
                        "Season": SEASON,
                    })
                    counter += 1
        driver.quit()
        return pd.DataFrame(all_data)

    def calculate_icc_points(self, df):
        df["Runs"] = pd.to_numeric(df["Runs"], errors="coerce").fillna(0).astype(int)
        df["average"] = pd.to_numeric(df["average"], errors="coerce").fillna(0)
        df["strike_rate"] = pd.to_numeric(df["strike_rate"], errors="coerce").fillna(0)
        df["Points"] = (
            df["Runs"] +
            df["average"] * 2 +
            df["strike_rate"] * 0.5
        )
        return df

    def generate_html(self, df):
        df = self.calculate_icc_points(df)
        df_sorted = df.sort_values("Points", ascending=False).reset_index(drop=True)
        df_sorted.insert(0, "Club Ranking", (df_sorted.index + 1).astype(int))
        html_table = df_sorted.to_html(index=False)
        html_table = html_table.replace('<th>Club Ranking</th>', '<th data-sort-method="number">Club Ranking</th>')
        html_table = html_table.replace('<th>Points</th>', '<th data-sort-method="number">Points</th>')
        html_table = html_table.replace('<th>Runs</th>', '<th data-sort-method="number">Runs</th>')
        return html_table

    def save_html(self, html_table):
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset=\"UTF-8\">
            <title>KNCB Batting Stats 2025</title>
            <style>
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; }}
                th {{ background-color: #f2f2f2; cursor: pointer; }}
            </style>
            <script src=\"https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js\"></script>
        </head>
        <body>
            <h2>KNCB Batting Stats 2025</h2>
            {html_table}
            <script>
                new Tablesort(document.querySelector(\"table\"));
            </script>
            <br>
            <div style=\"font-size: 0.95em; color: #555;\">
                <b>Points Calculation Reference:</b><br>
                Points = Runs + (Average × 2) + (Strike Rate × 0.5)<br>
                <i>ICC-style points are calculated based on runs, average, and strike rate.</i>
            </div>
        </body>
        </html>
        """
        with open(BATTING_HTML_PATH, 'w', encoding='utf-8') as f:
            f.write(html_content)
