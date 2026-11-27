"""Create fake Google Form responses (same mix as the real 2026 sign-up:
17 men, 9 women; 12 win / 11 flexible / 3 fun) for testing."""
import random
from pathlib import Path

import pandas as pd

OUT = Path(__file__).resolve().parents[1] / "data" / "sample" / "sample_responses.xlsx"

random.seed(7)
rows = []
genders = ["Male"] * 17 + ["Female"] * 9
attitudes = ["Play to win"] * 12 + ["Flexible"] * 11 + ["For fun"] * 3
random.shuffle(attitudes)
events_m = ["Men's singles", "Men's doubles", "Mixed doubles", "No preference"]
events_f = ["Women's singles", "Women's doubles", "Mixed doubles", "No preference"]
years = ["Econ 1", "Econ 2", "Econ 3", "Econ 4", "Graduated", "Double major"]

for i, (g, a) in enumerate(zip(genders, attitudes), start=1):
    base = {"Play to win": 4, "Flexible": 3, "For fun": 2}[a]
    self_level = max(1, min(5, base + random.choice([-1, 0, 0, 1])))
    ev = events_m if g == "Male" else events_f
    rows.append({
        "Timestamp": pd.Timestamp("2026-11-01 10:00") + pd.Timedelta(hours=i * 3),
        "Name": f"Player {i:02d}",
        "Student ID": f"B13{300000 + i}",
        "Gender": g,
        "Department & year": random.choice(years),
        "Self-rated level (1 = beginner, 5 = school-team level)": self_level,
        "Competition experience": random.choice(["None", "Department cup", "School team"]),
        "Attitude": a,
        "Preferred event (1st choice)": random.choice(ev),
        "Preferred event (2nd choice)": random.choice(ev),
    })

df = pd.DataFrame(rows)
# The organizer adds two columns in the response sheet:
#  - Organizer level: her own rating (overrides the self-rating if filled)
#  - Fixed team: optional lock, e.g. the captain of Team 1
df["Organizer level"] = None
for i in random.sample(range(len(df)), 10):
    df.loc[i, "Organizer level"] = max(1, min(5, df.iloc[i, 5] + random.choice([-1, 1])))
df["Fixed team"] = None
df.loc[0, "Fixed team"] = 1
df.to_excel(OUT, index=False)
print(df[["Name", "Gender", "Attitude", df.columns[5], "Organizer level", "Fixed team"]])
