# ECC Rankings (KNCB)

Scrape KNCB matchcentre stats for **Eindhoven CC**, compute ICC-style club rankings (klasse-weighted), and publish to **GitHub Pages** from the `docs/` folder.

## Quick start

```bash

python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
python -m ecc_rankings.run
```