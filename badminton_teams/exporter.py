"""Module 5 - Exporter: write and read the teams Excel file."""
import pandas as pd
from openpyxl.styles import Alignment, Font, PatternFill

from .config import ATTITUDE_ORDER, DISPLAY_NAMES

TEAM_COLORS = ["FDE2E2", "E2EFDA", "DDEBF7", "FFF2CC", "EADCF8", "FCE4D6"]
RESULT_COLORS = {"PASS": "C6EFCE", "WARN": "FFEB9C", "FAIL": "FFC7CE"}


def export_excel(df, summary, checks, issues, path):
    """Four sheets: Teams, Summary, Checks, Input issues."""
    players = df.rename(columns=DISPLAY_NAMES)
    players = players[[c for c in DISPLAY_NAMES.values() if c in players.columns]]
    issues_df = pd.DataFrame({"Input issue": issues or ["No issues found."]})

    with pd.ExcelWriter(path, engine="openpyxl") as xw:
        players.to_excel(xw, sheet_name="Teams", index=False)
        summary.to_excel(xw, sheet_name="Summary", index=False)
        checks.to_excel(xw, sheet_name="Checks", index=False)
        issues_df.to_excel(xw, sheet_name="Input issues", index=False)

        for ws in xw.book.worksheets:
            ws.freeze_panes = "A2"
            ws.page_setup.orientation = "landscape"       # print each sheet on one page width
            ws.sheet_properties.pageSetUpPr.fitToPage = True
            ws.page_setup.fitToWidth, ws.page_setup.fitToHeight = 1, 0
            for cell in ws[1]:
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill("solid", fgColor="305496")
                cell.alignment = Alignment(horizontal="center")
            for col in ws.columns:
                width = max(len(str(c.value or "")) for c in col)
                ws.column_dimensions[col[0].column_letter].width = min(width + 3, 60)

        for sheet in ("Teams", "Summary"):               # one colour per team
            for row in xw.book[sheet].iter_rows(min_row=2):
                if isinstance(row[0].value, int):
                    fill = PatternFill("solid", fgColor=TEAM_COLORS[(row[0].value - 1) % 6])
                    for c in row:
                        c.fill = fill
        for row in xw.book["Checks"].iter_rows(min_row=2):
            row[2].fill = PatternFill("solid", fgColor=RESULT_COLORS[row[2].value])


def read_teams_file(path):
    """Read the Teams sheet back (after the organizer edited it by hand)."""
    df = pd.read_excel(path, sheet_name="Teams")
    df = df.rename(columns={v: k for k, v in DISPLAY_NAMES.items()})
    df["team"] = pd.to_numeric(df["team"], errors="coerce").astype("Int64")
    df["att_order"] = df["attitude"].map(ATTITUDE_ORDER)
    return df.sort_values(["team", "level"], ascending=[True, False])
