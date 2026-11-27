"""All settings and rules in one place, so they are easy to change."""

MIN_WOMEN_PER_TEAM = 2      # hard rule from the organizer
MIN_MEN_PER_TEAM = 4        # men's singles 1 + men's doubles 2 + mixed 1 (warning only)
DEFAULT_TEAM_SIZE = 6

# Google Form question titles are long, so each column is found by a keyword.
# Short name -> words that may appear in the question title (English or Chinese).
COLUMN_KEYWORDS = {
    "timestamp": ["timestamp", "時間戳記"],
    "name": ["name", "姓名"],
    "student_id": ["student id", "學號"],
    "gender": ["gender", "性別"],
    "dept": ["department", "系級"],
    "self_level": ["self-rated level", "自評"],
    "experience": ["experience", "經驗"],
    "attitude": ["attitude", "態度"],
    "event1": ["1st choice", "第一"],
    "event2": ["2nd choice", "第二"],
    "organizer_level": ["organizer level", "主辦評分"],
    "fixed_team": ["fixed team", "指定隊伍"],
}

GENDER_MAP = {"male": "M", "m": "M", "男": "M", "female": "F", "f": "F", "女": "F"}
ATTITUDE_ORDER = {"win": 0, "flex": 1, "fun": 2}   # used to break ties in skill

# Names shown to the user in the Excel file
DISPLAY_NAMES = {
    "team": "Team", "name": "Name", "gender": "Gender", "level": "Level",
    "level_source": "Level from", "attitude": "Attitude", "event1": "1st event",
    "event2": "2nd event", "dept": "Department", "student_id": "Student ID",
}
