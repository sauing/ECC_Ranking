from __future__ import annotations

import json
import re
import time
from dataclasses import dataclass
from datetime import date
from typing import Any

import pandas as pd
from selenium.webdriver.common.by import By

from .config import (
    CHROME_PATH,
    CLUB_NAME,
    EINDHOVEN_NAME_MAP,
    HEADLESS,
    SCORECARD_BATTING_URLS,
    SCORECARD_BOWLING_URLS,
    WINDOW_SIZE,
)
from .driver import get_driver


@dataclass(frozen=True)
class FantasyRules:
    run: int = 1
    four: int = 1
    six: int = 2
    fifty_bonus: int = 4
    hundred_bonus: int = 8
    wicket: int = 20
    maiden: int = 2
    three_wicket_bonus: int = 4
    five_wicket_bonus: int = 8
    ten_wicket_bonus: int = 16
    econ_under3: int = 2
    econ_over6: int = -2
    econ_over8: int = -4
    econ_over12: int = -8
    catch: int = 8
    runout_direct: int = 8
    runout_shared: int = 4


def _to_num(v: Any, default: float = 0.0) -> float:
    if v is None:
        return default
    s = str(v).strip().replace("*", "")
    if not s:
        return default
    try:
        return float(s)
    except ValueError:
        m = re.search(r"-?\d+(?:\.\d+)?", s)
        return float(m.group(0)) if m else default


def _canon_name(name: Any) -> str:
    s = str(name or "").strip().lower()
    s = s.replace(".", " ")
    s = re.sub(r"\s+", " ", s)
    return s


def _name_aliases() -> dict[str, str]:
    return {_canon_name(k): v for k, v in EINDHOVEN_NAME_MAP.items()}


def _resolve_name(name: Any, aliases: dict[str, str]) -> str | None:
    k = _canon_name(name)
    if not k:
        return None
    if k in aliases:
        return aliases[k]

    # Fallback for scorecards like "A Manohar" / "J K Singh"
    compact = re.sub(r"\s+", " ", k)
    if compact in aliases:
        return aliases[compact]
    return None


def _choose_col(df: pd.DataFrame, candidates: tuple[str, ...]) -> str | None:
    lowered = {str(c).strip().lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in lowered:
            return lowered[cand.lower()]
    return None


def _is_batting_table(df: pd.DataFrame) -> bool:
    c_runs = _choose_col(df, ("R", "Runs"))
    c_balls = _choose_col(df, ("B", "BF", "Balls"))
    c_fours = _choose_col(df, ("4s", "4"))
    c_sixes = _choose_col(df, ("6s", "6"))
    return bool(c_runs and c_balls and c_fours and c_sixes)


def _is_bowling_table(df: pd.DataFrame) -> bool:
    c_overs = _choose_col(df, ("O", "Overs"))
    c_maid = _choose_col(df, ("M", "Mdns", "Maidens"))
    c_runs = _choose_col(df, ("R", "Runs"))
    c_wkts = _choose_col(df, ("W", "Wkts", "Wickets"))
    return bool(c_overs and c_maid and c_runs and c_wkts)


def _tables_from_rendered_div_rows(driver) -> list[pd.DataFrame]:
    rows = driver.find_elements(By.XPATH, "//*[@id='page-wrap']/div[4]/div/div[4]/div/div")
    if not rows:
        return []
    raw = [r.text.split("\n") for r in rows if r.text.strip()]
    if len(raw) < 2:
        return []
    header = raw[0]
    body = [r[: len(header)] for r in raw[1:]]
    return [pd.DataFrame(body, columns=header)]


def _safe_read_tables(url: str, driver=None) -> list[pd.DataFrame]:
    try:
        tables = pd.read_html(url)
        if tables:
            return tables
    except ValueError:
        pass

    if driver is None:
        return []

    driver.get(url)
    time.sleep(3)
    try:
        tables = pd.read_html(driver.page_source)
        if tables:
            return tables
    except ValueError:
        pass

    return _tables_from_rendered_div_rows(driver)


def _batting_from_url(url: str, aliases: dict[str, str], driver=None) -> pd.DataFrame:
    out = []
    tables = _safe_read_tables(url, driver=driver)
    for df in tables:
        if not _is_batting_table(df):
            continue

        player_col = df.columns[0]
        c_runs = _choose_col(df, ("R", "Runs"))
        c_balls = _choose_col(df, ("B", "BF", "Balls"))
        c_fours = _choose_col(df, ("4s", "4"))
        c_sixes = _choose_col(df, ("6s", "6"))

        for _, r in df.iterrows():
            full = _resolve_name(r.get(player_col), aliases)
            if not full:
                continue
            runs = int(_to_num(r.get(c_runs, 0)))
            out.append(
                {
                    "player_name": full,
                    "runs": runs,
                    "Four": int(_to_num(r.get(c_fours, 0))),
                    "Sixes": int(_to_num(r.get(c_sixes, 0))),
                    "Balls": int(_to_num(r.get(c_balls, 0))),
                    "50 runs": 1 if runs >= 50 else 0,
                    "100 runs": 1 if runs >= 100 else 0,
                }
            )
    return pd.DataFrame(out)


def _bowling_from_url(url: str, aliases: dict[str, str], driver=None) -> pd.DataFrame:
    out = []
    tables = _safe_read_tables(url, driver=driver)
    for df in tables:
        if not _is_bowling_table(df):
            continue

        player_col = df.columns[0]
        c_overs = _choose_col(df, ("O", "Overs"))
        c_maid = _choose_col(df, ("M", "Mdns", "Maidens"))
        c_runs = _choose_col(df, ("R", "Runs"))
        c_wkts = _choose_col(df, ("W", "Wkts", "Wickets"))
        c_econ = _choose_col(df, ("Econ", "Economy", "ER"))

        for _, r in df.iterrows():
            full = _resolve_name(r.get(player_col), aliases)
            if not full:
                continue
            wkts = int(_to_num(r.get(c_wkts, 0)))
            out.append(
                {
                    "player_name": full,
                    "Overs": float(_to_num(r.get(c_overs, 0))),
                    "Maiden": int(_to_num(r.get(c_maid, 0))),
                    "Runs": int(_to_num(r.get(c_runs, 0))),
                    "Economy": float(_to_num(r.get(c_econ, 0))),
                    "wickets": wkts,
                    "3 Wicket": 1 if wkts >= 3 else 0,
                    "5 Wicket": 1 if wkts >= 5 else 0,
                    "10 Wicket": 1 if wkts >= 10 else 0,
                }
            )
    return pd.DataFrame(out)


def _points_from_row(row: dict[str, Any], rules: FantasyRules) -> int:
    runs = int(_to_num(row.get("runs", 0)))
    fours = int(_to_num(row.get("Four", 0)))
    sixes = int(_to_num(row.get("Sixes", 0)))

    overs = float(_to_num(row.get("Overs", 0)))
    maidens = int(_to_num(row.get("Maiden", 0)))
    econ = float(_to_num(row.get("Economy", 0)))
    wickets = int(_to_num(row.get("wickets", 0)))

    catches = int(_to_num(row.get("catches", 0)))
    runout_direct = int(_to_num(row.get("run_outs_direct", 0)))
    runout_shared = int(_to_num(row.get("run_outs_shared", 0)))

    batting_points = (
        runs * rules.run
        + fours * rules.four
        + sixes * rules.six
        + (rules.fifty_bonus if runs >= 50 else 0)
        + (rules.hundred_bonus if runs >= 100 else 0)
    )

    haul_bonus = 0
    if wickets >= 10:
        haul_bonus = rules.ten_wicket_bonus
    elif wickets >= 5:
        haul_bonus = rules.five_wicket_bonus
    elif wickets >= 3:
        haul_bonus = rules.three_wicket_bonus

    economy_points = 0
    if overs >= 4:
        if econ < 3:
            economy_points = rules.econ_under3
        elif econ > 12:
            economy_points = rules.econ_over12
        elif econ > 8:
            economy_points = rules.econ_over8
        elif econ > 6:
            economy_points = rules.econ_over6

    bowling_points = wickets * rules.wicket + maidens * rules.maiden + haul_bonus + economy_points
    fielding_points = catches * rules.catch + runout_direct * rules.runout_direct + runout_shared * rules.runout_shared
    return int(batting_points + bowling_points + fielding_points)


def _merge_numeric(frames: list[pd.DataFrame]) -> pd.DataFrame:
    merged = pd.DataFrame(columns=["player_name"])
    for part in frames:
        if part is None or part.empty:
            continue
        part = part.copy().fillna(0)
        num_cols = [c for c in part.columns if c != "player_name"]
        part = part.groupby("player_name", as_index=False)[num_cols].sum()
        merged = part if merged.empty else pd.merge(merged, part, on="player_name", how="outer")
    return merged.fillna(0)


def build_fantasy_points_json(
    match_date: str | None = None,
    match_type: str = "T20",
    event_name: str = "Fantasy Points Update",
    team_name: str = CLUB_NAME,
    batting_urls: list[str] | None = None,
    bowling_urls: list[str] | None = None,
    rules: FantasyRules = FantasyRules(),
) -> dict[str, Any]:
    aliases = _name_aliases()

    batting_urls = batting_urls or list(SCORECARD_BATTING_URLS)
    bowling_urls = bowling_urls or list(SCORECARD_BOWLING_URLS)

    driver = get_driver(CHROME_PATH, HEADLESS, WINDOW_SIZE)
    try:
        batting_df = _merge_numeric([_batting_from_url(u, aliases, driver=driver) for u in batting_urls])
        bowling_df = _merge_numeric([_bowling_from_url(u, aliases, driver=driver) for u in bowling_urls])
    finally:
        driver.quit()
    merged = _merge_numeric([batting_df, bowling_df])

    players = []
    for _, r in merged.iterrows():
        runs = int(_to_num(r.get("runs", 0)))
        wickets = int(_to_num(r.get("wickets", 0)))
        rec = {
            "player_name": str(r.get("player_name", "")),
            "team_name": team_name,
            "runs": runs,
            "Four": int(_to_num(r.get("Four", 0))),
            "Sixes": int(_to_num(r.get("Sixes", 0))),
            "Balls": int(_to_num(r.get("Balls", 0))),
            "50 runs": 1 if runs >= 50 else 0,
            "100 runs": 1 if runs >= 100 else 0,
            "Overs": float(_to_num(r.get("Overs", 0))),
            "Maiden": int(_to_num(r.get("Maiden", 0))),
            "Runs": int(_to_num(r.get("Runs", 0))),
            "Economy": float(_to_num(r.get("Economy", 0))),
            "wickets": wickets,
            "3 Wicket": 1 if wickets >= 3 else 0,
            "5 Wicket": 1 if wickets >= 5 else 0,
            "10 Wicket": 1 if wickets >= 10 else 0,
            "catches": 0,
            "stumpings": 0,
            "run_outs": 0,
            "fantasy_points": 0,
        }
        rec["fantasy_points"] = _points_from_row(rec, rules)
        players.append(rec)

    return {
        "source": "manual",
        "is_final": True,
        "matchSummary": {
            "match_type": match_type,
            "date": match_date or date.today().isoformat(),
            "venue": "",
            "city": "",
            "teams": [team_name],
            "event_name": event_name,
            "winner": None,
        },
        "playersWithPoints": players,
    }


def save_fantasy_points_json(path: str, **kwargs: Any) -> str:
    payload = build_fantasy_points_json(**kwargs)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path
