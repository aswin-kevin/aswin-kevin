#!/usr/bin/env python3
"""Generates the static animated SVGs (header + footer) in assets/.

Run once after tweaking:  python3 scripts/generate_cosmos.py
Deterministic (seeded) so re-runs produce identical output.
"""
import math
import random
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
ASSETS.mkdir(exist_ok=True)

STAR_COLORS = ["#ffffff", "#ffffff", "#ffffff", "#cfe8ff", "#ffe9c4", "#dbeafe"]


def starfield(rng, w, h, n, rmin, rmax, cls="tw"):
    out = []
    for _ in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.uniform(rmin, rmax)
        delay, dur = rng.uniform(0, 6), rng.uniform(2.5, 7)
        c = rng.choice(STAR_COLORS)
        out.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" fill="{c}" class="{cls}" '
            f'style="animation-delay:-{delay:.2f}s;animation-duration:{dur:.2f}s"/>'
        )
    return "\n".join(out)


def lerp_color(a, b, t):
    a = [int(a[i : i + 2], 16) for i in (1, 3, 5)]
    b = [int(b[i : i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(x + (y - x) * t):02x}" for x, y in zip(a, b))


def galaxy(rng, arms=2, n=320, rmax=165):
    pts = []
    for k in range(arms):
        for i in range(n):
            t = i / n
            theta = t * 3.4 * math.pi + k * (2 * math.pi / arms)
            r = 6 + t * rmax
            spread = 4 + t * 16
            x = r * math.cos(theta) + rng.gauss(0, spread)
            y = r * math.sin(theta) + rng.gauss(0, spread)
            size = max(0.4, 2.2 - t * 1.7 + rng.uniform(-0.3, 0.3))
            if t < 0.45:
                c = lerp_color("#fff8e7", "#cbd5e1", t / 0.45)
            else:
                c = lerp_color("#cbd5e1", "#60a5fa", (t - 0.45) / 0.55)
            op = max(0.25, 1 - t * 0.6)
            pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.2f}" fill="{c}" opacity="{op:.2f}"/>')
    # halo dust
    for _ in range(140):
        a = rng.uniform(0, 2 * math.pi)
        r = abs(rng.gauss(0, 70))
        pts.append(
            f'<circle cx="{r*math.cos(a):.1f}" cy="{r*math.sin(a):.1f}" r="{rng.uniform(0.3,1.1):.2f}" '
            f'fill="#dbeafe" opacity="{rng.uniform(0.2,0.7):.2f}"/>'
        )
    return "\n".join(pts)


def header():
    rng = random.Random(42)
    W, H = 1200, 420
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Aswin Venkat — animated cosmos banner">
<style>
  .tw {{ animation-name: twinkle; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .15 }} 50% {{ opacity: 1 }} }}
  .shoot {{ animation: shoot 9s linear infinite; opacity: 0; }}
  @keyframes shoot {{
    0%   {{ transform: translate(0,0); opacity: 0 }}
    1%   {{ opacity: 1 }}
    9%   {{ transform: translate(620px,240px); opacity: 0 }}
    100% {{ transform: translate(620px,240px); opacity: 0 }}
  }}
  .s2 {{ animation-delay: 3.7s; animation-duration: 11s }}
  .s3 {{ animation-delay: 7.1s; animation-duration: 13s }}
  .neb {{ animation: drift 18s ease-in-out infinite alternate; }}
  .neb2 {{ animation: drift 24s ease-in-out infinite alternate-reverse; }}
  @keyframes drift {{ from {{ transform: translate(0,0) scale(1) }} to {{ transform: translate(30px,-12px) scale(1.08) }} }}
  .blink {{ animation: blink 1.1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity: 0 }} }}
  .hud {{ font: 600 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 2px; }}
  .title {{ font: 800 76px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; letter-spacing: 10px; }}
  .sub {{ font: 500 19px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #c9d1d9; letter-spacing: 1px; }}
</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#04060b"/>
    <stop offset=".55" stop-color="#0a1120"/>
    <stop offset="1" stop-color="#0f1b30"/>
  </linearGradient>
  <radialGradient id="nebA"><stop offset="0" stop-color="#1d4ed8" stop-opacity=".30"/><stop offset="1" stop-color="#1d4ed8" stop-opacity="0"/></radialGradient>
  <radialGradient id="nebB"><stop offset="0" stop-color="#0e7490" stop-opacity=".28"/><stop offset="1" stop-color="#0e7490" stop-opacity="0"/></radialGradient>
  <radialGradient id="nebC"><stop offset="0" stop-color="#334155" stop-opacity=".35"/><stop offset="1" stop-color="#334155" stop-opacity="0"/></radialGradient>
  <radialGradient id="core"><stop offset="0" stop-color="#fffbea"/><stop offset=".25" stop-color="#fde68a" stop-opacity=".8"/><stop offset="1" stop-color="#60a5fa" stop-opacity="0"/></radialGradient>
  <radialGradient id="planet" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#cbd5e1"/><stop offset=".45" stop-color="#3b5b8c"/><stop offset="1" stop-color="#0b1426"/>
  </radialGradient>
  <radialGradient id="moon" cx=".35" cy=".35"><stop offset="0" stop-color="#f8fafc"/><stop offset="1" stop-color="#64748b"/></radialGradient>
  <linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="#67e8f9" stop-opacity=".1"/><stop offset=".5" stop-color="#e0f2fe" stop-opacity=".9"/><stop offset="1" stop-color="#67e8f9" stop-opacity=".1"/></linearGradient>
  <linearGradient id="tail" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="txt" x1="0" x2="1" gradientUnits="objectBoundingBox">
    <stop offset="0" stop-color="#ffffff"/><stop offset=".35" stop-color="#e6edf3"/><stop offset=".65" stop-color="#9ccfff"/><stop offset="1" stop-color="#ffffff"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="3.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="soft"><feGaussianBlur stdDeviation="1.2"/></filter>
</defs>

<rect width="{W}" height="{H}" rx="18" fill="url(#sky)"/>
<g class="neb"><ellipse cx="300" cy="120" rx="320" ry="150" fill="url(#nebA)"/></g>
<g class="neb2"><ellipse cx="760" cy="330" rx="360" ry="140" fill="url(#nebB)"/></g>
<g class="neb"><ellipse cx="1020" cy="80" rx="260" ry="120" fill="url(#nebC)"/></g>

<g>{starfield(rng, W, H, 170, 0.3, 0.9)}</g>
<g>{starfield(rng, W, H, 45, 0.9, 1.7)}</g>

<!-- spiral galaxy -->
<g transform="translate(1015,185) rotate(-22) scale(1,0.42)">
  <ellipse rx="230" ry="230" fill="url(#core)" opacity=".35"/>
  <g filter="url(#soft)" opacity=".55">
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="140s" repeatCount="indefinite"/>
    {galaxy(random.Random(7))}
  </g>
  <g>
    <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="140s" repeatCount="indefinite"/>
    {galaxy(random.Random(7))}
  </g>
  <ellipse rx="34" ry="34" fill="url(#core)"/>
</g>

<!-- ringed planet with orbiting moon -->
<g transform="translate(150,318) rotate(-14)">
  <path d="M -98 0 A 98 19 0 0 1 98 0" fill="none" stroke="url(#ring)" stroke-width="5"/>
  <circle r="52" fill="url(#planet)"/>
  <path d="M -40 -14 Q 0 -6 40 -16" stroke="#e2e8f0" stroke-opacity=".25" stroke-width="5" fill="none"/>
  <path d="M -48 10 Q 0 20 46 8" stroke="#e2e8f0" stroke-opacity=".18" stroke-width="4" fill="none"/>
  <path d="M -98 0 A 98 19 0 0 0 98 0" fill="none" stroke="url(#ring)" stroke-width="5"/>
  <ellipse rx="150" ry="36" fill="none" stroke="#8b949e" stroke-opacity=".22" stroke-dasharray="3 6"/>
  <circle r="8" fill="url(#moon)">
    <animateMotion dur="14s" repeatCount="indefinite" path="M -150 0 A 150 36 0 0 0 150 0 A 150 36 0 0 0 -150 0"/>
    <animate attributeName="opacity" dur="14s" repeatCount="indefinite" keyTimes="0;0.68;0.70;0.80;0.82;1" values="1;1;0;0;1;1"/>
  </circle>
</g>

<!-- shooting stars -->
<g class="shoot"><line x1="80" y1="40" x2="200" y2="86" stroke="url(#tail)" stroke-width="2" stroke-linecap="round"/></g>
<g class="shoot s2"><line x1="420" y1="10" x2="530" y2="52" stroke="url(#tail)" stroke-width="1.6" stroke-linecap="round"/></g>
<g class="shoot s3"><line x1="240" y1="150" x2="330" y2="185" stroke="url(#tail)" stroke-width="1.3" stroke-linecap="round"/></g>

<!-- HUD -->
<text x="34" y="40" class="hud">◉ INCOMING TRANSMISSION</text>
<text x="34" y="60" class="hud" opacity=".6">RA 05h 35m 17s · DEC −05° 23′ 28″</text>
<text x="1166" y="400" class="hud" text-anchor="end" opacity=".7">AD ASTRA PER ASPERA</text>
<g stroke="#8b949e" stroke-opacity=".5" fill="none" stroke-width="1.5">
  <path d="M 14 34 V 14 H 34"/><path d="M 1186 34 V 14 H 1166"/>
  <path d="M 14 386 V 406 H 34"/><path d="M 1186 386 V 406 H 1166"/>
</g>

<!-- title -->
<text x="548" y="205" text-anchor="middle" class="title" fill="url(#txt)" filter="url(#glow)">ASWIN VENKAT</text>
<text x="548" y="252" text-anchor="middle" class="sub">AI Agents · Golang · Embedded Systems · Licensed Drone Pilot<tspan class="blink" fill="#58a6ff">▌</tspan></text>
<text x="548" y="118" text-anchor="middle" class="hud" fill="#58a6ff" style="fill:#58a6ff;letter-spacing:6px">BACKEND ENGINEER · CYBERSECURITY SAAS</text>
</svg>
'''
    (ASSETS / "cosmos-header.svg").write_text(svg, encoding="utf-8")


def footer():
    rng = random.Random(99)
    W, H = 1200, 220
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Planet horizon — thanks for visiting">
<style>
  .tw {{ animation-name: twinkle; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .15 }} 50% {{ opacity: 1 }} }}
  .atmo {{ animation: pulse 6s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .65 }} 50% {{ opacity: 1 }} }}
  .msg {{ font: 500 17px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #c9d1d9; letter-spacing: 2px; }}
</style>
<defs>
  <linearGradient id="fsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#04060b"/><stop offset="1" stop-color="#0a1120"/></linearGradient>
  <radialGradient id="atm" cx=".5" cy="1" r=".75"><stop offset=".72" stop-color="#22d3ee" stop-opacity=".0"/><stop offset=".86" stop-color="#22d3ee" stop-opacity=".55"/><stop offset=".93" stop-color="#1d4ed8" stop-opacity=".25"/><stop offset="1" stop-color="#1d4ed8" stop-opacity="0"/></radialGradient>
  <radialGradient id="earth" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#1e3a8a"/><stop offset=".4" stop-color="#0b1440"/><stop offset="1" stop-color="#04060b"/></radialGradient>
  <radialGradient id="sun"><stop offset="0" stop-color="#ffffff"/><stop offset=".2" stop-color="#fef3c7"/><stop offset="1" stop-color="#fef3c7" stop-opacity="0"/></radialGradient>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#fsky)"/>
<g>{starfield(rng, W, 150, 110, 0.3, 1.3)}</g>
<ellipse cx="600" cy="760" rx="1000" ry="640" fill="url(#atm)" class="atmo"/>
<filter id="haze" x="-10%" y="-10%" width="120%" height="120%"><feGaussianBlur stdDeviation="7"/></filter>
<ellipse cx="600" cy="760" rx="904" ry="604" fill="none" stroke="#38bdf8" stroke-width="10" filter="url(#haze)" class="atmo"/>
<ellipse cx="600" cy="760" rx="900" ry="600" fill="url(#earth)"/>
<ellipse cx="600" cy="760" rx="900" ry="600" fill="none" stroke="#a5f3fc" stroke-opacity=".7" stroke-width="1.5"/>
<ellipse cx="600" cy="160" rx="140" ry="24" fill="url(#sun)" opacity=".75" class="atmo"/>
<text x="600" y="70" text-anchor="middle" class="msg">THANKS FOR VISITING THIS CORNER OF THE UNIVERSE ✦</text>
</svg>
'''
    (ASSETS / "cosmos-footer.svg").write_text(svg, encoding="utf-8")


ICONS = {
    "shield": '<path d="M20 8 L30 12 V20 C30 26 25.5 30.5 20 32 C14.5 30.5 10 26 10 20 V12 Z"/><path d="M15.5 20 L19 23.5 L25 16.5"/>',
    "terminal": '<rect x="8" y="11" width="24" height="18" rx="3"/><path d="M12.5 17 L16 20 L12.5 23"/><path d="M18.5 23 H26"/>',
    "graph": '<path d="M20 11 L20 21 M20 21 L11 27 M20 21 L29 27 M11 27 L29 27"/>'
             '<circle cx="20" cy="11" r="2.8" fill="#0d1117"/><circle cx="20" cy="21" r="2.8" fill="#58a6ff"/>'
             '<circle cx="11" cy="27" r="2.8" fill="#0d1117"/><circle cx="29" cy="27" r="2.8" fill="#0d1117"/>',
    "drone": '<path d="M13 13 L27 27 M27 13 L13 27"/><rect x="16.5" y="16.5" width="7" height="7" rx="2" fill="#0d1117"/>'
             + "".join(
                 f'<ellipse cx="{x}" cy="{y}" rx="5" ry="1.3"><animateTransform attributeName="transform" type="rotate" '
                 f'from="0 {x} {y}" to="360 {x} {y}" dur="0.{4+i}s" repeatCount="indefinite"/></ellipse>'
                 for i, (x, y) in enumerate([(12, 12), (28, 12), (12, 28), (28, 28)])
             ),
}

CARDS = [
    ("shield", "NOW BUILDING", ["Cybersecurity SaaS", "backends"],
     ["Backend systems for attack", "surface & security platforms."],
     ["ASM", "THREAT INTEL", "SAST", "DAST", "CSPM"]),
    ("terminal", "WEAPON OF CHOICE", ["Go for scale.", "Python for the rest."],
     ["High-performance, scalable", "APIs and services."],
     ["GO", "PYTHON", "DEVOPS"]),
    ("graph", "ALL IN ON", ["Autonomous", "AI agents"],
     ["Automating operations that", "once took hours of effort."],
     ["LANGCHAIN", "LANGGRAPH", "DEEP AGENTS"]),
    ("drone", "OFF SCREEN", ["FPV freestyle", "drones"],
     ["Every component, wire and", "tune, built from scratch."],
     ["LICENSED PILOT", "FPV", "BUILDER"]),
]

TIMELINE = [
    ("Embedded", "COLLEGE · HARDWARE"),
    ("Mobile", "APPS"),
    ("Web", "PLATFORMS"),
    ("Backend", "SCALABLE SYSTEMS"),
    ("AI + Security", "NOW"),
]


def about():
    W, H = 1200, 590
    e = lambda t: t.replace("&", "&amp;")
    # timeline
    xs = [130 + i * 235 for i in range(len(TIMELINE))]
    ty = 165
    tl = [f'<line x1="{xs[0]}" y1="{ty}" x2="{xs[-1]}" y2="{ty}" stroke="#30363d" stroke-width="2"/>',
          f'<line x1="{xs[0]}" y1="{ty}" x2="{xs[-1]}" y2="{ty}" stroke="url(#prog)" stroke-width="2"/>',
          f'<circle r="3.5" fill="#9ccfff" filter="url(#g)"><animateMotion dur="5s" repeatCount="indefinite" path="M {xs[0]} {ty} H {xs[-1]}"/>'
          f'<animate attributeName="opacity" dur="5s" repeatCount="indefinite" values="0;1;1;0" keyTimes="0;.08;.9;1"/></circle>']
    for i, (x, (name, sub)) in enumerate(zip(xs, TIMELINE)):
        last = i == len(TIMELINE) - 1
        if last:
            tl.append(f'<circle cx="{x}" cy="{ty}" r="9" fill="none" stroke="#58a6ff"><animate attributeName="r" values="9;22" dur="2s" repeatCount="indefinite"/>'
                      f'<animate attributeName="opacity" values=".9;0" dur="2s" repeatCount="indefinite"/></circle>')
        tl.append(f'<circle cx="{x}" cy="{ty}" r="7" fill="{"#58a6ff" if last else "#0d1117"}" stroke="#58a6ff" stroke-width="2"/>')
        tl.append(f'<text x="{x}" y="{ty+36}" text-anchor="middle" class="tn{" now" if last else ""}">{e(name)}</text>')
        tl.append(f'<text x="{x}" y="{ty+54}" text-anchor="middle" class="ts">{e(sub)}</text>')
    # cards
    cards = []
    cw, chh, cy0 = 271, 290, 270
    for i, (icon, label, title, body, chips) in enumerate(CARDS):
        x = 40 + i * (cw + 12)
        g = [f'<g class="card" style="animation-delay:{0.15*i:.2f}s">',
             f'<rect x="{x}" y="{cy0}" width="{cw}" height="{chh}" rx="12" fill="#161b22" fill-opacity=".7" stroke="#30363d"/>',
             f'<rect x="{x}" y="{cy0}" width="{cw}" height="2" rx="1" fill="url(#topline)"/>',
             f'<g transform="translate({x+22},{cy0+22})"><rect width="40" height="40" rx="10" fill="#1f6feb" fill-opacity=".12" stroke="#1f6feb" stroke-opacity=".6"/>'
             f'<g fill="none" stroke="#58a6ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g></g>',
             f'<text x="{x+22}" y="{cy0+92}" class="cl">{label}</text>']
        for j, t in enumerate(title):
            g.append(f'<text x="{x+22}" y="{cy0+120+j*24}" class="ct">{e(t)}</text>')
        for j, t in enumerate(body):
            g.append(f'<text x="{x+22}" y="{cy0+186+j*19}" class="cb">{e(t)}</text>')
        # chips with wrapping
        cx, cyy, maxx = x + 22, cy0 + 236, x + cw - 18
        for c in chips:
            w = len(c) * 6.3 + 16
            if cx + w > maxx:
                cx, cyy = x + 22, cyy + 26
            g.append(f'<rect x="{cx:.1f}" y="{cyy}" width="{w:.1f}" height="20" rx="10" fill="#0d1117" stroke="#30363d"/>'
                     f'<text x="{cx + w/2:.1f}" y="{cyy+13.5}" text-anchor="middle" class="chip">{e(c)}</text>')
            cx += w + 6
        g.append("</g>")
        cards.append("".join(g))

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="About Aswin Venkat">
<style>
  .hdr {{ font: 700 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #e6edf3; letter-spacing: 3px; }}
  .meta {{ font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 1.5px; }}
  .sec {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 2px; }}
  .tn {{ font: 600 15px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #c9d1d9; }}
  .tn.now {{ fill: #58a6ff; }}
  .ts {{ font: 500 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #6e7681; letter-spacing: 1.2px; }}
  .cl {{ font: 600 10.5px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #58a6ff; letter-spacing: 2px; }}
  .ct {{ font: 700 20px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
  .cb {{ font: 400 13.5px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #8b949e; }}
  .chip {{ font: 600 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #c9d1d9; letter-spacing: .5px; }}
  .card {{ animation: rise .7s ease-out backwards; }}
  @keyframes rise {{ from {{ transform: translateY(10px) }} to {{ transform: none }} }}
  .dot {{ animation: blink 1.4s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: .2 }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#0b1626"/></linearGradient>
  <linearGradient id="prog" x1="0" x2="1"><stop offset="0" stop-color="#1f6feb" stop-opacity=".2"/><stop offset="1" stop-color="#58a6ff"/></linearGradient>
  <linearGradient id="topline" x1="0" x2="1"><stop offset="0" stop-color="#58a6ff" stop-opacity="0"/><stop offset=".5" stop-color="#58a6ff" stop-opacity=".8"/><stop offset="1" stop-color="#58a6ff" stop-opacity="0"/></linearGradient>
  <filter id="g" x="-200%" y="-200%" width="500%" height="500%"><feGaussianBlur stdDeviation="2.5" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="#30363d"/>
<circle cx="40" cy="42" r="5" fill="#3fb950" class="dot"/>
<text x="54" y="47" class="hdr">CREW PROFILE · ASWIN VENKAT</text>
<text x="1160" y="47" class="meta" text-anchor="end">STATUS: BUILDING AUTONOMOUS AGENTS</text>
<text x="50" y="105" class="sec">TRAJECTORY</text>
{"".join(tl)}
{"".join(cards)}
</svg>
"""
    (ASSETS / "about.svg").write_text(svg, encoding="utf-8")


CONNECT = [
    ("graph", "AI Agents", "Building or exploring", "autonomous agents"),
    ("drone", "FPV Drones", "Building from scratch &", "freestyle flying"),
    ("shield", "Cybersecurity", "Security product", "development"),
    ("terminal", "Go & DevOps", "Scalable backends", "and infrastructure"),
]
EMAIL = "aswinvenkat60@gmail.com"


def connect():
    W, H = 1200, 330
    tw, th, ty = 271, 120, 92
    tiles = []
    for i, (icon, title, l1, l2) in enumerate(CONNECT):
        x = 40 + i * (tw + 12)
        tiles.append(
            f'<g><rect x="{x}" y="{ty}" width="{tw}" height="{th}" rx="12" fill="#161b22" fill-opacity=".7" stroke="#30363d"/>'
            f'<g transform="translate({x+20},{ty+20})"><rect width="40" height="40" rx="10" fill="#1f6feb" fill-opacity=".12" stroke="#1f6feb" stroke-opacity=".6"/>'
            f'<g fill="none" stroke="#58a6ff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">{ICONS[icon]}</g></g>'
            f'<text x="{x+74}" y="{ty+38}" class="tt">{title.replace("&", "&amp;")}</text>'
            f'<text x="{x+74}" y="{ty+56}" class="tl">0{i+1}</text>'
            f'<text x="{x+20}" y="{ty+88}" class="tb">{l1.replace("&", "&amp;")}</text>'
            f'<text x="{x+20}" y="{ty+106}" class="tb">{l2.replace("&", "&amp;")}</text></g>'
        )
    cta_w, cta_h = 420, 52
    cx, cy = (W - cta_w) / 2, 240
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Let's connect if you're into AI agents, FPV drones, cybersecurity, or Go and DevOps. Email {EMAIL}">
<style>
  .hdr {{ font: 700 14px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #e6edf3; letter-spacing: 3px; }}
  .meta {{ font: 500 11px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #8b949e; letter-spacing: 1.5px; }}
  .tt {{ font: 700 17px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #e6edf3; }}
  .tl {{ font: 600 10px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #58a6ff; letter-spacing: 2px; }}
  .tb {{ font: 400 13.5px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; fill: #8b949e; }}
  .cta {{ font: 600 16px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #f0f6fc; letter-spacing: .5px; }}
  .dot {{ animation: blink 1.4s ease-in-out infinite; }}
  @keyframes blink {{ 50% {{ opacity: .2 }} }}
  .arrow {{ animation: nudge 1.6s ease-in-out infinite; }}
  @keyframes nudge {{ 50% {{ transform: translateX(5px) }} }}
</style>
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#0d1117"/><stop offset="1" stop-color="#0b1626"/></linearGradient>
  <linearGradient id="ctabg" x1="0" x2="1"><stop offset="0" stop-color="#1158c7"/><stop offset="1" stop-color="#1f6feb"/></linearGradient>
  <linearGradient id="shine" x1="0" x2="1">
    <stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".5" stop-color="#fff" stop-opacity=".28"/><stop offset="1" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <clipPath id="ctaclip"><rect x="{cx}" y="{cy}" width="{cta_w}" height="{cta_h}" rx="26"/></clipPath>
</defs>
<rect width="{W}" height="{H}" rx="18" fill="url(#bg)"/>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="17" fill="none" stroke="#30363d"/>
<circle cx="40" cy="42" r="5" fill="#3fb950" class="dot"/>
<text x="54" y="47" class="hdr">OPEN CHANNEL · LET'S CONNECT</text>
<text x="1160" y="47" class="meta" text-anchor="end">IF YOU'RE INTO ANY OF THESE</text>
{"".join(tiles)}
<rect x="{cx}" y="{cy}" width="{cta_w}" height="{cta_h}" rx="26" fill="url(#ctabg)"/>
<g clip-path="url(#ctaclip)">
  <rect x="{cx - 160}" y="{cy}" width="140" height="{cta_h}" fill="url(#shine)">
    <animate attributeName="x" values="{cx - 160};{cx + cta_w + 20};{cx + cta_w + 20}" keyTimes="0;.45;1" dur="4s" repeatCount="indefinite"/>
  </rect>
</g>
<g fill="none" stroke="#f0f6fc" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" transform="translate({cx + 30},{cy + 17})">
  <rect width="24" height="18" rx="3"/><path d="M 1 2 L 12 10 L 23 2"/>
</g>
<text x="{cx + 66}" y="{cy + 32}" class="cta">{EMAIL}</text>
<g class="arrow"><path d="M {cx + cta_w - 46} {cy + 26} H {cx + cta_w - 28} M {cx + cta_w - 34} {cy + 20} L {cx + cta_w - 28} {cy + 26} L {cx + cta_w - 34} {cy + 32}" fill="none" stroke="#f0f6fc" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></g>
</svg>
"""
    (ASSETS / "connect.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    header()
    footer()
    about()
    connect()
    print("wrote", ASSETS / "cosmos-header.svg", ASSETS / "cosmos-footer.svg")
