#!/usr/bin/env python3
"""Renders assets/contribution-skyline.svg: the last year of contributions as
an isometric 3D skyline, with a light wave + comet sweeping across it and
streak stats alongside. Styled to match the mission-control panel.

Env: GITHUB_TOKEN (required), GH_LOGIN (default: aswin-kevin). Stdlib only.
"""
import json
import math
import os
import re
import urllib.request
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

LOGIN = os.environ.get("GH_LOGIN", "aswin-kevin")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(__file__).resolve().parent.parent / "assets" / "contribution-skyline.svg"

W, H = 1200, 420
U = (14.8, 2.4)   # screen vector for +1 week
V = (-9.0, 7.0)   # screen vector for +1 weekday
K = 0.78          # bar footprint (rest is gap)
ORIGIN = (352, 170)
MAX_H = 78
WAVE_STEP = 0.07  # seconds between columns in the light wave
DUR = 7.0

# top / left-face / right-face colours per level
LEVEL_COLORS = [
    ("#1c2330", "#151b24", "#11161e"),
    ("#1a4b8c", "#123563", "#0e2a4f"),
    ("#1f6feb", "#164fa8", "#113e85"),
    ("#58a6ff", "#3b7fd1", "#2f68ad"),
    ("#a5d6ff", "#73b4f0", "#5a98d6"),
]
LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}
"""


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "cosmos-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors") or not (body.get("data") or {}).get("user"):
        raise SystemExit(f"GraphQL error for user {LOGIN!r}: {body.get('errors')}")
    return body["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def stats(days):
    """days: list of (date, count) sorted ascending."""
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    # current streak may end today or yesterday (today might not have activity yet)
    current = 0
    seq = list(days)
    if seq and seq[-1][1] == 0:
        seq = seq[:-1]
    for _, n in reversed(seq):
        if not n:
            break
        current += 1
    best_day, best = max(days, key=lambda d: d[1]) if days else (None, 0)
    by_wd = Counter()
    for d, n in days:
        by_wd[d.strftime("%A")] += n
    busiest = by_wd.most_common(1)[0][0] if any(by_wd.values()) else "—"
    return current, longest, best, best_day, busiest


def pt(c, r, h=0.0):
    return ORIGIN[0] + c * U[0] + r * V[0], ORIGIN[1] + c * U[1] + r * V[1] - h


def poly(points, fill):
    d = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    return f'<polygon points="{d}" fill="{fill}"/>'


def render(cal):
    weeks = cal["weeks"]
    cells, days = [], []
    for c, w in enumerate(weeks):
        for d in w["contributionDays"]:
            n = d["contributionCount"]
            cells.append((c, d["weekday"], n, LEVELS.index(d["contributionLevel"]), d["date"]))
            days.append((date.fromisoformat(d["date"]), n))
    days.sort()
    peak = max((x[2] for x in cells), default=0) or 1
    current, longest, best, best_day, busiest = stats(days)

    # painter's order: back rows first, then left to right
    bars = []
    for c, r, n, lvl, _ in sorted(cells, key=lambda x: (x[1], x[0])):
        h = 2.0 if n == 0 else 5 + math.sqrt(n / peak) * MAX_H
        top_c, left_c, right_c = LEVEL_COLORS[lvl]
        a, b = pt(c, r), pt(c + K, r)
        cc, d = pt(c + K, r + K), pt(c, r + K)
        lift = lambda p: (p[0], p[1] - h)
        g = [
            poly([d, cc, lift(cc), lift(d)], left_c),     # front face (faces +row)
            poly([b, cc, lift(cc), lift(b)], right_c),    # side face (faces +week)
            poly([lift(a), lift(b), lift(cc), lift(d)], top_c),
        ]
        if n:
            begin = c * WAVE_STEP
            top = " ".join(f"{x:.1f},{y:.1f}" for x, y in (lift(a), lift(b), lift(cc), lift(d)))
            g.append(
                f'<polygon points="{top}" fill="#ffffff" opacity="0">'
                f'<animate attributeName="opacity" values="0;.75;0;0" keyTimes="0;.04;.14;1" '
                f'dur="{DUR}s" begin="{begin:.2f}s" repeatCount="indefinite"/></polygon>'
            )
        bars.append("".join(g))

    # month labels along the front edge
    months, seen = [], set()
    for c, w in enumerate(weeks):
        first = date.fromisoformat(w["contributionDays"][0]["date"])
        key = (first.year, first.month)
        if first.day <= 7 and key not in seen and 0 < c < len(weeks) - 1:
            seen.add(key)
            x, y = pt(c, 7.6)
            months.append(f'<text x="{x:.1f}" y="{y + 12:.1f}" class="mon">{first.strftime("%b").upper()}</text>')

    # comet path: above the skyline, travelling with the wave
    n_cols = len(weeks)
    sx, sy = pt(-1, 3, MAX_H + 40)
    ex, ey = pt(n_cols + 1, 3, MAX_H + 40)
    travel = (n_cols + 2) * WAVE_STEP / DUR

    def stat(y, label, value, sub):
        return (f'<text x="44" y="{y}" class="lbl">{label}</text>'
                f'<text x="44" y="{y + 30}" class="val">{value}</text>'
                f'<text x="44" y="{y + 48}" class="sub">{sub}</text>')

    best_sub = best_day.strftime("%b %d, %Y").upper() if best_day and best else "—"
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    total = cal["totalContributions"]

    legend_x = 1000
    legend = "".join(
        f'<rect x="{legend_x + 40 + i * 16}" y="374" width="11" height="11" rx="2.5" fill="{LEVEL_COLORS[i][0]}"/>'
        for i in range(5)
    )

    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{LOGIN}: {total} contributions in the last year, current streak {current} days, longest streak {longest} days">
<style>
  .hdr {{ font: 700 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #e6edf3; letter-spacing: 3px; }}
  .meta {{ font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 1.5px; }}
  .lbl {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 2px; }}
  .val {{ font: 700 28px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
  .unit {{ font: 600 14px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #8b949e; }}
  .sub {{ font: 500 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #58a6ff; letter-spacing: 1.2px; }}
  .mon {{ font: 600 9.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #6e7681; letter-spacing: 1px; }}
  .leg {{ font: 500 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #6e7681; letter-spacing: 1px; }}
  .dot {{ animation: blink 1.4s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: .2 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#0b1626"/></linearGradient>
  <radialGradient id="floor" cx=".5" cy=".5" r=".5"><stop offset="0" stop-color="#1f6feb" stop-opacity=".16"/><stop offset="1" stop-color="#1f6feb" stop-opacity="0"/></radialGradient>
  <linearGradient id="tail" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset="1" stop-color="#9ccfff" stop-opacity=".9"/></linearGradient>
  <radialGradient id="halo"><stop offset="0" stop-color="#9ccfff" stop-opacity=".6"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{W - 2}" height="{H - 2}" rx="17" fill="none" stroke="#30363d"/>

<circle cx="40" cy="42" r="5" fill="#3fb950" class="dot"/>
<text x="54" y="47" class="hdr">CONTRIBUTION SKYLINE</text>
<text x="1160" y="47" class="meta" text-anchor="end">LAST 12 MONTHS · UPDATED {stamp}</text>
<line x1="265" y1="80" x2="265" y2="384" stroke="#30363d" stroke-dasharray="2 4"/>

{stat(98, "TOTAL", f"{total:,}", "CONTRIBUTIONS")}
{stat(170, "CURRENT STREAK", f'{current}<tspan class="unit"> days</tspan>', "AND COUNTING" if current else "TIME TO SHIP")}
{stat(242, "LONGEST STREAK", f'{longest}<tspan class="unit"> days</tspan>', "PERSONAL BEST")}
{stat(314, "BEST DAY", f'{best}<tspan class="unit"> contributions</tspan>' if best else "—", best_sub)}

<ellipse cx="{pt(n_cols / 2, 3.5)[0]:.0f}" cy="{pt(n_cols / 2, 3.5)[1]:.0f}" rx="470" ry="120" fill="url(#floor)"/>
{"".join(bars)}
{"".join(months)}

<g opacity="0">
  <animate attributeName="opacity" dur="{DUR}s" repeatCount="indefinite" keyTimes="0;.03;{travel - .03:.3f};{travel:.3f};1" values="0;1;1;0;0"/>
  <g>
    <animateMotion dur="{DUR}s" repeatCount="indefinite" rotate="auto" calcMode="linear" keyPoints="0;1;1" keyTimes="0;{travel:.3f};1" path="M {sx:.1f} {sy:.1f} L {ex:.1f} {ey:.1f}"/>
    <path d="M -60 0 L -5 -2.6 L 0 0 L -5 2.6 Z" fill="url(#tail)"/>
    <circle r="12" fill="url(#halo)"/>
    <circle r="3.6" fill="#f0f6fc"/>
  </g>
</g>

<text x="{legend_x}" y="384" class="leg">LESS</text>
{legend}
<text x="{legend_x + 126}" y="384" class="leg">MORE</text>
<text x="290" y="384" class="leg">BUSIEST DAY · {busiest.upper()}</text>
</svg>
'''


if __name__ == "__main__":
    new = render(fetch())
    # Skip rewriting when only the "UPDATED" date changed, to avoid daily churn commits.
    strip = lambda t: re.sub(r"UPDATED \d{4}-\d{2}-\d{2}", "", t)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if strip(old) == strip(new):
        print("skyline unchanged")
    else:
        OUT.write_text(new, encoding="utf-8")
        print("wrote", OUT)
