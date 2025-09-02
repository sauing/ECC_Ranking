# ECC_Ranking: KNCB Stats Scraper

This project scrapes and ranks KNCB cricket stats for Eindhoven CC, generating sortable HTML reports for bowling and batting, with ICC-style points.

## Features
- Selenium-based scraping of KNCB stats (batting & bowling)
- ICC-style points calculation
- Sortable HTML output
- Modular, extensible Python project structure

## Usage

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the main script:**
   ```bash
   python -m ecc_ranking.main
   ```

3. **Output:**
   - `kncb_bowling_stats_2025.html`
   - `kncb_batting_stats_2025.html`

## Project Structure

- `ecc_ranking/` - Main package
  - `scraping/` - Scraper classes
  - `utils.py` - Selenium driver/service helpers
  - `config.py` - Configurations
  - `main.py` - Entrypoint
- `tests/` - Test suite

## Requirements
- Python 3.8+
- Google Chrome browser
- ChromeDriver (auto-managed or manual)

## Notes
- For ChromeDriver issues, see the error messages or [chromedriver downloads](https://chromedriver.chromium.org/downloads).
- For headless mode, edit `config.py`.

## License
MIT

## 📊 View Published Stats

- [Batting Stats 2025](https://sauing.github.io/ECC_Ranking/docs/kncb_batting_stats_2025.html)
- [Bowling Stats 2025](https://sauing.github.io/ECC_Ranking/docs/kncb_bowling_stats_2025.html)
