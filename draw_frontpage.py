"""Draw the front page for news-image-20261117, round 2.

A one-page newspaper for Tuesday 17 November 2026: 45 stories from
seven regions, all drawn in code with PIL. No photos, no copied art:
every panel is a flat vector illustration drawn by the functions below,
and every word is rendered by this script, so nothing is garbled.

Layout (1024x1024, cream paper):
  kicker line -> navy masthead -> region count bar -> BY THE NUMBERS
  -> 3 illustrated leads -> 2 rows of 5 illustrated mid stories
  -> world map with numbered pins + ALSO list (stories 14-45)
  -> footer with sources and a DATE CHECK note.
"""

import hashlib
import os

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_PATH = os.path.join(HERE, "entry.png")

W, H = 1024, 1024

PAPER = (246, 239, 221)
INK = (22, 22, 22)
NAVY = (20, 38, 78)
GOLD = (201, 162, 39)
RED = (176, 30, 36)
BLUE = (46, 95, 163)
ORANGE = (198, 93, 33)
PURPLE = (122, 79, 163)
GREEN = (46, 125, 79)
TEAL = (14, 124, 123)
GREY = (90, 90, 90)
SKY = (191, 217, 232)
SEA = (127, 179, 213)
SAND = (232, 217, 176)
LAND_DOT = (201, 169, 106)
MAP_SEA = (207, 227, 238)
WHITE = (255, 255, 255)
BLACK = (10, 10, 10)

SERIF = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"


def fnt(path, size):
    return ImageFont.truetype(path, size)


def wrap_text(text, font, width):
    """Greedy word wrap; returns a list of lines that fit `width`."""
    lines = []
    for para in text.split("\n"):
        words = para.split()
        if not words:
            lines.append("")
            continue
        cur = words[0]
        for w in words[1:]:
            trial = cur + " " + w
            if font.getlength(trial) <= width:
                cur = trial
            else:
                lines.append(cur)
                cur = w
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, font, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=font, fill=fill)
        y += leading
    return y


def fit_lines(text, font_path, size, width, max_lines, min_size=8):
    """Shrink the font until `text` wraps into at most `max_lines`."""
    s = size
    while s > min_size:
        fo = fnt(font_path, s)
        if len(wrap_text(text, fo, width)) <= max_lines:
            return fo, wrap_text(text, fo, width)
        s -= 1
    fo = fnt(font_path, s)
    return fo, wrap_text(text, fo, width)[:max_lines]


# ---------------------------------------------------------------- stories
# Regions: (label, count, colour). Counts sum to 45.
REGIONS = [
    ("EUROPE", 12, BLUE),
    ("MIDDLE EAST", 8, ORANGE),
    ("ASIA", 10, PURPLE),
    ("AFRICA", 8, GREEN),
    ("AMERICAS", 5, RED),
    ("OCEANIA", 1, TEAL),
    ("WORLD", 1, GREY),
]

NUMBERS = [
    ("1,441", "drones Russia says it downed"),
    ("$115.8bn", "Nvidia's quarter"),
    ("11,000+", "Ebola cases in DR Congo"),
    ("-849", "Dow points"),
    ("66-52", "Knesset speaker vote"),
    ("25.9bn km", "Voyager 1 nears one light-day"),
]

# Leads: n, kicker, kicker colour, headline, summary, caption, illustrator.
LEADS = [
    dict(n=1, kick="EUROPE - WAR", col=BLUE,
         head="Ukraine says a Kerch Bridge road span fell into the sea",
         summ="Second strike in two days; Zelensky hails an "
              "'unprecedented operation'. The Kremlin vows to rebuild; "
              "two dead.",
         cap="KERCH STRAIT - STRUCK FOR A SECOND DAY", ill="kerch"),
    dict(n=2, kick="MIDDLE EAST - IRAN WAR", col=ORANGE,
         head="Iran sends drones at a US radar in Bahrain; US hits back",
         summ="Bahrain and the US say all were downed; US jets then "
              "strike Qeshm. Iran says tankers hit mines in Hormuz.",
         cap="STRAIT OF HORMUZ - IRAN'S CLAIM, UNVERIFIED", ill="gulf"),
    dict(n=3, kick="ASIA - DIPLOMACY", col=PURPLE,
         head="Trump holds his first Quad summit, in Manila",
         summ="The four unveil critical-minerals deals; Putin reaches "
              "Shenzhen for Thursday's talks with Trump and Xi.",
         cap="QUAD LEADERS' SUMMIT - MANILA", ill="quad"),
]

# Mid stories: n, kicker, colour, headline, summary, caption, illustrator.
MIDS = [
    dict(n=4, kick="US - BUSINESS", col=RED,
         head="Nvidia's quarterly sales double to $115.8bn",
         summ="Reported after the close. Earlier the Dow fell 849 points.",
         cap="NVIDIA QUARTER", ill="nvidia"),
    dict(n=5, kick="AFRICA - HEALTH", col=GREEN,
         head="Ebola cases in DR Congo top 11,000, WHO says",
         summ="Cases more than doubled in three months; about 5,400 died.",
         cap="DR CONGO - EBOLA", ill="ebola"),
    dict(n=6, kick="AMERICAS - HEALTH", col=RED,
         head="US, Mexico and Bolivia lose measles-free status",
         summ="PAHO cites a year of spread; the US has 5,400+ cases.",
         cap="PAHO - MEASLES", ill="measles"),
    dict(n=7, kick="GLOBAL - CLIMATE", col=GREY,
         head="COP31 split over fossil-fuel phase-out",
         summ="Nations weigh the first draft; the Antalya talks end Friday.",
         cap="ANTALYA - COP31", ill="cop31"),
    dict(n=8, kick="MIDDLE EAST - POLITICS", col=ORANGE,
         head="Netanyahu rival wins Knesset speaker vote",
         summ="Matan Kahana elected 66-52 after a six-hour filibuster.",
         cap="NEW SPEAKER", ill="knesset"),
    dict(n=9, kick="ASIA - DEFENCE", col=PURPLE,
         head="Japan scrambles jets over airspace breach",
         summ="Two suspected Russian aircraft off Fukuoka, Tokyo says.",
         cap="SEA OF JAPAN - JETS", ill="jets"),
    dict(n=10, kick="EUROPE - POLITICS", col=BLUE,
         head="Serbia's student-led majority takes its seats",
         summ="Student List holds 140 of 250 seats; Vucic's bloc has 103.",
         cap="BELGRADE - PARLIAMENT", ill="serbia"),
    dict(n=11, kick="ASIA - LABOUR", col=GREEN,
         head="Bangladesh police tear-gas garment workers",
         summ="They want Tk 30,000 a month, up from 12,500; 37 shut.",
         cap="DHAKA - WAGES", ill="bangladesh"),
    dict(n=12, kick="RUSSIA - AIR CRASH", col=BLUE,
         head="Russian An-12 crash in Siberia kills all 19",
         summ="Air force plane came down near Kemerovo; a fault suspected.",
         cap="KEMEROVO - ALL 19 ABOARD", ill="an12"),
    dict(n=13, kick="AFRICA - JUSTICE", col=GREEN,
         head="Mozambique puts opposition leader on trial",
         summ="Venancio Mondlane faces 5 charges over deadly 2024 protests.",
         cap="MAPUTO - TRIAL", ill="mozambique"),
]

# ALSO list: (n, region colour, bold kicker, text). One line each.
ALSO = [
    (14, BLUE, "Kyiv:", "missiles hit the North and South Dnipro bridges"),
    (15, BLUE, "Russia:", "says it downed a record 1,441 drones overnight"),
    (16, BLUE, "Moldova:", "shuts its airspace over a Russian drone"),
    (17, BLUE, "Prague:", "two trains collide; 46 people injured"),
    (18, BLUE, "France:", "public-sector strike; 146,000 march"),
    (19, BLUE, "Poland:", "Tusk's government survives a no-confidence vote"),
    (20, BLUE, "Germany:", "Deutsche Bank shares fall after a huge data leak"),
    (21, BLUE, "Turkey:", "police seize opposition channel Sozcu TV"),
    (22, BLUE, "UK:", "sanctions 8 settlement firms; Tzav 9"),
    (23, ORANGE, "Gaza:", "UN says 1.4m face acute hunger in winter"),
    (24, ORANGE, "West Bank:", "settlers kill a woman, 72, near Jericho"),
    (25, ORANGE, "Oman:", "Iran's Araghchi holds shipping-safety talks"),
    (26, ORANGE, "Kuwait:", "air defences repel drones"),
    (27, ORANGE, "Yemen:", "Houthis advance on Aden as forces pull back"),
    (28, ORANGE, "Hormuz:", "two ships burn after mine blast, Iran says"),
    (29, GREEN, "Sudan:", "UN verifies 2,230 civilian deaths, Jan-Oct"),
    (30, GREEN, "Guinea:", "224 jailed in a gold-mining crackdown"),
    (31, GREEN, "Kenya:", "WFP aids 30,000 who fled Ethiopia clashes"),
    (32, GREEN, "South Africa:", "police probe deadly mass shootings"),
    (33, GREEN, "Togo:", "beat Algeria 3-0 in AFCON qualifier"),
    (34, GREEN, "Fela Kuti:", "first African in the Rock Hall of Fame"),
    (35, PURPLE, "India:", "Cyclone Akvan heads for Andhra Pradesh"),
    (36, PURPLE, "India:", "bus falls into Uttarakhand gorge, 8 dead"),
    (37, PURPLE, "China-Canada:", "Xi and Carney agree tariff cuts"),
    (38, PURPLE, "Malaysia:", "Macron visit seals a strategic partnership"),
    (39, PURPLE, "Thailand:", "pledges to scrap tariffs on US goods"),
    (40, PURPLE, "South Korea:", "IMF lifts 2026 growth forecast to 3.9%"),
    (41, PURPLE, "India:", "beat Pakistan 2-1 in SAFF final"),
    (42, RED, "US Senate:", "Van Hollen challenges Schumer for leader"),
    (43, RED, "Apple:", "Pay, iCloud and App Store outage; not a hack"),
    (44, RED, "Haiti:", "Aristide's party will field no candidates"),
    (45, TEAL, "Australia:", "eases planned backpacker visa curbs"),
]

# Pin positions for stories 1-13: (lon, lat) of the story's place.
PINS = {
    1: (34.0, 45.0), 2: (50.6, 26.2), 3: (121.0, 14.6),
    4: (-95.0, 37.0), 5: (25.0, -2.0), 6: (-64.0, -17.0),
    7: (30.7, 36.9), 8: (35.2, 31.8), 9: (130.4, 33.6),
    10: (20.5, 44.8), 11: (90.4, 23.8), 12: (86.0, 55.0),
    13: (32.6, -25.9),
}
# Label offsets (dx, dy) to de-crowd the Middle East / Europe cluster.
PIN_OFF = {1: (-16, -14), 7: (2, 16), 8: (16, -6), 9: (10, -8),
           10: (-18, 8), 2: (14, 12)}
# Small dots for ALSO stories with a clear place: (lon, lat, colour).
DOTS = [
    (30.5, 50.4, BLUE), (37.6, 55.7, BLUE), (28.8, 47.0, BLUE),
    (14.4, 50.1, BLUE), (2.35, 48.85, BLUE), (13.4, 52.5, BLUE),
    (32.85, 39.9, BLUE), (-0.1, 51.5, BLUE), (34.45, 31.5, ORANGE),
    (32.5, 15.6, ORANGE), (36.8, -1.3, GREEN), (28.0, -26.2, GREEN),
    (1.2, 6.1, GREEN), (77.2, 28.6, PURPLE), (79.0, 30.0, PURPLE),
    (116.4, 39.9, PURPLE), (101.7, 3.1, PURPLE), (100.5, 13.75, PURPLE),
    (127.0, 37.5, PURPLE), (67.0, 24.86, PURPLE), (-77.0, 38.9, RED),
    (-72.3, 18.5, RED), (149.1, -35.3, TEAL),
]

# ------------------------------------------------------------- tiny flags
def flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=RED if i % 2 == 0 else WHITE)
    d.rectangle([x, y, x + w * 0.4, y + h * 4 / 7], fill=NAVY)
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * w * 0.09, y + 2 + r * h * 0.18,
                       x + 6 + c * w * 0.09, y + 5 + r * h * 0.18],
                      fill=WHITE)


def flag_in(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=(255, 153, 51))
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=WHITE)
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=(19, 136, 8))
    d.ellipse([x + w / 2 - h / 6, y + h / 3, x + w / 2 + h / 6,
               y + 2 * h / 3], outline=NAVY, width=1)


def flag_jp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    d.ellipse([x + w / 2 - h / 5, y + h / 2 - h / 5,
               x + w / 2 + h / 5, y + h / 2 + h / 5], fill=RED)


def flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    d.rectangle([x, y, x + w / 2, y + h / 2], fill=RED)
    d.line([x, y, x + w / 2, y + h / 2], fill=WHITE, width=1)
    d.line([x + w / 2, y, x, y + h / 2], fill=WHITE, width=1)
    for sx, sy in [(0.72, 0.3), (0.85, 0.55), (0.68, 0.72), (0.85, 0.78)]:
        d.ellipse([x + w * sx - 1, y + h * sy - 1, x + w * sx + 1,
                   y + h * sy + 1], fill=WHITE)


def flag_mx(d, x, y, w, h):
    d.rectangle([x, y, x + w / 3, y + h], fill=GREEN)
    d.rectangle([x + w / 3, y, x + 2 * w / 3, y + h], fill=WHITE)
    d.rectangle([x + 2 * w / 3, y, x + w, y + h], fill=RED)


def flag_bo(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h / 3], fill=RED)
    d.rectangle([x, y + h / 3, x + w, y + 2 * h / 3], fill=(255, 235, 0))
    d.rectangle([x, y + 2 * h / 3, x + w, y + h], fill=GREEN)


# --------------------------------------------------------- illustrations
# Every illustrator gets (draw, x, y, w, h) for its panel and draws a
# flat vector scene. `band` paints the black caption strip at the bottom.

def band(d, x, y, w, h, text, fill=BLACK):
    d.rectangle([x, y + h - 13, x + w, y + h], fill=fill)
    d.text((x + 5, y + h - 12), text, font=fnt(SANS_B, 8), fill=WHITE)


def ill_kerch(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.62, x + w, y + h], fill=SEA)
    for i in range(5):  # waves
        d.arc([x + 12 + i * 62, y + h * 0.7, x + 52 + i * 62, y + h * 0.86],
              200, 340, fill=WHITE, width=2)
    d.rectangle([x, y + h * 0.42, x + w * 0.44, y + h * 0.48], fill=INK)
    d.rectangle([x + w * 0.58, y + h * 0.42, x + w, y + h * 0.48], fill=INK)
    d.polygon([(x + w * 0.44, y + h * 0.48), (x + w * 0.52, y + h * 0.62),
               (x + w * 0.47, y + h * 0.62)], fill=INK)
    for px in (0.08, 0.3, 0.68, 0.88):  # pillars
        d.rectangle([x + w * px, y + h * 0.48, x + w * px + 6, y + h * 0.62],
                    fill=INK)
    d.arc([x + w * 0.18, y + h * 0.05, x + w * 0.42, y + h * 0.5],
          180, 360, fill=INK, width=3)
    d.arc([x + w * 0.6, y + h * 0.05, x + w * 0.84, y + h * 0.5],
          180, 360, fill=INK, width=3)
    for cx, cy, r in [(0.5, 0.3, 14), (0.46, 0.24, 10), (0.54, 0.22, 8)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(120, 120, 120))
    for sx, sy in [(0.52, 0.36), (0.56, 0.32), (0.48, 0.38)]:
        d.polygon([(x + w * sx, y + h * sy - 7), (x + w * sx - 5,
                   y + h * sy + 5), (x + w * sx + 5, y + h * sy + 5)],
                  fill=(255, 170, 0))
    for jx, jy in [(0.2, 0.12), (0.8, 0.1)]:  # jets
        d.polygon([(x + w * jx, y + h * jy), (x + w * jx + 16,
                   y + h * jy + 4), (x + w * jx, y + h * jy + 8)],
                  fill=INK)
    d.text((x + 6, y + 4), "CRIMEA", font=fnt(SANS_B, 8), fill=INK)
    d.text((x + w - 42, y + 4), "RUSSIA", font=fnt(SANS_B, 8), fill=INK)
    band(d, x, y, w, h, "KERCH STRAIT")


def ill_gulf(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SAND)
    d.polygon([(x, y + h * 0.45), (x + w * 0.35, y + h * 0.3),
               (x + w * 0.7, y + h * 0.45), (x + w, y + h * 0.35),
               (x + w, y + h), (x, y + h)], fill=SEA)
    d.polygon([(x + w * 0.1, y + h * 0.32), (x + w * 0.3, y + h * 0.25),
               (x + w * 0.45, y + h * 0.4), (x + w * 0.2, y + h * 0.5)],
              fill=(214, 196, 150))
    for i in range(5):  # dashed drone path
        d.line([x + w * (0.2 + i * 0.09), y + h * (0.32 - i * 0.02),
                x + w * (0.27 + i * 0.09), y + h * (0.3 - i * 0.02)],
               fill=RED, width=2)
    d.polygon([(x + w * 0.62, y + h * 0.2), (x + w * 0.66, y + h * 0.24),
               (x + w * 0.62, y + h * 0.28), (x + w * 0.58, y + h * 0.24)],
              fill=INK)
    d.rectangle([x + w * 0.74, y + h * 0.55, x + w * 0.9, y + h * 0.62],
                fill=(90, 40, 40))
    d.rectangle([x + w * 0.79, y + h * 0.48, x + w * 0.83, y + h * 0.55],
                fill=(90, 40, 40))
    for cx, cy, r in [(0.82, 0.44, 7), (0.85, 0.4, 5)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(120, 120, 120))
    d.text((x + 6, y + 4), "BAHRAIN", font=fnt(SANS_B, 8), fill=INK)
    d.text((x + w - 40, y + 4), "QESHM", font=fnt(SANS_B, 8), fill=INK)
    d.text((x + w * 0.42, y + h * 0.55), "HORMUZ",
           font=fnt(SANS_B, 8), fill=INK)
    band(d, x, y, w, h, "GULF - DRONES DOWNED")


def ill_quad(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 228, 245))
    d.rectangle([x, y, x + w, y + 16], fill=PURPLE)
    d.text((x + w / 2 - 62, y + 3), "QUAD LEADERS' SUMMIT",
           font=fnt(SANS_B, 9), fill=WHITE)
    d.rectangle([x + w * 0.08, y + h * 0.66, x + w * 0.92, y + h * 0.75],
                fill=(120, 72, 32))
    d.rectangle([x + w * 0.1, y + h * 0.75, x + w * 0.14, y + h * 0.9],
                fill=(90, 54, 24))
    d.rectangle([x + w * 0.86, y + h * 0.75, x + w * 0.9, y + h * 0.9],
                fill=(90, 54, 24))
    fw, fh = w * 0.17, 24
    for i, fn in enumerate([flag_us, flag_in, flag_jp, flag_au]):
        fx = x + w * (0.08 + i * 0.21)
        d.rectangle([fx + fw / 2 - 1, y + h * 0.3, fx + fw / 2 + 1,
                     y + h * 0.64], fill=INK)
        fn(d, fx, y + h * 0.3, fw, fh)
    for i, nm in enumerate(["US", "INDIA", "JAPAN", "AUSTRALIA"]):
        d.text((x + w * (0.08 + i * 0.21), y + h * 0.3 + fh + 2), nm,
               font=fnt(SANS_B, 7), fill=INK)
    band(d, x, y, w, h, "MANILA - CRITICAL MINERALS", fill=PURPLE)


def ill_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(16, 40, 24))
    d.rectangle([x + 10, y + 10, x + 52, y + 52], fill=(118, 185, 0))
    d.rectangle([x + 20, y + 20, x + 42, y + 42], fill=(16, 40, 24))
    d.text((x + 27, y + 25), "AI", font=fnt(SANS_B, 12), fill=(118, 185, 0))
    for i, bh in enumerate([10, 16, 12, 22, 30]):
        d.rectangle([x + 62 + i * 16, y + 52 - bh, x + 74 + i * 16, y + 52],
                    fill=(118, 185, 0))
    d.text((x + 62, y + 8), "$115.8bn", font=fnt(SANS_B, 13),
           fill=(118, 185, 0))
    d.text((x + 62, y + 26), "+103% y/y", font=fnt(SANS, 9), fill=WHITE)
    band(d, x, y, w, h, "DOW -849", fill=(16, 40, 24))


def ill_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.polygon([(x + 12, y + h - 16), (x + 62, y + 12), (x + 112, y + h - 16)],
              fill=WHITE, outline=INK)
    d.rectangle([x + 52, y + 26, x + 72, y + 34], fill=RED)
    d.rectangle([x + 60, y + 18, x + 64, y + 42], fill=RED)
    for bx, bh in [(128, 12), (146, 22), (164, 34)]:
        d.rectangle([x + bx, y + h - 16 - bh, x + bx + 12, y + h - 16],
                    fill=RED)
    d.text((x + 126, y + 6), "11,000+", font=fnt(SANS_B, 11), fill=RED)
    for cx, cy in [(0.62, 0.35), (0.72, 0.5), (0.85, 0.3)]:
        px, py = x + w * cx, y + h * cy
        for k in range(8):
            import math
            a = k * math.pi / 4
            d.line([px, py, px + 9 * math.cos(a), py + 9 * math.sin(a)],
                   fill=RED, width=1)
        d.ellipse([px - 5, py - 5, px + 5, py + 5], fill=RED)
    band(d, x, y, w, h, "CASES DOUBLED IN 3 MONTHS", fill=RED)


def ill_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(250, 240, 230))
    import math
    px, py = x + 34, y + h / 2 - 4
    for k in range(10):
        a = k * math.pi / 5
        d.line([px, py, px + 15 * math.cos(a), py + 15 * math.sin(a)],
               fill=RED, width=2)
    d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=RED)
    fw, fh = 34, 20
    for i, fn in enumerate([flag_us, flag_mx, flag_bo]):
        fn(d, x + 62 + i * 40, y + 8, fw, fh)
    for i, nm in enumerate(["US", "MEXICO", "BOLIVIA"]):
        d.text((x + 62 + i * 40, y + 30), nm, font=fnt(SANS_B, 7), fill=INK)
    band(d, x, y, w, h, "MEASLES-FREE STATUS LOST", fill=RED)


def ill_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(225, 238, 245))
    d.ellipse([x + 10, y + 8, x + 74, y + h - 20], fill=SEA)
    d.ellipse([x + 22, y + 20, x + 40, y + 34], fill=GREEN)
    d.ellipse([x + 44, y + 40, x + 62, y + 52], fill=GREEN)
    d.ellipse([x + 28, y + h - 34, x + 46, y + h - 22], fill=GREEN)
    d.rectangle([x + 96, y + 12, x + w - 10, y + h - 16], fill=WHITE,
                outline=INK)
    d.text((x + 104, y + 16), "DRAFT", font=fnt(SANS_B, 10), fill=RED)
    for i in range(3):
        d.line([x + 104, y + 32 + i * 7, x + w - 18, y + 32 + i * 7],
               fill=(170, 170, 170), width=2)
    d.line([x + 78, y + h / 2, x + 92, y + h / 2], fill=RED, width=3)
    d.polygon([(x + 92, y + h / 2 - 4), (x + 92, y + h / 2 + 4),
               (x + 100, y + h / 2)], fill=RED)
    band(d, x, y, w, h, "DRAFT TEXT DIVIDES SUMMIT")


def ill_knesset(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 220))
    d.polygon([(x + 20, y + 34), (x + 95, y + 6), (x + 170, y + 34)],
              fill=(200, 190, 170))
    for i in range(5):
        d.rectangle([x + 26 + i * 30, y + 36, x + 34 + i * 30, y + h - 16],
                    fill=(200, 190, 170))
    d.rectangle([x + 16, y + h - 18, x + 178, y + h - 14], fill=INK)
    d.rectangle([x + 130, y + 8, x + 160, y + 18], fill=(120, 72, 32))
    d.line([x + 158, y + 18, x + 172, y + 32], fill=(120, 72, 32), width=3)
    d.rectangle([x + 8, y + 8, x + 84, y + 18], fill=BLUE)
    d.text((x + 12, y + 9), "66", font=fnt(SANS_B, 8), fill=WHITE)
    d.rectangle([x + 86, y + 8, x + 132, y + 18], fill=RED)
    d.text((x + 90, y + 9), "52", font=fnt(SANS_B, 8), fill=WHITE)
    band(d, x, y, w, h, "KAHANA 66 - KATZ 52")


def ill_jets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w - 52, y + 4, x + w - 16, y + 40], fill=RED)
    for jx, jy, s in [(0.25, 0.35, 1), (0.55, 0.55, -1)]:
        px, py = x + w * jx, y + h * jy
        d.polygon([(px, py), (px + 34 * s, py + 5), (px + 30 * s, py + 10),
                   (px + 4 * s, py + 10)], fill=(70, 70, 70))
        d.polygon([(px + 12 * s, py), (px + 18 * s, py - 8),
                   (px + 22 * s, py)], fill=(70, 70, 70))
    for r in (18, 30):
        d.arc([x + 8, y + h - 14 - r, x + 8 + 2 * r, y + h - 14 + r],
              270, 360, fill=INK, width=1)
    band(d, x, y, w, h, "2 JETS OFF FUKUOKA")


def ill_serbia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(235, 230, 245))
    d.polygon([(x + 30, y + 30), (x + 97, y + 8), (x + 164, y + 30)],
              fill=(180, 170, 200))
    for i in range(4):
        d.rectangle([x + 38 + i * 34, y + 32, x + 46 + i * 34, y + h - 16],
                    fill=(180, 170, 200))
    for i in range(9):
        cx = x + 14 + i * 20
        d.ellipse([cx, y + h - 26, cx + 8, y + h - 18], fill=INK)
        d.rectangle([cx - 1, y + h - 18, cx + 9, y + h - 14], fill=RED)
    d.text((x + 8, y + 4), "140", font=fnt(SANS_B, 14), fill=BLUE)
    d.text((x + 40, y + 8), "OF 250 SEATS", font=fnt(SANS_B, 8), fill=INK)
    band(d, x, y, w, h, "STUDENT LIST SWORN IN")


def ill_bangladesh(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 235, 220))
    d.rectangle([x + 10, y + 22, x + 110, y + h - 16], fill=(150, 150, 150))
    d.rectangle([x + 96, y + 6, x + 106, y + 22], fill=(150, 150, 150))
    for cx, cy, r in [(0.55, 0.14, 5), (0.58, 0.1, 4)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(160, 160, 160))
    for i in range(4):
        d.rectangle([x + 20 + i * 22, y + 30, x + 32 + i * 22, y + 42],
                    fill=(90, 90, 90))
    for i in range(5):
        cx = x + 122 + i * 14
        d.ellipse([cx, y + h - 28, cx + 7, y + h - 21], fill=INK)
        d.rectangle([cx, y + h - 21, cx + 7, y + h - 16], fill=GREEN)
    d.rectangle([x + 118, y + 6, x + w - 8, y + 22], fill=WHITE,
                outline=INK)
    d.text((x + 121, y + 9), "TK 30,000", font=fnt(SANS_B, 9), fill=INK)
    band(d, x, y, w, h, "37 FACTORIES SHUT")


def ill_an12(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(200, 210, 220))
    d.polygon([(x, y + h - 16), (x + 60, y + 22), (x + 120, y + h - 16)],
              fill=(140, 150, 160))
    d.polygon([(x + 110, y + h - 16), (x + 160, y + 30),
               (x + w, y + h - 16)], fill=(160, 170, 180))
    px, py = x + 55, y + 18
    d.polygon([(px, py), (px + 80, py + 6), (px + 76, py + 12),
               (px + 8, py + 12)], fill=(60, 60, 60))
    d.polygon([(px + 30, py), (px + 40, py - 10), (px + 46, py)],
              fill=(60, 60, 60))
    d.polygon([(px + 66, py + 6), (px + 76, py - 4), (px + 80, py + 6)],
              fill=(60, 60, 60))
    for cx, cy, r in [(0.3, 0.35, 8), (0.38, 0.3, 6), (0.24, 0.42, 5)]:
        d.ellipse([x + w * cx - r, y + h * cy - r, x + w * cx + r,
                   y + h * cy + r], fill=(120, 120, 120))
    band(d, x, y, w, h, "FAULT SUSPECTED", fill=RED)


def ill_mozambique(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 232, 220))
    d.polygon([(x + 24, y + 30), (x + 97, y + 8), (x + 170, y + 30)],
              fill=(190, 180, 160))
    for i in range(4):
        d.rectangle([x + 32 + i * 34, y + 32, x + 40 + i * 34, y + h - 16],
                    fill=(190, 180, 160))
    d.rectangle([x + 20, y + h - 18, x + 174, y + h - 14], fill=INK)
    d.rectangle([x + 8, y + 8, x + 78, y + 20], fill=GREEN)
    d.text((x + 12, y + 10), "5 CHARGES", font=fnt(SANS_B, 9), fill=WHITE)
    d.rectangle([x + 140, y + 8, x + 162, y + 16], fill=(120, 72, 32))
    d.line([x + 160, y + 16, x + 172, y + 28], fill=(120, 72, 32), width=3)
    band(d, x, y, w, h, "MONDLANE ON TRIAL")


ILLS = {
    "kerch": ill_kerch, "gulf": ill_gulf, "quad": ill_quad,
    "nvidia": ill_nvidia, "ebola": ill_ebola, "measles": ill_measles,
    "cop31": ill_cop31, "knesset": ill_knesset, "jets": ill_jets,
    "serbia": ill_serbia, "bangladesh": ill_bangladesh,
    "an12": ill_an12, "mozambique": ill_mozambique,
}

# ------------------------------------------------------------------- map
# Coarse continent outlines as (lon, lat) lists. Public-domain style
# geography, traced from memory of the world map; the dotted rendering
# forgives the coarseness.
LAND = [
    [(-168, 66), (-150, 70), (-130, 71), (-110, 68), (-95, 69), (-85, 67),
     (-78, 71), (-68, 60), (-58, 52), (-64, 45), (-72, 40), (-76, 34),
     (-81, 31), (-86, 30), (-90, 21), (-96, 16), (-102, 18), (-108, 23),
     (-114, 29), (-122, 37), (-124, 48), (-135, 58), (-152, 58),
     (-166, 60)],
    [(-56, 60), (-48, 60), (-42, 64), (-32, 68), (-24, 70), (-20, 74),
     (-28, 76), (-42, 77), (-55, 75), (-58, 68)],
    [(-79, 9), (-72, 12), (-63, 10), (-55, 6), (-50, 0), (-44, -4),
     (-37, -7), (-35, -14), (-39, -21), (-47, -27), (-54, -34),
     (-62, -41), (-68, -50), (-71, -54), (-73, -46), (-73, -36),
     (-72, -26), (-76, -14), (-81, -4), (-80, 3)],
    [(-10, 36), (-9, 43), (-2, 48), (1, 51), (5, 53), (8, 57), (11, 58),
     (18, 56), (21, 55), (25, 59), (28, 62), (30, 66), (27, 71),
     (22, 70), (16, 68), (10, 64), (5, 59), (-2, 57), (-8, 54),
     (-10, 49), (-9, 43)],
    [(-6, 35), (-10, 31), (-16, 25), (-17, 18), (-16, 12), (-12, 7),
     (-8, 4), (0, 6), (6, 4), (9, 4), (9, -1), (12, -6), (13, -12),
     (13, -18), (15, -24), (17, -30), (20, -35), (26, -34), (32, -29),
     (35, -24), (39, -18), (40, -11), (41, -4), (46, 0), (51, 3),
     (51, 11), (47, 12), (43, 13), (39, 17), (37, 21), (35, 27),
     (33, 31), (28, 32), (20, 32), (11, 34), (5, 37), (0, 36)],
    [(28, 41), (30, 46), (28, 51), (31, 56), (33, 61), (36, 66),
     (41, 68), (47, 68), (53, 69), (59, 69), (66, 70), (72, 72),
     (78, 73), (85, 74), (92, 75), (99, 76), (106, 77), (112, 74),
     (118, 73), (124, 72), (131, 72), (138, 72), (145, 71), (152, 70),
     (158, 66), (162, 61), (158, 56), (153, 59), (147, 60), (142, 53),
     (140, 47), (137, 42), (132, 38), (128, 34), (124, 31), (121, 27),
     (118, 23), (113, 21), (109, 18), (106, 12), (103, 8), (100, 6),
     (98, 4), (100, 0), (103, -4), (107, -7), (111, -8), (114, -11),
     (117, -14), (120, -18), (122, -21), (125, -24), (128, -27),
     (131, -30), (134, -32), (137, -35), (140, -38), (143, -39),
     (146, -41), (149, -42), (147, -40), (144, -38), (141, -36),
     (138, -33), (135, -30), (132, -26), (130, -21), (128, -16),
     (126, -11), (124, -6), (122, -1), (120, 4), (117, 9), (114, 13),
     (111, 17), (108, 21), (105, 25), (102, 29), (99, 33), (96, 37),
     (92, 40), (88, 42), (84, 40), (80, 38), (76, 34), (72, 30),
     (68, 26), (64, 25), (60, 25), (57, 27), (54, 28), (51, 29),
     (48, 30), (45, 31), (42, 34), (39, 37), (36, 39), (33, 41),
     (30, 39)],
    [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (141, 39),
     (141, 41), (143, 43), (145, 44), (143, 42), (141, 39), (139, 36),
     (136, 34), (133, 33)],
    [(114, -22), (114, -30), (115, -33), (118, -35), (122, -34),
     (126, -32), (129, -32), (132, -32), (135, -35), (138, -38),
     (140, -38), (142, -37), (145, -38), (147, -39), (150, -37),
     (152, -32), (153, -27), (152, -24), (150, -22), (146, -19),
     (143, -15), (141, -13), (139, -14), (136, -12), (134, -12),
     (132, -11), (130, -13), (128, -15), (126, -14), (124, -16),
     (122, -17), (120, -20), (117, -21)],
    [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51),
     (-2, 50)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (45, -22), (43, -19)],
    [(167, -45), (170, -42), (173, -40), (175, -38), (177, -38),
     (176, -40), (173, -42), (170, -44), (167, -46)],
    [(120, 18), (122, 16), (124, 13), (126, 10), (124, 8), (122, 10),
     (120, 14)],
    [(131, -1), (135, -2), (138, -4), (141, -6), (144, -7), (147, -8),
     (146, -8), (142, -8), (138, -8), (134, -7), (131, -4)],
    [(80, 6), (81, 8), (80, 10), (79, 8)],
    [(120, 22), (121, 24), (121, 25), (120, 23)],
]

LAT_TOP, LAT_BOT = 80.0, -60.0


def lonlat_to_xy(lon, lat, bx, by, scale):
    return bx + (lon + 180.0) * scale, by + (LAT_TOP - lat) * scale


def draw_dotted_map(d, bx, by, bw, bh):
    """Sea background, dotted land, numbered pins 1-13, dots 14-45."""
    d.rectangle([bx, by, bx + bw, by + bh], fill=MAP_SEA)
    scale = bw / 360.0
    mh = int((LAT_TOP - LAT_BOT) * scale)
    my = by + (bh - mh) // 2
    mask = Image.new("L", (bw, mh), 0)
    md = ImageDraw.Draw(mask)
    for poly in LAND:
        pts = [lonlat_to_xy(lon, lat, 0, 0, scale) for lon, lat in poly]
        md.polygon(pts, fill=255)
    step = 4
    for gy in range(2, mh - 1, step):
        for gx in range(2, bw - 1, step):
            if mask.getpixel((gx, gy)):
                d.ellipse([bx + gx - 1.5, my + gy - 1.5, bx + gx + 1.5,
                           my + gy + 1.5], fill=LAND_DOT)
    for lon, lat, col in DOTS:
        px, py = lonlat_to_xy(lon, lat, bx, my, scale)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=col)
    for n, (lon, lat) in PINS.items():
        ax, ay = lonlat_to_xy(lon, lat, bx, my, scale)
        dx, dy = PIN_OFF.get(n, (0, 0))
        lx, ly = ax + dx, ay + dy
        col = None
        for story in LEADS + MIDS:
            if story["n"] == n:
                col = story["col"]
        if dx or dy:
            d.line([ax, ay, lx, ly], fill=INK, width=1)
        d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], fill=col,
                  outline=WHITE, width=1)
        num = str(n)
        tw = fnt(SANS_B, 9).getlength(num)
        d.text((lx - tw / 2, ly - 6), num, font=fnt(SANS_B, 9), fill=WHITE)


# ---------------------------------------------------------------- layout
def hline(d, x, y, w, weight=2, fill=INK):
    d.rectangle([x, y, x + w, y + weight - 1], fill=fill)


def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    mx = 8
    cw = W - 2 * mx  # 1008

    # top rules + kicker line
    hline(d, mx, 6, cw, 2)
    hline(d, mx, 10, cw, 1)
    d.text((mx, 14), "THE WORLD IN ONE DAY", font=fnt(SANS_B, 15),
           fill=RED)
    right = "45 STORIES  -  7 REGIONS  -  14 FIELDS  -  ALL FROM TUESDAY"
    d.text((W - mx - fnt(SANS_B, 11).getlength(right), 17), right,
           font=fnt(SANS_B, 11), fill=INK)

    # navy masthead
    d.rectangle([mx, 32, W - mx, 98], fill=NAVY)
    title = "Tuesday 17 November 2026"
    tf = fnt(SERIF_B, 52)
    d.text(((W - tf.getlength(title)) / 2, 40), title, font=tf, fill=WHITE)
    d.rectangle([mx, 100, W - mx, 102], fill=GOLD)

    # region count bar (7 equal segments)
    seg = cw // 7
    for i, (name, count, col) in enumerate(REGIONS):
        x0 = mx + i * seg
        x1 = mx + (i + 1) * seg if i < 6 else W - mx
        d.rectangle([x0, 104, x1, 120], fill=col)
        label = "%s %d" % (name, count)
        lf = fnt(SANS_B, 11)
        d.text((x0 + (x1 - x0 - lf.getlength(label)) / 2, 107), label,
               font=lf, fill=WHITE)

    # BY THE NUMBERS strip
    y0, y1 = 124, 162
    cell = cw // 6
    for i, (big, label) in enumerate(NUMBERS):
        x0 = mx + i * cell
        if i:
            d.line([x0, y0 + 4, x0, y1 - 4], fill=(190, 180, 160), width=1)
        bf = fnt(SERIF_B, 20)
        d.text((x0 + 6, y0 + 2), big, font=bf, fill=RED)
        for j, ln in enumerate(wrap_text(label, fnt(SANS, 9), cell - 12)):
            d.text((x0 + 6, y0 + 24 + j * 11), ln, font=fnt(SANS, 9),
                   fill=INK)
    hline(d, mx, y1 + 2, cw, 1)

    # 3 leads
    ly, lh = 168, 234
    lw = (cw - 16) // 3
    for i, st in enumerate(LEADS):
        x0 = mx + i * (lw + 8)
        ILLS[st["ill"]](d, x0, ly, lw, 112)
        ty = ly + 118
        d.text((x0, ty), "%d  -  %s" % (st["n"], st["kick"]),
               font=fnt(SANS_B, 11), fill=st["col"])
        fo, lines = fit_lines(st["head"], SERIF_B, 21, lw, 2)
        draw_lines(d, x0, ty + 15, lines, fo, INK, 25)
        sf = fnt(SANS, 11)
        slines = wrap_text(st["summ"], sf, lw)[:3]
        draw_lines(d, x0, ty + 15 + 25 * len(lines) + 3, slines, sf,
                   (60, 60, 60), 14)

    # 2 rows of 5 mids
    mw = (cw - 32) // 5
    for row in range(2):
        my = 406 + row * 140
        for col_i in range(5):
            st = MIDS[row * 5 + col_i]
            x0 = mx + col_i * (mw + 8)
            ILLS[st["ill"]](d, x0, my, mw, 62)
            ty = my + 66
            d.text((x0, ty), "%d  -  %s" % (st["n"], st["kick"]),
                   font=fnt(SANS_B, 9), fill=st["col"])
            fo, lines = fit_lines(st["head"], SERIF_B, 14, mw, 2)
            draw_lines(d, x0, ty + 12, lines, fo, INK, 17)
            sf = fnt(SANS, 10)
            slines = wrap_text(st["summ"], sf, mw)[:2]
            draw_lines(d, x0, ty + 12 + 17 * len(lines) + 2, slines, sf,
                       (60, 60, 60), 12)

    # bottom divider
    hline(d, mx, 690, cw, 2)

    # map panel (left)
    px0, pw = mx, 330
    d.text((px0, 696), "WHERE IT HAPPENED", font=fnt(SANS_B, 12), fill=RED)
    draw_dotted_map(d, px0, 716, pw, 124)
    ly = 848
    d.text((px0, ly), "Pins 1-13: lead stories  -  dots: stories 14-45",
           font=fnt(SANS, 9), fill=INK)
    lx = px0
    for name, _, col in [("Americas", 0, RED), ("Europe", 0, BLUE),
                         ("Middle East", 0, ORANGE), ("Asia", 0, PURPLE),
                         ("Africa", 0, GREEN), ("Oceania", 0, TEAL)]:
        d.ellipse([lx, ly + 16, lx + 7, ly + 23], fill=col)
        lx += 10
        lf = fnt(SANS, 9)
        d.text((lx, ly + 14), name, font=lf, fill=INK)
        lx += int(lf.getlength(name)) + 8
    # DATE CHECK box
    d.rectangle([px0, 882, px0 + pw, 992], outline=RED, width=1)
    d.text((px0 + 6, 886), "DATE CHECK", font=fnt(SANS_B, 11), fill=RED)
    dc = ("Left out on purpose, because they happened before - or "
          "after - this date: Anthropic's IPO prices Wednesday; "
          "Voyager 1 crosses one light-day Wednesday; a Vulcan rocket "
          "lost 40 Amazon satellites on 15 Nov.")
    draw_lines(d, px0 + 6, 902, wrap_text(dc, fnt(SANS, 10), pw - 12),
               fnt(SANS, 10), INK, 13)

    # ALSO list (right)
    ax0 = px0 + pw + 8
    aw = W - mx - ax0
    d.text((ax0, 696), "ALSO ON TUESDAY 17 NOVEMBER",
           font=fnt(SANS_B, 12), fill=RED)
    colw = (aw - 10) // 2
    bf = fnt(SANS_B, 11)
    tf = fnt(SANS, 11)
    for idx, (n, col, kick, text) in enumerate(ALSO):
        col_i = idx // 16
        row_i = idx % 16
        x0 = ax0 + col_i * (colw + 10)
        y = 716 + row_i * 17
        chip = "%d" % n
        cw2 = max(16, int(bf.getlength(chip)) + 6)
        d.rectangle([x0, y, x0 + cw2, y + 13], fill=col)
        d.text((x0 + 3, y + 1), chip, font=fnt(SANS_B, 9), fill=WHITE)
        tx = x0 + cw2 + 4
        d.text((tx, y), kick, font=bf, fill=INK)
        rest = text
        d.text((tx + bf.getlength(kick) + 3, y), rest, font=tf, fill=INK)

    # footer
    hline(d, mx, 998, cw, 1)
    d.text((mx, 1002), "Every story here happened or was first reported "
           "on Tuesday 17 November 2026. Disputed claims name their source.",
           font=fnt(SANS, 10), fill=INK)
    d.text((mx, 1014), "Sources: Reuters, AP, AFP, BBC, Al Jazeera, WHO, "
           "UN News. Original drawings - no photos copied.",
           font=fnt(SANS, 9), fill=(90, 90, 90))

    img.save(OUT_PATH, "PNG")
    data = open(OUT_PATH, "rb").read()
    print("entry.png %dx%d %d bytes" % (W, H, len(data)))
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    build()
