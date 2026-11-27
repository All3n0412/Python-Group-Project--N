"""Command line: python run.py [responses.xlsx] [-o teams.xlsx] [--check teams.xlsx]"""
import sys

from badminton_teams.cli import main

if __name__ == "__main__":
    sys.exit(main())
