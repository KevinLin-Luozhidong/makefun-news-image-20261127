#!/usr/bin/env python3
"""make.fun news-image-20261127: one image summing up Friday 27 Nov 2026.

Broadsheet rebuild. Pure Python standard library only: the grader
installs nothing and the program runs with no network, 1 CPU / 512 MB /
60 s. All news is embedded below, so nothing is fetched at run time.
The program paints a 1024x1024 broadsheet front page and writes a
deterministic PNG to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Layout: masthead with the date and a coverage counter, twelve lead
stories (two big, ten compact) each with its own code-drawn picture,
a numbered ALSO ON FRIDAY list of 24 more stories, a world map with
numbered pins, a THE DAY IN UTC timeline, a DATE CHECK box naming
what was left out and why, a tag legend and wire credits in the
footer -- 36 dated stories in all.

Scope follows the rules: events that happened, or were first
reported, on 27 November 2026 in any time zone. Several items
happened on Thu 26 Nov (Kuwait, Jazan, the Zelensky warning, the
Argentina vote, the ECB choice, the Mackenzie verdict, the Mexico
SpaceX request, the UK train verdict) and were first widely
reported on Fri 27 Nov; the DATE CHECK box says so on the face of
the image. Items that were already reported before 27 Nov -- the
SpaceX Starmind clearance (25 Nov), the UK migration release
(26 Nov), the birthright ruling (25 Nov), the Gaza toll of ten
(26 Nov), the Canary record arrivals (24 Nov), the Cairo tanker
crash (25 Nov) -- are left out, and the box names them.

Every fact was checked on 27-28 Nov 2026 in at least one named
wire or outlet (see README.md). Claims are tagged CLAIM and
attributed where they are claims ("Italy and Kuwait blame Iran;
Tehran denies it"). No photos, no portraits, no faces: every
picture is drawn from rectangles, circles and lines.

Run locally:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
Then check out/entry.png: 1024x1024, <= 1 MiB, identical on every run.
"""
import binascii
import math
import os
import struct
import sys
import zlib

PAGE_W, PAGE_H = 1024, 1024

# ---- palette ---------------------------------------------------------
INK = (18, 26, 34)
PAPER = (248, 246, 241)
CARD = (255, 255, 255)
RULE = (212, 208, 198)
GREY = (98, 106, 116)
BODY = (54, 62, 72)
MAST = (13, 38, 64)
SCARLET = (176, 42, 34)
GOLD = (230, 182, 72)
GOLD_DK = (172, 128, 30)
TEAL = (13, 114, 108)
BLUE = (28, 88, 158)
ORANGE = (196, 106, 16)
GREEN = (36, 116, 66)
PLUM = (86, 66, 136)
WHITE = (255, 255, 255)
SKY = (172, 194, 212)
SEA = (16, 66, 108)
NIGHT = (11, 17, 31)
LAND = (166, 184, 158)
FLAME = (228, 118, 18)
FLAME_Y = (242, 194, 64)
SMOKE = (118, 120, 124)
DARK = (19, 27, 35)

# ---- the news --------------------------------------------------------
# headline + deck are kept short on purpose: a headline wraps to at
# most 3 lines at scale 3 (17 chars a line) and a deck to at most 2
# lines at scale 2 (27 chars a line), so headline and deck can never
# run into each other or into the credit line at the foot of a card.
# Tag meaning (the legend in the footer spells it out):
#   OFFICIAL   = on the record.  CONFIRMED = two or more wires.
#   REPORTED   = one named outlet.  CLAIM   = one side's account.
# Big cards (01, 07) take a three-line headline at scale 3 and a
# two-line deck at scale 2. Compact cards take a two-line headline
# and a one-line deck, both at scale 2. Decks are one line long.
LEADS = [
    dict(code="01", city="KUWAIT", colour=SCARLET, tag="CONFIRMED",
         head="Two Italians killed in Kuwait drone strike",
         deck="Italy and Kuwait blame Iran; Tehran denies it.",
         credit="CNN - WSJ - DAWN - REUTERS", art="drone"),
    dict(code="02", city="WELLINGTON", colour=BLUE, tag="OFFICIAL",
         head="NZ coalition loses its majority",
         deck="65 of 130 seats; one short.",
         credit="RNZ", art="ballot"),
    dict(code="03", city="NEW YORK", colour=PLUM, tag="REPORTED",
         head="Trump backs Huang return to Nvidia",
         deck="Trump: he is no threat, he says.",
         credit="ET", art="chip"),
    dict(code="04", city="USA", colour=TEAL, tag="CONFIRMED",
         head="Storm wrecks US Thanksgiving",
         deck="400 flights cut; 900,000 dark.",
         credit="WSJ", art="storm"),
    dict(code="05", city="JAZAN", colour=ORANGE, tag="REPORTED",
         head="Houthi hit kills worker at Saudi refinery",
         deck="Some halted; Brent near $97.",
         credit="REUTERS", art="refinery"),
    dict(code="06", city="KYIV", colour=GOLD_DK, tag="CLAIM",
         head="Zelensky warns of new mass strike",
         deck="Heed the alarms, Zelensky says.",
         credit="REUTERS", art="alarm"),
    dict(code="07", city="BRUSSELS", colour=BLUE, tag="CONFIRMED",
         head="EU summit stalls on budget and Ukraine loan",
         deck="24 of 27 back the EUR45bn loan; no deal till December.",
         credit="EURONEWS - AP", art="summit"),
    dict(code="08", city="GAZA", colour=SCARLET, tag="REPORTED",
         head="Hamas chief's son survives dawn strike",
         deck="No deaths; daughter-in-law hurt.",
         credit="REUTERS", art="gaza"),
    dict(code="09", city="USA", colour=PLUM, tag="REPORTED",
         head="Black Friday shoppers return to the malls",
         deck="Adobe forecast: $12.9bn online.",
         credit="REUTERS", art="blackfriday"),
    dict(code="10", city="MARKET", colour=GREEN, tag="CONFIRMED",
         head="Asia rallies as Wall Street surges",
         deck="Shanghai +3.7%; gold $3,670.",
         credit="BLOOMBERG", art="markets"),
    dict(code="11", city="CHCH", colour=TEAL, tag="CONFIRMED",
         head="NZ reach 246 for 5 on day one",
         deck="Brar debut wicket; Latham 59.",
         credit="REUTERS", art="cricket"),
    dict(code="12", city="NIGER", colour=ORANGE, tag="REPORTED",
         head="Niger camp attack kills 13 guards",
         deck="13 National Guard dead in Sanam.",
         credit="AL JAZEERA", art="africa"),
]

# The numbered ALSO ON FRIDAY list, stories 13 to 36. One line each,
# at most 36 characters after the number, so each fits a half-width
# column at scale 2. All happened, or were first widely reported, on
# Fri 27 Nov 2026 (sources in README.md).
ALSO = [
    "USA: Trump holiday post attacks foes",
    "IRAQ: Trump backs PM's crackdown",
    "CPTPP: 3 nations join accession talks",
    "ECB: De Cos to succeed Lagarde",
    "ICC: Duterte trial opens Monday",
    "SPAIN: Campaign ends; vote on Sunday",
    "GAZA: MSF clinic hit; 2 killed",
    "GUINEA-BISSAU: Vote delayed to 2028",
    "KENYA: Cult leader convicted of terror",
    "MEXICO: Seeks talks on SpaceX airspace",
    "UK: Train rampage man guilty of 14",
    "CANARIES: 8 dead on boat; 100 rescued",
    "EGYPT: Funerals for 31 tanker dead",
    "UN: Hunger to worsen in 16 hotspots",
    "INDIA: Police free 164 in cyber raid",
    "JAPAN: Tokyo core prices rise 2.9%",
    "ARGENTINA: Bank printing money barred",
    "SRI LANKA: UN urges wartime apology",
    "CHINA: Huawei unveils custom HBM chip",
    "CANADA: Top court upholds symbols ban",
    "UN: Chief condemns Kuwait attacks",
    "SUDAN: 383,000 fled Kordofan in a year",
    "IRAQ: Two border crossings shut",
    "OPEC+: Ministers meet Sunday",
]

# The day in UTC, in time order. Each line fits one scale-2 row.
TIMELINE = [
    "00:16 EU summit ends",
    "06:05 Asia rallies",
    "09:25 CPTPP talks open",
    "11:49 Niger attack kills 13",
    "18:00 Wall St: S&P +1.6%",
]

# What was left out of the paper and why: every item below was
# already reported before 27 Nov, so it fails the dating rule even
# though it is real news. Each line fits one scale-2 row.
DATECHECK = [
    "Starmind: FCC Wed 25 Nov",
    "UK migration: ONS Thu 26 Nov",
    "Birthright: ruled Wed 25 Nov",
    "Gaza 10 killed: Thu 26 Nov",
    "Canary record: Tue 24 Nov",
    "Egypt crash: Wed 25 Nov",
]

# Story places for the map pins: (story number, latitude, longitude,
# label nudge dx, label nudge dy). Two pins share a city (New York,
# Gaza, Baghdad, New Zealand), so those get a nudge to keep the
# numbers apart.
PINS = [
    ("01", 29.3, 48.0, 0, 0), ("02", -41.3, 174.8, 0, -6),
    ("03", 40.7, -74.0, 0, 0), ("04", 39.0, -77.0, 0, 8),
    ("05", 16.9, 42.6, 0, 0), ("06", 50.5, 30.5, 0, 0),
    ("07", 50.8, 4.4, 0, 0), ("08", 31.5, 34.5, 0, 0),
    ("09", 40.0, -90.0, 0, -8), ("10", 31.2, 121.5, 0, 0),
    ("11", -43.5, 172.6, 10, 4), ("12", 13.5, 2.1, 0, 0),
    ("13", 38.9, -77.0, 8, -2), ("14", 33.3, 44.4, 0, 0),
    ("15", 21.0, 105.8, 0, 0), ("16", 50.1, 8.7, 0, 0),
    ("17", 52.1, 4.3, 0, -8), ("18", 40.4, -3.7, 0, 0),
    ("19", 31.5, 34.5, -14, 8), ("20", 11.9, -15.6, 0, 0),
    ("21", -4.0, 39.7, 0, 0), ("22", 19.4, -99.1, 0, 0),
    ("23", 51.5, -0.1, 0, 0), ("24", 28.3, -16.6, 0, 0),
    ("25", 30.0, 31.2, 0, 0), ("26", 41.9, 12.5, 0, 0),
    ("27", 28.6, 77.2, 0, 0), ("28", 35.7, 139.7, 0, 0),
    ("29", -34.6, -58.4, 0, 0), ("30", 6.9, 79.9, 0, 0),
    ("31", 22.5, 114.1, 0, 0), ("32", 45.4, -75.7, 0, 0),
    ("33", 40.7, -74.0, -14, 8), ("34", 12.0, 29.5, 0, 0),
    ("35", 33.3, 44.4, -14, -8), ("36", 48.2, 16.4, 0, 0),
]

# ---- 5x7 letterforms -------------------------------------------------
# Each letter is seven rows; each row is one integer whose five bits
# are the pixels, leftmost pixel in the highest bit (16). Headlines
# are set in sentence case, so lowercase letters are kept too; the
# masthead, tags and counters are written as capitals in the data.
GLYPHS = {
    "A": (14, 17, 17, 31, 17, 17, 17),
    "B": (30, 17, 17, 30, 17, 17, 30),
    "C": (14, 17, 16, 16, 16, 17, 14),
    "D": (28, 18, 17, 17, 17, 18, 28),
    "E": (31, 16, 16, 30, 16, 16, 31),
    "F": (31, 16, 16, 30, 16, 16, 16),
    "G": (14, 17, 16, 23, 17, 17, 15),
    "H": (17, 17, 17, 31, 17, 17, 17),
    "I": (14, 4, 4, 4, 4, 4, 14),
    "J": (7, 2, 2, 2, 2, 18, 12),
    "K": (17, 18, 20, 24, 20, 18, 17),
    "L": (16, 16, 16, 16, 16, 16, 31),
    "M": (17, 27, 21, 21, 17, 17, 17),
    "N": (17, 25, 21, 19, 17, 17, 17),
    "O": (14, 17, 17, 17, 17, 17, 14),
    "P": (30, 17, 17, 30, 16, 16, 16),
    "Q": (14, 17, 17, 17, 21, 18, 13),
    "R": (30, 17, 17, 30, 20, 18, 17),
    "S": (15, 16, 16, 14, 1, 1, 30),
    "T": (31, 4, 4, 4, 4, 4, 4),
    "U": (17, 17, 17, 17, 17, 17, 14),
    "V": (17, 17, 17, 17, 17, 10, 4),
    "W": (17, 17, 17, 21, 21, 27, 17),
    "X": (17, 17, 10, 4, 10, 17, 17),
    "Y": (17, 17, 10, 4, 4, 4, 4),
    "Z": (31, 1, 2, 4, 8, 16, 31),
    "a": (0, 14, 1, 15, 17, 17, 15),
    "b": (16, 16, 30, 17, 17, 17, 17),
    "c": (0, 0, 14, 17, 16, 17, 14),
    "d": (1, 1, 13, 19, 17, 17, 15),
    "e": (0, 0, 14, 17, 30, 16, 14),
    "f": (6, 8, 8, 30, 8, 8, 8),
    "g": (0, 15, 17, 17, 15, 1, 14),
    "h": (16, 16, 22, 25, 17, 17, 17),
    "i": (4, 0, 12, 4, 4, 4, 14),
    "j": (2, 0, 6, 2, 2, 18, 12),
    "k": (16, 16, 18, 20, 24, 20, 18),
    "l": (12, 4, 4, 4, 4, 4, 14),
    "m": (0, 0, 26, 21, 21, 21, 21),
    "n": (0, 0, 22, 25, 17, 17, 17),
    "o": (0, 0, 14, 17, 17, 17, 14),
    "p": (0, 0, 30, 17, 17, 30, 16),
    "q": (0, 0, 15, 17, 17, 15, 1),
    "r": (0, 0, 22, 25, 16, 16, 16),
    "s": (0, 0, 15, 16, 14, 1, 30),
    "t": (8, 8, 30, 8, 8, 9, 6),
    "u": (0, 0, 17, 17, 17, 19, 13),
    "v": (0, 0, 17, 17, 17, 10, 4),
    "w": (0, 0, 17, 21, 21, 21, 10),
    "x": (0, 0, 17, 10, 4, 10, 17),
    "y": (0, 0, 17, 17, 15, 1, 14),
    "z": (0, 0, 31, 2, 4, 8, 31),
    "0": (14, 17, 19, 21, 25, 17, 14),
    "1": (4, 12, 4, 4, 4, 4, 14),
    "2": (14, 17, 1, 6, 8, 16, 31),
    "3": (31, 2, 4, 2, 1, 17, 14),
    "4": (2, 6, 10, 18, 31, 2, 2),
    "5": (31, 16, 30, 1, 1, 17, 14),
    "6": (6, 8, 16, 30, 17, 17, 14),
    "7": (31, 1, 2, 4, 8, 8, 8),
    "8": (14, 17, 17, 14, 17, 17, 14),
    "9": (14, 17, 17, 15, 1, 2, 12),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 12, 12),
    ",": (0, 0, 0, 0, 12, 4, 8),
    ":": (0, 12, 12, 0, 12, 12, 0),
    ";": (0, 12, 12, 0, 12, 4, 8),
    "'": (4, 4, 8, 0, 0, 0, 0),
    "-": (0, 0, 0, 14, 0, 0, 0),
    "(": (2, 4, 8, 8, 8, 4, 2),
    ")": (8, 4, 2, 2, 2, 4, 8),
    "/": (1, 2, 2, 4, 8, 8, 16),
    "%": (25, 26, 2, 4, 8, 11, 19),
    "+": (0, 4, 4, 14, 4, 4, 0),
    "&": (12, 18, 20, 8, 21, 18, 13),
    "$": (4, 15, 20, 14, 5, 30, 4),
    "!": (4, 4, 4, 4, 4, 0, 4),
    "?": (14, 17, 1, 6, 4, 0, 4),
    "=": (0, 0, 14, 0, 14, 0, 0),
    '"': (10, 10, 0, 0, 0, 0, 0),
    "*": (0, 21, 14, 21, 0, 0, 0),
}
UNKNOWN_GLYPH = GLYPHS["?"]


def glyph_width(text, scale):
    """Pixel width of text at a scale (each char is 6 units wide)."""
    if not text:
        return 0
    return len(text) * 6 * scale - scale


def split_lines(text, limit):
    """Greedy word wrap; a single over-long word stays whole on a line."""
    out, current = [], ""
    for word in text.split():
        trial = (current + " " + word).strip()
        if len(trial) <= limit:
            current = trial
        else:
            if current:
                out.append(current)
            current = word
    if current:
        out.append(current)
    return out


# ---- drawing surface -------------------------------------------------
class Page:
    """A flat RGB canvas kept as one bytearray; rows are slices of it."""

    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.buf = bytearray(bytes(bg) * w) * h

    def px(self, x, y, colour):
        if 0 <= x < self.w and 0 <= y < self.h:
            at = (y * self.w + x) * 3
            self.buf[at:at + 3] = bytes(colour)

    def box(self, x, y, w, h, colour):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        run = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            at = (yy * self.w + x0) * 3
            self.buf[at:at + len(run)] = run

    def frame(self, x, y, w, h, colour, thick=1):
        self.box(x, y, w, thick, colour)
        self.box(x, y + h - thick, w, thick, colour)
        self.box(x, y, thick, h, colour)
        self.box(x + w - thick, y, thick, h, colour)

    def diag(self, x0, y0, x1, y1, colour, thick=1):
        dx, dy = abs(x1 - x0), abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx - dy
        while True:
            self.box(x0, y0, thick, thick, colour)
            if x0 == x1 and y0 == y1:
                return
            step = 2 * err
            if step > -dy:
                err -= dy
                x0 += sx
            if step < dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, colour):
        for dy in range(-r, r + 1):
            half = int(math.sqrt(max(0, r * r - dy * dy)))
            self.box(cx - half, cy + dy, 2 * half + 1, 1, colour)

    def hoop(self, cx, cy, r, colour, thick=2):
        for k in range(thick):
            rr = r - k
            for deg in range(360):
                rad = math.radians(deg)
                self.px(cx + int(rr * math.cos(rad)),
                        cy + int(rr * math.sin(rad)), colour)

    def tri(self, pts, colour):
        rows = [p[1] for p in pts]
        for y in range(min(rows), max(rows) + 1):
            hits = []
            for i in range(len(pts)):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % len(pts)]
                if (ay <= y < by) or (by <= y < ay):
                    hits.append(ax + (y - ay) * (bx - ax) / (by - ay))
            hits.sort()
            for j in range(0, len(hits) - 1, 2):
                self.box(int(hits[j]), y,
                         int(hits[j + 1]) - int(hits[j]) + 1, 1, colour)

    def glyphs(self, x, y, text, scale, colour):
        """Paint one scale-by-scale square per set bit of each glyph."""
        cx = x
        for ch in text:
            rows = GLYPHS.get(ch, UNKNOWN_GLYPH)
            for r, bits in enumerate(rows):
                for c in range(5):
                    if bits & (16 >> c):
                        self.box(cx + c * scale, y + r * scale,
                                 scale, scale, colour)
            cx += 6 * scale
        return cx

    def centred(self, y, text, scale, colour):
        x = (self.w - glyph_width(text, scale)) // 2
        self.glyphs(x, y, text, scale, colour)


# ---- pictures --------------------------------------------------------
# One drawn picture per lead story, filling a (w x h) box. Shapes only:
# no photos, no faces, no flags, no portraits.
# ---- pictures --------------------------------------------------------
# One drawn picture per lead story, filling a (w x h) box. Every scene
# is drawn from fractions of the box, so the same code serves the big
# cards (150 wide) and the compact cards (84 wide). Shapes only: no
# photos, no faces, no flags, no portraits.
def picture(pg, kind, x, y, w, h):
    """Draw one scene. R/D/L/T take fractions of the box."""
    def R(fx0, fy0, fx1, fy1, colour):
        pg.box(x + int(fx0 * w), y + int(fy0 * h),
               int((fx1 - fx0) * w), int((fy1 - fy0) * h), colour)

    def D(fcx, fcy, fr, colour):
        pg.disc(x + int(fcx * w), y + int(fcy * h),
                max(1, int(fr * min(w, h))), colour)

    def L(fx0, fy0, fx1, fy1, colour, thick=2):
        pg.diag(x + int(fx0 * w), y + int(fy0 * h),
                x + int(fx1 * w), y + int(fy1 * h), colour, thick)

    def T(pts, colour):
        pg.tri([(x + int(fx * w), y + int(fy * h)) for fx, fy in pts],
               colour)

    ts = 2 if w > 130 else 1  # letter scale for words inside a picture
    if kind == "drone":
        R(0, 0, 1, 0.55, SKY)
        R(0, 0.55, 1, 1, (150, 148, 138))
        # ground station: low block with a lit window row
        R(0.06, 0.72, 0.40, 1, DARK)
        R(0.10, 0.80, 0.15, 0.88, FLAME_Y)
        R(0.18, 0.80, 0.23, 0.88, FLAME_Y)
        R(0.26, 0.80, 0.31, 0.88, FLAME_Y)
        # drone: centre body, two arms, spinning rotors
        R(0.38, 0.28, 0.62, 0.38, DARK)
        R(0.46, 0.26, 0.54, 0.40, (60, 66, 74))
        R(0.28, 0.30, 0.38, 0.36, DARK)
        R(0.62, 0.30, 0.72, 0.36, DARK)
        R(0.22, 0.28, 0.34, 0.31, (90, 96, 104))
        R(0.66, 0.28, 0.78, 0.31, (90, 96, 104))
        D(0.28, 0.32, 0.04, DARK)
        D(0.72, 0.32, 0.04, DARK)
        # blast flame under the drone, smoke above it
        T([(0.44, 0.52), (0.50, 0.38), (0.56, 0.52)], FLAME)
        D(0.5, 0.55, 0.04, FLAME_Y)
        D(0.38, 0.10, 0.07, SMOKE)
        D(0.48, 0.06, 0.08, SMOKE)
        D(0.58, 0.11, 0.06, SMOKE)
    elif kind == "ballot":
        R(0, 0, 1, 1, (222, 232, 238))
        # parliament seats: rows of dots, one bloc in the lead colour
        for row in range(3):
            for col in range(9):
                D(0.10 + col * 0.09, 0.14 + row * 0.16, 0.045,
                  BLUE if col < 5 else (150, 158, 166))
        # ballot box with a big tick
        R(0.60, 0.62, 0.92, 0.96, MAST)
        R(0.64, 0.56, 0.88, 0.62, INK)
        L(0.66, 0.80, 0.72, 0.88, GOLD, 4)
        L(0.72, 0.88, 0.88, 0.66, GOLD, 4)
    elif kind == "chip":
        R(0, 0, 1, 1, NIGHT)
        pg.glyphs(x + int(0.08 * w), y + int(0.06 * h), "2ND TERM", ts,
                  WHITE)
        for sx, sy in ((0.08, 0.30), (0.25, 0.42), (0.55, 0.26),
                       (0.85, 0.36), (0.95, 0.55), (0.35, 0.24)):
            D(sx, sy, 0.015, WHITE)
        # chip: square die, gold frame and core, pins on all sides
        R(0.24, 0.28, 0.56, 0.72, (46, 58, 74))
        R(0.24, 0.28, 0.56, 0.32, GOLD)
        R(0.24, 0.68, 0.56, 0.72, GOLD)
        R(0.24, 0.28, 0.28, 0.72, GOLD)
        R(0.52, 0.28, 0.56, 0.72, GOLD)
        R(0.36, 0.40, 0.44, 0.60, GOLD)
        for i in range(5):
            off = 0.28 + i * 0.06
            R(off, 0.22, off + 0.02, 0.28, (150, 156, 164))
            R(off, 0.72, off + 0.02, 0.78, (150, 156, 164))
            R(0.18, off, 0.24, off + 0.02, (150, 156, 164))
            R(0.56, off, 0.62, off + 0.02, (150, 156, 164))
        # rising arrow to the right of the chip
        L(0.66, 0.78, 0.90, 0.30, GREEN, 4)
        T([(0.90, 0.30), (0.80, 0.30), (0.90, 0.44)], GREEN)
    elif kind == "storm":
        R(0, 0, 1, 1, (96, 104, 116))
        # dark cloud bank across the top, lightning fork
        D(0.18, 0.16, 0.12, (52, 58, 68))
        D(0.38, 0.10, 0.14, (52, 58, 68))
        D(0.58, 0.16, 0.12, (52, 58, 68))
        D(0.80, 0.12, 0.12, (52, 58, 68))
        L(0.48, 0.24, 0.42, 0.45, FLAME_Y, 3)
        L(0.42, 0.45, 0.48, 0.45, FLAME_Y, 3)
        L(0.48, 0.45, 0.42, 0.66, FLAME_Y, 3)
        # rain slashes
        for fx in (0.08, 0.22, 0.36, 0.50, 0.64, 0.78, 0.92):
            L(fx, 0.52, fx - 0.04, 0.68, (200, 210, 220), 2)
        # grounded plane silhouette, low, with a red tail
        R(0.10, 0.78, 0.60, 0.88, DARK)
        T([(0.60, 0.78), (0.72, 0.78), (0.60, 0.88)], DARK)
        R(0.20, 0.68, 0.24, 0.78, SCARLET)
    elif kind == "refinery":
        R(0, 0, 1, 0.6, (236, 164, 74))
        R(0, 0.6, 1, 1, (238, 198, 118))
        pg.glyphs(x + int(0.62 * w), y + int(0.10 * h), "$97", ts,
                  SCARLET)
        # two distillation towers and a pipe run
        R(0.12, 0.18, 0.20, 1, DARK)
        R(0.26, 0.34, 0.32, 1, (52, 58, 66))
        R(0.12, 0.86, 0.80, 0.92, DARK)
        R(0.145, 0.30, 0.165, 0.38, FLAME_Y)
        R(0.145, 0.46, 0.165, 0.54, FLAME_Y)
        R(0.145, 0.62, 0.165, 0.70, FLAME_Y)
        # flame and smoke at the far tower
        T([(0.44, 0.52), (0.50, 0.16), (0.56, 0.52)], FLAME)
        T([(0.47, 0.52), (0.50, 0.30), (0.53, 0.52)], FLAME_Y)
        D(0.44, 0.20, 0.05, SMOKE)
        D(0.52, 0.12, 0.06, SMOKE)
        D(0.60, 0.20, 0.05, SMOKE)
    elif kind == "alarm":
        R(0, 0, 1, 1, NIGHT)
        for sx, sy in ((0.08, 0.12), (0.30, 0.24), (0.55, 0.10),
                       (0.82, 0.20), (0.94, 0.30), (0.45, 0.36)):
            D(sx, sy, 0.015, WHITE)
        # alarm bell centre-left, sound rings to its right
        T([(0.14, 0.62), (0.28, 0.24), (0.42, 0.62)], GOLD)
        R(0.10, 0.62, 0.46, 0.70, GOLD)
        D(0.28, 0.76, 0.05, FLAME_Y)
        for rr in (0.10, 0.16, 0.22):
            pg.hoop(x + int(0.55 * w), y + int(0.44 * h),
                    max(2, int(rr * min(w, h))), FLAME, 2)
        # city silhouette below
        R(0.56, 0.62, 0.68, 1, (8, 12, 22))
        R(0.70, 0.52, 0.80, 1, (8, 12, 22))
        R(0.82, 0.66, 0.94, 1, (8, 12, 22))
        R(0.59, 0.70, 0.61, 0.74, FLAME_Y)
        R(0.73, 0.62, 0.75, 0.66, FLAME_Y)
        R(0.85, 0.74, 0.87, 0.78, FLAME_Y)
    elif kind == "summit":
        R(0, 0, 1, 1, (228, 234, 240))
        pg.glyphs(x + int(0.30 * w), y + int(0.06 * h), "NO DEAL", ts,
                  SCARLET)
        # flags at both ends of the hall
        R(0.06, 0.10, 0.08, 0.52, INK)
        T([(0.08, 0.10), (0.20, 0.16), (0.08, 0.22)], TEAL)
        R(0.92, 0.10, 0.94, 0.52, INK)
        T([(0.92, 0.10), (0.80, 0.16), (0.92, 0.22)], GOLD_DK)
        # chairs behind a long table, papers on the table
        R(0.14, 0.38, 0.22, 0.52, DARK)
        R(0.36, 0.38, 0.44, 0.52, DARK)
        R(0.56, 0.38, 0.64, 0.52, DARK)
        R(0.78, 0.38, 0.86, 0.52, DARK)
        R(0.10, 0.52, 0.90, 0.62, MAST)
        R(0.16, 0.62, 0.20, 0.86, MAST)
        R(0.80, 0.62, 0.84, 0.86, MAST)
        R(0.26, 0.54, 0.34, 0.60, WHITE)
        R(0.48, 0.54, 0.56, 0.60, WHITE)
        R(0.68, 0.54, 0.76, 0.60, WHITE)
        # a red cross over the middle paper: no deal signed
        L(0.46, 0.52, 0.58, 0.62, SCARLET, 3)
        L(0.58, 0.52, 0.46, 0.62, SCARLET, 3)
    elif kind == "gaza":
        R(0, 0, 1, 0.35, (242, 166, 92))
        R(0, 0.35, 1, 0.62, (238, 198, 118))
        R(0, 0.62, 1, 1, (120, 110, 100))
        # low sun over a dawn skyline, one roof broken
        D(0.78, 0.18, 0.09, FLAME_Y)
        R(0.08, 0.42, 0.24, 0.92, DARK)
        R(0.28, 0.52, 0.44, 0.92, (52, 58, 66))
        R(0.48, 0.38, 0.62, 0.92, DARK)
        R(0.66, 0.56, 0.82, 0.92, (52, 58, 66))
        R(0.86, 0.48, 0.96, 0.92, DARK)
        T([(0.48, 0.38), (0.55, 0.30), (0.62, 0.38)], DARK)
        # smoke rising from the broken roof
        D(0.55, 0.28, 0.05, SMOKE)
        D(0.58, 0.18, 0.07, SMOKE)
        D(0.52, 0.10, 0.05, SMOKE)
        # lit windows in the standing blocks
        R(0.11, 0.50, 0.13, 0.55, FLAME_Y)
        R(0.51, 0.46, 0.53, 0.51, FLAME_Y)
        R(0.69, 0.64, 0.71, 0.69, FLAME_Y)
    elif kind == "blackfriday":
        R(0, 0, 1, 1, (232, 228, 218))
        # shopfront: striped awning, lit windows, door
        R(0.06, 0.30, 0.94, 0.92, MAST)
        R(0.06, 0.30, 0.94, 0.40, WHITE)
        for fx in (0.06, 0.22, 0.38, 0.54, 0.70, 0.86):
            R(fx, 0.30, fx + 0.08, 0.40, SCARLET)
        pg.glyphs(x + int(0.36 * w), y + int(0.44 * h), "SALE", ts,
                  SCARLET)
        R(0.12, 0.52, 0.34, 0.72, SKY)
        R(0.66, 0.52, 0.88, 0.72, SKY)
        R(0.42, 0.58, 0.58, 0.92, WHITE)
        R(0.42, 0.58, 0.44, 0.92, GOLD)
        R(0.56, 0.58, 0.58, 0.92, GOLD)
        # shopping bags and a queue at the door
        R(0.13, 0.82, 0.15, 0.86, INK)
        R(0.10, 0.86, 0.22, 0.98, SCARLET)
        R(0.29, 0.84, 0.31, 0.88, INK)
        R(0.26, 0.88, 0.36, 0.98, TEAL)
        D(0.70, 0.94, 0.03, DARK)
        D(0.80, 0.94, 0.03, DARK)
        D(0.90, 0.94, 0.03, DARK)
    elif kind == "markets":
        R(0, 0, 1, 1, (238, 240, 236))
        # grid, then five rising candlesticks with wicks
        R(0.08, 0.25, 0.92, 0.27, RULE)
        R(0.08, 0.50, 0.92, 0.52, RULE)
        R(0.08, 0.75, 0.92, 0.77, RULE)
        for fx, fy in ((0.12, 0.60), (0.24, 0.52), (0.36, 0.42),
                       (0.48, 0.34), (0.60, 0.22)):
            R(fx, fy, fx + 0.08, 0.90, GREEN)
            R(fx + 0.03, fy - 0.06, fx + 0.05, fy, GREEN)
        # rising arrow over the bars, gold coin at the foot
        L(0.10, 0.62, 0.88, 0.14, GREEN, 3)
        T([(0.88, 0.14), (0.76, 0.14), (0.88, 0.30)], GREEN)
        D(0.82, 0.82, 0.09, GOLD)
        D(0.82, 0.82, 0.05, GOLD_DK)
    elif kind == "cricket":
        R(0, 0, 1, 1, (196, 214, 178))
        pg.glyphs(x + int(0.58 * w), y + int(0.08 * h), "246/5", ts,
                  INK)
        # the strip, crease lines, stumps at both ends
        R(0.30, 0.10, 0.52, 0.90, (222, 205, 164))
        R(0.30, 0.22, 0.52, 0.25, WHITE)
        R(0.30, 0.72, 0.52, 0.75, WHITE)
        for fy in (0.10, 0.72):
            R(0.38, fy, 0.40, fy + 0.12, GOLD_DK)
            R(0.42, fy, 0.44, fy + 0.12, GOLD_DK)
            R(0.46, fy, 0.48, fy + 0.12, GOLD_DK)
        # bat, ball, fielders
        L(0.62, 0.30, 0.78, 0.62, INK, 4)
        D(0.82, 0.70, 0.05, SCARLET)
        D(0.12, 0.30, 0.03, WHITE)
        D(0.88, 0.30, 0.03, WHITE)
        D(0.12, 0.70, 0.03, WHITE)
    elif kind == "africa":
        R(0, 0, 1, 0.55, (244, 196, 120))
        R(0, 0.55, 1, 1, (198, 158, 92))
        # sun, flat-top acacia, two huts with smoke
        D(0.82, 0.16, 0.08, FLAME_Y)
        R(0.14, 0.34, 0.18, 0.66, DARK)
        R(0.06, 0.28, 0.30, 0.36, DARK)
        R(0.10, 0.24, 0.26, 0.30, DARK)
        T([(0.42, 0.78), (0.50, 0.58), (0.58, 0.78)], (120, 90, 60))
        T([(0.60, 0.78), (0.68, 0.58), (0.76, 0.78)], (120, 90, 60))
        R(0.48, 0.70, 0.52, 0.78, DARK)
        R(0.66, 0.70, 0.70, 0.78, DARK)
        D(0.50, 0.50, 0.04, SMOKE)
        D(0.52, 0.40, 0.05, SMOKE)
        D(0.49, 0.30, 0.04, SMOKE)
        # red alert triangle over the huts
        T([(0.84, 0.88), (0.92, 0.68), (0.98, 0.88)], SCARLET)
        R(0.905, 0.74, 0.925, 0.82, WHITE)
        D(0.915, 0.85, 0.015, WHITE)


def world_map(pg, x, y, w, h):
    """A plain world map: grey-blue sea, green land blobs, and a red
    pin for every one of the 36 stories, placed by latitude and
    longitude on a flat projection. The twelve leads get a ringed pin
    with their number; the twenty-four briefs get a plain dot, so the
    crowded parts of the map stay readable."""
    pg.box(x, y, w, h, (230, 236, 242))
    pg.frame(x, y, w, h, RULE, 1)
    blobs = [
        (0.16, 0.30, 0.10), (0.24, 0.42, 0.08), (0.30, 0.55, 0.06),
        (0.30, 0.62, 0.07), (0.33, 0.78, 0.05),
        (0.48, 0.28, 0.05), (0.52, 0.34, 0.04),
        (0.52, 0.52, 0.09), (0.55, 0.66, 0.06),
        (0.68, 0.28, 0.11), (0.78, 0.40, 0.08), (0.62, 0.42, 0.06),
        (0.78, 0.58, 0.05),
        (0.86, 0.74, 0.06),
        (0.94, 0.86, 0.02),
    ]
    for fx, fy, fr in blobs:
        pg.disc(x + int(fx * w), y + int(fy * h),
                max(2, int(fr * min(w, h))), LAND)
    for no, lat, lon, dx, dy in PINS:
        px = x + int((lon + 180.0) / 360.0 * w) + dx
        py = y + int((90.0 - lat) / 180.0 * h) + dy
        if int(no) <= 12:
            # a lead story: a ringed pin with its number beside it.
            # Gaza (08) and London (23) sit left of a neighbour's
            # number, so their numbers go on the left; Jazan (05)
            # sits under Kuwait (01), so its number drops two lower.
            pg.disc(px, py, 3, SCARLET)
            pg.hoop(px, py, 5, WHITE, 1)
            lx = px - 17 if no in ("08", "23") else px + 5
            if lx + 12 > x + w:
                lx = px - 17
            ly = py - 4 + (2 if no == "05" else 0)
            if ly < y:
                ly = y
            if ly + 7 > y + h:
                ly = y + h - 7
            pg.glyphs(lx, ly, no, 1, SCARLET)
        else:
            # a brief: a plain dot, no number, so Europe does not
            # turn into a pile of overlapping digits
            pg.disc(px, py, 2, SCARLET)


# ---- page ------------------------------------------------------------
def build_page():
    pg = Page(PAGE_W, PAGE_H, PAPER)

    # masthead: nameplate, date in red, coverage counter, red + ink rules
    pg.centred(10, "THE WORLD IN ONE DAY", 5, MAST)
    pg.centred(50, "FRIDAY 27 NOVEMBER 2026", 4, SCARLET)
    pg.centred(82, "36 STORIES - 7 REGIONS - 12 FIELDS - HAPPENED OR FIRST REPORTED 27 NOV 2026",
               2, GREY)
    pg.box(0, 100, PAGE_W, 4, SCARLET)
    pg.box(0, 106, PAGE_W, 2, INK)

    # twelve lead cards: two big (01, 07) on the first row, then ten
    # compact cards in two columns. Card width 491, gap 10, margin 16.
    margin, gap = 16, 10
    cw = (PAGE_W - 2 * margin - gap) // 2
    big = [LEADS[0], LEADS[6]]
    small = [LEADS[i] for i in range(12) if i not in (0, 6)]
    for col, story in enumerate(big):
        x = margin + col * (cw + gap)
        y = 108
        colour = story["colour"]
        pg.box(x, y, cw, 148, CARD)
        pg.frame(x, y, cw, 148, RULE, 1)
        pg.box(x, y, cw, 6, colour)
        picture(pg, story["art"], x + 8, y + 6, 148, 132)
        tx = x + 164
        pg.glyphs(tx, y + 6,
                  story["code"] + " " + story["city"] + " - "
                  + story["tag"], 2, colour)
        # headline, up to 3 lines at scale 3; deck fixed below it
        ty = y + 22
        for line in split_lines(story["head"], 17)[:3]:
            pg.glyphs(tx, ty, line, 3, INK)
            ty += 23
        dy = y + 94
        for line in split_lines(story["deck"], 26)[:2]:
            pg.glyphs(tx, dy, line, 2, BODY)
            dy += 18
        # credit line at the foot of the card
        pg.box(tx, y + 130, cw - 164 - 8, 1, RULE)
        pg.glyphs(tx, y + 133, story["credit"], 2, GREY)

    # ten compact cards: picture left, tag line, two-line headline,
    # one-line deck. Rows are 65 high with a 6 gap.
    for i, story in enumerate(small):
        col, row = i % 2, i // 2
        x = margin + col * (cw + gap)
        y = 262 + row * 71
        colour = story["colour"]
        pg.box(x, y, cw, 65, CARD)
        pg.frame(x, y, cw, 65, RULE, 1)
        pg.box(x, y, 6, 65, colour)
        picture(pg, story["art"], x + 14, y + 7, 76, 50)
        tx = x + 98
        pg.glyphs(tx, y + 3,
                  story["code"] + " " + story["city"] + " - "
                  + story["tag"] + " - " + story["credit"], 2, colour)
        ty = y + 18
        for line in split_lines(story["head"], 32)[:2]:
            pg.glyphs(tx, ty, line, 2, INK)
            ty += 16
        pg.glyphs(tx, y + 50, story["deck"], 2, BODY)

    # ALSO ON FRIDAY: stories 13 to 36, two columns of twelve
    ay = 617
    pg.box(margin, ay, 16, 16, SCARLET)
    pg.glyphs(margin + 24, ay, "ALSO ON FRIDAY", 3, SCARLET)
    pg.box(300, ay + 8, PAGE_W - 32 - 300, 1, RULE)
    for j, item in enumerate(ALSO):
        col, row = j % 2, j // 2
        x = margin + col * (cw + gap)
        iy = 639 + row * 15
        pg.glyphs(x + 8, iy, "%02d" % (13 + j), 2, SCARLET)
        pg.glyphs(x + 44, iy, item, 2, INK)

    # bottom band: story locator map, UTC timeline, date check
    by = 825
    pg.glyphs(margin, by, "STORY LOCATOR", 2, SCARLET)
    pg.glyphs(332, by, "THE DAY IN UTC", 2, SCARLET)
    pg.glyphs(678, by, "DATE CHECK: LEFT OUT", 2, SCARLET)
    world_map(pg, margin, by + 18, 300, 92)
    pg.glyphs(margin, by + 114, "PIN NUMBERS MATCH THE STORIES ABOVE.", 1,
              GREY)
    ty = by + 18
    for line in TIMELINE:
        pg.glyphs(332, ty, line, 2, INK)
        ty += 17
    dy = by + 18
    for line in DATECHECK:
        pg.glyphs(678, dy, line, 2, INK)
        dy += 17

    # footer: tag legend, then the wire credits
    fy = 950
    pg.box(0, fy, PAGE_W, 2, INK)
    pg.glyphs(20, fy + 8,
              "HOW SURE: OFFICIAL = ON RECORD - CONFIRMED = 2+ WIRES",
              2, GREY)
    pg.glyphs(20, fy + 23,
              "REPORTED = NAMED OUTLET - CLAIM = ONE SIDE'S ACCOUNT",
              2, GREY)
    pg.glyphs(20, fy + 38,
              "SOURCES: REUTERS, AP, CNN, WSJ, DAWN, NIKKEI, STRAITS TIMES, ET, RNZ,",
              2, GREY)
    pg.glyphs(20, fy + 53,
              "KYIV POST, NDTV, AL JAZEERA, EURONEWS, UN, BLOOMBERG, ICC, AFP, SCMP.",
              2, GREY)
    return pg


# ---- PNG writer ------------------------------------------------------
def _chunk(kind, data):
    body = kind + data
    return (struct.pack(">I", len(data)) + body
            + struct.pack(">I", binascii.crc32(body) & 0xFFFFFFFF))


def write_png(pg, path):
    raw = bytearray()
    stride = PAGE_W * 3
    for yy in range(PAGE_H):
        raw.append(0)  # filter 0: no filtering on this scanline
        raw += pg.buf[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", PAGE_W, PAGE_H, 8, 2, 0, 0, 0)
    png = (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
           + _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
           + _chunk(b"IEND", b""))
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    size = write_png(build_page(), path)
    sys.stderr.write("wrote %s (%d bytes)\n" % (path, size))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
