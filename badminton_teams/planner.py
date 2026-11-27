"""Module 2 - Planner: decide how many teams and how big, and whether it is possible."""
from .config import MIN_WOMEN_PER_TEAM
from .loader import InputDataError


def plan_team_sizes(n_players, team_size):
    """26 players, size 6 -> [7, 7, 6, 6] (bigger teams first)."""
    if team_size < 2:
        raise InputDataError("Team size must be at least 2.")
    k = n_players // team_size
    if k == 0:
        raise InputDataError(f"Only {n_players} players: not enough for one team of {team_size}.")
    base, extra = divmod(n_players, k)
    return [base + 1 if t < extra else base for t in range(k)]


def check_feasibility(df, sizes):
    """Stop early if the hard rules cannot be met."""
    k = len(sizes)
    women = int((df["gender"] == "F").sum())
    if women < MIN_WOMEN_PER_TEAM * k:
        raise InputDataError(
            f"Only {women} women for {k} teams (need {MIN_WOMEN_PER_TEAM * k}). "
            f"Use a bigger team size (fewer teams) or recruit more women.")
    bad_fixed = df["fixed_team"].notna() & ~df["fixed_team"].between(1, k)
    if bad_fixed.any():
        names = ", ".join(df.loc[bad_fixed, "name"].astype(str))
        raise InputDataError(f"'Fixed team' must be between 1 and {k}: {names}")
