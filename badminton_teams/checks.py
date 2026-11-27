"""Module 4 - Rule checker: team summary and PASS / WARN / FAIL table."""
import pandas as pd

from .config import MIN_MEN_PER_TEAM, MIN_WOMEN_PER_TEAM


def summarize(df):
    """One row per team: size, gender count, skill statistics, attitudes."""
    g = df.groupby("team")
    return pd.DataFrame({
        "Players": g.size(),
        "Men": g["gender"].apply(lambda s: int((s == "M").sum())),
        "Women": g["gender"].apply(lambda s: int((s == "F").sum())),
        "Avg level": g["level"].mean().round(2),
        "Max level": g["level"].max(),
        "Min level": g["level"].min(),
        "Play to win": g["attitude"].apply(lambda s: int((s == "win").sum())),
        "Flexible": g["attitude"].apply(lambda s: int((s == "flex").sum())),
        "For fun": g["attitude"].apply(lambda s: int((s == "fun").sum())),
    }).reset_index().rename(columns={"team": "Team"})


def check_rules(df, summary, max_men=None):
    """Return a table with columns Rule, Team, Result, Detail."""
    rows = []
    unplaced = int(df["team"].isna().sum())
    rows.append(("Every player is on exactly one team", "All",
                 "PASS" if unplaced == 0 else "FAIL", f"{unplaced} unplaced"))

    for _, r in summary.iterrows():
        t, women, men = int(r["Team"]), int(r["Women"]), int(r["Men"])
        rows.append((f"At least {MIN_WOMEN_PER_TEAM} women", t,
                     "PASS" if women >= MIN_WOMEN_PER_TEAM else "FAIL",
                     f"{women} woman" if women == 1 else f"{women} women"))
        if max_men is not None:
            rows.append((f"At most {max_men} men", t,
                         "PASS" if men <= max_men else "FAIL", f"{men} men"))
        enough = men >= MIN_MEN_PER_TEAM
        rows.append((f"At least {MIN_MEN_PER_TEAM} men (for lineups)", t,
                     "PASS" if enough else "WARN",
                     f"{men} men" + ("" if enough else "; women must cover men's games")))

    avgs = summary["Avg level"].tolist()
    gradient_ok = all(a >= b for a, b in zip(avgs, avgs[1:]))
    rows.append(("Skill gradient (Team 1 strongest)", "All",
                 "PASS" if gradient_ok else "WARN", " -> ".join(f"{a:.2f}" for a in avgs)))
    return pd.DataFrame(rows, columns=["Rule", "Team", "Result", "Detail"])


def overall_result(checks):
    """FAIL if any rule fails, else WARN if any warning, else PASS."""
    results = set(checks["Result"])
    return "FAIL" if "FAIL" in results else "WARN" if "WARN" in results else "PASS"
