import os

# Club & season
CLUB_NAME =  "Eindhoven CC"
SEASON = "2025"

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

# Scorecard URLs provided for Eindhoven fantasy extraction
SCORECARD_BATTING_URLS = [
    "https://matchcentre.kncb.nl/match/134453-7258356/scorecard/?period=2821922",
    "https://matchcentre.kncb.nl/match/134453-7325757/scorecard/?period=3192887",
    "https://matchcentre.kncb.nl/match/134453-7323292/scorecard/?period=2844072",
    "https://matchcentre.kncb.nl/match/134453-7326824/scorecard/?period=2882755",
]

SCORECARD_BOWLING_URLS = [
    "https://matchcentre.kncb.nl/match/134453-7258356/scorecard/?period=2820388",
    "https://matchcentre.kncb.nl/match/134453-7325757/scorecard/?period=3196879",
    "https://matchcentre.kncb.nl/match/134453-7323292/scorecard/?period=2838772",
    "https://matchcentre.kncb.nl/match/134453-7326824/scorecard/?period=2879841",
]

EINDHOVEN_NAME_MAP = {
    "a manohar": "aarav manohar",
    "a shenan": "aaron shenan",
    "a rajaraman": "abhinav rajaraman",
    "a chandurkar": "abhishek chandrukar",
    "a singh": "abhishek kumar singh",
    "a ladhad": "abhishek ladhad",
    "a bura": "aditya bura",
    "a ranjan": "amit ranjan",
    "a bindra": "amitoz bindra",
    "a ghai": "ankush ghai",
    "a shinde": "aryan shinde",
    "a malviya": "ashish malviya",
    "d vibhandik": "deovrat",
    "g saxena": "gaurav saxena",
    "g ponnampalam": "gobu",
    "h singh": "himanshu singh",
    "h ramesh babu": "hrishikesh ramesh babu",
    "i farooq": "irfaan farooq",
    "jk singh": "jk singh",
    "j k singh": "jk singh",
    "k kumar singh": "kamlesh singh",
    "k subramanian": "karthik subramanian",
    "k patel": "kishan patel",
    "m desai": "mahesh desai",
    "m sinha": "manirup sinha",
    "m robinson": "mark robinson",
    "m moolman": "milan moolman",
    "m karche": "mohseen karche",
    "n gandhi": "nisarg gandhi",
    "o jan": "obaid jan",
    "o mandem": "omkar mandem",
    "p patil": "pradeep patil",
    "p verma": "pranav verma",
    "p reddy": "praneeth reddy",
    "p tiwari": "prateek tiwari",
    "r patel": "ravi patel",
    "s singh": "saurabh singh",
    "s khoja": "shamshudeen khoja",
    "s shekhar": "shashank shekhar",
    "s parakala": "shravan parakala",
    "s trehan": "shrey trehan",
    "s ravi": "shreyas ravi",
    "s jaiswal": "sidhant jaiswal",
    "s dutta": "soumick dutta",
    "s mohanty": "soumya",
    "s ramesh": "sudarshan ramesh",
    "s kumar": "sudhir kumar",
    "s sahu": "sudipt sahu",
    "t sanap": "tirthak sanap",
    "u ahmed": "umair ahmed",
    "u kumar": "umesh",
    "m zafar": "usman",
    "v krishnan": "vijay krishnan",
    "v babu": "viknesh babu",
    "v vashishtha": "vikrant vashishtha",
    "v venkatesan": "vimalraj venkatesan",
    "v singh": "vivek singh",
    "y kamate": "yash kamate",
    "y singh": "yashwant singh",
    "z farooq": "zahid farooq",
    "a  bura": "aditya bura",
    "k  kumar singh": "kamlesh singh",
    "v vashishttha": "vikrant vashishtha",
    "j.k singh": "jk singh",
    "j k singh": "jk singh",
}
