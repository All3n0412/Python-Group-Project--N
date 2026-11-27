"""Low-fidelity wireframes of the main screens (grey boxes + feature tags)."""
from PIL import Image, ImageDraw, ImageFont

F = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
font = lambda s, b=False: ImageFont.truetype(FB if b else F, s)
W, H, PAD = 560, 400, 26
GRID = (3, 2)
img = Image.new("RGB", (GRID[0] * (W + PAD) + PAD, GRID[1] * (H + PAD + 30) + PAD), "white")
d = ImageDraw.Draw(img)
LINE, FILL, DARK, TAG = "#555555", "#EDEDED", "#9E9E9E", "#305496"


def box(x, y, w, h, text="", fill=FILL, size=13, bold=False, align="center", outline=LINE):
    d.rounded_rectangle([x, y, x + w, y + h], 6, fill=fill, outline=outline, width=2)
    if text:
        f = font(size, bold)
        tw = d.textlength(text, font=f)
        tx = x + (w - tw) / 2 if align == "center" else x + 10
        d.text((tx, y + (h - size) / 2 - 2), text, fill="#222222", font=f)


def lines(x, y, w, n, gap=22, short=False):
    for i in range(n):
        d.line([x, y + i * gap, x + (w * (0.6 if short and i % 2 else 1)), y + i * gap], fill=DARK, width=6)


def tag(x, y, label):
    f = font(12, True)
    tw = d.textlength(label, font=f)
    d.rounded_rectangle([x, y, x + tw + 14, y + 22], 11, fill=TAG)
    d.text((x + 7, y + 3), label, fill="white", font=f)


def panel(col, row, title):
    x = PAD + col * (W + PAD)
    y = PAD + row * (H + PAD + 30)
    d.text((x, y), title, fill="#111111", font=font(16, True))
    y += 30
    d.rectangle([x, y, x + W, y + H], outline="#333333", width=3)
    return x, y


# A. Main window (start)
x, y = panel(0, 0, "Screen A — Main window (start)")
box(x, y, W, 28, "Badminton Team Formation", fill="#D0D7E5", bold=True)
box(x + 15, y + 45, W - 30, 90, fill="white")
d.text((x + 25, y + 50), "1. Input", fill="#333", font=font(12, True))
box(x + 30, y + 72, 190, 30, "Choose responses file…", size=12)
lines(x + 235, y + 87, 280, 1)
d.text((x + 30, y + 110), "Players per team:", fill="#333", font=font(12))
box(x + 160, y + 106, 60, 24, "6 ▲▼", fill="white", size=11)
box(x + 15, y + 145, W - 30, 82, fill="white")
d.text((x + 25, y + 150), "2. Actions", fill="#333", font=font(12, True))
box(x + 30, y + 166, 110, 28, "Form teams", size=12, fill="#C9DAF2")
box(x + 150, y + 166, 180, 28, "Re-check edited file…", size=12)
box(x + 340, y + 166, 140, 28, "Open Excel file", size=12, fill="#F5F5F5", outline="#BBBBBB")
box(x + 15, y + 237, W - 30, 128, fill="white")
d.text((x + 25, y + 242), "3. Result (empty until teams are formed)", fill="#888", font=font(12, True))
box(x, y + H - 28, W, 28, "Step 1: choose the Google Form responses file.", fill="#F2F2F2", size=12, align="left")
tag(x + 230, y + 108, "F8"); tag(x + 50, y + 199, "F2–F5"); tag(x + 220, y + 199, "F6"); tag(x + 390, y + 199, "F7")

# B. File picker
x, y = panel(1, 0, "Screen B — File picker")
box(x, y, W, 28, "Choose the Google Form responses file", fill="#D0D7E5", bold=True)
box(x + 15, y + 45, 150, 270, fill="#F7F7F7")
for i, t in enumerate(["Desktop", "Downloads", "Documents", "project"]):
    d.text((x + 28, y + 58 + i * 28), "▸ " + t, fill="#333", font=font(12))
box(x + 180, y + 45, W - 195, 270, fill="white")
for i, t in enumerate(["responses_2026.xlsx", "responses_old.csv", "teams.xlsx"]):
    box(x + 190, y + 55 + i * 34, W - 215, 26, "📄 " + t if False else t, fill="#E8F0FC" if i == 0 else "white", size=12, align="left")
d.text((x + 190, y + 170), "Only .xlsx and .csv files are shown", fill="#888", font=font(11))
box(x + 15, y + 330, 300, 28, "File name: responses_2026.xlsx", fill="white", size=12, align="left")
box(x + 330, y + 330, 100, 28, "Open", fill="#C9DAF2", size=12)
box(x + 440, y + 330, 100, 28, "Cancel", size=12)
tag(x + 400, y + 300, "F8")

# C. Main window (results)
x, y = panel(2, 0, "Screen C — Main window (results)")
box(x, y, W, 28, "Badminton Team Formation", fill="#D0D7E5", bold=True)
box(x + 15, y + 40, W - 30, 40, fill="white")
d.text((x + 25, y + 52), "1. Input  ·  2. Actions  (same as Screen A)", fill="#888", font=font(12))
heads = ["Team", "Players", "Men", "Women", "Avg", "Min", "Max"]
cw = (W - 90) / len(heads)
for i, h in enumerate(heads):
    box(x + 25 + i * cw, y + 92, cw, 24, h, fill="#D9D9D9", size=11, bold=True)
colors = ["#FDE2E2", "#E2EFDA", "#DDEBF7", "#FFF2CC"]
vals = [["1", "7", "4", "3", "4.71", "4", "5"], ["2", "7", "5", "2", "3.29", "2", "5"],
        ["3", "6", "4", "2", "2.67", "2", "4"], ["4", "6", "4", "2", "2.17", "1", "4"]]
for r, (c, v) in enumerate(zip(colors, vals)):
    for i, t in enumerate(v):
        box(x + 25 + i * cw, y + 116 + r * 22, cw, 22, t, fill=c, size=11, outline="#AAAAAA")
for i, h in enumerate(["Result", "Rule", "Team", "Detail"]):
    ws = [70, 220, 50, W - 90 - 340][i]
    box(x + 25 + [0, 70, 290, 340][i], y + 215, ws, 24, h, fill="#D9D9D9", size=11, bold=True)
for r in range(5):
    box(x + 25, y + 239 + r * 22, 70, 22, "PASS", fill="#C6EFCE", size=11, outline="#AAAAAA")
    lines(x + 105, y + 250 + r * 22, 200, 1); lines(x + 375, y + 250 + r * 22, 90, 1)
box(x, y + H - 28, W, 28, "Overall: PASS · saved as teams.xlsx in <same folder>", fill="#F2F2F2", size=12, align="left")
tag(x + W - 58, y + 94, "F5"); tag(x + W - 58, y + 217, "F6"); tag(x + W - 58, y + H - 26, "F7")

# D. Error dialog
x, y = panel(0, 1, "Screen D — Error message")
box(x, y, W, 28, "Badminton Team Formation", fill="#D0D7E5", bold=True)
for i in range(3):
    box(x + 15, y + 45 + i * 110, W - 30, 95, fill="#F7F7F7", outline="#CCCCCC")
box(x + 95, y + 120, 370, 150, fill="white", outline="#333333")
box(x + 95, y + 120, 370, 26, "Cannot form teams", fill="#D0D7E5", bold=True, size=12)
d.ellipse([x + 110, y + 165, x + 140, y + 195], fill="#E53935")
d.text((x + 152, y + 160), "Only 7 women for 4 teams (need 8).", fill="#222", font=font(12, True))
d.text((x + 152, y + 180), "Use a bigger team size (fewer teams)", fill="#222", font=font(12))
d.text((x + 152, y + 198), "or recruit more women.", fill="#222", font=font(12))
box(x + 240, y + 232, 80, 28, "OK", size=12, fill="#C9DAF2")
tag(x + 400, y + 92, "F2/F4")
d.text((x + 20, y + 290), "Other messages: missing gender/level (names the rows),", fill="#555", font=font(12))
d.text((x + 20, y + 308), "wrong file type, 'Fixed team' out of range.", fill="#555", font=font(12))

# E. Excel output
x, y = panel(1, 1, "Screen E — teams.xlsx (Excel output)")
box(x, y, W, 28, "teams.xlsx — Excel", fill="#D7EBD9", bold=True)
heads = ["Team", "Name", "Gender", "Level", "Level from", "Attitude", "1st event"]
cw = (W - 30) / len(heads)
for i, h in enumerate(heads):
    box(x + 15 + i * cw, y + 42, cw, 24, h, fill="#305496", size=10, bold=True, outline="#305496")
d.text((x + 15, y + 44), "", fill="white")
for r in range(10):
    c = colors[min(r // 3, 3)]
    for i in range(len(heads)):
        box(x + 15 + i * cw, y + 66 + r * 22, cw, 22, fill=c, outline="#BBBBBB")
d.text((x + 20, y + 290), "(one colour per team; organizer may edit the Team column)", fill="#555", font=font(11))
for i, t in enumerate(["Teams", "Summary", "Checks", "Input issues"]):
    box(x + 15 + i * 125, y + H - 40, 118, 26, t, fill="white" if i else "#D7EBD9", size=11, bold=(i == 0))
tag(x + 470, y + 300, "F7"); tag(x + 20, y + H - 70, "F6 (Checks)")

# F. Google Form
x, y = panel(2, 1, "Screen F — Google Form (players)")
box(x, y, W, 40, "2026 Econ Badminton Cup — Sign-up", fill="#EADCF8", bold=True, size=14)
qs = [("Name *", "text"), ("Gender *  ○ Male  ○ Female", "radio"),
      ("Self-rated level *  ○1 ○2 ○3 ○4 ○5", "radio"),
      ("Attitude *  ○ Play to win  ○ Flexible  ○ For fun", "radio"),
      ("Preferred event 1st / 2nd  [dropdown]", "radio")]
for i, (q, kind) in enumerate(qs):
    box(x + 15, y + 52 + i * 62, W - 30, 54, fill="white")
    d.text((x + 28, y + 60 + i * 62), q, fill="#222", font=font(12, True))
    if kind == "text":
        d.line([x + 28, y + 92, x + 300, y + 92], fill=DARK, width=2)
    else:
        d.text((x + 28, y + 80 + i * 62), "level guide: 1 = beginner … 5 = school team" if "level" in q else "",
               fill="#777", font=font(11))
tag(x + 470, y + 8, "F1"); tag(x + 470, y + 172, "F3")

img.save("wireframes.png")
print(img.size)
