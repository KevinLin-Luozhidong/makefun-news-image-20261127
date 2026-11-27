#!/usr/bin/env python3
"""make.fun news-image-20261127: one image summing up Friday 27 Nov 2026.

Written fresh in this session for the 27 November bounty. Pure Python
standard library only: the grader installs nothing and the program runs
with no network, 1 CPU / 512 MB / 60 s. All news is embedded below, so
nothing is fetched at run time. The program paints a 1024x1024
newspaper front page and writes a deterministic PNG to
/output/entry.png (or $MAKEFUN_OUTPUT_DIR).

Layout: masthead with the date, six lead stories in a 3-by-2 grid, each
with its own code-drawn picture, then an IN BRIEF band with a simple
world map and six one-line stories -- twelve stories in all. The day's
scope follows the rules: events that happened, or were first reported,
on 27 November 2026 in any time zone. Several leads happened on Thu 26
Nov (Kuwait, Jazan, the Zelensky warning, the Argentina vote) or Wed 25
Nov (the birthright ruling) and were first widely reported on Fri 27
Nov; the masthead says so on the face of the image.

Every fact was checked on 27 Nov 2026 in at least two sources (see
README.md). Claims are attributed where they are claims ("Italy and
Kuwait blame Iran; Tehran denies it"). No photos, no portraits, no
faces: every picture is drawn from rectangles, circles and lines.

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
LEADS = [
    dict(code="01", kicker="GULF", city="KUWAIT", colour=SCARLET,
         head="Two Italians killed in Kuwait drone strike",
         deck="Italy, Kuwait blame Iran; Tehran denies it.",
         credit="CNN - WSJ - DAWN - REUTERS", art="drone"),
    dict(code="02", kicker="POLITICS", city="WELLINGTON", colour=BLUE,
         head="NZ coalition loses its majority",
         deck="65 of 130 seats; Luxon needs Opportunity.",
         credit="REUTERS - RNZ - NIKKEI", art="ballot"),
    dict(code="03", kicker="TECH", city="NEW YORK", colour=PLUM,
         head="Trump backs Huang return to Nvidia",
         deck="Trump: he is no threat; return is a great thing.",
         credit="STRAITS TIMES - ET - NDTV", art="chip"),
    dict(code="04", kicker="WEATHER", city="USA", colour=TEAL,
         head="Storm wrecks US Thanksgiving",
         deck="400 flights cut; 900,000 lose power; parade put off.",
         credit="WSJ - NDTV - REUTERS", art="storm"),
    dict(code="05", kicker="ENERGY", city="JAZAN", colour=ORANGE,
         head="Houthi hit kills worker at Saudi refinery",
         deck="Jazan refinery halts work; Brent crude near $97.",
         credit="REUTERS - WSJ", art="refinery"),
    dict(code="06", kicker="CONFLICT", city="KYIV", colour=GOLD_DK,
         head="Zelensky warns of new mass strike",
         deck="Russia readying a strike, he says; heed the alarms.",
         credit="REUTERS - KYIV POST - NDTV", art="alarm"),
]

# One line each, at most 50 characters, so each fits the brief band.
BRIEFS = [
    "UK: Net migration falls to 77,000.",
    "ARGENTINA: Bank barred from printing money.",
    "USA: Second judge blocks birthright order.",
    "INDIA: Delhi police free 164 in cyber raid.",
    "JAPAN: Tokyo prices rise 2.9% in November.",
    "WORLD: UN urges Sri Lanka wartime apology.",
]
BRIEF_CREDIT = "ONS - AP - REUTERS - NDTV - AL JAZEERA - UN"

# ---- 5x7 letterforms -------------------------------------------------
# Each letter is seven rows; each row is one integer whose five bits
# are the pixels, leftmost pixel in the highest bit (16). Text is set
# in capitals only, so only capitals, digits and punctuation are kept.
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
        for ch in text.upper():
            rows = GLYPHS.get(ch, UNKNOWN_GLYPH)
            for r, bits in enumerate(rows):
                for c in range(5):
                    if bits & (16 >> c):
                        self.box(cx + c * scale, y + r * scale,
                                 scale, scale, colour)
            cx += 6 * scale
        return cx

    def centred(self, y, text, scale, colour):
        x = (self.w - glyph_width(text.upper(), scale)) // 2
        self.glyphs(x, y, text, scale, colour)


# ---- pictures --------------------------------------------------------
# One drawn picture per lead story, filling a (w x h) box. Shapes only:
# no photos, no faces, no flags, no portraits.
def picture(pg, kind, x, y, w, h):
    if kind == "drone":
        pg.box(x, y, w, int(h * 0.55), SKY)
        pg.box(x, y + int(h * 0.55), w, h - int(h * 0.55), (150, 148, 138))
        # ground station: low block with a lit window row
        pg.box(x + 18, y + h - 34, 96, 34, DARK)
        for wx in range(x + 28, x + 100, 16):
            pg.box(wx, y + h - 26, 7, 7, FLAME_Y)
        # drone: centre body, four arms, spinning rotors
        dx, dy = x + w // 2, y + 34
        pg.box(dx - 26, dy - 5, 52, 10, DARK)
        pg.box(dx - 8, dy - 8, 16, 16, (60, 66, 74))
        for ax in (dx - 34, dx + 34):
            pg.box(ax - 3, dy - 3, 6, 6, DARK)
            pg.box(ax - 16, dy - 6, 32, 3, (90, 96, 104))
        # blast starburst under the drone, smoke above it
        for ddx, ddy in ((-1, -1), (0, -1), (1, -1), (-1, 0), (1, 0),
                         (-1, 1), (0, 1), (1, 1)):
            pg.diag(dx, dy + 22, dx + ddx * 24, dy + 22 + ddy * 18, FLAME, 3)
        pg.disc(dx, dy + 22, 6, FLAME_Y)
        for cx, cy, r in ((dx - 30, y + 12, 8), (dx - 12, y + 6, 10),
                          (dx + 8, y + 10, 7)):
            pg.disc(cx, cy, r, SMOKE)
    elif kind == "ballot":
        pg.box(x, y, w, h, (222, 232, 238))
        # parliament seats: rows of dots, one bloc in the lead colour
        for row in range(3):
            for col in range(9):
                bx = x + 26 + col * 30
                by = y + 14 + row * 18
                pg.disc(bx, by, 6, BLUE if col < 5 else (150, 158, 166))
        # ballot box with a big tick
        pg.box(x + w - 118, y + h - 44, 92, 44, MAST)
        pg.box(x + w - 104, y + h - 50, 64, 6, INK)
        pg.diag(x + w - 104, y + h - 26, x + w - 84, y + h - 10, GOLD, 5)
        pg.diag(x + w - 84, y + h - 10, x + w - 44, y + h - 40, GOLD, 5)
    elif kind == "chip":
        pg.box(x, y, w, h, NIGHT)
        for sx, sy in ((16, 12), (60, 26), (120, 10), (200, 20), (260, 12),
                       (300, 30), (90, 40), (180, 44)):
            pg.disc(x + sx, y + sy, 2, WHITE)
        # chip: square die, inner core, pins on all four sides
        cx, cy = x + 110, y + 52
        pg.box(cx - 34, cy - 34, 68, 68, (46, 58, 74))
        pg.frame(cx - 34, cy - 34, 68, 68, GOLD, 2)
        pg.box(cx - 16, cy - 16, 32, 32, GOLD)
        for i in range(5):
            off = -28 + i * 14
            pg.box(cx + off, cy - 44, 4, 10, (150, 156, 164))
            pg.box(cx + off, cy + 34, 4, 10, (150, 156, 164))
            pg.box(cx - 44, cy + off, 10, 4, (150, 156, 164))
            pg.box(cx + 34, cy + off, 10, 4, (150, 156, 164))
        # rising arrow to the right of the chip
        pg.diag(x + 210, y + 84, x + 262, y + 30, GREEN, 4)
        pg.tri([(x + 262, y + 30), (x + 244, y + 30), (x + 262, y + 48)],
               GREEN)
        pg.glyphs(x + 196, y + 8, "2ND TERM", 2, WHITE)
    elif kind == "storm":
        pg.box(x, y, w, h, (96, 104, 116))
        # dark cloud bank across the top, lightning fork
        for cx, cy, r in ((60, 18, 22), (110, 10, 26), (170, 18, 22),
                          (240, 12, 24), (290, 20, 18)):
            pg.disc(x + cx, y + cy, r, (52, 58, 68))
        pg.diag(x + 150, y + 30, x + 132, y + 58, FLAME_Y, 4)
        pg.diag(x + 132, y + 58, x + 146, y + 58, FLAME_Y, 4)
        pg.diag(x + 146, y + 58, x + 130, y + 84, FLAME_Y, 4)
        # rain slashes
        for rx in range(x + 12, x + w - 8, 26):
            pg.diag(rx, y + 52, rx - 8, y + 78, (200, 210, 220), 2)
        # grounded plane silhouette, low, with a red tail
        pg.box(x + 30, y + h - 26, 150, 10, DARK)
        pg.tri([(x + 180, y + h - 26), (x + 210, y + h - 26),
                (x + 180, y + h - 16)], DARK)
        pg.box(x + 60, y + h - 38, 8, 12, SCARLET)
    elif kind == "refinery":
        pg.box(x, y, w, int(h * 0.6), (236, 164, 74))
        pg.box(x, y + int(h * 0.6), w, h - int(h * 0.6), (238, 198, 118))
        # two distillation towers and a pipe run
        pg.box(x + 40, y + 18, 26, h - 18, DARK)
        pg.box(x + 86, y + 34, 22, h - 34, (52, 58, 66))
        pg.box(x + 40, y + h - 16, w - 80, 8, DARK)
        for wy in range(y + 30, y + h - 20, 16):
            pg.box(x + 48, wy, 5, 5, FLAME_Y)
        # flame and smoke at the far tower
        pg.tri([(x + 150, y + 52), (x + 164, y + 16), (x + 178, y + 52)],
               FLAME)
        pg.tri([(x + 158, y + 52), (x + 164, y + 30), (x + 170, y + 52)],
               FLAME_Y)
        for cx, cy, r in ((150, 22, 9), (170, 12, 11), (188, 22, 8)):
            pg.disc(x + cx, y + cy, r, SMOKE)
        pg.glyphs(x + 210, y + 14, "$97", 4, SCARLET)
    elif kind == "alarm":
        pg.box(x, y, w, h, NIGHT)
        for sx, sy in ((18, 14), (70, 28), (140, 12), (210, 24), (270, 14),
                       (310, 30), (110, 40)):
            pg.disc(x + sx, y + sy, 2, WHITE)
        # alarm bell centre-left, sound arcs to its right
        bx, by = x + 90, y + 58
        pg.tri([(bx - 30, by + 22), (bx, by - 26), (bx + 30, by + 22)],
               GOLD)
        pg.box(bx - 36, by + 22, 72, 8, GOLD)
        pg.disc(bx, by + 36, 6, FLAME_Y)
        for r in (30, 42, 54):
            pg.hoop(bx + 44, by, r, FLAME, 2)
        # city silhouette below
        for bx0, bw, bh in ((180, 42, 44), (230, 34, 60), (272, 46, 38)):
            pg.box(x + bx0, y + h - bh, bw, bh, (8, 12, 22))
            pg.box(x + bx0 + 8, y + h - bh + 10, 4, 4, FLAME_Y)
            pg.box(x + bx0 + 20, y + h - bh + 20, 4, 4, FLAME_Y)


def world_map(pg, x, y, w, h):
    """A plain world map: grey-blue sea, green land blobs, red dots
    at the day's story places (Kuwait, Jazan, Kyiv, UK, NZ, US,
    Argentina, India, Japan, Sri Lanka)."""
    pg.box(x, y, w, h, (230, 236, 242))
    pg.frame(x, y, w, h, RULE, 1)
    blobs = [
        (30, 44, 24), (54, 62, 17), (62, 100, 15),
        (146, 38, 11), (154, 74, 19),
        (210, 44, 28), (234, 80, 11),
        (260, 108, 11),
    ]
    for cx, cy, r in blobs:
        pg.disc(x + cx, y + cy, r, LAND)
        pg.disc(x + cx + 8, y + cy + 6, max(2, r - 6), LAND)
    dots = [
        (204, 56), (198, 64), (178, 50), (144, 70),
        (274, 100), (34, 52), (54, 92), (236, 48),
        (262, 58), (240, 74),
    ]
    for dx, dy in dots:
        pg.disc(x + dx, y + dy, 4, SCARLET)
        pg.hoop(x + dx, y + dy, 6, WHITE, 1)


# ---- page ------------------------------------------------------------
def build_page():
    pg = Page(PAGE_W, PAGE_H, PAPER)

    # masthead: nameplate, date in red, scope line, red + ink rules
    pg.centred(14, "THE WORLD IN ONE DAY", 5, MAST)
    pg.centred(54, "FRIDAY 27 NOVEMBER 2026", 4, SCARLET)
    pg.centred(90, "TWELVE STORIES THAT DEFINED THE DAY - INCLUDING FIRST REPORTED FRI 27 NOV",
               2, GREY)
    pg.box(0, 112, PAGE_W, 4, SCARLET)
    pg.box(0, 118, PAGE_W, 2, INK)

    # six lead cards: 3 columns by 2 rows
    margin, gap = 18, 12
    cw = (PAGE_W - 2 * margin - 2 * gap) // 3
    ch = 300
    top = 126
    for i, story in enumerate(LEADS):
        col, row = i % 3, i // 3
        x = margin + col * (cw + gap)
        y = top + row * (ch + gap)
        colour = story["colour"]
        pg.box(x, y, cw, ch, CARD)
        pg.frame(x, y, cw, ch, RULE, 1)
        pg.box(x, y, cw, 6, colour)
        picture(pg, story["art"], x + 8, y + 12, cw - 16, 100)
        # number disc + kicker - city
        pg.disc(x + 24, y + 132, 13, colour)
        num = story["code"]
        pg.glyphs(x + 24 - glyph_width(num, 2) // 2, y + 125,
                  num, 2, WHITE)
        pg.glyphs(x + 44, y + 125,
                  story["kicker"] + " - " + story["city"], 2, colour)
        # headline, up to 3 lines at scale 3; the deck starts below
        # however many headline lines there are, so they never meet
        ty = y + 154
        for line in split_lines(story["head"], 17)[:3]:
            pg.glyphs(x + 14, ty, line, 3, INK)
            ty += 24
        # deck, up to 2 lines at scale 2
        dy = ty + 6
        for line in split_lines(story["deck"], 27)[:2]:
            pg.glyphs(x + 14, dy, line, 2, BODY)
            dy += 19
        # credit line at the foot of the card
        pg.box(x + 14, y + ch - 26, cw - 28, 1, RULE)
        pg.glyphs(x + 14, y + ch - 18, story["credit"], 2, GREY)

    # IN BRIEF band: world map on the left, six one-liners on the right
    band_y = top + 2 * ch + gap + 12
    pg.box(margin, band_y, 16, 16, SCARLET)
    pg.glyphs(margin + 24, band_y, "IN BRIEF", 3, SCARLET)
    pg.box(margin + 150, band_y + 8, PAGE_W - 2 * margin - 150, 1, RULE)
    world_map(pg, margin, band_y + 26, 320, 168)
    bx = margin + 336
    for j, item in enumerate(BRIEFS):
        iy = band_y + 30 + j * 27
        pg.disc(bx + 6, iy + 6, 5, SCARLET)
        pg.glyphs(bx + 18, iy, item, 2, INK)

    # footer: sources, then the drawn-graphics note
    fy = band_y + 26 + 168 + 10
    pg.box(0, fy, PAGE_W, 2, INK)
    pg.glyphs(20, fy + 10,
              "SOURCES: REUTERS, AP, CNN, WSJ, DAWN, NIKKEI, STRAITS TIMES, ET,",
              2, GREY)
    pg.glyphs(20, fy + 30,
              "RNZ, KYIV POST, NDTV, AL JAZEERA, ONS, UN.",
              2, GREY)
    pg.glyphs(20, fy + 50,
              "ALL GRAPHICS DRAWN IN CODE; NO PHOTOS, NO PORTRAITS.",
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
