"""
Build a SIMULATED input file from the real 11/22 team list.

Real data kept : team, gender, events (from the organizer's 11/22 list)
Simulated      : skill level and attitude (the organizer did not record them)
Names removed  : players are coded P01-P25 (keep the name list privately)

Simulation rules (all assumptions, documented for the report):
  1. Team base level follows the order of the list (the first team = 1st team):
       預算無限rich 4.2, 寓望無限ambition 3.5, 壞東西bads 2.9, 好東西goods 2.4
  2. Role adjustment inside a team (stronger players usually play singles):
       men's singles +0.5, men's doubles 0, mixed (man) -0.3
       woman playing women's singles +0.3, other women 0
  3. Random noise ~ Normal(0, 0.6), then rounded and kept within 1-5
  4. Self-rated level = organizer level +/- 1 sometimes (self-rating bias)
  5. Attitude: 12 play to win, 10 flexible, 3 for fun (same mix as the form)
"""
from pathlib import Path

import numpy as np
import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "sample" / "real_roster_simulated_levels.xlsx"

rng = np.random.default_rng(2026)          # fixed seed -> same result every run

EVENT = {"男單": "Men's singles", "男雙": "Men's doubles", "女單": "Women's singles",
         "女雙": "Women's doubles", "混雙": "Mixed doubles"}

# (team, gender, events) in the order of the 11/22 list
roster = [
    ("預算無限rich", "M", "男單"), ("預算無限rich", "M", "男雙"), ("預算無限rich", "M", "男雙"),
    ("預算無限rich", "M", "混雙"), ("預算無限rich", "F", "女單&女雙"),
    ("預算無限rich", "F", "女雙&混雙"), ("預算無限rich", "F", "女單&女雙"),
    ("寓望無限ambition", "M", "男單"), ("寓望無限ambition", "M", "男雙"),
    ("寓望無限ambition", "M", "男雙"), ("寓望無限ambition", "M", "混雙"),
    ("寓望無限ambition", "F", "女單&女雙"), ("寓望無限ambition", "F", "女雙&混雙"),
    ("壞東西bads", "M", "男單"), ("壞東西bads", "M", "男雙"), ("壞東西bads", "M", "男雙"),
    ("壞東西bads", "M", "混雙"), ("壞東西bads", "F", "女單&女雙"), ("壞東西bads", "F", "女雙&混雙"),
    ("好東西goods", "M", "男單"), ("好東西goods", "M", "男雙"), ("好東西goods", "M", "男雙"),
    ("好東西goods", "M", "混雙"), ("好東西goods", "F", "女單&女雙"), ("好東西goods", "F", "女雙&混雙"),
]
TEAM_ORDER = ["預算無限rich", "寓望無限ambition", "壞東西bads", "好東西goods"]
TEAM_BASE = dict(zip(TEAM_ORDER, [4.2, 3.5, 2.9, 2.4]))
ATTITUDE = {  # per team, in list order
    "預算無限rich": ["Play to win"] * 7,
    "寓望無限ambition": ["Play to win"] * 5 + ["Flexible"],
    "壞東西bads": ["Flexible"] * 4 + ["For fun"] * 2,
    "好東西goods": ["Flexible"] * 5 + ["For fun"],
}


def role_bonus(gender, events):
    if gender == "M":
        return {"男單": 0.5, "男雙": 0.0, "混雙": -0.3}[events]
    return 0.3 if "女單" in events else 0.0


rows, seen = [], {t: 0 for t in TEAM_ORDER}
for i, (team, g, ev) in enumerate(roster, start=1):
    level = TEAM_BASE[team] + role_bonus(g, ev) + rng.normal(0, 0.6)
    level = int(np.clip(round(level), 1, 5))
    self_level = int(np.clip(level + rng.choice([-1, 0, 0, 0, 1]), 1, 5))
    evs = [EVENT[e] for e in ev.split("&")]
    rows.append({
        "Timestamp": pd.Timestamp("2026-11-01 09:00") + pd.Timedelta(hours=5 * i),
        "Name": f"P{i:02d}",
        "Gender": "Male" if g == "M" else "Female",
        "Self-rated level (1 = beginner, 5 = school-team level)": self_level,
        "Attitude": ATTITUDE[team][seen[team]],
        "Preferred event (1st choice)": evs[0],
        "Preferred event (2nd choice)": evs[1] if len(evs) > 1 else "No preference",
        "Organizer level": level,
        "Actual 11/22 team": team,
    })
    seen[team] += 1

df = pd.DataFrame(rows)
df.to_excel(OUT, index=False)
print(df.drop(columns="Timestamp").to_string(index=False))
