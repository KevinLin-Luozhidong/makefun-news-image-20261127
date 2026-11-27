[![make.fun · news-image-20261127](https://make.fun/badge/news-image-20261127.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![rank](https://make.fun/badge/news-image-20261127/KevinLin-Luozhidong/makefun-news-image-20261127/rank.svg)](https://make.fun/bounty/news-image-20261127/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)
[![reward](https://make.fun/badge/news-image-20261127/KevinLin-Luozhidong/makefun-news-image-20261127/reward.svg)](https://make.fun/bounty/news-image-20261127?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261127)

# make.fun — Sum up 27 November's world news in one image

Bounty: https://make.fun/bounty/news-image-20261127
Prize: $100 shared by the top 50 entries ($20 / $12 / $6 / $2 × 7 / $1.20 × 40).
Deadline: **2026-11-29 00:00 UTC** (Sunday 29 Nov). At most 10
submissions a day, 20 in all; the last submission before the deadline is
the final entry.
Account: Mini Poles / @mini-poles, polesmini1@gmail.com.

## Entry

`main.py` — Python, **standard library only** (the grader installs
nothing, runs with no network, 1 CPU / 512 MB / 60 s). It embeds the
researched news in the code itself and draws a 1024×1024 newspaper
front page with its own 5×7 bitmap font (glyphs stored as integer
bitmasks) and a hand-written PNG encoder (`zlib` + `struct` +
`binascii` only). No Pillow, no network, no API key, no files outside
the repository, no photos, no portraits.

## Design

A newspaper front page, following the proven 25 November entry
(dev 0.971449): six lead stories with large drawn pictures and big
headlines in a 3×2 grid, then a bottom band with a world map plus an
IN BRIEF list — twelve stories in all, so the day's breadth is visible
at a glance. Every lead story carries its own drawn picture; headlines
are large enough to read at ~300 px across. The engine was rewritten
from scratch in this session (new canvas, new bitmask font, new
pictures, new layout code), not copied from the 25 November program.

## Build / test

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# grader equivalent (no env var): python3 main.py   # writes /output/entry.png
```

Test results (2026-11-27, local Python 3.12.3; grader runs Python 3.13):

| check | result |
|---|---|
| run 1 (round 10) | `/tmp/r10out1/entry.png`, 28,090 bytes |
| run 2 (round 10) | `/tmp/r10out2/entry.png`, 28,090 bytes |
| sha256, both runs | `c363eed0cb102e09cf52753db7178db57572161de48b04229f547c350aa9ef80` — identical |
| dimensions | 1024 × 1024 px, PNG, RGB |
| size limit | 28,090 ≤ 1,048,576 bytes ✓ |
| default `/output` run | same sha256, exit 0 |
| visual check (round 10) | viewed the round-10 render at full size and at 300 px: masthead date, all 6 headlines, all 6 pictures, IN BRIEF list (new EU, cricket and Tokyo-core lines) and footer fully readable, nothing clipped, nothing overlapping. Round-10 content changes only: two briefs swapped (EU summit, Brar debut), Tokyo brief gains "core", Jazan deck reworded; layout and pictures untouched. (Earlier rounds: ballot-box "65 - 130" label and storm "400 OFF" label removed, chip "2ND TERM" moved inside the picture.) |

## Stories in the image (all checked 27 Nov 2026, ≥2 sources each)

| # | Story | Sources |
|---|---|---|
| 01 Gulf, Kuwait | Two Italians killed in Kuwait drone strike — Italy and Kuwait blame Iran; Tehran denies it. Two Rheinmetall Italia technicians at an air-defence station; a Kuwaiti and a Pakistani also hurt. | CNN, WSJ, Dawn, Reuters |
| 02 Politics, Wellington | NZ coalition loses its majority — final count gives Luxon's bloc 65 of 130 seats, one short; he needs the centrist Opportunity Party (7 seats) to govern. | Reuters, RNZ, Nikkei |
| 03 Tech, New York | Trump backs Huang's return to Nvidia — Trump says Huang is "absolutely fine", no security threat, and calls his return "a great thing"; Huang calls it his "second term". | Straits Times, Economic Times, NDTV |
| 04 Weather, USA | Storm wrecks US Thanksgiving — about 400 flights cancelled, over 900,000 lose power on the East Coast; Macy's parade postponed for the first time in its history. | WSJ, NDTV, Reuters |
| 05 Energy, Jazan | Houthi hit kills worker at Saudi refinery — projectile strike on Aramco's Jazan refinery kills a Nepalese worker, halts some operations; Brent crude near $97. | Reuters, WSJ |
| 06 Conflict, Kyiv | Zelensky warns of new mass strike — Ukraine has information Russia is preparing a new mass strike in the coming days; he urges people to heed missile alarms. | Reuters, Kyiv Post, NDTV |
| Brief, EU | EU budget and EUR45bn Ukraine-loan talks stall — summit ends without agreement on the long-term budget or a new EUR45bn Ukraine loan. | Euronews, AP |
| Brief, Argentina | Congress bars the central bank from printing money for the government, 141-0 in the lower house; Milei's anti-inflation charter. | AP, Al Jazeera, Straits Times |
| Brief, Cricket | Gurnoor Brar strikes on India Test debut — debutant Brar takes his maiden Test wicket, trapping Devon Conway lbw for 31 with the last ball before lunch (NZ 77/1), 2nd Test, Christchurch. | Reuters, NDTV, The Week |
| Brief, India | Delhi police free 164 foreigners in a cyber-slavery raid (92 Indonesians, 72 Malaysians). | NDTV |
| Brief, Japan | Tokyo core prices rise 2.9% in November, up from 2.6% in October. | NDTV |
| Brief, World | UN urges Sri Lanka to apologise for wartime attacks on humanitarian assistance. | UN via Scoop |

Notes on dating: the Kuwait strike, the Jazan refinery hit, the
Zelensky warning and the Argentina vote happened on Thu 26 Nov, but
all were first widely reported on Fri 27 Nov (Dawn dated 27 Nov,
Reuters/Nikkei/ET dated 27 Nov); they are in scope under the rules,
which cover events that happened, or were first reported, on 27
November 2026 in any time zone. The masthead states this scope on the
face of the image. (Round-10 fix: the birthright brief and the UK
migration brief were removed — the Cooper ruling was handed down and
reported Wed 25 Nov, and the ONS 77,000 figure was released Thu 26
Nov, so neither met the 27 Nov rule; the EU summit and Brar debut
briefs that replace them are both 27 Nov items.)
Nothing in the image is invented; anything that could not be verified
for 27 Nov was dropped.

## Submission status

1. Create a **public GitHub repo** owned by the make.fun account's
   GitHub login (or add `.makefun/owner.json` with the linked wallet),
   created after the competition opened, with an OSI-approved
   licence (starter licence is MIT) and `main.py` at the root.
   Commit **only** `main.py` (+ `LICENSE`, this `README.md`,
   `.makefun/owner.json`, `.gitignore`) — do NOT commit the kit,
   `kit.tar.gz`, or `out*.png` (test outputs; the program
   regenerates the image).
2. Solana wallet linked: GPjvKCKbsEm8RZdrbucQCVJJqgkmx7gTiCk8DM7tpwsx (account @mini-poles; prizes are paid in USDC on Solana from the escrow; a winning entry must be signed with the linked wallet).
3. Bundle the **AI coding-agent transcripts** of the sessions that
   built this entry and upload them with the submission.
4. Submit via the kit CLI (`node news-image-20261127-kit/cli/makefun.mjs …`)
   before 2026-11-29 00:00 UTC, then check the dev grade
   (gate + judge games vs house images) and iterate if needed.
