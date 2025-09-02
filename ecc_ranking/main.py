from .scraping.bowling import BowlingScraper
from .scraping.batting import BattingScraper

def main():
    bowling = BowlingScraper()
    df_bowling = bowling.scrape()
    html_bowling = bowling.generate_html(df_bowling)
    bowling.save_html(html_bowling)
    print("✅ Bowling HTML successfully saved as kncb_bowling_stats_2025.html")

    batting = BattingScraper()
    df_batting = batting.scrape()
    html_batting = batting.generate_html(df_batting)
    batting.save_html(html_batting)
    print("✅ Batting HTML successfully saved as kncb_batting_stats_2025.html")

if __name__ == "__main__":
    main()

