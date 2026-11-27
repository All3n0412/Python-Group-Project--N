"""Simple window (tkinter) so the organizer never needs the terminal."""
import os
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from . import pipeline
from .config import DEFAULT_TEAM_SIZE
from .loader import InputDataError

RESULT_COLORS = {"PASS": "#C6EFCE", "WARN": "#FFEB9C", "FAIL": "#FFC7CE"}
TEAM_COLORS = ["#FDE2E2", "#E2EFDA", "#DDEBF7", "#FFF2CC", "#EADCF8", "#FCE4D6"]


class TeamApp(tk.Tk):
    def __init__(self, initial_file=None):
        super().__init__()
        self.title("Badminton Team Formation")
        self.geometry("880x640")
        self.input_path = tk.StringVar(value=initial_file or "")
        self.team_size = tk.IntVar(value=DEFAULT_TEAM_SIZE)
        self.status = tk.StringVar(value="Step 1: choose the Google Form responses file.")
        self.result = None
        self._build()

    # ---------- layout ----------
    def _build(self):
        pad = {"padx": 10, "pady": 6}
        top = ttk.LabelFrame(self, text="1. Input")
        top.pack(fill="x", **pad)
        ttk.Button(top, text="Choose responses file…", command=self.choose_file).grid(row=0, column=0, **pad)
        ttk.Label(top, textvariable=self.input_path, width=70).grid(row=0, column=1, sticky="w", **pad)
        ttk.Label(top, text="Players per team:").grid(row=1, column=0, sticky="e", **pad)
        ttk.Spinbox(top, from_=4, to=10, textvariable=self.team_size, width=5).grid(row=1, column=1, sticky="w", **pad)

        actions = ttk.LabelFrame(self, text="2. Actions")
        actions.pack(fill="x", **pad)
        ttk.Button(actions, text="Form teams", command=self.form_teams).pack(side="left", **pad)
        ttk.Button(actions, text="Re-check edited file…", command=self.recheck).pack(side="left", **pad)
        self.open_btn = ttk.Button(actions, text="Open Excel file", command=self.open_excel, state="disabled")
        self.open_btn.pack(side="left", **pad)

        res = ttk.LabelFrame(self, text="3. Result")
        res.pack(fill="both", expand=True, **pad)
        cols = ("Team", "Players", "Men", "Women", "Avg level", "Min level", "Max level")
        self.summary = ttk.Treeview(res, columns=cols, show="headings", height=6)
        for c in cols:
            self.summary.heading(c, text=c)
            self.summary.column(c, width=105, anchor="center")
        self.summary.pack(fill="x", **pad)
        for i, color in enumerate(TEAM_COLORS, start=1):
            self.summary.tag_configure(f"team{i}", background=color)

        self.checks = ttk.Treeview(res, columns=("Result", "Rule", "Team", "Detail"), show="headings", height=9)
        for c, w in (("Result", 70), ("Rule", 300), ("Team", 60), ("Detail", 300)):
            self.checks.heading(c, text=c)
            self.checks.column(c, width=w, anchor="w" if c in ("Rule", "Detail") else "center")
        self.checks.pack(fill="both", expand=True, **pad)
        for name, color in RESULT_COLORS.items():
            self.checks.tag_configure(name, background=color)

        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w").pack(fill="x", side="bottom")

    # ---------- actions ----------
    def choose_file(self):
        path = filedialog.askopenfilename(title="Choose the Google Form responses file",
                                          filetypes=[("Excel or CSV", "*.xlsx *.csv")])
        if path:
            self.input_path.set(path)
            self.status.set("Step 2: press 'Form teams'.")

    def form_teams(self):
        if not self.input_path.get():
            messagebox.showwarning("No file", "Please choose the responses file first.")
            return
        try:
            self.result = pipeline.form_teams_from_file(self.input_path.get(),
                                                        team_size=int(self.team_size.get()))
        except (InputDataError, FileNotFoundError, ValueError) as err:
            messagebox.showerror("Cannot form teams", str(err))
            self.status.set("Fix the problem above and try again.")
            return
        self.show_result()

    def recheck(self):
        path = filedialog.askopenfilename(title="Choose the edited teams.xlsx",
                                          filetypes=[("Excel", "*.xlsx")])
        if not path:
            return
        try:
            self.result = pipeline.recheck_file(path)
        except Exception as err:                  # wrong file, missing columns...
            messagebox.showerror("Cannot check this file", str(err))
            return
        self.show_result()

    def show_result(self):
        r = self.result
        self.summary.delete(*self.summary.get_children())
        for _, row in r.summary.iterrows():
            t = int(row["Team"])
            self.summary.insert("", "end", tags=(f"team{(t - 1) % 6 + 1}",),
                                values=(t, row["Players"], row["Men"], row["Women"],
                                        f"{row['Avg level']:.2f}", f"{row['Min level']:g}", f"{row['Max level']:g}"))
        self.checks.delete(*self.checks.get_children())
        for _, row in r.checks.iterrows():
            self.checks.insert("", "end", tags=(row["Result"],),
                               values=(row["Result"], row["Rule"], row["Team"], row["Detail"]))
        self.open_btn.config(state="normal")
        self.status.set(f"Overall: {r.overall}  ·  saved as {os.path.basename(r.output_path)} "
                        f"in {os.path.dirname(os.path.abspath(r.output_path))}")

    def open_excel(self):
        path = self.result.output_path
        if sys.platform.startswith("win"):
            os.startfile(path)                        # noqa: only exists on Windows
        else:
            subprocess.Popen(["open" if sys.platform == "darwin" else "xdg-open", path])


def main(initial_file=None, auto_run=False):
    app = TeamApp(initial_file)
    if auto_run and initial_file:                     # used for demos / screenshots
        app.after(300, app.form_teams)
    app.mainloop()


if __name__ == "__main__":
    main()
