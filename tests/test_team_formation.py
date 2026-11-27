"""Test cases for the main features and the important error situations."""
import pandas as pd
import pytest

from badminton_teams import pipeline
from badminton_teams.loader import InputDataError
from badminton_teams.planner import plan_team_sizes
from conftest import SAMPLE, make_responses


# ---------- TC1: normal case ----------
def test_sample_file_forms_valid_gradient_teams(tmp_path):
    result = pipeline.form_teams_from_file(SAMPLE, tmp_path / "teams.xlsx")
    s = result.summary
    assert s["Players"].tolist() == [7, 7, 6, 6]               # 26 players -> 4 teams
    assert (s["Women"] >= 2).all()                              # hard rule
    assert s["Avg level"].is_monotonic_decreasing               # skill gradient
    assert result.overall == "PASS"
    sheets = pd.ExcelFile(tmp_path / "teams.xlsx").sheet_names
    assert sheets == ["Teams", "Summary", "Checks", "Input issues"]


# ---------- TC2: team planning ----------
@pytest.mark.parametrize("n, size, expected", [(26, 6, [7, 7, 6, 6]), (12, 6, [6, 6]), (25, 6, [7, 6, 6, 6])])
def test_plan_team_sizes(n, size, expected):
    assert plan_team_sizes(n, size) == expected


def test_too_few_players_for_one_team():
    with pytest.raises(InputDataError):
        plan_team_sizes(5, 6)


# ---------- TC3: not enough women ----------
def test_too_few_women_stops_with_message(write_xlsx):
    players = [("Male", 3, "Play to win")] * 9 + [("Female", 3, "Flexible")] * 3   # 2 teams need 4
    with pytest.raises(InputDataError, match="Only 3 women for 2 teams"):
        pipeline.form_teams_from_file(write_xlsx(make_responses(players)))


# ---------- TC4: safety check keeps women for later teams ----------
def test_strong_women_are_not_all_taken_by_team_1(write_xlsx, tmp_path):
    # the 4 best players are all women, but 2 teams need 2 women each
    players = [("Female", 5, "Play to win")] * 4 + [("Male", 3, "Flexible")] * 8
    result = pipeline.form_teams_from_file(write_xlsx(make_responses(players)), tmp_path / "t.xlsx")
    assert result.summary["Women"].tolist() == [2, 2]


# ---------- TC5: missing data ----------
def test_missing_gender_or_level_lists_the_player(write_xlsx):
    df = make_responses([("Male", 3, "Flexible")] * 10 + [("Female", 3, "Flexible")] * 2)
    df.loc[3, "Gender"] = ""                      # P04 forgot gender
    df.loc[5, "Self-rated level (1-5)"] = 9       # P06 typed an invalid level
    with pytest.raises(InputDataError) as err:
        pipeline.form_teams_from_file(write_xlsx(df))
    assert "P04: gender" in str(err.value) and "P06: level" in str(err.value)


# ---------- TC6: duplicate sign-up ----------
def test_duplicate_submission_keeps_latest(write_xlsx, tmp_path):
    df = make_responses([("Male", 3, "Flexible")] * 8 + [("Female", 3, "Flexible")] * 4)
    again = df.iloc[[0]].copy()
    again["Timestamp"] += pd.Timedelta(days=1)
    again["Self-rated level (1-5)"] = 5           # P01 resubmitted with a new level
    result = pipeline.form_teams_from_file(write_xlsx(pd.concat([df, again])), tmp_path / "t.xlsx")
    p01 = result.players[result.players["name"] == "P01"]
    assert len(p01) == 1 and p01["level"].iloc[0] == 5
    assert any("duplicate" in msg for msg in result.issues)


# ---------- TC7: organizer level overrides self-rating ----------
def test_organizer_level_overrides_self_rating(write_xlsx, tmp_path):
    df = make_responses([("Male", 2, "Flexible")] * 8 + [("Female", 2, "Flexible")] * 4,
                        **{"Organizer level": [5] + [None] * 11})
    result = pipeline.form_teams_from_file(write_xlsx(df), tmp_path / "t.xlsx")
    p01 = result.players.set_index("name").loc["P01"]
    assert p01["level"] == 5 and p01["level_source"] == "organizer" and p01["team"] == 1


# ---------- TC8: locked player ----------
def test_fixed_team_is_respected(write_xlsx, tmp_path):
    df = make_responses([("Male", 5, "Play to win")] + [("Male", 3, "Flexible")] * 9
                        + [("Female", 3, "Flexible")] * 4,
                        **{"Fixed team": [2] + [None] * 13})        # best player locked to Team 2
    result = pipeline.form_teams_from_file(write_xlsx(df), tmp_path / "t.xlsx")
    assert result.players.set_index("name").loc["P01", "team"] == 2


# ---------- TC9: 'for fun' players kept together ----------
def test_fun_players_kept_on_last_team(write_xlsx, tmp_path):
    players = ([("Male", 4, "Play to win")] * 4 + [("Female", 4, "Play to win")] * 2
               + [("Male", 3, "For fun")] * 4 + [("Female", 3, "For fun")] * 2)
    result = pipeline.form_teams_from_file(write_xlsx(make_responses(players)), tmp_path / "t.xlsx")
    last = result.players[result.players["team"] == 2]
    assert (last["attitude"] == "fun").all()


# ---------- TC10: re-check after hand edit ----------
def test_recheck_flags_team_with_one_woman(tmp_path):
    out = tmp_path / "teams.xlsx"
    pipeline.form_teams_from_file(SAMPLE, out)
    teams = pd.read_excel(out, sheet_name="Teams")
    woman = teams[(teams["Team"] == 4) & (teams["Gender"] == "F")].index[0]
    teams.loc[woman, "Team"] = 3                                    # organizer moves a woman
    with pd.ExcelWriter(out) as xw:
        teams.to_excel(xw, sheet_name="Teams", index=False)
    result = pipeline.recheck_file(out)
    team4 = result.checks[(result.checks["Team"] == 4) & result.checks["Rule"].str.contains("women")]
    assert team4["Result"].iloc[0] == "FAIL" and result.overall == "FAIL"


# ---------- TC11: other input formats ----------
def test_csv_and_chinese_question_titles(tmp_path):
    df = make_responses([("男", 3, "劍指冠軍")] * 8 + [("女", 3, "歡樂隊伍")] * 4)
    df = df.rename(columns={"Name": "姓名", "Gender": "性別", "Self-rated level (1-5)": "自評程度",
                            "Attitude": "參賽態度", "Student ID": "學號", "Timestamp": "時間戳記"})
    path = tmp_path / "responses.csv"
    df.to_csv(path, index=False)
    result = pipeline.form_teams_from_file(path, tmp_path / "t.xlsx")
    assert result.summary["Players"].sum() == 12
    assert set(result.players["attitude"]) == {"win", "fun"}


def test_wrong_file_type_is_rejected(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("hello")
    with pytest.raises(InputDataError, match="xlsx or .csv"):
        pipeline.form_teams_from_file(path)


# ---------- TC12: output file locked (open in Excel on Windows) ----------
def test_locked_output_file_gives_clear_message(tmp_path, monkeypatch):
    from badminton_teams import exporter

    def locked(*args, **kwargs):
        raise PermissionError("file is open")
    monkeypatch.setattr(exporter, "export_excel", locked)
    with pytest.raises(InputDataError, match="open in Excel"):
        pipeline.form_teams_from_file(SAMPLE, tmp_path / "teams.xlsx")


# ---------- TC13: our real Google Form export (exact question titles and options) ----------
def test_our_google_form_export_is_read_correctly(write_xlsx, tmp_path):
    """Column titles and answer options copied from the live form (forms.gle/MzTkN82yTcJC9o7UA)."""
    genders = ["Male 男"] * 8 + ["Female 女"] * 4
    attitudes = ["Play to win 劍指冠軍", "Flexible 都可以", "For fun 歡樂參加"] * 4
    df = pd.DataFrame({
        "Timestamp": pd.date_range("2026-11-28", periods=12, freq="h"),
        "Email Address": [f"p{i}@ntu.edu.tw" for i in range(12)],
        "Name 姓名": [f"P{i:02d}" for i in range(12)],
        "Student ID 學號": [f"B14{i:06d}" for i in range(12)],
        "Gender 性別": genders,
        "Department and year 系級": ["Econ 2"] * 12,
        "Self-rated level 自評程度": [5, 4, 4, 3, 3, 3, 2, 2, 5, 3, 2, 1],
        "Competition experience 比賽經驗": ["None 無"] * 12,
        "Attitude 參賽態度": attitudes,
        "Preferred event (1st choice) 第一志願項目": ["Men's doubles 男雙"] * 12,
        "Preferred event (2nd choice) 第二志願項目": ["Mixed doubles 混雙"] * 12,
        "Notes for the organizer 備註": [""] * 12,
    })
    result = pipeline.form_teams_from_file(write_xlsx(df), tmp_path / "t.xlsx")
    assert set(result.players["gender"]) == {"M", "F"}
    assert result.summary["Women"].tolist() == [2, 2]
    assert set(result.players["attitude"]) == {"win", "flex", "fun"}
    assert result.overall == "PASS"
