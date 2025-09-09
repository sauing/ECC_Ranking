import pandas as pd

class AllRounderLeaderboard:
    HTML_PATH: str

    def __init__(self, season: str, club: str, html_path: str, bat_weight: float = 0.55, bowl_weight: float = 0.45):
        self.season = season
        self.club = club
        self.HTML_PATH = html_path
        self.bat_weight = float(bat_weight)
        self.bowl_weight = float(bowl_weight)

    def _best_per_player(self, df: pd.DataFrame,
                         points_col: str = "Points",
                         klasse_candidates: tuple[str, ...] = ("Klasse", "Klasse Mix", "klasse", "klasse_mix")
                         ) -> pd.DataFrame:
        if df is None or df.empty:
            return pd.DataFrame(columns=["Player", points_col, "Klasse"])
        klasse_col = next((c for c in klasse_candidates if c in df.columns), None)
        cols = ["Player", points_col] + ([klasse_col] if klasse_col else [])
        df2 = df[[c for c in cols if c in df.columns]].copy()
        df2[points_col] = pd.to_numeric(df2[points_col], errors="coerce").fillna(0)
        idx = df2.groupby("Player")[points_col].idxmax()
        best = df2.loc[idx].reset_index(drop=True)
        if klasse_col and klasse_col in best.columns:
            best.rename(columns={klasse_col: "Klasse"}, inplace=True)
        else:
            best["Klasse"] = ""
        return best[["Player", points_col, "Klasse"]]

    def compute(self, df_bat_scored: pd.DataFrame, df_bowl_scored: pd.DataFrame) -> pd.DataFrame:
        bat_best = self._best_per_player(df_bat_scored).rename(columns={"Points": "Bat Points", "Klasse": "Bat Klasse"})
        bowl_best = self._best_per_player(df_bowl_scored).rename(columns={"Points": "Bowl Points", "Klasse": "Bowl Klasse"})
        allr = pd.merge(bat_best, bowl_best, on="Player", how="outer")
        for c in ["Bat Points", "Bowl Points"]:
            if c not in allr.columns: allr[c] = 0
            allr[c] = pd.to_numeric(allr[c], errors="coerce").fillna(0).astype(int)

        allr["Bat %ile"] = 0.0
        mask_b = allr["Bat Points"] > 0
        if mask_b.any(): allr.loc[mask_b, "Bat %ile"] = allr.loc[mask_b, "Bat Points"].rank(pct=True, method="max")
        allr["Bowl %ile"] = 0.0
        mask_bo = allr["Bowl Points"] > 0
        if mask_bo.any(): allr.loc[mask_bo, "Bowl %ile"] = allr.loc[mask_bo, "Bowl Points"].rank(pct=True, method="max")

        allr["ARI"] = (1000.0 * (0.55 * allr["Bat %ile"] + 0.45 * allr["Bowl %ile"])).round(0).astype(int)

        keep = ["Player", "Bat Points", "Bowl Points", "Bat %ile", "Bowl %ile", "ARI", "Bat Klasse", "Bowl Klasse"]
        keep = [c for c in keep if c in allr.columns]
        allr = allr[keep].sort_values("ARI", ascending=False).reset_index(drop=True)

        allr.insert(0, "Club Ranking", (allr.index + 1).astype(int))
        allr.insert(1, "Badge", allr["Club Ranking"].map({1:"🥇",2:"🥈",3:"🥉"}).fillna(""))
        return allr

    @staticmethod
    def _table_html(df: pd.DataFrame) -> str:
        html = df.to_html(index=False, escape=False)
        for col in ["Club Ranking", "ARI", "Bat Points", "Bowl Points"]:
            html = html.replace(f"<th>{col}</th>", f'<th data-sort-method="number">{col}</th>')
        return html

    def generate_html(self, df_allr: pd.DataFrame) -> str:
        body = "<p>No all-rounder records found.</p>" if df_allr.empty else self._table_html(df_allr)
        return f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>ECC All-Rounder Leaderboard {self.season}</title>
  <style>
    body {{ font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; margin: 24px; }}
    h2 {{ margin-bottom: 0.5rem; }}
    table {{ border-collapse: collapse; width: 100%; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; }}
    th {{ background-color: #f2f2f2; cursor: pointer; }}
    tr:nth-child(even) {{ background-color:#fafafa; }}
    .meta {{ font-size: 0.95em; color: #555; margin-top: 1rem; }}
  </style>
  <script src="https://unpkg.com/tablesort@5.2.1/dist/tablesort.min.js"></script>
</head>
<body>
  <h2>ECC All-Rounder Leaderboard {self.season} — {self.club}</h2>
  {body}
  <script>document.querySelectorAll('table').forEach(t => new Tablesort(t));</script>
  <div class="meta">
    <b>How ARI is calculated:</b><br>
    • Best batting & best bowling ICC-style points per player (klasse-weighted).<br>
    • Convert to percentiles; ARI = 1000 × (0.55 × Bat %ile + 0.45 × Bowl %ile).<br>
    • Missing side counts as 0; badges show overall club rank.
  </div>
</body>
</html>"""

    def save_html(self, html: str):
        with open(self.HTML_PATH, "w", encoding="utf-8") as f:
            f.write(html)
