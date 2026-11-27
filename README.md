# Badminton Team Formation

Turns Google Form sign-ups into **skill-gradient badminton teams** (Team 1 strongest, then Team 2, …), checks every rule, and exports a colour-coded Excel file.

Built for the NTU Economics department's entry to the College of Social Sciences Badminton Cup. Python Programming Foundation final project, Fall 2026.

**Sign-up form:** https://forms.gle/MzTkN82yTcJC9o7UA

**Group members: start with [HOW_TO_USE.md](HOW_TO_USE.md).** It covers getting the code, running it, what each file is for, and the Git workflow.

## Features

| ID | Feature | What it does |
|---|---|---|
| F1 | Google Form | Players sign up: gender, self-rated level 1–5, attitude, preferred events |
| F2 | Load & clean | Reads `.xlsx` / `.csv`, finds columns by keyword (English or Chinese), removes duplicate sign-ups, lists bad rows |
| F3 | Skill rating | Organizer's rating overrides the self-rating |
| F4 | Team planning | Works out team count and sizes (26 players → 7, 7, 6, 6); stops early if the rules can't be met |
| F5 | Gradient formation | Fills Team 1 with the best players, then Team 2, …; safety checks keep ≥ 2 women per team; supports locked players and a "for fun" team |
| F6 | Rule checker | PASS / WARN / FAIL table; re-checks a file after hand edits |
| F7 | Excel export | `teams.xlsx` with sheets Teams · Summary · Checks · Input issues |
| F8 | Window | tkinter window and file picker, so no typing is needed |

## Install

```
git clone https://github.com/All3n0412/Python-Group-Project--N.git
cd Python-Group-Project--N
pip install -r requirements.txt
```

You need Python 3.10 or newer. tkinter comes with Python on Windows and macOS.

## Run

**Window (recommended):** double-click `Start Team Formation.bat` (Windows), or run:

```
python run_gui.py
```

**Command line:**

```
python run.py                                    # a window opens to choose the file
python run.py responses.xlsx                     # teams.xlsx saved next to it
python run.py responses.xlsx -o my_teams.xlsx --team-size 6
python run.py --check teams.xlsx                 # re-check after editing the Team column
```

## Input file

Download the form responses from Google Sheets (*File → Download → .xlsx*). Columns are found by keyword:

| Needed | Keyword in the question title |
|---|---|
| ✔ | `Name` / `姓名` |
| ✔ | `Gender` / `性別` (Male / Female / 男 / 女, or both, e.g. "Male 男") |
| ✔ | `Self-rated level` / `自評` (1–5), or `Organizer level` / `主辦評分` |
| optional | `Timestamp`, `Student ID`, `Attitude` (Play to win / Flexible / For fun), `1st choice`, `2nd choice` |
| optional | `Fixed team` / `指定隊伍` (lock a player to a team number) |

## Project structure

```
badminton_teams/      the program (one module per responsibility)
  config.py           rules and column keywords
  loader.py           read + clean the form data
  planner.py          number and size of teams, feasibility check
  formation.py        skill-gradient team formation
  checks.py           summary + PASS/WARN/FAIL rules
  exporter.py         write / read the Excel file
  pipeline.py         connects the modules (used by the CLI and the window)
  cli.py, gui.py      command line and tkinter window
tests/                pytest test cases (17)
tools/                sample-data generators and the 11/22 comparison script
data/sample/          fake / anonymized data only
docs/                 diagrams and screenshots
```

## Tests

```
python -m pytest -v
```

## Data privacy

Only fake or anonymized data is in this repository. The real sign-up sheet (names, student IDs) stays on the organizer's computer. `data/real/` and output files are git-ignored.
