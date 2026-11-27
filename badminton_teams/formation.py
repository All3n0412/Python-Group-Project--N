"""Module 3 - Formation engine: build teams with a skill gradient.

Team 1 picks first and keeps the best available players until it is full,
then Team 2, and so on. Two safety checks keep at least 2 women for every team.
"""
from .config import MIN_WOMEN_PER_TEAM


def rank_players(df):
    """Best first: higher level, then win > flex > fun, then earlier sign-up."""
    return df.sort_values(["level", "att_order", "timestamp"], ascending=[False, True, True])


def lock_fun_team(df, sizes):
    """If there are enough 'for fun' players to fill the last team, keep them together."""
    df = df.copy()
    fun = df[(df["attitude"] == "fun") & df["fixed_team"].isna()]
    if len(fun) >= sizes[-1]:
        fun_women = int((fun["gender"] == "F").sum())
        seats = sizes[-1] - max(0, MIN_WOMEN_PER_TEAM - fun_women)   # leave room for women
        chosen = fun.sort_values("gender").index[:seats]             # "F" before "M"
        df.loc[chosen, "fixed_team"] = len(sizes)
    return df


def _women_needed_later(df, t, k):
    """How many more women the teams after team t still need."""
    return sum(max(0, MIN_WOMEN_PER_TEAM - int(((df["team"] == u) & (df["gender"] == "F")).sum()))
               for u in range(t + 1, k + 1))


def form_teams(df, sizes, max_men=None):
    """Return the players with a new 'team' column (1 = strongest)."""
    k = len(sizes)
    df = rank_players(df).copy()
    df["team"] = df["fixed_team"]                # locked players are placed first

    for t in range(1, k + 1):
        while (df["team"] == t).sum() < sizes[t - 1]:
            team = df[df["team"] == t]
            pool = df[df["team"].isna()]         # not yet placed, best first
            if pool.empty:
                break
            seats_left = sizes[t - 1] - len(team)
            women_needed_here = max(0, MIN_WOMEN_PER_TEAM - int((team["gender"] == "F").sum()))
            men_here = int((team["gender"] == "M").sum())
            women_left = int((pool["gender"] == "F").sum())

            best = pool.iloc[0]
            best_woman = pool[pool["gender"] == "F"].head(1)
            best_man = pool[pool["gender"] == "M"].head(1)

            if best["gender"] == "M":
                # Safety check 1: still room for this team's women (and men cap, if any)
                men_full = max_men is not None and men_here >= max_men
                ok = seats_left - 1 >= women_needed_here and not men_full
                pick = best if ok or best_woman.empty else best_woman.iloc[0]
            else:
                # Safety check 2: enough women left for the teams after this one
                ok = women_left - 1 >= _women_needed_later(df, t, k) + max(0, women_needed_here - 1)
                pick = best if ok or best_man.empty else best_man.iloc[0]
            df.loc[pick.name, "team"] = t

    df["team"] = df["team"].astype("Int64")
    return df.sort_values(["team", "level"], ascending=[True, False])
