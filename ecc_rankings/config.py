import os

# Club & season
CLUB_NAME = os.environ.get("ECC_CLUB", "Eindhoven CC")
SEASON = os.environ.get("ECC_SEASON", "2025")

# Output directory for GitHub Pages
OUTPUT_DIR = os.environ.get("ECC_OUTPUT_DIR", "docs")

# Klasse difficulty multipliers
KLASSE_WEIGHTS = {
    "Eerste_Klasse": 1.15,
    "Tweede_Klasse": 1.07,
    "Vierde_Klasse": 1.00,
}

# KNCB pages (team filter only where it works)
BOWLING_URLS = {
    "Eerste_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73934&season=19&team=136540",
    "Tweede_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73940&season=19",
    "Vierde_Klasse":  "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73942&season=19",
}

BATTING_URLS = {
    "Eerste_Klasse": "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73934&season=19",
    "Tweede_Klasse": "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73940&season=19",
    "Vierde_Klasse":  "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73942&season=19",
}

# Chrome
CHROME_PATH = os.environ.get("CHROME_PATH", "")  # leave empty to auto-manage
HEADLESS = os.environ.get("HEADLESS", "1") != "0"
WINDOW_SIZE = os.environ.get("WINDOW_SIZE", "1920,1080")
