# How to use this repository (for group members)

This guide covers getting the code, running the program, what each file is for, and how to share your changes. You don't need Git experience.

Repository: https://github.com/All3n0412/Python-Group-Project--N

---

## 1. Get the code

**Option A: just look or try it (no Git needed)**
Open the repository page → green **Code** button → **Download ZIP**, then unzip it anywhere.

**Option B: you will change code (recommended)**
Install Git from https://git-scm.com (default options are fine), then in a terminal:

```
git clone https://github.com/All3n0412/Python-Group-Project--N.git
cd Python-Group-Project--N
```

To push changes, ask Allen to add you as a collaborator (GitHub → Settings → Collaborators).

## 2. Install (once)

1. Install **Python 3.10 or newer** from https://python.org. On Windows, tick **"Add python.exe to PATH"** during installation.
2. In a terminal inside the project folder, run:

```
pip install -r requirements.txt
```

This installs pandas, openpyxl and pytest.

## 3. Run the program

| What you want | How |
|---|---|
| Use the window (easiest) | Double-click **`Start Team Formation.bat`**, or run `python run_gui.py` |
| Try it on fake data | In the window, choose `data/sample/sample_responses.xlsx` → **Form teams** |
| Command line | `python run.py data/sample/sample_responses.xlsx` |
| Re-check after editing teams by hand | `python run.py --check teams.xlsx`, or the **Re-check edited file…** button |
| Run all tests | `python -m pytest -v` (all should say PASSED) |

The result `teams.xlsx` is saved **in the same folder as the file you chose**, with four sheets:
- **Teams:** who is on which team. You can edit the *Team* column by hand.
- **Summary:** size, men/women and average level per team.
- **Checks:** every rule marked PASS / WARN / FAIL.
- **Input issues:** problems found in the form data.

## 4. What every file is

### Main folder

| File | What it is |
|---|---|
| `README.md` | Short project description: features, install, run |
| `HOW_TO_USE.md` | This guide |
| `requirements.txt` | Python packages to install |
| `.gitignore` | Files Git must **not** upload (outputs, real data, cache) |
| `run_gui.py` | Starts the window |
| `run.py` | Starts the command-line version |
| `Start Team Formation.bat` | Windows double-click launcher for the window |

### `badminton_teams/`: the program itself

Data flows through these modules in this order: loader → planner → formation → checks → exporter.

| File | What it does | Change it when… |
|---|---|---|
| `config.py` | All rules (min. 2 women, min. 4 men) and the keywords used to find form columns | a rule changes, or the form questions are renamed |
| `loader.py` | Reads the form file and cleans it (gender, attitude, level, duplicates) | the form gets new questions |
| `planner.py` | Decides how many teams and how big; stops if the rules can't be met | team-size rules change |
| `formation.py` | **The core algorithm:** ranks players and fills Team 1, 2, 3… with safety checks for women | the team logic changes |
| `checks.py` | Builds the team summary and the PASS/WARN/FAIL rule table | a new rule needs checking |
| `exporter.py` | Writes and reads the coloured Excel file | the Excel layout changes |
| `pipeline.py` | Connects all modules; the window and the command line both call it | a new step is added |
| `gui.py` | The tkinter window | the window changes |
| `cli.py` | The command line (`run.py`) | command options change |

### `tests/`

| File | What it is |
|---|---|
| `test_team_formation.py` | 16 automated test cases (TC1–TC12 in the HW5 report) |
| `conftest.py` | Helpers that build small fake form files for the tests |

### `tools/`: helper scripts, not part of the program

| File | What it is |
|---|---|
| `make_sample_data.py` | Creates the fake `sample_responses.xlsx` (26 players) |
| `simulate_real_roster.py` | Creates `real_roster_simulated_levels.xlsx` from the real 11/22 team list. Names are replaced by P01–P25, and **levels are simulated** |
| `compare_with_1122.py` | Runs the program on that roster and compares it with the organizer's real 11/22 teams; writes `output/teams_program_vs_1122.xlsx` |

### `data/sample/`

Fake or anonymized input files that are safe to share: `sample_responses.xlsx` and `real_roster_simulated_levels.xlsx`.

### `docs/`

- `diagrams/`: the architecture, user flow and wireframe images used in the report. The `.dot` and `.py` files are their editable sources.
- `screenshots/`: screenshots of the program running, also used in the report.

To redraw a diagram after editing a `.dot` file, install Graphviz and run:

```
dot -Tpng -Gdpi=170 architecture.dot -o architecture.png
```

## 5. Sharing your changes (Git workflow)

Every time you work on the code:

```
git pull                      # 1. get everyone else's latest changes FIRST
# ... edit files ...
python -m pytest              # 2. make sure all tests still pass
git add .                     # 3. stage your changes
git commit -m "Short description of what you changed"
git push                      # 4. upload
```

Rules:
- **Pull before you start.** This avoids most conflicts.
- **Stick to your own module** (see the roles in HW5 report §5.4). Two people editing the same file at the same time causes conflicts.
- **Never commit real sign-up data** (real names, student IDs). Keep it in a `data/real/` folder, which Git ignores.
- **If `git push` is rejected:** run `git pull`, then `git push` again.
- **If `git pull` reports a conflict:** don't panic. Open the file, keep the right lines, delete the `<<<<<<<`, `=======` and `>>>>>>>` markers, then `git add .`, `git commit` and `git push`. If unsure, ask Allen before forcing anything.

## 6. Common problems

| Message | Fix |
|---|---|
| `'python' is not recognized…` | Python is not on PATH: reinstall and tick "Add python.exe to PATH", or use `py` instead of `python` |
| `ModuleNotFoundError: No module named 'pandas'` | Run `pip install -r requirements.txt` |
| "Cannot save teams.xlsx: it is probably open in Excel" | Close `teams.xlsx` in Excel and press **Form teams** again |
| "Only 7 women for 4 teams…" | Not enough women for that many teams: raise **Players per team**, or recruit more women |
| "Column for 'gender' not found" | A form question title changed: add the new wording to `COLUMN_KEYWORDS` in `config.py` |
| The window doesn't open from the .bat file | Run `python run_gui.py` in a terminal to see the error message |
