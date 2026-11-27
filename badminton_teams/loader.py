"""Module 1 - Loader: read the Google Form export and clean it."""
import pandas as pd

from .config import ATTITUDE_ORDER, COLUMN_KEYWORDS, GENDER_MAP


class InputDataError(Exception):
    """Raised when the input file cannot be used; the message explains why."""


def load_responses(path):
    """Read a .xlsx or .csv file and rename the columns to short names."""
    path = str(path)
    if path.lower().endswith(".csv"):
        df = pd.read_csv(path)
    elif path.lower().endswith((".xlsx", ".xls")):
        df = pd.read_excel(path)
    else:
        raise InputDataError("Please choose an .xlsx or .csv file.")

    rename, used = {}, set()
    for short, keywords in COLUMN_KEYWORDS.items():
        for col in df.columns:
            if col in used:
                continue
            if any(k in str(col).lower() for k in keywords):
                rename[col] = short
                used.add(col)
                break
    return df.rename(columns=rename)


def _gender(answer):
    """'Male 男', 'female', '女'... -> M / F. Checks 'female' first ('female' contains 'male')."""
    text = str(answer).strip().lower()
    if text in GENDER_MAP:
        return GENDER_MAP[text]
    if "female" in text or "女" in text:
        return "F"
    if "male" in text or "男" in text:
        return "M"
    return None


def _attitude(answer):
    """Turn a free-text attitude answer into win / flex / fun."""
    text = str(answer).lower()
    if "win" in text or "冠軍" in text:
        return "win"
    if "fun" in text or "歡樂" in text:
        return "fun"
    return "flex"


def clean(df):
    """Standardise values. Returns (clean DataFrame, list of issues)."""
    issues = []
    for needed in ("name", "gender"):
        if needed not in df.columns:
            raise InputDataError(f"Column for '{needed}' not found. Check the form questions.")
    if "self_level" not in df.columns and "organizer_level" not in df.columns:
        raise InputDataError("No skill level column found (self-rated or organizer level).")

    df = df.copy()
    if "timestamp" not in df.columns:            # keep the original order instead
        df["timestamp"] = range(len(df))

    # Same student submitted twice -> keep the latest answer
    if "student_id" in df.columns:
        before = len(df)
        df = df.sort_values("timestamp").drop_duplicates("student_id", keep="last")
        if len(df) < before:
            issues.append(f"Removed {before - len(df)} duplicate submission(s); kept the latest.")

    df["gender"] = df["gender"].map(_gender)
    df["attitude"] = df["attitude"].map(_attitude) if "attitude" in df.columns else "flex"

    # Skill level: the organizer's rating wins, otherwise the self-rating
    blank = pd.Series(float("nan"), index=df.index)
    org = pd.to_numeric(df["organizer_level"], errors="coerce") if "organizer_level" in df else blank
    own = pd.to_numeric(df["self_level"], errors="coerce") if "self_level" in df else blank
    df["level"] = org.fillna(own)
    df["level_source"] = org.notna().map({True: "organizer", False: "self"})
    df.loc[~df["level"].between(1, 5), "level"] = float("nan")

    for _, row in df.iterrows():
        if pd.isna(row["gender"]):
            issues.append(f"{row['name']}: gender missing or unclear.")
        if pd.isna(row["level"]):
            issues.append(f"{row['name']}: level missing or not between 1 and 5.")

    fixed = df["fixed_team"] if "fixed_team" in df.columns else blank
    df["fixed_team"] = pd.to_numeric(fixed, errors="coerce")
    df["att_order"] = df["attitude"].map(ATTITUDE_ORDER)
    return df.reset_index(drop=True), issues


def problem_rows(df):
    """Rows that cannot be placed until the organizer fixes them."""
    return df[df["gender"].isna() | df["level"].isna()]
