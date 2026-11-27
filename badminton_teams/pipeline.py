"""Connects the modules. Both the command line and the window call these two functions."""
import os
from dataclasses import dataclass, field

import pandas as pd

from . import checks, exporter, formation, loader, planner
from .config import DEFAULT_TEAM_SIZE


@dataclass
class Result:
    players: pd.DataFrame
    summary: pd.DataFrame
    checks: pd.DataFrame
    output_path: str
    issues: list = field(default_factory=list)

    @property
    def overall(self):
        return checks.overall_result(self.checks)


def default_output_path(input_path):
    """Save teams.xlsx next to the input file."""
    return os.path.join(os.path.dirname(os.path.abspath(input_path)), "teams.xlsx")


def form_teams_from_file(input_path, output_path=None, team_size=DEFAULT_TEAM_SIZE, max_men=None):
    """Form responses file -> teams.xlsx. Raises loader.InputDataError on bad input."""
    df, issues = loader.clean(loader.load_responses(input_path))
    bad = loader.problem_rows(df)
    if not bad.empty:
        raise loader.InputDataError("Please fix these rows first:\n" + "\n".join(issues))

    sizes = planner.plan_team_sizes(len(df), team_size)
    planner.check_feasibility(df, sizes)
    df = formation.lock_fun_team(df, sizes)
    df = formation.form_teams(df, sizes, max_men)

    summary = checks.summarize(df)
    table = checks.check_rules(df, summary, max_men)
    output_path = output_path or default_output_path(input_path)
    exporter.export_excel(df, summary, table, issues, output_path)
    return Result(df, summary, table, output_path, issues)


def recheck_file(teams_path, max_men=None):
    """Re-check a teams.xlsx after hand edits and rewrite its Summary/Checks sheets."""
    df = exporter.read_teams_file(teams_path)
    summary = checks.summarize(df)
    table = checks.check_rules(df, summary, max_men)
    exporter.export_excel(df, summary, table, [], teams_path)
    return Result(df, summary, table, teams_path)
