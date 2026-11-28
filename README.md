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

A newspaper front page rebuilt as a full broadsheet: twelve lead
stories (two big, ten compact), each with its own code-drawn picture,
a dateline, a tag (OFFICIAL / CONFIRMED / REPORTED / CLAIM) and a
source credit; a numbered ALSO ON FRIDAY list of 24 more stories; a
world map with a numbered pin for every lead and a dot for every
brief; a THE DAY IN UTC timeline; a DATE CHECK box naming what was
left out and why; a tag legend and wire credits in the footer — 36
dated stories in all, across 7 regions and 12 fields. Headlines are
set in sentence case with a new lowercase letter set added to the
5×7 bitmap font, and are large enough to read at ~300 px across.
The engine was rewritten from scratch in this session (new canvas,
new bitmask font, new pictures, new layout code), not copied from the
25 November program.

## Build / test

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
# grader equivalent (no env var): python3 main.py   # writes /output/entry.png
```

Test results (2026-11-28, local Python 3.12.3; grader runs Python 3.13):

| check | result |
|---|---|
| run 1 (broadsheet, fact-fix) | `out/entry.png`, 39,819 bytes |
| run 2 (broadsheet, fact-fix) | `out2/entry.png`, 39,819 bytes |
| sha256, both runs | `52b8269f4c62b7d32f4c16cb13b52cce8d2cf36356104eab02f11f66074cbaa9` — identical |
| dimensions | 1024 × 1024 px, PNG, RGB |
| size limit | 39,819 ≤ 1,048,576 bytes ✓ |
| default `/output` run | same sha256, exit 0 |
| visual check (fact-fix) | viewed the render at full size and at 300 px: masthead date and counter, all 12 headlines and pictures, the 24-item ALSO ON FRIDAY list, the pinned map, the UTC timeline, the DATE CHECK box, the tag legend and the footer all readable, nothing clipped, nothing overlapping. Fixes in this round: lead 12 rewritten to the Niger Sanam attack alone (Nigeria reprisal dropped), Black Friday deck marked as an Adobe forecast, Shanghai +3.2% corrected to the +3.7% final close. (Broadsheet check: the drone blast was redrawn as a flame (it read as a red X), and the map labels for Gaza, London and Jazan were moved so no two numbers touch. Earlier rounds: ballot-box "65 - 130" label and storm "400 OFF" label removed, chip "2ND TERM" moved inside the picture.) |

## Stories in the image (all checked 27–28 Nov 2026, ≥1 named source each)

| # | Story | Sources |
|---|---|---|
| 01 Gulf, Kuwait | Two Italians killed in Kuwait drone strike — Italy and Kuwait blame Iran; Tehran denies it. Two Rheinmetall Italia technicians at an air-defence station; a Kuwaiti and a Pakistani also hurt. | CNN, WSJ, Dawn, Reuters |
| 02 Politics, Wellington | NZ coalition loses its majority — final count gives Luxon's bloc 65 of 130 seats, one short; he needs the centrist Opportunity Party (7 seats) to govern. | Reuters, RNZ, Nikkei |
| 03 Tech, New York | Trump backs Huang's return to Nvidia — Trump says Huang is "absolutely fine", no security threat, and calls his return "a great thing"; Huang calls it his "second term". | Straits Times, Economic Times, NDTV |
| 04 Weather, USA | Storm wrecks US Thanksgiving — about 400 flights cancelled, over 900,000 lose power on the East Coast; Macy's parade postponed for the first time in its history. | WSJ, NDTV, Reuters |
| 05 Energy, Jazan | Houthi hit kills worker at Saudi refinery — projectile strike on Aramco's Jazan refinery kills a Nepalese worker, halts some operations; Brent crude near $97. | Reuters, WSJ |
| 06 Conflict, Kyiv | Zelensky warns of new mass strike — Ukraine has information Russia is preparing a new mass strike in the coming days; he urges people to heed missile alarms. | Reuters, Kyiv Post, NDTV |
| 07 Politics, Brussels | EU summit ends in disarray — no deal on the 2028–2034 budget or the EUR45bn Ukraine loan; 24 of 27 back the loan, Costa offers a EUR1.78tn compromise, next summit 17–18 Dec. | Euronews, AP, Xinhua |
| 08 Conflict, Gaza | Hamas chief's son survives dawn strike — Izzeldeen al-Hayya, son of Hamas chief Khalil al-Hayya, survives a dawn strike on a Gaza City apartment; his daughter-in-law is wounded, no one is killed; Israel does not comment; Hamas links it to Katz threats. | Reuters |
| 09 Retail, USA | Black Friday shoppers return to the malls — Adobe forecasts $12.9bn in online sales (+9.2%); NRF expects 126m shoppers on the day, 182.7m across the Thanksgiving weekend. | Reuters, Adobe, NRF |
| 10 Markets | Asia rallies as Wall Street surges — Shanghai +3.7%, ChiNext +10%, Nikkei +2.0%, KOSPI +4.2%; S&P +1.6%, Nasdaq +2.3%, Dow +1.1% on a half day; gold rebounds +2.5% to about $3,670 after a 14-month low; silver +7.5%. | Morningstar/Dow Jones, Bloomberg, Investopedia |
| 11 Sport, Christchurch | NZ reach 246 for 5 on day one, 2nd Test — Latham 59, Blundell 53 not out, Phillips 36 not out; debutant Gurnoor Brar takes his maiden Test wicket, Conway lbw 31 with the last ball before lunch; Akash Deep 2/52, Bumrah wicketless. | Reuters, NDTV, Dawn, Cricinfo |
| 12 Conflict, Niger | Niger camp attack kills 13 guards — 13 National Guard killed in the Sanam camp attack (Thu 26 Nov, reported Fri 27 Nov). The Nigeria reprisal story (30 killed, Tue 24 Nov, reported 25–26 Nov) was dropped: not a 27-Nov event. | Al Jazeera |
| 13 USA | Trump lashes out at foes, migrants and his own data agency in a 461-word Thanksgiving post on Truth Social (posted Thu, reported Fri). | Reuters |
| 14 Iraq | Trump backs Iraqi PM Ali al-Zaidi's crackdown on militias, oil smuggling and state control of weapons. | Reuters |
| 15 Vietnam | CPTPP to start accession talks with the UAE, Indonesia and the Philippines. | Reuters |
| 16 Frankfurt | De Cos to lead the ECB after Lagarde — chosen Thu 26 Nov, reported Fri 27 Nov; Boone and Brunnermeier join the board. | WSJ, Reuters, Le Monde |
| 17 The Hague | ICC: Duterte trial opens Monday 30 Nov, 10:00 — 3 counts of crimes against humanity, 85 murders and 2 attempted murders, about 100 witnesses, 500+ victims. | ICC |
| 18 Spain | Campaign ends Fri, snap vote Sun 29 Nov — Sánchez vows to defy the polls, the PP is favoured. | Reuters |
| 19 Gaza City | Israeli strike hits an MSF clinic, 2 watchmen killed; MSF calls it a direct hit, its 17th staffer killed; Israel says both were Hamas military wing. | Al Jazeera |
| 20 Guinea-Bissau | Military junta delays elections to Nov 2028. | Reuters |
| 21 Kenya | Cult leader Paul Mackenzie convicted of terrorism charges (verdict Thu 26 Nov, reported Fri); already serving 200 years over about 190–200 child murders. | Reuters, Straits Times |
| 22 Mexico | Mexico seeks talks with the US on SpaceX airspace use after Starship debris (Sheinbaum said Thu 26 Nov, reported Fri). | Reuters |
| 23 UK | Anthony Williams guilty of 14 attempted murders in the train rampage (verdict Thu 26 Nov, reported Fri 27 Nov; attacks 31 Oct–1 Nov 2025, all survived). | AP |
| 24 Canary Islands | 8 migrants dead, about 100 rescued from a boat. | Reuters |
| 25 Egypt | Funerals held Fri for 31 killed in the Cairo tanker fire (crash Wed 25 Nov). | Al Jazeera |
| 26 Rome | UN: FAO/WFP warn hunger will worsen in 16 hotspots, famine risk in Sudan and South Sudan. | UN News, ReliefWeb, Al Jazeera |
| 27 India | Delhi police free 164 foreigners in a cyber-slavery raid (92 Indonesians, 72 Malaysians). | Reuters |
| 28 Japan | Tokyo core prices rise 2.9% in November, up from 2.6% in October. | NDTV |
| 29 Argentina | Congress bars the central bank from printing money for the government, 141-0 in the lower house; Milei's anti-inflation charter. | AP, Al Jazeera, Straits Times |
| 30 Sri Lanka | UN urges Sri Lanka to apologise for wartime attacks on humanitarian assistance. | UN via Scoop |
| 31 China | Huawei unveils a custom HBM design, 4096 data pins, twice Samsung/SK Hynix density, to be revealed at ISSCC in Feb 2027 (Bloomberg reported Thu 26 Nov, reported Fri). | Bloomberg, Silicon Report, Korea Herald |
| 32 Canada | Supreme Court largely upholds Quebec's Bill 21 religious-symbols ban, 6-1, in a 520-page ruling. | WSJ, AP, Dawn |
| 33 New York | UN chief condemns the Kuwait drone attacks. | UN News |
| 34 Sudan | 383,000 fled Kordofan in the past year. | UN/IOM via UN News |
| 35 Iraq | Iraq closes two Kurdish border crossings with Syria and Iran (reported Thu 26 Nov, in the Trump–Iraq article). | Reuters |
| 36 Vienna | OPEC+ ministers meet Sunday as Brent nears $97. | Bloomberg, walldembrief |

Notes on dating: the Kuwait strike, the Jazan refinery hit, the
Zelensky warning, the Argentina vote, the ECB choice, the Mackenzie
verdict, the Mexico SpaceX request, the UK train verdict, the Huawei
HBM report and the Iraq border closures happened on Thu 26 Nov, but
all were first widely reported on Fri 27 Nov; they are in scope under
the rules, which cover events that happened, or were first reported,
on 27 November 2026 in any time zone. The masthead states this scope
on the face of the image, and the DATE CHECK box names what was left
out: the SpaceX Starmind clearance (FCC Wed 25 Nov), the UK
migration release (ONS Thu 26 Nov), the birthright ruling (handed
down Wed 25 Nov), the Gaza toll of ten (Thu 26 Nov, reported 26
Nov), the Canary record arrivals (Tue 24 Nov, reported 25 Nov) and
the Cairo tanker crash (Wed 25 Nov; the funerals, held Fri 27 Nov,
are in). (Round-10 fix: the birthright brief and the UK migration
brief were removed — the Cooper ruling was handed down and reported
Wed 25 Nov, and the ONS 77,000 figure was released Thu 26 Nov, so
neither met the 27 Nov rule; the EU summit and Brar debut briefs
that replace them are both 27 Nov items.) (Fact-fix round, 28 Nov:
lead 12 was rewritten — it had merged the Niger Sanam attack with a
separate Nigeria reprisal and invented a combined toll; the lead is
now the Sanam attack alone, and the Nigeria reprisal, attacked Tue
24 Nov and reported 25–26 Nov, is out.)
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
