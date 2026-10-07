#!/usr/bin/env python3
"""
Builds every animated SVG used by the profile README into ../assets.

    python scripts/build_assets.py

All copy (roles, terminal lines, stats, projects, jokes) lives in the
CONTENT section right below - edit it there and re-run instead of touching
the generated SVGs by hand. Only the Python standard library is needed.

Animations use CSS keyframes + SMIL so they keep playing when GitHub renders
the SVG through an <img> tag (no JavaScript, no external fonts or images).
"""
import base64
import html
import os
import random
import re
from string import Template

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ASSETS = os.path.join(ROOT, "assets")

# ════════════════════════════════════════════════════════════════════════════
# CONTENT
# ════════════════════════════════════════════════════════════════════════════

NAME = "PREM SINGH"
MOTTO = "JALWA HAI HAMARA"

ROLES = [
    "Full Stack Developer",
    "AI/ML Engineer",
    "Computer Vision Tinkerer",
    "Open Source Contributor",
    "Turning chai into commits",
]

TICKER = [  # (symbol, move, up?)
    ("PYTHON", "4.20%", True), ("TYPESCRIPT", "3.14%", True),
    ("REACT", "2.71%", True), ("PYTORCH", "6.90%", True),
    ("SLEEP", "404", False), ("OPENCV", "1.61%", True),
    ("CHAI", "99.9%", True), ("BUGS", "87.3%", False),
    ("NEXT.JS", "1.41%", True), ("MERGED_PRS", "3", True),
    ("DOCKER", "2.02%", True), ("SHIP_SPEED", "9000", True),
]

# terminal: ("cmd", text) | ("out", [(text, colour), ...]) | ("prompt",)
TERMINAL = [
    ("cmd", "whoami"),
    ("out", [("Prem Singh", "fg"), (" - full stack developer & AI/ML engineer", "muted")]),
    ("cmd", "cat about.txt"),
    ("out", [("I build intelligent systems and robust web apps that solve real problems.", "fg2")]),
    ("out", [("Lately: AI tools, trading bots and computer-vision hacks.", "fg2")]),
    ("cmd", "ls ~/skills --equipped"),
    ("out", [("python/  typescript/  react/  next.js/  pytorch/  opencv/  docker/", "cyan")]),
    ("cmd", "git log --oneline -3"),
    ("out", [("3f9c2e1 ", "yellow"), ("feat: control the mouse with hand gestures", "fg2")]),
    ("out", [("8a41d07 ", "yellow"), ("feat: whatsapp bot that hunts IPO breakouts", "fg2")]),
    ("out", [("c0ffee5 ", "yellow"), ("chore: convert chai into code (again)", "fg2")]),
    ("cmd", "sudo rm -rf ./bugs"),
    ("out", [("[sudo] password for prem: ********", "muted")]),
    ("out", [("error: ", "red"), ("./bugs is load-bearing. operation cancelled.", "fg2")]),
    ("prompt",),
]

CHARACTER = {
    "class": "Full-Stack Mage",
    "subclass": "AI Summoner",
    "alignment": "Chaotic Good",
    "stats": [  # (label, value 0-100, colour) - value > 100 overflows the bar
        ("FULL-STACK SORCERY", 90, "cyan"),
        ("NEURAL NET SUMMONING", 84, "violet"),
        ("COMPUTER VISION", 82, "blue"),
        ("ALGO TRADING", 72, "green"),
        ("DEBUGGING @ 3 AM", 96, "orange"),
        ("CHAI DEPENDENCY", 135, "red"),
    ],
    "moves": [  # (button, label, colour)
        ("A", "Gesture Aim", "green"),
        ("B", "IPO Radar", "red"),
        ("X", "Road-Risk Oracle", "blue"),
        ("Y", "Vault Lock", "yellow"),
    ],
}

PROJECTS = [  # file, title, two description lines, loot, accent, illustration
    ("01-hand-gesture", "CS2 Hand-Gesture Control",
     ["Aim & fire in CS2 with just your hand - webcam",
      "hand-tracking with tap, hold & burst fire modes."],
     ["Python", "OpenCV", "MediaPipe"], "cyan", "hand"),
    ("02-ipo-screener", "IPO Breakout Screener",
     ["WhatsApp bot that scans NSE IPOs and flags stocks",
      "trading above their first-month listing high."],
     ["Python", "Twilio", "yfinance", "Docker"], "green", "chart"),
    ("03-road-ai", "Road Accident Intelligence",
     ["Road-safety analytics: India risk heatmap, trend",
      "charts and an AI assistant over Databricks data."],
     ["FastAPI", "React", "Databricks", "OpenAI"], "orange", "road"),
    ("04-taskflow", "TaskFlow",
     ["AI task manager that prioritises and breaks down",
      "work, with cron reminders and web push alerts."],
     ["Next.js", "MongoDB", "OpenAI", "NextAuth"], "violet", "tasks"),
    ("05-notes-vault", "Terminal Notes Vault",
     ["Encrypted notes vault for your terminal - tags,",
      "PBKDF2 keys and lockout after 3 failed tries."],
     ["Python", "stdlib-only", "pip package"], "yellow", "vault"),
    ("06-lucky-card", "Lucky Card",
     ["On-chain dApp: draw a random lucky card from a",
      "smart contract on the Flare Coston2 testnet."],
     ["Solidity", "JavaScript", "Flare"], "red", "cards"),
]

HEADERS = [  # file, number, title, subtitle, accent
    ("01-whoami", "01", "WHOAMI", "// boot sequence", "cyan"),
    ("02-character", "02", "CHARACTER SELECT", "// player 1 has entered the game", "violet"),
    ("03-inventory", "03", "INVENTORY", "// equipped tech", "orange"),
    ("04-quests", "04", "QUEST LOG", "// featured builds", "green"),
    ("05-open-source", "05", "OPEN SOURCE", "// boss fights won", "yellow"),
    ("06-stats", "06", "STATS", "// live from github", "blue"),
    ("07-side-quests", "07", "SIDE QUESTS", "// psst... click stuff", "red"),
    ("08-co-op", "08", "CO-OP MODE", "// let's build together", "teal"),
]

CLASSIFIED = [
    ("> ACCESS GRANTED. clearance level: JALWA", "green"),
    ("FILE  prem_singh.classified", "muted"),
    ("[01] Controls a mouse without touching it (OpenCV + MediaPipe)", "fg2"),
    ("[02] Runs a WhatsApp bot that hunts IPO breakouts on NSE", "fg2"),
    ("[03] Has merged PRs in learning-unlimited/ESP-Website", "fg2"),
    ("[04] Known weakness: \"just one more feature\" at 3 AM", "fg2"),
    ("[05] Motto: JALWA HAI HAMARA", "orange"),
]

NOW_PLAYING = {
    "title": "lofi beats to debug to",
    "artist": "Prem Singh  ·  Jalwa Hai Hamara (Deluxe Edition)",
    "up_next": ["merge_conflict (remix)", "404: sleep not found", "ship_it.mp3"],
}

# ════════════════════════════════════════════════════════════════════════════
# DESIGN TOKENS
# ════════════════════════════════════════════════════════════════════════════

C = {
    "bg": "#0d1117", "ink": "#0b0f19", "panel": "#0f1422", "panel2": "#151b2c",
    "line": "#263049", "fg": "#e6edf3", "fg2": "#c0caf5", "muted": "#8b93b8",
    "dim": "#565f89", "cyan": "#7dcfff", "blue": "#7aa2f7", "violet": "#bb9af7",
    "orange": "#ff9e64", "yellow": "#e0af68", "green": "#9ece6a", "red": "#f7768e",
    "teal": "#73daca",
}
SANS = "system-ui, -apple-system, 'Segoe UI', Roboto, Ubuntu, 'Helvetica Neue', Arial, sans-serif"
MONO = "ui-monospace, 'SF Mono', 'Cascadia Code', Consolas, Menlo, 'DejaVu Sans Mono', 'Liberation Mono', monospace"
CW = 0.6  # monospace advance as a fraction of font-size (textLength pins it)

# 5x7 pixel font, so headings look identical on every OS
FONT = {
    "A": [".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "B": ["####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."],
    "C": [".####", "#....", "#....", "#....", "#....", "#....", ".####"],
    "D": ["####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."],
    "E": ["#####", "#....", "#....", "####.", "#....", "#....", "#####"],
    "F": ["#####", "#....", "#....", "####.", "#....", "#....", "#...."],
    "G": [".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."],
    "H": ["#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"],
    "I": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "#####"],
    "J": ["..###", "...#.", "...#.", "...#.", "#..#.", "#..#.", ".##.."],
    "K": ["#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"],
    "L": ["#....", "#....", "#....", "#....", "#....", "#....", "#####"],
    "M": ["#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"],
    "N": ["#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"],
    "O": [".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "P": ["####.", "#...#", "#...#", "####.", "#....", "#....", "#...."],
    "Q": [".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"],
    "R": ["####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"],
    "S": [".####", "#....", "#....", ".###.", "....#", "....#", "####."],
    "T": ["#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."],
    "U": ["#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."],
    "V": ["#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."],
    "W": ["#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"],
    "X": ["#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"],
    "Y": ["#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."],
    "Z": ["#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"],
    "0": [".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."],
    "1": ["..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."],
    "2": [".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"],
    "3": ["####.", "....#", "....#", ".###.", "....#", "....#", "####."],
    "4": ["...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."],
    "5": ["#####", "#....", "####.", "....#", "....#", "#...#", ".###."],
    "6": [".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."],
    "7": ["#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."],
    "8": [".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."],
    "9": [".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."],
    " ": ["...", "...", "...", "...", "...", "...", "..."],
    "-": ["....", "....", "....", "####", "....", "....", "...."],
    ".": [".", ".", ".", ".", ".", ".", "#"],
    "!": ["#", "#", "#", "#", "#", ".", "#"],
    "?": [".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."],
    "/": ["....#", "...#.", "...#.", "..#..", ".#...", ".#...", "#...."],
}

# 16x18 sprite for the character sheet
SPRITE = [
    "...pppppppppp...",
    "..p.kkkkkkkk.p..",
    ".p.kHhhHhhHhk.p.",
    ".pkhhhHhhhhHhkp.",
    ".pkhhhhhhhhhhkp.",
    "cpkhhhhhhhhhhkpc",
    "cpkhhshhhhshhkpc",
    "cpkssessssesskpc",
    "cpkssessssesskpc",
    ".pkrsssmmsssrkp.",
    "...kdssssssdk...",
    ".kbbbbkddkbbbbk.",
    ".kbbbbtbbtbbbbk.",
    "kbbbbbtbbtbbbbbk",
    "kbbsllllllllsbbk",
    "kbBslllLLlllsBbk",
    "kbBBllllllllBBbk",
    ".kkkkkkkkkkkkkk.",
]
SPRITE_PAL = {
    "k": "#11131c", "h": "#5a3825", "H": "#7a4b30", "s": "#f1c27d", "d": "#d9a066",
    "e": "#11131c", "r": "#e8967a", "m": "#a0522d", "p": "#2b2f3a", "c": "#7dcfff",
    "b": "#3d59a1", "B": "#2c437e", "t": "#e6edf3", "l": "#a9b1d6", "L": "#7dcfff",
}

# ════════════════════════════════════════════════════════════════════════════
# HELPERS
# ════════════════════════════════════════════════════════════════════════════


def esc(s):
    return html.escape(s, quote=False)


def q(s):
    return html.escape(s, quote=True)


def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def css(s, **kw):
    d = dict(C)
    d.update(SANS=SANS, MONO=MONO, **kw)
    return Template(s).substitute(d)


BASE_CSS = """
text{white-space:pre}
.sans{font-family:$SANS}
.mono{font-family:$MONO}
.b{font-weight:700}
.blink{animation:blink 1.06s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
"""


def svg(w, h, title, defs="", style="", body=""):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}" fill="none" xml:space="preserve" role="img" aria-label="{q(title)}">\n'
        f"<title>{esc(title)}</title>\n<defs>{defs}</defs>\n"
        f"<style>{css(BASE_CSS)}{style}</style>\n{body}\n</svg>\n"
    )


def save(rel, content):
    path = os.path.join(ASSETS, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    print(f"  {rel:<34} {len(content.encode()) / 1024:6.1f} KB")


def glyph(ch):
    return FONT.get(ch.upper()) or FONT["?"]


def pwidth(text, px):
    return sum((len(glyph(ch)[0]) + 1) * px for ch in text) - px


def ptext(text, x, y, px, gap=None):
    """Pixel-font text -> list of (char, path_d), total width."""
    gap = px * 0.16 if gap is None else gap
    s = px - gap
    out, cx = [], x
    for ch in text:
        g = glyph(ch)
        d = "".join(
            f"M{n(cx + c * px)} {n(y + r * px)}h{n(s)}v{n(s)}h{n(-s)}z"
            for r, row in enumerate(g) for c, v in enumerate(row) if v == "#"
        )
        out.append((ch, d))
        cx += (len(g[0]) + 1) * px
    return out, cx - x - px


def ppath(text, x, y, px, gap=None):
    chars, w = ptext(text, x, y, px, gap)
    return "".join(d for _, d in chars), w


def mtext(x, y, text, size, color, extra="", anchor=None, cls="mono"):
    """Monospace text with its width pinned so it renders the same on every OS."""
    m = re.search(r'\s*class="([^"]*)"', extra)
    if m:
        cls, extra = m.group(1), extra.replace(m.group(0), "")
    a = f' text-anchor="{anchor}"' if anchor else ""
    return (f'<text class="{cls}" x="{n(x)}" y="{n(y)}" font-size="{size}" fill="{color}"{a} '
            f'textLength="{n(len(text) * size * CW)}" lengthAdjust="spacing"{extra}>{esc(text)}</text>')


def discrete(attr, events, dur, repeat=True):
    """SMIL discrete animation from (time, value) events."""
    ev = []
    for t, v in sorted(events, key=lambda e: e[0]):
        t = max(0.0, min(float(t), dur))
        if ev and abs(ev[-1][0] - t) < 1e-4:
            ev[-1] = (t, v)
        else:
            ev.append((t, v))
    assert ev[0][0] == 0, "first event must be at t=0"
    kts = ";".join("0" if t == 0 else f"{t / dur:.5f}".rstrip("0").rstrip(".") for t, _ in ev)
    vals = ";".join(str(v) for _, v in ev)
    tail = 'repeatCount="indefinite"' if repeat else 'fill="freeze"'
    return (f'<animate attributeName="{attr}" calcMode="discrete" dur="{n(dur)}s" '
            f'keyTimes="{kts}" values="{vals}" {tail}/>')


def typing(t0, chars, cw, speed):
    return [(t0 + k * speed, n(k * cw)) for k in range(chars + 1)]


def chip(x, y, text, color, size=13, pad=10, h=24):
    w = len(text) * size * CW + pad * 2
    return (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{h}" rx="{h / 2}" '
            f'fill="{color}" fill-opacity=".12" stroke="{color}" stroke-opacity=".45"/>'
            + mtext(x + pad, y + h / 2 + size * 0.36, text, size, color)), w


def b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


# ════════════════════════════════════════════════════════════════════════════
# HERO
# ════════════════════════════════════════════════════════════════════════════


def build_hero():
    W, H = 1200, 600
    rnd = random.Random(7)
    img = b64(os.path.join(ROOT, "github.jpeg"))

    px, nx, ny = 11, 64, 384
    letters, nw = ptext(NAME, nx, ny, px)

    defs = f"""
<clipPath id="card"><rect width="{W}" height="{H}" rx="24"/></clipPath>
<linearGradient id="fadeB" x1="0" y1="0" x2="0" y2="1">
  <stop offset=".28" stop-color="{C['ink']}" stop-opacity="0"/>
  <stop offset=".70" stop-color="{C['ink']}" stop-opacity=".84"/>
  <stop offset="1" stop-color="{C['ink']}" stop-opacity=".97"/></linearGradient>
<linearGradient id="fadeL" x1="0" y1="0" x2="1" y2="0">
  <stop offset="0" stop-color="{C['ink']}" stop-opacity=".8"/>
  <stop offset=".62" stop-color="{C['ink']}" stop-opacity="0"/></linearGradient>
<radialGradient id="vig" cx=".5" cy=".42" r=".78">
  <stop offset=".55" stop-color="#000" stop-opacity="0"/>
  <stop offset="1" stop-color="#000" stop-opacity=".55"/></radialGradient>
<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse">
  <rect width="4" height="1.2" fill="#000" opacity=".3"/></pattern>
<linearGradient id="scan" x1="0" y1="0" x2="0" y2="1">
  <stop offset="0" stop-color="{C['cyan']}" stop-opacity="0"/>
  <stop offset=".5" stop-color="{C['cyan']}" stop-opacity=".10"/>
  <stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/></linearGradient>
<radialGradient id="fly"><stop offset="0" stop-color="#fff4d6"/>
  <stop offset=".35" stop-color="#ffc98a" stop-opacity=".8"/>
  <stop offset="1" stop-color="#ff9e64" stop-opacity="0"/></radialGradient>
<linearGradient id="ng" gradientUnits="userSpaceOnUse" x1="{nx}" y1="0" x2="{n(nx + nw)}" y2="0" spreadMethod="repeat">
  <stop offset="0" stop-color="{C['cyan']}"/><stop offset=".33" stop-color="{C['violet']}"/>
  <stop offset=".66" stop-color="{C['orange']}"/><stop offset="1" stop-color="{C['cyan']}"/>
  <animateTransform attributeName="gradientTransform" type="translate" from="0 0" to="{n(nw)} 0" dur="7s" repeatCount="indefinite"/>
</linearGradient>
<filter id="glow" x="-10%" y="-40%" width="120%" height="180%">
  <feGaussianBlur stdDeviation="7" result="b"/>
  <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
"""
    style = css("""
.kb{transform-origin:640px 300px;animation:kb 26s ease-in-out infinite alternate}
@keyframes kb{from{transform:scale(1.03)}to{transform:scale(1.13) translate(-18px,8px)}}
.scan{animation:scan 7s linear infinite}
@keyframes scan{from{transform:translateY(0)}to{transform:translateY(780px)}}
.ff{animation-name:ff;animation-timing-function:linear;animation-iteration-count:infinite;transform-box:fill-box;transform-origin:center}
@keyframes ff{0%{transform:translate(0,0);opacity:0}15%{opacity:.95}50%{transform:translate(16px,-80px)}85%{opacity:.7}100%{transform:translate(-8px,-160px);opacity:0}}
.rec{animation:blink 1.6s steps(1) infinite}
.drop{animation:drop .8s cubic-bezier(.2,1.5,.35,1) both}
@keyframes drop{from{transform:translateY(-70px);opacity:0}to{transform:none;opacity:1}}
.gA,.gB{animation:gA 4.8s steps(1) infinite}
.gB{animation-name:gB}
@keyframes gA{0%,84%{transform:translate(0,0);opacity:0}85%{transform:translate(-9px,3px);opacity:.9}88%{transform:translate(7px,-2px);opacity:.9}91%{transform:translate(-3px,1px);opacity:.6}94%,100%{opacity:0}}
@keyframes gB{0%,84%{transform:translate(0,0);opacity:0}85%{transform:translate(9px,-3px);opacity:.9}88%{transform:translate(-6px,2px);opacity:.9}91%{transform:translate(3px,0);opacity:.6}94%,100%{opacity:0}}
.jit{animation:jit 4.8s steps(1) infinite}
@keyframes jit{0%,84%,94%,100%{transform:none}86%{transform:translateX(5px) skewX(-6deg)}89%{transform:translateX(-4px)}}
.ripple{animation:ripple 1.8s ease-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes ripple{from{transform:scale(1);opacity:.85}to{transform:scale(3.4);opacity:0}}
.sticker{animation:wob 5s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes wob{0%,100%{transform:rotate(-7deg)}50%{transform:rotate(-3deg) translateY(-4px)}}
""")

    body = [f'<g clip-path="url(#card)">',
            f'<rect width="{W}" height="{H}" fill="{C["ink"]}"/>',
            f'<image class="kb" href="data:image/jpeg;base64,{img}" x="0" y="-48" width="{W}" height="675" preserveAspectRatio="xMidYMid slice"/>',
            f'<rect width="{W}" height="{H}" fill="#1a1b40" opacity=".16"/>',
            f'<rect width="{W}" height="{H}" fill="url(#fadeL)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#fadeB)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#vig)"/>',
            f'<rect width="{W}" height="{H}" fill="url(#sl)" opacity=".6"/>',
            f'<rect class="scan" y="-170" width="{W}" height="170" fill="url(#scan)"/>']

    # fireflies drifting up through the window light
    for _ in range(18):
        x, y = rnd.uniform(470, 1180), rnd.uniform(90, 590)
        r = rnd.uniform(3.5, 8)
        dur, delay = rnd.uniform(7, 13), -rnd.uniform(0, 13)
        body.append(f'<circle class="ff" cx="{n(x)}" cy="{n(y)}" r="{n(r)}" fill="url(#fly)" '
                    f'style="animation-duration:{n(dur)}s;animation-delay:{n(delay)}s"/>')

    # HUD frame
    body.append(f'<path d="M28 72V28H72M1128 28H1172V72M1172 528V572H1128M72 572H28V528" '
                f'stroke="{C["cyan"]}" stroke-opacity=".6" stroke-width="2"/>')
    body.append(f'<circle class="rec" cx="56" cy="52" r="5.5" fill="{C["red"]}"/>')
    body.append(mtext(70, 57, "LIVE", 14, C["red"], ' class="mono b"'))
    body.append(mtext(116, 57, "PREM_SINGH.EXE  //  SESSION 2026", 14, C["fg2"], ' opacity=".75"'))

    label = "OPEN TO COLLABS"
    cwid = len(label) * 14 * CW + 52
    cx0 = 1150 - cwid
    body.append(f'<rect x="{n(cx0)}" y="36" width="{n(cwid)}" height="32" rx="16" fill="{C["ink"]}" '
                f'fill-opacity=".72" stroke="{C["green"]}" stroke-opacity=".55"/>')
    body.append(f'<circle class="ripple" cx="{n(cx0 + 20)}" cy="52" r="5" fill="{C["green"]}"/>')
    body.append(f'<circle cx="{n(cx0 + 20)}" cy="52" r="5" fill="{C["green"]}"/>')
    body.append(mtext(cx0 + 34, 57, label, 14, C["green"], ' class="mono b"'))

    body.append(mtext(1150, 560, "BUGS: 0*   *probably", 13, C["fg2"], ' opacity=".55"', anchor="end"))

    # "> hello world, I'm" - typed once
    hello = "hello world, I'm"
    hs, hcw = 22, 22 * CW
    hx = nx + 2 * hcw
    body.append(f'<clipPath id="hc"><rect x="{n(hx)}" y="{352 - hs}" height="{hs * 1.5}" width="{n(len(hello) * hcw + 4)}">'
                f'{discrete("width", [(0, 0)] + typing(0.3, len(hello), hcw, 0.05), 0.35 + len(hello) * 0.05, repeat=False)}'
                f'</rect></clipPath>')
    body.append(mtext(nx, 352, ">", hs, C["orange"], ' class="mono b"'))
    body.append(f'<g clip-path="url(#hc)">{mtext(hx, 352, hello, hs, C["teal"])}</g>')

    # glitchy pixel name
    allpath = "".join(d for _, d in letters)
    body.append(f'<g class="gA"><path d="{allpath}" fill="{C["cyan"]}" opacity=".9"/></g>')
    body.append(f'<g class="gB"><path d="{allpath}" fill="#ff3d81" opacity=".9"/></g>')
    body.append('<g class="jit" filter="url(#glow)">')
    for i, (ch, d) in enumerate(letters):
        if d:
            body.append(f'<g class="drop" style="animation-delay:{n(1.0 + i * 0.07)}s"><path d="{d}" fill="url(#ng)"/></g>')
    body.append("</g>")

    # rotating roles, typed + deleted on a loop
    rs, rcw, ry = 28, 28 * CW, 518
    rx = nx + 2 * rcw
    slot, dur = 4.0, 4.0 * len(ROLES)
    body.append(mtext(nx, ry, "$", rs, C["orange"], ' class="mono b"'))
    cursor = [(0, n(rx))]
    for i, role in enumerate(ROLES):
        s = i * slot
        ev = [(0, 0)] + typing(s + 0.15, len(role), rcw, 0.055)
        hold = s + 0.15 + len(role) * 0.055 + 1.7
        ev += [(hold + k * 0.022, n((len(role) - k) * rcw)) for k in range(len(role) + 1)]
        cursor += [(t, n(rx + float(w))) for t, w in ev if t > 0]
        full = n(len(role) * rcw + 4) if i == 0 else 0
        body.append(f'<clipPath id="r{i}"><rect x="{n(rx)}" y="{ry - rs}" height="{rs * 1.5}" width="{full}">'
                    f'{discrete("width", ev, dur)}</rect></clipPath>')
        body.append(f'<g clip-path="url(#r{i})">{mtext(rx, ry, role, rs, C["cyan"], " class=\"mono b\"")}</g>')
    body.append(f'<g class="blink"><rect x="{n(rx + len(ROLES[0]) * rcw)}" y="{ry - rs * 0.82}" width="{n(rcw * 0.6)}" '
                f'height="{rs * 1.0}" fill="{C["orange"]}">{discrete("x", cursor, dur)}</rect></g>')

    # motto sticker
    spx = 3
    sw = pwidth(MOTTO, spx)
    pw, ph = sw + 36, 7 * spx + 30
    sp, _ = ppath(MOTTO, -sw / 2, -7 * spx / 2, spx, gap=0)
    body.append(f'<g transform="translate(1000 462)"><g class="sticker">'
                f'<rect x="{n(-pw / 2 + 5)}" y="{n(-ph / 2 + 6)}" width="{n(pw)}" height="{n(ph)}" rx="8" fill="#000" opacity=".45"/>'
                f'<rect x="{n(-pw / 2)}" y="{n(-ph / 2)}" width="{n(pw)}" height="{n(ph)}" rx="8" fill="{C["yellow"]}"/>'
                f'<rect x="{n(-pw / 2 + 4)}" y="{n(-ph / 2 + 4)}" width="{n(pw - 8)}" height="{n(ph - 8)}" rx="5" stroke="#1a1b26" stroke-opacity=".35" stroke-dasharray="4 4"/>'
                f'<path d="{sp}" fill="#1a1b26"/>'
                f'<rect x="-34" y="{n(-ph / 2 - 10)}" width="68" height="18" fill="#fff" opacity=".35" transform="rotate(4)"/>'
                f'</g></g>')

    body.append("</g>")
    body.append(f'<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="23.5" stroke="{C["cyan"]}" stroke-opacity=".25" stroke-width="1.5"/>')
    save("hero.svg", svg(W, H, f"{NAME.title()} - " + " | ".join(ROLES[:2]), defs, style, "\n".join(body)))


# ════════════════════════════════════════════════════════════════════════════
# TICKER
# ════════════════════════════════════════════════════════════════════════════


def build_ticker():
    W, H, fs = 1200, 54, 17
    cw = fs * CW
    parts, chars = [], 0
    for sym, move, up in TICKER:
        for txt, col in ((sym + " ", C["fg2"]), (("▲ " if up else "▼ ") + move, C["green"] if up else C["red"]),
                         ("   ·   ", C["dim"])):
            parts.append(f'<tspan fill="{col}">{esc(txt)}</tspan>')
            chars += len(txt)
    tw = chars * cw
    line = lambda x: (f'<text class="mono b" x="{n(x)}" y="33" font-size="{fs}" textLength="{n(tw)}" '
                      f'lengthAdjust="spacing">{"".join(parts)}</text>')
    defs = f"""
<clipPath id="tk"><rect width="{W}" height="{H}" rx="12"/></clipPath>
<linearGradient id="fl" x1="0" x2="1"><stop offset="0" stop-color="{C['bg']}"/><stop offset="1" stop-color="{C['bg']}" stop-opacity="0"/></linearGradient>
<linearGradient id="fr" x1="1" x2="0"><stop offset="0" stop-color="{C['bg']}"/><stop offset="1" stop-color="{C['bg']}" stop-opacity="0"/></linearGradient>
"""
    style = css(".roll{animation:roll %ss linear infinite}@keyframes roll{to{transform:translateX(-%spx)}}" % (n(tw / 65), n(tw)))
    body = f"""<g clip-path="url(#tk)">
<rect width="{W}" height="{H}" fill="{C['bg']}"/>
<g class="roll">{line(200)}{line(200 + tw)}</g>
<rect x="190" width="60" height="{H}" fill="url(#fl)"/>
<rect x="{W - 60}" width="60" height="{H}" fill="url(#fr)"/>
<rect width="196" height="{H}" fill="{C['panel2']}"/>
<circle class="blink" cx="26" cy="27" r="5" fill="{C['red']}"/>
{mtext(42, 33, "PSX", 17, C['fg'], ' class="mono b"')}
{mtext(84, 33, "LIVE", 13, C['red'], ' class="mono b"')}
{mtext(124, 33, "24/7", 13, C['dim'])}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" stroke="{C['line']}"/>"""
    save("ticker.svg", svg(W, H, "Prem Stock Exchange ticker - Python up, sleep down", defs, style, body))


# ════════════════════════════════════════════════════════════════════════════
# ACHIEVEMENT TOAST
# ════════════════════════════════════════════════════════════════════════════


def build_achievement():
    W, H = 780, 130
    cx, cy, r = 70, 65, 46
    full = W - 30
    T = 9.0
    k = lambda *ts: ";".join(f"{t / T:.4f}" for t in ts)
    defs = f"""
<linearGradient id="xg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#5fd35f"/><stop offset="1" stop-color="#107c10"/></linearGradient>
<linearGradient id="pill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#232838"/><stop offset="1" stop-color="#151926"/></linearGradient>
<linearGradient id="shine" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".18"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
<clipPath id="pc"><rect x="{cx - r}" y="{cy - r}" height="{2 * r}" rx="{r}" width="{full}">
  <animate attributeName="width" dur="{T}s" repeatCount="indefinite" calcMode="spline"
    keyTimes="0;{k(0.45, 1.05, 7.7, 8.25)};1" values="{2 * r};{2 * r};{full};{full};{2 * r};{2 * r}"
    keySplines=".2 .8 .2 1;.2 .8 .2 1;0 0 1 1;.6 0 .8 .2;0 0 1 1"/></rect></clipPath>
"""
    trophy = ("M-15 -20h30v10a15 15 0 0 1-30 0z M-15 -16h-7a7 7 0 0 0 7 11 M15 -16h7a7 7 0 0 1-7 11 "
              "M-4 5h8v8h-8z M-12 13h24v6h-24z")
    body = f"""
<g clip-path="url(#pc)">
  <rect x="{cx - r}" y="{cy - r}" width="{full}" height="{2 * r}" rx="{r}" fill="url(#pill)" stroke="#39405a"/>
  <g opacity="0">
    <animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;{k(0.9, 1.25, 7.5, 7.75)};1" values="0;0;1;1;0;0"/>
    <text class="sans b" x="{cx + r + 26}" y="54" font-size="15" letter-spacing="2.5" fill="{C['green']}">ACHIEVEMENT UNLOCKED</text>
    <text class="sans b" x="{cx + r + 26}" y="88" font-size="27" fill="{C['fg']}">You found Prem's profile</text>
    <text class="sans b" x="{full - 10}" y="88" font-size="27" fill="{C['yellow']}" text-anchor="end">+50 G</text>
  </g>
  <rect x="-200" y="0" width="160" height="{H}" fill="url(#shine)" transform="skewX(-20)">
    <animate attributeName="x" dur="{T}s" repeatCount="indefinite" keyTimes="0;{k(1.3, 2.3)};1" values="-200;-200;{W + 100};{W + 100}"/>
  </rect>
</g>
<g transform="translate({cx} {cy})">
  <g>
    <animateTransform attributeName="transform" type="scale" dur="{T}s" repeatCount="indefinite" calcMode="spline"
      keyTimes="0;{k(0.3, 0.45, 8.25, 8.6)};1" values="0;1.15;1;1;0;0" keySplines=".3 1.6 .5 1;.5 0 .5 1;0 0 1 1;.6 0 .9 .3;0 0 1 1"/>
    <circle r="{r - 4}" fill="url(#xg)"/>
    <circle r="{r - 4}" stroke="#fff" stroke-opacity=".35" stroke-width="2"/>
    <circle r="{r - 4}" stroke="#9ece6a" stroke-width="3" opacity="0">
      <animate attributeName="r" dur="{T}s" repeatCount="indefinite" keyTimes="0;{k(0.4, 1.4)};1" values="{r - 4};{r - 4};{r + 26};{r + 26}"/>
      <animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" keyTimes="0;{k(0.4, 1.4)};1" values="0;.9;0;0"/>
    </circle>
    <path d="{trophy}" fill="#fff" stroke="#fff" stroke-width="1.5" stroke-linejoin="round"/>
    <path d="M-15 -16h-7a7 7 0 0 0 7 11 M15 -16h7a7 7 0 0 1-7 11" stroke="#fff" stroke-width="3" fill="none"/>
  </g>
</g>"""
    save("achievement.svg", svg(W, H, "Achievement unlocked: You found Prem's profile (+50 G)", defs, "", body))


# ════════════════════════════════════════════════════════════════════════════
# SECTION HEADERS
# ════════════════════════════════════════════════════════════════════════════


def build_headers():
    W, H, px = 1200, 84, 5
    y0 = (H - 7 * px) / 2
    for fname, num, title, sub, accent in HEADERS:
        col = C[accent]
        nd, nwid = ppath(num, 32, y0, px)
        dx = 32 + nwid + 22
        td, twid = ppath(title, dx + 24, y0, px)
        defs = f"""<clipPath id="hc"><rect width="{W}" height="{H}" rx="14"/></clipPath>
<linearGradient id="gl" x1="0" x2="1"><stop offset="0" stop-color="{col}" stop-opacity="0"/><stop offset=".5" stop-color="{col}"/><stop offset="1" stop-color="{col}" stop-opacity="0"/></linearGradient>"""
        style = css(".glint{animation:gl 6s ease-in-out infinite}@keyframes gl{from{transform:translateX(-260px)}to{transform:translateX(1260px)}}")
        body = f"""<g clip-path="url(#hc)">
<rect width="{W}" height="{H}" fill="{C['bg']}"/>
<rect width="5" height="{H}" fill="{col}"/>
<path d="{nd}" fill="{col}"/>
<path d="M{n(dx)} 24V60" stroke="{C['line']}" stroke-width="2"/>
<path d="{td}" fill="{C['fg']}"/>
<rect class="blink" x="{n(dx + 24 + twid + 12)}" y="{n(y0)}" width="{px * 3}" height="{px * 7}" fill="{col}"/>
{mtext(W - 32, 48, sub, 16, C['muted'], anchor="end")}
<rect class="glint" y="{H - 2}" width="240" height="2" fill="url(#gl)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="13.5" stroke="{C['line']}"/>"""
        save(f"headers/{fname}.svg", svg(W, H, f"{num} - {title.title()}", defs, style, body))


# ════════════════════════════════════════════════════════════════════════════
# TERMINAL
# ════════════════════════════════════════════════════════════════════════════


def build_terminal():
    W, fs, lh = 1200, 20, 32
    cw = fs * CW
    top, left = 98, 40
    H = top + (len(TERMINAL) - 1) * lh + 44
    T = 24.0
    clear = T - 0.7
    t = 0.6
    body, cursor_x, cursor_y, cursor_o = [], [(0, left)], [(0, top)], [(0, 0)]
    for i, step in enumerate(TERMINAL):
        y = top + i * lh
        vis = discrete("opacity", [(0, 0), (t, 1), (clear, 0)], T)
        if step[0] in ("cmd", "prompt"):
            body.append(f'<g>{vis}{mtext(left, y, "~", fs, C["cyan"], " class=\"mono b\"")}'
                        f'{mtext(left + 2 * cw, y, "❯", fs, C["violet"], " class=\"mono b\"")}</g>')
            cx = left + 4 * cw
            cursor_x.append((t, n(cx)))
            cursor_y.append((t, y - fs * 0.8))
            cursor_o.append((t, 1))
            if step[0] == "prompt":
                cursor_o.append((clear, 0))
                break
            cmd = step[1]
            t += 0.4
            ev = [(0, 0)] + typing(t, len(cmd), cw, 0.06) + [(clear, 0)]
            cursor_x += [(tt, n(cx + float(w))) for tt, w in ev[1:-1]]
            body.append(f'<clipPath id="c{i}"><rect x="{n(cx)}" y="{y - fs}" height="{fs * 1.5}" width="{n(len(cmd) * cw + 2)}">'
                        f'{discrete("width", ev, T)}</rect></clipPath>')
            body.append(f'<g clip-path="url(#c{i})">{mtext(cx, y, cmd, fs, C["fg"])}</g>')
            t += len(cmd) * 0.06 + 0.35
            cursor_o.append((t, 0))
        else:
            segs = step[1]
            total = sum(len(s) for s, _ in segs)
            spans = "".join(f'<tspan fill="{C[col]}">{esc(s)}</tspan>' for s, col in segs)
            body.append(f'<g>{vis}<text class="mono" x="{left}" y="{y}" font-size="{fs}" textLength="{n(total * cw)}" '
                        f'lengthAdjust="spacing">{spans}</text></g>')
            t += 0.14
            if i + 1 < len(TERMINAL) and TERMINAL[i + 1][0] != "out":
                t += 0.5
    assert t < clear - 6, "terminal script too long for the loop"

    body.append(f'<g class="blink"><rect x="{left}" y="{top}" width="{n(cw * 0.62)}" height="{fs * 1.05}" fill="{C["orange"]}">'
                f'{discrete("x", cursor_x, T)}{discrete("y", cursor_y, T)}{discrete("opacity", cursor_o, T)}</rect></g>')

    # ascii mug with animated steam in the empty corner
    mug = ["  ..........", "  |        |]", "  |        |/", "  \\        /", "   `------'"]
    mx, my = 920, H - 150
    mugs = "".join(mtext(mx, my + j * 24, row, 20, C["dim"]) for j, row in enumerate(mug))
    steam = [("     ( (", "      ) )"), ("      ) )", "     ( (")]
    steam_s = "".join(f'<g class="st{j}">{mtext(mx, my - 52, a, 20, C["dim"])}{mtext(mx, my - 28, b, 20, C["dim"])}</g>'
                      for j, (a, b) in enumerate(steam))

    defs = f"""<clipPath id="win"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<radialGradient id="tg" cx=".85" cy=".1" r=".6"><stop offset="0" stop-color="{C['violet']}" stop-opacity=".10"/><stop offset="1" stop-color="{C['violet']}" stop-opacity="0"/></radialGradient>"""
    style = css(".st0,.st1{animation:st 1.4s steps(1) infinite}.st1{animation-delay:-.7s}"
                "@keyframes st{0%{opacity:1}50%{opacity:0}}")
    title = "prem@jalwa-hai-hamara: ~/portfolio — zsh"
    out = f"""<g clip-path="url(#win)">
<rect width="{W}" height="{H}" fill="#0f131d"/>
<rect width="{W}" height="{H}" fill="url(#tg)"/>
<rect width="{W}" height="50" fill="#151a28"/>
<path d="M0 50H{W}" stroke="{C['line']}"/>
<circle cx="28" cy="25" r="7" fill="#ff5f57"/><circle cx="52" cy="25" r="7" fill="#febc2e"/><circle cx="76" cy="25" r="7" fill="#28c840"/>
{mtext(W / 2, 30, title, 14, C['muted'], anchor="middle")}
{mtext(W - 28, 30, "⌘ 1", 13, C['dim'], anchor="end")}
{mugs}{steam_s}
{"".join(body)}
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" stroke="{C['line']}"/>"""
    save("terminal.svg", svg(W, H, "Terminal: whoami - Prem Singh, full stack developer and AI/ML engineer", defs, style, out))


# ════════════════════════════════════════════════════════════════════════════
# CHARACTER SHEET
# ════════════════════════════════════════════════════════════════════════════


def build_character():
    W, H = 1200, 600
    ch = CHARACTER
    body = []
    defs = f"""<pattern id="dots" width="22" height="22" patternUnits="userSpaceOnUse"><circle cx="2" cy="2" r="1.2" fill="{C['line']}"/></pattern>
<radialGradient id="pg" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="{C['cyan']}" stop-opacity=".25"/><stop offset="1" stop-color="{C['cyan']}" stop-opacity="0"/></radialGradient>
<clipPath id="cc"><rect x="1" y="1" width="1198" height="{H - 2}" rx="20"/></clipPath>"""
    style = css("""
.bob{animation:bob 1.2s steps(1) infinite}
@keyframes bob{50%{transform:translateY(-7px)}}
.tw{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}
@keyframes tw{0%,100%{opacity:.15;transform:scale(.6)}50%{opacity:1;transform:scale(1)}}
.over{animation:blink .5s steps(1) infinite}
""")
    # card
    body.append(f'<g clip-path="url(#cc)"><rect width="{W}" height="{H}" fill="{C["panel"]}"/>'
                f'<rect width="{W}" height="{H}" fill="url(#dots)" opacity=".55"/></g>')
    body.append(f'<rect x="1" y="1" width="1198" height="{H - 2}" rx="20" stroke="{C["line"]}" stroke-width="1.5"/>')

    # portrait
    fx, fy, fw, fh = 36, 36, 360, 300
    body.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="16" fill="{C["ink"]}" stroke="{C["cyan"]}" stroke-opacity=".45" stroke-width="2"/>')
    body.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="16" fill="url(#pg)"/>')
    body.append(f'<path d="M{fx + 30} {fy + fh - 34}H{fx + fw - 30}" stroke="{C["line"]}" stroke-width="2" stroke-dasharray="6 8"/>')
    sp = 14
    sx = fx + (fw - 16 * sp) / 2
    sy = fy + fh - 34 - 18 * sp - 4
    body.append(f'<ellipse cx="{fx + fw / 2}" cy="{fy + fh - 34}" rx="110" ry="9" fill="#000" opacity=".45"/>')
    pix = []
    for r, row in enumerate(SPRITE):
        assert len(row) == 16, f"sprite row {r} is {len(row)} wide"
        for c, v in enumerate(row):
            if v != ".":
                pix.append(f'<rect x="{n(sx + c * sp)}" y="{n(sy + r * sp)}" width="{sp + 0.4}" height="{sp + 0.4}" fill="{SPRITE_PAL[v]}"/>')
    body.append(f'<g class="bob">{"".join(pix)}</g>')
    for (x, y, d) in [(fx + 50, fy + 70, 0), (fx + 312, fy + 110, 0.8), (fx + 290, fy + 50, 1.6), (fx + 70, fy + 200, 1.2)]:
        body.append(f'<path class="tw" style="animation-delay:{d}s" d="M{x} {y - 9}v18M{x - 9} {y}h18" stroke="{C["yellow"]}" stroke-width="3"/>')
    pc, pw = chip(fx + 16, fy + 16, "P1", C["orange"], 13, 10)
    body.append(pc)
    body.append(chip(fx + fw - 16 - (len("LVL 2006") * 13 * CW + 20), fy + 16, "LVL 2006", C["green"], 13, 10)[0])

    # identity
    nd, nwid = ppath(NAME, fx + (fw - pwidth(NAME, 5)) / 2, 360, 5)
    body.append(f'<path d="{nd}" fill="{C["fg"]}"/>')
    rows = [("CLASS", ch["class"]), ("SUBCLASS", ch["subclass"]), ("ALIGNMENT", ch["alignment"])]
    for j, (k, v) in enumerate(rows):
        y = 428 + j * 28
        body.append(mtext(fx + 4, y, k, 15, C["dim"]))
        body.append(mtext(fx + 120, y, v, 15, C["fg2"]))
    for j, (k, col, frac, txt) in enumerate([("HP", "red", 1.0, "100/100"), ("MP", "blue", 1.0, "∞ chai")]):
        y = 528 + j * 30
        body.append(mtext(fx + 4, y + 13, k, 15, C[col], ' class="mono b"'))
        body.append(f'<rect x="{fx + 44}" y="{y}" width="210" height="16" rx="3" fill="{C["ink"]}" stroke="{C["line"]}"/>')
        body.append(f'<rect x="{fx + 46}" y="{y + 2}" width="{206 * frac}" height="12" rx="2" fill="{C[col]}"/>')
        body.append(mtext(fx + 266, y + 13, txt, 14, C["muted"]))

    # stats
    gx, gy = 452, 44
    sd, _ = ppath("STATS", gx, gy, 4)
    body.append(f'<path d="{sd}" fill="{C["cyan"]}"/>')
    body.append(mtext(1116, gy + 24, "base stats before chai buff", 13, C["dim"], anchor="end"))
    seg_n, seg_w, seg_gap = 24, 23, 4.5
    track_w = seg_n * (seg_w + seg_gap) - seg_gap
    for j, (label, val, col) in enumerate(ch["stats"]):
        y = gy + 72 + j * 66
        over = val > 100
        body.append(mtext(gx, y, label, 16, C["fg2"]))
        body.append(mtext(gx + track_w, y, "OVERFLOW!" if over else str(val), 16, C["red"] if over else C[col],
                          ' class="mono b over"' if over else ' class="mono b"', anchor="end"))
        segs = []
        lit = round(seg_n * val / 100)
        for s in range(max(seg_n, lit)):
            x = gx + s * (seg_w + seg_gap)
            on = s < lit
            if s < seg_n:
                segs.append(f'<rect x="{n(x)}" y="{y + 12}" width="{seg_w}" height="18" rx="3" fill="{C["ink"]}" stroke="{C["line"]}"/>')
            if on:
                begin = n(0.6 + j * 0.25 + s * 0.035)
                fill = C[col] if s < seg_n else C["red"]
                segs.append(f'<rect x="{n(x + 2)}" y="{y + 14}" width="{seg_w - 4}" height="14" rx="2" fill="{fill}">'
                            f'<animate attributeName="opacity" values="0;1" dur=".01s" begin="{begin}s" fill="freeze"/>'
                            f'<set attributeName="opacity" to="0" begin="0s"/></rect>')
        body.append("".join(segs))

    # special moves
    my = gy + 72 + len(ch["stats"]) * 66 + 10
    md, _ = ppath("SPECIAL MOVES", gx, my - 26, 3)
    body.append(f'<path d="{md}" fill="{C["orange"]}"/>')
    x = gx
    for btn, label, col in ch["moves"]:
        w = len(label) * 14 * CW + 54
        body.append(f'<rect x="{n(x)}" y="{my}" width="{n(w)}" height="34" rx="17" fill="{C["ink"]}" stroke="{C["line"]}"/>')
        body.append(f'<circle cx="{n(x + 17)}" cy="{my + 17}" r="12" fill="{C[col]}"/>')
        body.append(f'<text class="sans b" x="{n(x + 17)}" y="{my + 22}" font-size="14" fill="{C["ink"]}" text-anchor="middle">{btn}</text>')
        body.append(mtext(x + 38, my + 22, label, 14, C["fg2"]))
        x += w + 12

    save("character.svg", svg(W, H, "Character sheet: Prem Singh, Full-Stack Mage / AI Summoner", defs, style, "\n".join(body)))


# ════════════════════════════════════════════════════════════════════════════
# QUEST CARDS
# ════════════════════════════════════════════════════════════════════════════

def il_hand(a):
    pts = [(70, 150), (45, 138), (30, 120), (20, 102), (12, 86), (50, 95), (46, 68), (44, 50), (42, 32),
           (68, 92), (68, 62), (68, 42), (68, 24), (86, 95), (90, 68), (92, 50), (94, 36),
           (102, 103), (110, 82), (115, 68), (119, 55)]
    bones = [(0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8), (5, 9), (9, 13), (13, 17),
             (9, 10), (10, 11), (11, 12), (13, 14), (14, 15), (15, 16), (0, 17), (17, 18), (18, 19), (19, 20)]
    lines = "".join(f'M{pts[i][0]} {pts[i][1]}L{pts[j][0]} {pts[j][1]}' for i, j in bones)
    joints = "".join(f'<circle cx="{x}" cy="{y}" r="3.6" fill="{C["fg"]}" stroke="{a}" stroke-width="1.5"/>' for x, y in pts)
    path = [(395, 85), (470, 70), (440, 128), (488, 118), (488, 118), (395, 85)]
    xs = ";".join(f"{x} {y}" for x, y in path)
    return f"""
<g transform="translate(118 22)"><g>
  <animateTransform attributeName="transform" type="rotate" values="-4 70 150;4 70 150;-4 70 150" dur="4s" repeatCount="indefinite" calcMode="spline" keySplines=".45 0 .55 1;.45 0 .55 1"/>
  <path d="{lines}" stroke="{a}" stroke-width="3" stroke-linecap="round"/>{joints}
  <circle cx="42" cy="32" r="6" fill="{a}"/>
  <circle cx="42" cy="32" r="6" stroke="{a}" stroke-width="2"><animate attributeName="r" values="6;18" dur="1.4s" repeatCount="indefinite"/><animate attributeName="opacity" values="1;0" dur="1.4s" repeatCount="indefinite"/></circle>
</g></g>
<path d="M172 56C260 40 300 60 360 78" stroke="{a}" stroke-opacity=".5" stroke-width="2" stroke-dasharray="4 7"><animate attributeName="stroke-dashoffset" values="22;0" dur=".8s" repeatCount="indefinite"/></path>
<rect x="352" y="34" width="176" height="128" rx="10" fill="{C['bg']}" stroke="{C['line']}"/>
{mtext(364, 52, "CS2 // AIM ASSIST: YOU", 10, C['dim'])}
<circle cx="488" cy="118" r="11" stroke="{C['red']}" stroke-width="2"/><circle cx="488" cy="118" r="3" fill="{C['red']}"/>
<g><animateTransform attributeName="transform" type="translate" values="{xs}" keyTimes="0;.22;.44;.66;.84;1" dur="4s" repeatCount="indefinite"/>
  <g transform="translate(0 0)"><path d="M-14 0h9M5 0h9M0 -14v9M0 5v9" stroke="{C['green']}" stroke-width="2.5"/><circle r="2" fill="{C['green']}"/></g>
</g>
<text class="mono b" x="440" y="152" font-size="12" fill="{C['red']}" text-anchor="middle" opacity="0">HEADSHOT!
  <animate attributeName="opacity" values="0;0;1;1;0;0" keyTimes="0;.65;.67;.84;.86;1" dur="4s" repeatCount="indefinite"/></text>"""


def il_chart(a):
    base = 150
    hi = 92
    candles = [(52, 132, 118, 140, 112), (78, 120, 130, 136, 112), (104, 128, 108, 134, 100),
               (130, 112, 100, 118, 90), (156, 104, 116, 122, 98), (182, 114, 98, 120, 94),
               (208, 98, 84, 102, 78), (234, 86, 72, 90, 64), (260, 74, 80, 86, 66),
               (286, 78, 60, 82, 54), (312, 62, 48, 66, 42)]
    out = [f'<path d="M40 {hi}H330" stroke="{C["yellow"]}" stroke-width="1.5" stroke-dasharray="6 5"/>',
           mtext(44, hi - 8, "1ST-MONTH HIGH", 10, C["yellow"])]
    T = 6.0
    for i, (x, o, c, h, l) in enumerate(candles):
        up = c < o
        col = C["green"] if up else C["red"]
        t = 0.2 + i * 0.22
        out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (t, 1), (T - 0.3, 0)], T)}'
                   f'<path d="M{x} {h}V{l}" stroke="{col}" stroke-width="2"/>'
                   f'<rect x="{x - 7}" y="{min(o, c)}" width="14" height="{max(abs(o - c), 2)}" rx="2" fill="{col}"/></g>')
    bt = 0.2 + 6 * 0.22
    out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (bt, 1), (T - 0.3, 0)], T)}'
               f'<rect x="170" y="36" width="96" height="22" rx="11" fill="{a}"/>'
               f'{mtext(180, 51, "▲ BREAKOUT", 11, C["ink"], " class=\"mono b\"")}'
               f'<path d="M208 58L208 74" stroke="{a}" stroke-width="2"/></g>')
    bub_t = 0.2 + 10 * 0.22 + 0.3
    out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (bub_t, 1), (T - 0.3, 0)], T)}'
               f'<rect x="352" y="62" width="176" height="72" rx="14" fill="#1d3b2a" stroke="{a}" stroke-opacity=".5"/>'
               f'<path d="M352 116l-12 14 22-6z" fill="#1d3b2a"/>'
               f'{mtext(366, 86, "IPO 2024 scan done", 12, C["fg"])}'
               f'{mtext(366, 106, "3 breakouts found", 12, a, " class=\"mono b\"")}'
               f'{mtext(470, 126, "09:15 ✓✓", 10, C["cyan"])}</g>')
    out.append(f'<path d="M40 {base + 14}H330" stroke="{C["line"]}"/>')
    return "".join(out)


def il_road(a):
    out = [f'<path d="M40 182L150 46H186L296 182Z" fill="#161c2c"/>',
           f'<path d="M40 182L150 46M296 182L186 46" stroke="{C["dim"]}" stroke-width="2"/>',
           f'<path d="M168 182V46" stroke="{C["yellow"]}" stroke-width="4" stroke-dasharray="14 12">'
           f'<animate attributeName="stroke-dashoffset" values="0;-26" dur=".5s" repeatCount="indefinite"/></path>',
           f'<ellipse cx="168" cy="46" rx="90" ry="8" fill="{a}" opacity=".22"/>',
           mtext(330, 44, "RISK HEATMAP", 10, C["dim"])]
    rnd = random.Random(3)
    for r in range(5):
        for c in range(9):
            x, y = 336 + c * 22, 64 + r * 22
            roll = rnd.random()
            col, rr = (C["red"], 6) if roll > .84 else (C["orange"], 5) if roll > .62 else (C["green"], 4)
            op = ".95" if col != C["green"] else ".4"
            dur = n(rnd.uniform(1.2, 2.4))
            anim = (f'<animate attributeName="r" values="{rr};{rr + 3};{rr}" dur="{dur}s" repeatCount="indefinite"/>'
                    if col == C["red"] else "")
            out.append(f'<circle cx="{x}" cy="{y}" r="{rr}" fill="{col}" opacity="{op}">{anim}</circle>')
    out.append(f'<rect x="336" y="160" width="184" height="22" rx="11" fill="{C["ink"]}" stroke="{a}" stroke-opacity=".5"/>'
               + mtext(346, 175, "AI › high-risk zones flagged", 10, a))
    return "".join(out)


def il_tasks(a):
    T = 6.0
    tasks = ["plan sprint", "fix auth bug", "write tests", "ship v1.0"]
    out = [f'<rect x="40" y="52" width="290" height="128" rx="12" fill="{C["ink"]}" stroke="{C["line"]}"/>',
           mtext(56, 72, "TODAY", 11, C["dim"], ' class="mono b"')]
    for i, t in enumerate(tasks):
        y = 98 + i * 24
        tt = 0.6 + i * 1.0
        out.append(f'<rect x="56" y="{y - 13}" width="17" height="17" rx="4" stroke="{a}" stroke-width="2"/>')
        out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (tt, 1), (T - 0.4, 0)], T)}'
                   f'<rect x="56" y="{y - 13}" width="17" height="17" rx="4" fill="{a}"/>'
                   f'<path d="M60 {y - 5}l4 4 6-8" stroke="{C["ink"]}" stroke-width="2.5" fill="none"/></g>')
        out.append(mtext(86, y, t, 14, C["fg2"]))
        out.append(f'<path d="M84 {y - 5}H{86 + len(t) * 8.4 + 4}" stroke="{C["muted"]}" stroke-width="2" opacity="1">'
                   f'{discrete("opacity", [(0, 0), (tt + 0.15, 1), (T - 0.4, 0)], T)}</path>')
    out.append(f'<g transform="translate(420 92)"><g><animateTransform attributeName="transform" type="rotate" values="0;90" dur="3s" repeatCount="indefinite"/>'
               f'<path d="M0 -26Q4 -4 26 0Q4 4 0 26Q-4 4 -26 0Q-4 -4 0 -26Z" fill="{a}"/></g>'
               f'<circle r="38" stroke="{a}" stroke-opacity=".3" stroke-dasharray="3 6"/></g>')
    out.append(chip(356, 148, "AI PRIORITY: HIGH", a, 11, 8, 22)[0])
    out.append(f'<g transform="translate(508 96)"><g><animateTransform attributeName="transform" type="rotate" values="0 0 -12;16 0 -12;-14 0 -12;8 0 -12;0 0 -12;0 0 -12" keyTimes="0;.08;.16;.24;.32;1" dur="3s" repeatCount="indefinite"/>'
               f'<path d="M-11 6V-3a11 11 0 0 1 22 0V6l3 4H-14z" fill="{C["fg2"]}"/><circle cy="13" r="3.5" fill="{C["fg2"]}"/></g>'
               f'<circle cx="11" cy="-12" r="8" fill="{C["red"]}"/>{mtext(11, -8, "3", 11, C["ink"], " class=\"mono b\"", anchor="middle")}</g>')
    return "".join(out)


def il_vault(a):
    T = 6.0
    out = [f'<rect x="40" y="50" width="300" height="132" rx="10" fill="{C["bg"]}" stroke="{C["line"]}"/>',
           f'<circle cx="56" cy="63" r="4" fill="#ff5f57"/><circle cx="70" cy="63" r="4" fill="#febc2e"/><circle cx="84" cy="63" r="4" fill="#28c840"/>',
           mtext(56, 90, "$ vault unlock", 13, C["fg"])]
    out.append(mtext(56, 112, "password:", 13, C["muted"]))
    stars = "********"
    sx = 56 + 10 * 13 * CW
    ev = [(0, 0)] + typing(0.6, len(stars), 13 * CW, 0.12) + [(T - 0.3, 0)]
    out.append(f'<clipPath id="pw"><rect x="{n(sx)}" y="98" height="20" width="{n(len(stars) * 13 * CW)}">{discrete("width", ev, T)}</rect></clipPath>'
               f'<g clip-path="url(#pw)">{mtext(sx, 112, stars, 13, a)}</g>')
    ut = 0.6 + len(stars) * 0.12 + 0.3
    out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (ut, 1), (T - 0.3, 0)], T)}'
               + mtext(56, 134, "✓ vault unlocked", 13, C["green"], ' class="mono b"') + "</g>")
    x = 56
    for j, tag in enumerate(["#ideas", "#todo", "#secrets"]):
        c_, w = chip(x, 148, tag, [C["cyan"], C["violet"], C["orange"]][j], 11, 8, 22)
        out.append(f'<g opacity="1">{discrete("opacity", [(0, 0), (ut + 0.3 + j * 0.25, 1), (T - 0.3, 0)], T)}{c_}</g>')
        x += w + 8
    lift = [(0, "0 0"), (ut, "0 -14"), (T - 0.3, "0 0")]
    kts = ";".join("0" if t == 0 else f"{t / T:.4f}" for t, _ in lift)
    out.append(f'<g transform="translate(440 120)">'
               f'<g><animateTransform attributeName="transform" type="translate" calcMode="discrete" values="{";".join(v for _, v in lift)}" keyTimes="{kts}" dur="{T}s" repeatCount="indefinite"/>'
               f'<path d="M-24 -6V-30a24 24 0 0 1 48 0V-6" stroke="{C["fg2"]}" stroke-width="9" fill="none"/></g>'
               f'<rect x="-40" y="-12" width="80" height="64" rx="12" fill="{a}"/>'
               f'<circle cy="14" r="8" fill="{C["ink"]}"/><path d="M-3 16h6l2 16h-10z" fill="{C["ink"]}"/></g>')
    return "".join(out)


def il_cards(a):
    T = 4.0
    back = (f'<rect x="-42" y="-60" width="84" height="120" rx="10" fill="#2a1f3d" stroke="{C["violet"]}" stroke-width="2"/>'
            f'<rect x="-32" y="-50" width="64" height="100" rx="6" stroke="{C["violet"]}" stroke-opacity=".5" stroke-dasharray="4 4"/>'
            f'<path d="M0 -18L14 0L0 18L-14 0Z" fill="{C["violet"]}" opacity=".7"/>')
    front = (f'<rect x="-42" y="-60" width="84" height="120" rx="10" fill="{C["fg"]}" stroke="{a}" stroke-width="2"/>'
             f'<text class="sans b" x="-30" y="-36" font-size="18" fill="{a}">7</text>'
             f'<text class="sans b" x="30" y="52" font-size="18" fill="{a}" text-anchor="end">7</text>'
             f'<path d="M0 -24l7 15 16 2-12 11 3 16-14-8-14 8 3-16-12-11 16-2z" fill="{a}"/>')
    side = lambda x, rot: f'<g transform="translate({x} 100) rotate({rot})">{back}</g>'
    flip = (f'<g transform="translate(280 96)"><g>'
            f'<animateTransform attributeName="transform" type="scale" values="1 1;1 1;0.02 1;1 1;1 1;0.02 1;1 1" keyTimes="0;.3;.4;.5;.8;.9;1" dur="{T}s" repeatCount="indefinite"/>'
            f'<g>{discrete("opacity", [(0, 1), (0.4 * T, 0), (0.9 * T, 1)], T)}{back}</g>'
            f'<g opacity="0">{discrete("opacity", [(0, 0), (0.4 * T, 1), (0.9 * T, 0)], T)}{front}</g>'
            f'</g></g>')
    chain = []
    for i in range(3):
        x = 412 + i * 40
        chain.append(f'<rect x="{x}" y="150" width="26" height="22" rx="5" fill="{C["ink"]}" stroke="{a}">'
                     f'<animate attributeName="fill" values="{C["ink"]};{a};{C["ink"]}" dur="1.8s" begin="{i * 0.3}s" repeatCount="indefinite"/></rect>')
        if i:
            chain.append(f'<path d="M{x - 14} 161h14" stroke="{a}" stroke-width="2"/>')
    spark = "".join(f'<path class="tw" style="animation-delay:{d}s" d="M{x} {y - 7}v14M{x - 7} {y}h14" stroke="{C["yellow"]}" stroke-width="2.5"/>'
                    for x, y, d in [(196, 46, 0), (366, 58, .7), (350, 156, 1.4), (206, 160, 1.9)])
    return (side(214, -14) + side(346, 14) + flip + spark + "".join(chain)
            + mtext(412, 142, "FLARE COSTON2", 10, C["dim"]))


ILLUSTRATIONS = {"hand": il_hand, "chart": il_chart, "road": il_road, "tasks": il_tasks, "vault": il_vault, "cards": il_cards}


def build_quests():
    W, H = 560, 340
    for i, (fname, title, desc, loot, accent, kind) in enumerate(PROJECTS):
        a = C[accent]
        defs = f"""<pattern id="g" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1.5" cy="1.5" r="1" fill="{C['line']}"/></pattern>
<radialGradient id="glo" cx=".5" cy=".55" r=".6"><stop offset="0" stop-color="{a}" stop-opacity=".22"/><stop offset="1" stop-color="{a}" stop-opacity="0"/></radialGradient>
<clipPath id="ia"><rect x="12" y="12" width="{W - 24}" height="178" rx="12"/></clipPath>"""
        style = css(".tw{animation:tw 2.4s ease-in-out infinite;transform-box:fill-box;transform-origin:center}"
                    "@keyframes tw{0%,100%{opacity:.15;transform:scale(.6)}50%{opacity:1;transform:scale(1)}}")
        qlabel = f"QUEST {i + 1:02d}"
        ql, qw = chip(24, 22, qlabel, C["fg2"], 11, 9, 22)
        cl_text = "✓ CLEARED"
        cl, cw_ = chip(W - 24 - (len(cl_text) * 11 * CW + 18), 22, cl_text, C["green"], 11, 9, 22)
        x, chips = 70, []
        for item in loot:
            c_, w = chip(x, 296, item, a, 13, 10, 26)
            chips.append(c_)
            x += w + 8
        body = f"""<rect x=".75" y=".75" width="{W - 1.5}" height="{H - 1.5}" rx="18" fill="{C['panel']}" stroke="{C['line']}" stroke-width="1.5"/>
<g clip-path="url(#ia)"><rect x="12" y="12" width="{W - 24}" height="178" fill="{C['ink']}"/><rect x="12" y="12" width="{W - 24}" height="178" fill="url(#g)"/>
<rect x="12" y="12" width="{W - 24}" height="178" fill="url(#glo)"/>{ILLUSTRATIONS[kind](a)}</g>
<rect x="12" y="12" width="{W - 24}" height="178" rx="12" stroke="{C['line']}"/>
{ql}{cl}
<rect x="24" y="214" width="4" height="26" rx="2" fill="{a}"/>
<text class="sans b" x="38" y="235" font-size="25" fill="{C['fg']}">{esc(title)}</text>
<circle cx="{W - 38}" cy="227" r="16" stroke="{C['line']}" stroke-width="1.5"/>
<path d="M{W - 44} {233}l12-12M{W - 41} 221h9v9" stroke="{a}" stroke-width="2.2" stroke-linecap="round" fill="none"/>
<text class="sans" x="24" y="263" font-size="16" fill="{C['muted']}">{esc(desc[0])}</text>
<text class="sans" x="24" y="284" font-size="16" fill="{C['muted']}">{esc(desc[1])}</text>
{mtext(24, 314, "LOOT", 12, C['dim'], ' class="mono b"')}
{"".join(chips)}"""
        save(f"quests/{fname}.svg", svg(W, H, f"Quest {i + 1:02d}: {title} - {' '.join(desc)}", defs, style, body))


# ════════════════════════════════════════════════════════════════════════════
# CLASSIFIED FILE (decrypts itself)
# ════════════════════════════════════════════════════════════════════════════


def build_classified():
    W, fs, lh = 1200, 21, 36
    cw = fs * CW
    top = 106
    H = top + (len(CLASSIFIED) - 1) * lh + 46
    T, frames, fdur = 14.0, 9, 0.07
    rnd = random.Random(42)
    glyphs = "!<>-_\\/[]{}=+*^?#01$%&"
    body = []
    for i, (line, col) in enumerate(CLASSIFIED):
        y = top + i * lh
        t0 = 0.5 + i * 0.55
        for f in range(frames + 1):
            if f < frames:
                k = int(len(line) * f / frames)
                txt = line[:k] + "".join(c if c == " " else rnd.choice(glyphs) for c in line[k:])
                color = C["green"] if f % 2 else C["dim"]
                ev = [(0, 0), (t0 + f * fdur, 1), (t0 + (f + 1) * fdur, 0)]
                base = 0
            else:
                txt, color = line, C[col]
                ev = [(0, 0), (t0 + f * fdur, 1), (T - 0.6, 0)]
                base = 1
            body.append(f'<g opacity="{base}">{discrete("opacity", ev, T)}{mtext(40, y, txt, fs, color)}</g>')
    defs = f"""<clipPath id="cf"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<pattern id="sl" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1.2" fill="#000" opacity=".35"/></pattern>"""
    stamp_d, sw = ppath("TOP SECRET", 0, 0, 4)
    body_s = f"""<g clip-path="url(#cf)">
<rect width="{W}" height="{H}" fill="#0a0f0a"/>
<rect width="{W}" height="50" fill="#101a10"/><path d="M0 50H{W}" stroke="#1f3a1f"/>
{mtext(40, 31, "~/secret/classified.txt", 14, C['green'])}
{mtext(W - 40, 31, "AES-256 → DECRYPTING", 14, C['green'], ' class="mono blink"', anchor="end")}
{"".join(body)}
<g transform="translate({W - 330} {H - 110}) rotate(-12)" opacity=".85">
<rect x="-14" y="-14" width="{n(sw + 28)}" height="56" rx="6" stroke="{C['red']}" stroke-width="4"/>
<path d="{stamp_d}" fill="{C['red']}"/></g>
<rect width="{W}" height="{H}" fill="url(#sl)"/>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="15.5" stroke="#1f3a1f"/>"""
    save("classified.svg", svg(W, H, "Classified file: " + " / ".join(l for l, _ in CLASSIFIED[2:]), defs, "", body_s))


# ════════════════════════════════════════════════════════════════════════════
# NOW PLAYING
# ════════════════════════════════════════════════════════════════════════════


def build_now_playing():
    W, H = 1200, 250
    np_ = NOW_PLAYING
    cx, cy, r = 140, 125, 96
    grooves = "".join(f'<circle cx="{cx}" cy="{cy}" r="{rr}" stroke="#1f2433" stroke-width="1"/>' for rr in range(44, 94, 6))
    defs = f"""<linearGradient id="npbg" x1="0" x2="1"><stop offset="0" stop-color="#141a2b"/><stop offset="1" stop-color="{C['bg']}"/></linearGradient>
<linearGradient id="lab" x1="0" x2="1" y1="0" y2="1"><stop offset="0" stop-color="{C['orange']}"/><stop offset="1" stop-color="{C['red']}"/></linearGradient>
<linearGradient id="prog" x1="0" x2="1"><stop offset="0" stop-color="{C['cyan']}"/><stop offset="1" stop-color="{C['violet']}"/></linearGradient>
<clipPath id="npc"><rect width="{W}" height="{H}" rx="20"/></clipPath>"""
    style = css(f"""
.spin{{animation:spin 3.2s linear infinite;transform-origin:{cx}px {cy}px}}
@keyframes spin{{to{{transform:rotate(360deg)}}}}
.eq{{animation:eq .9s ease-in-out infinite alternate;transform-box:fill-box;transform-origin:bottom}}
@keyframes eq{{from{{transform:scaleY(.25)}}to{{transform:scaleY(1)}}}}
.beat{{animation:beat 1.2s ease-in-out infinite;transform-box:fill-box;transform-origin:center}}
@keyframes beat{{0%,100%{{transform:scale(1)}}15%{{transform:scale(1.25)}}30%{{transform:scale(1)}}}}
.pg{{animation:pg 40s linear infinite}}
@keyframes pg{{from{{transform:scaleX(.02)}}to{{transform:scaleX(1)}}}}
.kn{{animation:kn 40s linear infinite}}
@keyframes kn{{from{{transform:translateX(0)}}to{{transform:translateX(560px)}}}}
""")
    eq = "".join(f'<rect class="eq" style="animation-delay:-{d}s" x="{270 + k * 7}" y="40" width="4" height="18" rx="1.5" fill="{C["green"]}"/>'
                 for k, d in enumerate([0.1, 0.5, 0.3, 0.8, 0.2]))
    nexts = "".join(mtext(930, 92 + j * 24, f"0{j + 1}  {t}", 14, C["fg2"] if j == 0 else C["muted"]) for j, t in enumerate(np_["up_next"]))
    body = f"""<g clip-path="url(#npc)">
<rect width="{W}" height="{H}" fill="url(#npbg)"/>
<g class="spin"><circle cx="{cx}" cy="{cy}" r="{r}" fill="#0a0c12"/>{grooves}
<circle cx="{cx}" cy="{cy}" r="34" fill="url(#lab)"/>
<path d="{ppath('PS', cx - 13, cy - 10, 3, 0)[0]}" fill="{C['ink']}"/>
<circle cx="{cx}" cy="{cy}" r="4" fill="{C['bg']}"/></g>
<path d="M{cx - 70} {cy - 50}A86 86 0 0 1 {cx + 10} {cy - 86}" stroke="#fff" stroke-opacity=".08" stroke-width="18" fill="none"/>
<g><path d="M238 30V120l-20 24" stroke="{C['fg2']}" stroke-width="5" stroke-linecap="round" fill="none"/>
<circle cx="238" cy="30" r="10" fill="{C['panel2']}" stroke="{C['fg2']}" stroke-width="3"/><rect x="208" y="138" width="18" height="12" rx="2" fill="{C['fg2']}" transform="rotate(-50 217 144)"/></g>
{eq}
{mtext(312, 56, "NOW PLAYING", 14, C['green'], ' class="mono b" letter-spacing="2"')}
<text class="sans b" x="268" y="108" font-size="38" fill="{C['fg']}">{esc(np_['title'])}</text>
<text class="sans" x="270" y="142" font-size="18" fill="{C['muted']}">{esc(np_['artist'])}</text>
<rect x="270" y="176" width="570" height="6" rx="3" fill="{C['line']}"/>
<rect class="pg" x="270" y="176" width="570" height="6" rx="3" fill="url(#prog)" style="transform-origin:270px 179px"/>
<circle class="kn" cx="275" cy="179" r="8" fill="{C['fg']}"/>
{mtext(270, 212, "on repeat", 13, C['dim'])}
{mtext(840, 212, "∞", 15, C['dim'], anchor="end")}
{mtext(930, 64, "UP NEXT", 12, C['dim'], ' class="mono b" letter-spacing="2"')}
{nexts}
<g transform="translate(0 190)">
<path d="M946 0V18M966 0l-16 9 16 9z" fill="{C['fg2']}" stroke="{C['fg2']}" stroke-width="2" stroke-linejoin="round"/>
<circle cx="1010" cy="9" r="22" fill="{C['fg']}"/><rect x="1002" y="0" width="5" height="18" rx="1" fill="{C['bg']}"/><rect x="1013" y="0" width="5" height="18" rx="1" fill="{C['bg']}"/>
<path d="M1074 0V18M1054 0l16 9-16 9z" fill="{C['fg2']}" stroke="{C['fg2']}" stroke-width="2" stroke-linejoin="round"/>
<path class="beat" d="M1130 18l-11-10a6.5 6.5 0 0 1 11-7 6.5 6.5 0 0 1 11 7z" fill="{C['red']}"/>
</g>
</g>
<rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="19.5" stroke="{C['line']}"/>"""
    save("now-playing.svg", svg(W, H, f"Now playing: {np_['title']} - {np_['artist']}", defs, style, body))


if __name__ == "__main__":
    print("building assets ->", ASSETS)
    build_hero()
    build_ticker()
    build_achievement()
    build_headers()
    build_terminal()
    build_character()
    build_quests()
    build_classified()
    build_now_playing()
