#!/usr/bin/env python3
"""Injects NASA's Astronomy Picture of the Day into README.md between
<!-- APOD:START --> and <!-- APOD:END --> markers.

Source: the official APOD page on science.nasa.gov (apod.nasa.gov redirects
there). api.nasa.gov is not used: since Sep 2026 it returns the NASA logo
instead of the picture.

On any failure the README is left untouched and the script exits non-zero.
"""
import html
import re
import urllib.request
from pathlib import Path

README = Path(__file__).resolve().parent.parent / "README.md"
START, END = "<!-- APOD:START -->", "<!-- APOD:END -->"
UA = {"User-Agent": "Mozilla/5.0 (cosmos-readme)"}


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def meta(page, prop):
    for tag in re.findall(r"<meta\b[^>]*>", page):
        if re.search(rf'property="{re.escape(prop)}"', tag):
            m = re.search(r'content="([^"]*)"', tag)
            if m:
                return html.unescape(m.group(1))
    return None


def text_of(fragment):
    """Strip tags (as spaces, so <br> doesn't glue words) and collapse whitespace."""
    text = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", fragment)).split())
    return re.sub(r"\s+([,.;:!?)])", r"\1", text).replace("( ", "(")


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
    if not img or not img.startswith("https://assets.science.nasa.gov/") or "nasa-logo" in img:
        raise ValueError(f"no usable APOD image (got {img!r})")
    expl = ""
    for p in re.findall(r"<p(?:\s[^>]*)?>(.*?)</p>", art, re.S):
        text = text_of(p)
        if text.startswith("Explanation:"):
            expl = text[len("Explanation:"):]
            expl = re.split(r"Tomorrow['’]s picture:", expl)[0].strip()
            break
    return {"title": title, "date": date, "img": img, "link": link, "explanation": expl}


def fetch():
    try:
        return from_site()
    except Exception as e:  # noqa: BLE001
        raise SystemExit(f"APOD unavailable: {e}")


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

<b>{e(d["title"])}</b><br/>
<sub>📅 {e(d["date"])} · via <a href="https://science.nasa.gov/apod/">NASA APOD</a></sub>
{details}
</div>
{END}"""


def main():
    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit("APOD markers not found in README.md")
    new_block = block(fetch())
    new = re.sub(re.escape(START) + r".*?" + re.escape(END), lambda _: new_block, text, flags=re.S)
    README.write_text(new, encoding="utf-8")
    print("APOD updated")


if __name__ == "__main__":
    main()
