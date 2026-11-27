#!/usr/bin/env python3
"""Injects NASA's Astronomy Picture of the Day into README.md between
<!-- APOD:START --> and <!-- APOD:END --> markers.

Primary source: the official APOD page on science.nasa.gov (apod.nasa.gov now
redirects there). Fallback: api.nasa.gov, used only if it returns a sane result
(as of Nov 2026 its scraper returns the NASA logo instead of the picture).

Env: NASA_API_KEY (optional, fallback only; defaults to DEMO_KEY).
On any failure the README is left untouched.
"""
import html
import json
import os
import re
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
KEY = os.environ.get("NASA_API_KEY") or "DEMO_KEY"
START, END = "<!-- APOD:START -->", "<!-- APOD:END -->"
UA = {"User-Agent": "Mozilla/5.0 (cosmos-readme)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def meta(page, prop):
    m = re.search(rf'<meta property="{prop}" content="([^"]*)"', page)
    return html.unescape(m.group(1)) if m else None


def from_site():
    landing = get("https://science.nasa.gov/apod/")
    m = re.search(r'href="(https://science\.nasa\.gov/image-article/apod-[^"]+)"', landing)
    if not m:
        raise ValueError("no APOD article link on landing page")
    link = m.group(1)
    art = get(link)
    # og:title looks like "APOD: 2026 November 26 - Eye in the Sky: ... - NASA Science"
    raw = meta(art, "og:title") or ""
    t = re.match(r"APOD:\s*(\d{4} \w+ \d{1,2})\s*[-–]\s*(.*?)\s*-\s*NASA Science$", raw)
    date, title = (t.group(1), t.group(2)) if t else ("", raw)
    img = meta(art, "og:image")
    if not img or "apod" not in img:
        raise ValueError("no APOD image found")
    expl = ""
    for p in re.findall(r"<p[^>]*>(.*?)</p>", art, re.S):
        text = html.unescape(re.sub(r"<[^>]+>", "", p)).strip()
        if text.startswith("Explanation:"):
            expl = " ".join(text[len("Explanation:"):].split())
            break
    return {"title": title, "date": date, "img": img, "link": link, "explanation": expl}


def from_api():
    d = json.loads(get(f"https://api.nasa.gov/planetary/apod?api_key={KEY}&thumbs=true"))
    img = d.get("url") if d.get("media_type") == "image" else d.get("thumbnail_url")
    if not img or "nasa-logo" in img or d.get("title") == "NASA Science":
        raise ValueError("API returned placeholder data")
    ds = d["date"]
    return {
        "title": d.get("title", ""),
        "date": ds,
        "img": img,
        "link": f"https://apod.nasa.gov/apod/ap{ds[2:4]}{ds[5:7]}{ds[8:10]}.html",
        "explanation": " ".join(d.get("explanation", "").split()),
    }


def fetch():
    errors = []
    for source in (from_site, from_api):
        try:
            return source()
        except Exception as e:  # noqa: BLE001 — try the next source
            errors.append(f"{source.__name__}: {e}")
    raise SystemExit("APOD unavailable — " + " | ".join(errors))


def block(d):
    e = html.escape
    details = (
        f"""
<details>
<summary><sub>🔭 Read NASA's explanation</sub></summary>
<br/>
<p align="left">{e(d["explanation"])}</p>
</details>
"""
        if d["explanation"]
        else ""
    )
    return f"""{START}
<div align="center">

<a href="{e(d["link"])}"><img src="{e(d["img"])}" alt="{e(d["title"])}" width="85%"/></a>

**{e(d["title"])}**<br/>
<sub>📅 {e(d["date"])} · via <a href="https://science.nasa.gov/apod/">NASA APOD</a></sub>
{details}
</div>
{END}"""


def main():
    text = README.read_text()
    if START not in text or END not in text:
        raise SystemExit("APOD markers not found in README.md")
    new_block = block(fetch())
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: new_block, text, flags=re.S)
    README.write_text(new)
    print("APOD updated")


if __name__ == "__main__":
    main()
