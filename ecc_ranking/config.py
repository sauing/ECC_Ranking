# Configuration for ECC Ranking project

CHROME_PATH = r'C:/Users/saurabh.singh2/Downloads/chromedriver-win64 (1)/chromedriver-win64/chromedriver'
HEADLESS = False

BOWLING_URLS = {
    "Eerste_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73934&season=19&team=136540",
    "Tweede_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73940&season=19",
    "Vierde_Klasse": "https://matchcentre.kncb.nl/statistics/bowling?entity=134453&grade=73942&season=19",
}
BOWLING_HTML_PATH = 'kncb_bowling_stats_2025.html'

BATTING_URLS = {
    "Eerste_Klasse": "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73934&season=19",
    "Tweede_Klasse": "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73940&season=19",
    "Vierde_Klasse": "https://matchcentre.kncb.nl/statistics/batting?entity=134453&grade=73942&season=19",
}
BATTING_HTML_PATH = 'kncb_batting_stats_2025.html'

CLUB_NAME = "Eindhoven CC"
SEASON = "2025"

