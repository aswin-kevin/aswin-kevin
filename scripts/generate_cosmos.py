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

STAR_COLORS = ["#ffffff", "#ffffff", "#ffffff", "#cfe8ff", "#ffe9c4", "#e2d6ff"]


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
                c = lerp_color("#fff4d6", "#f0abfc", t / 0.45)
            else:
                c = lerp_color("#f0abfc", "#60a5fa", (t - 0.45) / 0.55)
            op = max(0.25, 1 - t * 0.6)
            pts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{size:.2f}" fill="{c}" opacity="{op:.2f}"/>')
    # halo dust
    for _ in range(140):
        a = rng.uniform(0, 2 * math.pi)
        r = abs(rng.gauss(0, 70))
        pts.append(
            f'<circle cx="{r*math.cos(a):.1f}" cy="{r*math.sin(a):.1f}" r="{rng.uniform(0.3,1.1):.2f}" '
            f'fill="#e9d5ff" opacity="{rng.uniform(0.2,0.7):.2f}"/>'
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
  .hud {{ font: 600 12px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #a5b4fc; letter-spacing: 2px; }}
  .title {{ font: 800 76px 'Segoe UI', 'Helvetica Neue', Arial, sans-serif; letter-spacing: 10px; }}
  .sub {{ font: 500 19px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #c7d2fe; letter-spacing: 1px; }}
</style>
<defs>
  <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="#03010a"/>
    <stop offset=".55" stop-color="#0b0628"/>
    <stop offset="1" stop-color="#140a3a"/>
  </linearGradient>
  <radialGradient id="nebA"><stop offset="0" stop-color="#a855f7" stop-opacity=".55"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
  <radialGradient id="nebB"><stop offset="0" stop-color="#06b6d4" stop-opacity=".40"/><stop offset="1" stop-color="#06b6d4" stop-opacity="0"/></radialGradient>
  <radialGradient id="nebC"><stop offset="0" stop-color="#ec4899" stop-opacity=".35"/><stop offset="1" stop-color="#ec4899" stop-opacity="0"/></radialGradient>
  <radialGradient id="core"><stop offset="0" stop-color="#fffbea"/><stop offset=".25" stop-color="#fde68a" stop-opacity=".8"/><stop offset="1" stop-color="#c084fc" stop-opacity="0"/></radialGradient>
  <radialGradient id="planet" cx=".35" cy=".3" r=".8">
    <stop offset="0" stop-color="#c4b5fd"/><stop offset=".45" stop-color="#7c3aed"/><stop offset="1" stop-color="#1e1048"/>
  </radialGradient>
  <radialGradient id="moon" cx=".35" cy=".35"><stop offset="0" stop-color="#f8fafc"/><stop offset="1" stop-color="#64748b"/></radialGradient>
  <linearGradient id="ring" x1="0" x2="1"><stop offset="0" stop-color="#67e8f9" stop-opacity=".1"/><stop offset=".5" stop-color="#e0f2fe" stop-opacity=".9"/><stop offset="1" stop-color="#67e8f9" stop-opacity=".1"/></linearGradient>
  <linearGradient id="tail" x1="1" y1="0" x2="0" y2="0"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>
  <linearGradient id="txt" x1="0" x2="1" gradientUnits="objectBoundingBox">
    <stop offset="0" stop-color="#67e8f9"/><stop offset=".35" stop-color="#e9d5ff"/><stop offset=".65" stop-color="#f0abfc"/><stop offset="1" stop-color="#67e8f9"/>
    <animateTransform attributeName="gradientTransform" type="translate" values="-1 0;1 0" dur="8s" repeatCount="indefinite"/>
  </linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%">
    <feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
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
  <path d="M -40 -14 Q 0 -6 40 -16" stroke="#ddd6fe" stroke-opacity=".25" stroke-width="5" fill="none"/>
  <path d="M -48 10 Q 0 20 46 8" stroke="#ddd6fe" stroke-opacity=".18" stroke-width="4" fill="none"/>
  <path d="M -98 0 A 98 19 0 0 0 98 0" fill="none" stroke="url(#ring)" stroke-width="5"/>
  <ellipse rx="150" ry="36" fill="none" stroke="#a5b4fc" stroke-opacity=".18" stroke-dasharray="3 6"/>
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
<g stroke="#a5b4fc" stroke-opacity=".45" fill="none" stroke-width="1.5">
  <path d="M 14 34 V 14 H 34"/><path d="M 1186 34 V 14 H 1166"/>
  <path d="M 14 386 V 406 H 34"/><path d="M 1186 386 V 406 H 1166"/>
</g>

<!-- title -->
<text x="548" y="205" text-anchor="middle" class="title" fill="url(#txt)" filter="url(#glow)">ASWIN VENKAT</text>
<text x="548" y="252" text-anchor="middle" class="sub">&gt; cybersecurity · ai agents · web &amp; mobile · robotics<tspan class="blink" fill="#67e8f9">▌</tspan></text>
</svg>
'''
    (ASSETS / "cosmos-header.svg").write_text(svg)


def footer():
    rng = random.Random(99)
    W, H = 1200, 220
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="Planet horizon — thanks for visiting">
<style>
  .tw {{ animation-name: twinkle; animation-iteration-count: infinite; animation-timing-function: ease-in-out; }}
  @keyframes twinkle {{ 0%,100% {{ opacity: .15 }} 50% {{ opacity: 1 }} }}
  .atmo {{ animation: pulse 6s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity: .65 }} 50% {{ opacity: 1 }} }}
  .msg {{ font: 500 17px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; fill: #e0e7ff; letter-spacing: 2px; }}
</style>
<defs>
  <linearGradient id="fsky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#03010a"/><stop offset="1" stop-color="#0b0628"/></linearGradient>
  <radialGradient id="atm" cx=".5" cy="1" r=".75"><stop offset=".72" stop-color="#22d3ee" stop-opacity=".0"/><stop offset=".86" stop-color="#22d3ee" stop-opacity=".55"/><stop offset=".93" stop-color="#a855f7" stop-opacity=".25"/><stop offset="1" stop-color="#a855f7" stop-opacity="0"/></radialGradient>
  <radialGradient id="earth" cx=".5" cy="0" r="1"><stop offset="0" stop-color="#1e3a8a"/><stop offset=".4" stop-color="#0b1440"/><stop offset="1" stop-color="#03010a"/></radialGradient>
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
    (ASSETS / "cosmos-footer.svg").write_text(svg)


if __name__ == "__main__":
    header()
    footer()
    print("wrote", ASSETS / "cosmos-header.svg", ASSETS / "cosmos-footer.svg")
