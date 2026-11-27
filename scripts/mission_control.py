#!/usr/bin/env python3
"""Renders assets/mission-control.svg — GitHub stats as a spacecraft HUD,
with top languages drawn as planets orbiting a star.

Env: GITHUB_TOKEN (required), GH_LOGIN (default: aswin-kevin)
Stdlib only, so the workflow needs no pip install.
"""
import json
import math
import os
import re
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

LOGIN = os.environ.get("GH_LOGIN", "aswin-kevin")
TOKEN = os.environ["GITHUB_TOKEN"]
OUT = Path(__file__).resolve().parent.parent / "assets" / "mission-control.svg"

QUERY = """
query($login: String!, $after: String) {
  user(login: $login) {
    createdAt
    followers { totalCount }
    pullRequests { totalCount }
    issues { totalCount }
    contributionsCollection {
      totalCommitContributions
      contributionCalendar { totalContributions }
    }
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100, after: $after,
                 orderBy: {field: STARGAZERS, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        stargazerCount
        forkCount
        languages(first: 10, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def query(after=None):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN, "after": after}}).encode(),
        headers={"Authorization": f"bearer {TOKEN}", "User-Agent": "cosmos-readme"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        body = json.load(r)
    if body.get("errors") or not (body.get("data") or {}).get("user"):
        raise SystemExit(f"GraphQL error for user {LOGIN!r}: {body.get('errors')}")
    return body["data"]["user"]


def fetch():
    user = query()
    repos = user["repositories"]
    while repos["pageInfo"]["hasNextPage"]:  # accounts with >100 repos
        nxt = query(repos["pageInfo"]["endCursor"])["repositories"]
        repos["nodes"].extend(nxt["nodes"])
        repos["pageInfo"] = nxt["pageInfo"]
    return user


def fmt(n):
    return f"{n/1000:.1f}k" if n >= 10000 else f"{n:,}"


def render(u):
    repos = u["repositories"]["nodes"]
    stars = sum(r["stargazerCount"] for r in repos)
    forks = sum(r["forkCount"] for r in repos)
    cc = u["contributionsCollection"]
    langs = {}
    colors = {}
    for r in repos:
        for e in r["languages"]["edges"]:
            n = e["node"]["name"]
            langs[n] = langs.get(n, 0) + e["size"]
            colors[n] = e["node"]["color"] or "#8b949e"
    total = sum(langs.values()) or 1
    top = [kv for kv in sorted(langs.items(), key=lambda kv: -kv[1]) if kv[1] / total >= 0.001][:6]
    created = datetime.fromisoformat(u["createdAt"].replace("Z", "+00:00"))
    now = datetime.now(timezone.utc)
    years = (now - created).days / 365.25

    stats = [
        ("★", "STARS COLLECTED", fmt(stars)),
        ("⌁", "CONTRIBUTIONS · 1Y", fmt(cc["contributionCalendar"]["totalContributions"])),
        ("◆", "COMMITS · 1Y", fmt(cc["totalCommitContributions"])),
        ("⇄", "PULL REQUESTS", fmt(u["pullRequests"]["totalCount"])),
        ("!", "ISSUES OPENED", fmt(u["issues"]["totalCount"])),
        ("◎", "PUBLIC REPOS", fmt(u["repositories"]["totalCount"])),
        ("⑂", "FORKS", fmt(forks)),
        ("☄", "FOLLOWERS", fmt(u["followers"]["totalCount"])),
    ]

    W, H = 1200, 380
    rows = []
    for i, (icon, label, val) in enumerate(stats):
        col, row = divmod(i, 4)
        x, y = 50 + col * 290, 118 + row * 58
        rows.append(f'''
  <g class="row" style="animation-delay:{i*0.12:.2f}s">
    <text x="{x}" y="{y}" class="icon">{escape(icon)}</text>
    <text x="{x+28}" y="{y-14}" class="lbl">{label}</text>
    <text x="{x+28}" y="{y+10}" class="val">{val}</text>
    <line x1="{x+28}" y1="{y+20}" x2="{x+250}" y2="{y+20}" class="rule"/>
  </g>''')

    # language orbits
    cx, cy = 870, 205
    orbits, legend = [], []
    for i, (name, size) in enumerate(top):
        rx, ry = 42 + i * 20, 16 + i * 8
        pct = size / total * 100
        r = 3.5 + min(8, pct / 7)
        dur = 9 + i * 5
        c = colors[name]
        start = i * 57 % 360
        a = math.radians(start)
        sx, sy = rx * math.cos(a), ry * math.sin(a)
        orbits.append(
            f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry:.1f}" class="orbit"/>'
            f'<circle r="{r:.1f}" fill="{c}" filter="url(#pglow)">'
            f'<animateMotion dur="{dur}s" repeatCount="indefinite" '
            f'path="M {cx+sx:.1f} {cy+sy:.1f} A {rx} {ry:.1f} 0 1 1 {cx-sx:.1f} {cy-sy:.1f} A {rx} {ry:.1f} 0 1 1 {cx+sx:.1f} {cy+sy:.1f}"/>'
            f'</circle>'
        )
        ly = 112 + i * 34
        legend.append(
            f'<circle cx="1032" cy="{ly-4}" r="5" fill="{c}"/>'
            f'<text x="1044" y="{ly}" class="lang">{escape(name)}</text>'
            f'<text x="1044" y="{ly+14}" class="pct">{pct:.1f}%</text>'
        )
    if not top:
        legend.append('<text x="1032" y="120" class="pct">no data yet</text>')

    stamp = now.strftime("%Y-%m-%d %H:%M UTC")
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Mission control: GitHub stats for {LOGIN}">
<style>
  .hdr {{ font: 700 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #e6edf3; letter-spacing: 3px; }}
  .meta {{ font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 1.5px; }}
  .lbl {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 2px; }}
  .val {{ font: 700 24px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
  .icon {{ font: 700 20px 'Segoe UI Symbol', 'Apple Symbols', sans-serif; fill: #58a6ff; }}
  .lang {{ font: 600 13px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
  .pct {{ font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #94a3b8; }}
  .rule {{ stroke: #30363d; stroke-opacity: 1; stroke-dasharray: 2 4; }}
  .orbit {{ fill: none; stroke: #8b949e; stroke-opacity: .25; }}
  .row {{ animation: boot .6s ease-out backwards; }}
  @keyframes boot {{ from {{ transform: translateX(-12px) }} to {{ transform: none }} }}
  .sweep {{ transform-origin: {cx}px {cy}px; animation: spin 6s linear infinite; }}
  @keyframes spin {{ to {{ transform: rotate(360deg) }} }}
  .dot {{ animation: blink 1.4s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: .2 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#0b1626"/></linearGradient>
  <radialGradient id="star"><stop offset="0" stop-color="#fffbea"/><stop offset=".4" stop-color="#fbbf24"/><stop offset="1" stop-color="#f97316" stop-opacity="0"/></radialGradient>
  <linearGradient id="beam" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset="1" stop-color="#58a6ff" stop-opacity=".3"/></linearGradient>
  <filter id="pglow" x="-100%" y="-100%" width="300%" height="300%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="#30363d"/>
<line x1="640" y1="70" x2="640" y2="345" class="rule"/>

<circle cx="40" cy="42" r="5" fill="#22c55e" class="dot"/>
<text x="54" y="47" class="hdr">MISSION CONTROL · TELEMETRY</text>
<text x="1160" y="47" class="meta" text-anchor="end">LAST SYNC {stamp} · {years:.1f} YEARS IN ORBIT</text>
{"".join(rows)}

<text x="680" y="100" class="lbl">LANGUAGE ORBITS</text>
<path class="sweep" d="M {cx} {cy} L {cx+150} {cy-24} A 152 152 0 0 1 {cx+150} {cy+24} Z" fill="url(#beam)" opacity=".5"/>
{"".join(orbits)}
<circle cx="{cx}" cy="{cy}" r="26" fill="url(#star)"/>
<circle cx="{cx}" cy="{cy}" r="9" fill="#fffbea"/>
{"".join(legend)}
</svg>
'''


if __name__ == "__main__":
    OUT.parent.mkdir(exist_ok=True)
    new = render(fetch())
    # Only rewrite when something other than the sync timestamp changed,
    # so the daily job doesn't create a commit just to bump the clock.
    strip = lambda s: re.sub(r"LAST SYNC [^·]*·", "", s)
    old = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
    if strip(old) == strip(new):
        print("telemetry unchanged")
    else:
        OUT.write_text(new, encoding="utf-8")
        print("wrote", OUT)
