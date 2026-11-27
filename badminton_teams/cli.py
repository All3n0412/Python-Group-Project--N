"""Command-line interface.

    python run.py                          -> a window opens to choose the file
    python run.py responses.xlsx           -> teams.xlsx saved next to it
    python run.py responses.xlsx -o my_teams.xlsx --team-size 6
    python run.py --check teams.xlsx       -> re-check after hand edits
"""
import argparse
import sys

from . import pipeline
from .config import DEFAULT_TEAM_SIZE
from .loader import InputDataError


def ask_for_file(title):
    """Open a file-picker window. Returns None if cancelled or no window is possible."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        path = filedialog.askopenfilename(title=title,
                                          filetypes=[("Excel or CSV", "*.xlsx *.csv")])
        root.destroy()
        return path or None
    except Exception:            # e.g. no screen available
        return None


def build_parser():
    p = argparse.ArgumentParser(
        description="Badminton team formation",
        epilog="Example: python run.py responses.xlsx -o teams.xlsx")
    p.add_argument("input", nargs="?", help="Google Form responses (.xlsx or .csv)")
    p.add_argument("-o", "--output", default=None, help="output file (default: teams.xlsx next to input)")
    p.add_argument("--team-size", type=int, default=DEFAULT_TEAM_SIZE)
    p.add_argument("--max-men", type=int, default=None, help="optional cap on men per team")
    p.add_argument("--check", nargs="?", const="", default=None,
                   help="re-check an edited teams.xlsx (no file name = choose in a window)")
    return p


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        if args.check is not None:
            path = args.check or ask_for_file("Choose the edited teams.xlsx")
            if not path:
                print("No file chosen. Usage: python run.py --check teams.xlsx")
                return 1
            result = pipeline.recheck_file(path, args.max_men)
            print(result.checks.to_string(index=False))
        else:
            path = args.input
            if path is None:
                print("Please choose the Google Form responses file...")
                path = ask_for_file("Choose the Google Form responses file")
            if not path:
                print("No file chosen. Usage: python run.py responses.xlsx -o teams.xlsx")
                return 1
            result = pipeline.form_teams_from_file(path, args.output, args.team_size, args.max_men)
            print(result.summary.to_string(index=False))
        print(f"\nOverall: {result.overall}")
        print(f"Saved -> {result.output_path}")
        return 0
    except InputDataError as err:
        print(f"Cannot continue: {err}")
        return 1
    except FileNotFoundError as err:
        print(f"File not found: {err.filename}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
