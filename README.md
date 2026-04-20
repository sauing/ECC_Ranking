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
