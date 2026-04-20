# ECC Rankings (KNCB)

[![CI](https://github.com/sauing/ECC_Ranking/actions/workflows/ci.yml/badge.svg)](https://github.com/sauing/ECC_Ranking/actions/workflows/ci.yml)

**[View Published Rankings Page](https://sauing.github.io/ECC_Ranking/)**

Scrape KNCB matchcentre stats for **Eindhoven CC**, compute ICC-style club rankings (klasse-weighted), and publish to **GitHub Pages** from the `docs/` folder.

## Quick start

> **Note:** Ensure that `requirements.txt` exists in the repository root before running setup or CI.

```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows
pip install -r requirements.txt
python -m ecc_rankings.run
```


## Fantasy points JSON

Generate Eindhoven fantasy-points JSON from KNCB scorecard batting+bowling URLs (only mapped Eindhoven players):

```bash
python -m ecc_rankings.run_fantasy
```

This writes `docs/ecc_fantasy_points_2025.json` using custom rules for runs, boundaries, wickets, maidens, economy and fielding. Ensure dependencies are installed with `pip install -r requirements.txt`.


## How to test fantasy generator

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pytest -q
python -m ecc_rankings.run_fantasy
python -m json.tool docs/ecc_fantasy_points_2025.json > /dev/null
```

Optional quick check for mapped players in output:

```bash
python - <<'PY2'
import json
with open("docs/ecc_fantasy_points_2025.json", encoding="utf-8") as f:
    d = json.load(f)
print("players:", len(d.get("playersWithPoints", [])))
print("sample:", d.get("playersWithPoints", [])[0] if d.get("playersWithPoints") else {})
PY2
```
