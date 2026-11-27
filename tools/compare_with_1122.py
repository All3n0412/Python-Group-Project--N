"""Run the program on the simulated 11/22 roster, then compare its teams with
the organizer's real 11/22 teams (same players, same simulated levels).

    python tools/compare_with_1122.py
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from badminton_teams import pipeline  # noqa: E402

INPUT = ROOT / "data" / "sample" / "real_roster_simulated_levels.xlsx"
OUTPUT = ROOT / "output" / "teams_program_vs_1122.xlsx"
OUTPUT.parent.mkdir(exist_ok=True)

pipeline.form_teams_from_file(INPUT, OUTPUT)          # step 1: the program forms teams
inp = pd.read_excel(INPUT)
out = pd.read_excel(OUTPUT, sheet_name="Teams")
order = {"預算無限rich": 1, "寓望無限ambition": 2, "壞東西bads": 3, "好東西goods": 4}
df = out.merge(inp[["Name", "Actual 11/22 team"]], on="Name")
df["Actual tier"] = df["Actual 11/22 team"].map(order)

def stats(group_col):
    g = df.groupby(group_col)
    return pd.DataFrame({"Players": g.size(),
                         "Women": g["Gender"].apply(lambda s: (s == "F").sum()),
                         "Avg level": g["Level"].mean().round(2),
                         "Min": g["Level"].min(), "Max": g["Level"].max()})

manual = stats("Actual tier").assign(Method="11/22 by hand")
program = stats("Team").assign(Method="Program")
compare = (pd.concat([manual, program]).rename_axis("Tier").reset_index()
           .sort_values(["Tier", "Method"])[["Tier", "Method", "Players", "Women",
                                             "Avg level", "Min", "Max"]])
moves = pd.crosstab(df["Actual 11/22 team"], df["Team"]).loc[list(order)]
moves.columns = [f"Program team {c}" for c in moves.columns]
moves = moves.rename_axis("Actual 11/22 team").reset_index()
same = (df["Actual tier"] == df["Team"]).sum()

print(compare.to_string(index=False)); print(); print(moves.to_string(index=False))
print(f"\nSame tier in both: {same} of {len(df)} players")
changed = df[df["Actual tier"] != df["Team"]][["Name", "Gender", "Level", "Attitude",
                                                "Actual 11/22 team", "Team"]]
changed = changed.rename(columns={"Team": "Program team"})
print(changed.to_string(index=False))

with pd.ExcelWriter(OUTPUT, engine="openpyxl", mode="a", if_sheet_exists="overlay") as xw:
    compare.to_excel(xw, sheet_name="Compare 11-22", index=False)
    moves.to_excel(xw, sheet_name="Compare 11-22", index=False, startrow=len(compare) + 3)
    changed.to_excel(xw, sheet_name="Players moved", index=False)
    note = pd.DataFrame({"Note": [f"Same tier in both: {same} of {len(df)} players.",
                                  "Levels are SIMULATED (see tools/simulate_real_roster.py)."]})
    note.to_excel(xw, sheet_name="Compare 11-22", index=False,
                  startrow=len(compare) + len(moves) + 6)

    # simple formatting: bold blue headers, wider columns
    from openpyxl.styles import Alignment, Font, PatternFill
    header_rows = {"Compare 11-22": [1, len(compare) + 4, len(compare) + len(moves) + 7],
                   "Players moved": [1]}
    for name, rows in header_rows.items():
        ws = xw.book[name]
        for r in rows:
            for cell in ws[r]:
                if cell.value is not None:
                    cell.font = Font(bold=True, color="FFFFFF")
                    cell.fill = PatternFill("solid", fgColor="305496")
        for col in ws.columns:                       # fixed widths, one page wide
            ws.column_dimensions[col[0].column_letter].width = 22 if col[0].column == 1 else 16
        ws.page_setup.orientation = "landscape"
        ws.sheet_properties.pageSetUpPr.fitToPage = True
        ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
        for row in ws.iter_rows():                   # centre everything except notes
            for c in row:
                if not str(c.value or "").startswith(("Same tier", "Levels are")):
                    c.alignment = Alignment(horizontal="center")
        for row in ws.iter_rows(min_row=2):          # shade the program rows
            if any(c.value == "Program" for c in row):
                for c in row:
                    c.fill = PatternFill("solid", fgColor="E2EFDA")
