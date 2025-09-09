# ECC Rankings (KNCB)

Scrape KNCB matchcentre stats for **Eindhoven CC**, compute ICC-style club rankings (klasse-weighted), and publish to **GitHub Pages** from the `docs/` folder.

## Quick start

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
python -m ecc_rankings.run
```

## Published Stats Pages

The following pages are published via GitHub Pages from the `docs/` folder:

- [Allrounder Stats 2025](docs/kncb_allrounder_stats_2025.html)
- [Batting Stats 2025](docs/kncb_batting_stats_2025.html)
- [Bowling Stats 2025](docs/kncb_bowling_stats_2025.html)
