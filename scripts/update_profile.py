#!/usr/bin/env python3
"""Regenerate the QueryaHub organization profile.

Writes assets/banner.svg, assets/project-*.svg and assets/stats.svg from live
GitHub numbers and rewrites the crew block of profile/README.md.
Env: GITHUB_TOKEN (read access to the organization's public repositories).
"""
import json
import math
import os
import random
import re
import urllib.request
from html import escape
from pathlib import Path

ORG = "QueryaHub"
ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
README = ROOT / "profile" / "README.md"
BOT_LOGINS = {"actions-user", "github-actions", "dependabot", "renovate"}
START, END = "<!--CREW:START-->", "<!--CREW:END-->"

PROJECTS = [
    ("querya", "Querya-Desktop", "01 // DATABASE STUDIO", "Querya Desktop",
     "Cross-platform SQL & NoSQL studio with a 2D virtualized grid and DML staging buffer.",
     "FLUTTER  •  POSTGRESQL  •  MYSQL  •  SQLITE  •  REDIS  •  MONGODB", "#4fb0f5"),
    ("oxyjwt", "OxyJWT", "02 // CRYPTO LIBRARY", "OxyJWT",
     "Drop-in PyJWT replacement with a Rust core: up to 4x faster, JWKS support.",
     "PYTHON  •  RUST  •  PYO3  •  MATURIN  •  JWKS", "#b45cff"),
    ("oxyroute", "OxyRoute", "03 // WEB FRAMEWORK", "OxyRoute",
     "Python web framework that moves the request hot path into native Rust code.",
     "PYTHON  •  RUST  •  ASGI  •  ROUTING", "#ff6ac1"),
    ("engine", "flutter-engine-linux-120hz", "04 // ENGINE PATCH", "Flutter Engine 120 Hz",
     "Patched Flutter Linux GTK engine with vsync support for high refresh rates.",
     "FLUTTER  •  GTK  •  LINUX  •  VSYNC", "#5eead4"),
    ("clickhouse", "clickhouse-query-ext", "05 // DRIVER EXTENSION", "ClickHouse Extension",
     "ClickHouse driver extension for Querya Desktop, written in Rust.",
     "RUST  •  CLICKHOUSE  •  QUERYA EXTENSION", "#fbbf24"),
]


def api(path):
    url = f"https://api.github.com{path}{'&' if '?' in path else '?'}per_page=100"
    out = []
    while url:
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
        })
        with urllib.request.urlopen(req) as resp:
            data = json.load(resp)
            link = resp.headers.get("Link", "")
        out.extend(data if isinstance(data, list) else [data])
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        url = m.group(1) if m else None
    return out


def is_bot(u):
    login = u["login"].lower()
    return u.get("type") == "Bot" or login.endswith("[bot]") or login in BOT_LOGINS


def compact(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def logo_path():
    svg = (ROOT / "profile" / "logo.svg").read_text()
    return re.search(r'<clipPath id="clip-1">\s*<path[^>]* d="([^"]+)"', svg).group(1)


def star_field(rng, w, h, n, twinkle):
    out = []
    for i in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, h)
        r = rng.choice([0.5, 0.6, 0.8, 1.0, 1.3])
        o = rng.uniform(0.25, 0.9)
        fill = rng.choice(["#ffffff", "#cfe3ff", "#e6d4ff"])
        if i < twinkle:
            dur, begin = rng.uniform(2.5, 6), -rng.uniform(0, 6)
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}">'
                       f'<animate attributeName="opacity" values="{o:.2f};0.1;{o:.2f}" '
                       f'dur="{dur:.1f}s" begin="{begin:.1f}s" repeatCount="indefinite"/></circle>')
        else:
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" opacity="{o:.2f}"/>')
    return "\n    ".join(out)


def banner():
    rng = random.Random(7)
    cx, cy = 235, 180
    rx, ry, rot = 300, 78, -16
    ring = f"M {cx - rx} {cy} a {rx} {ry} 0 1 0 {2 * rx} 0 a {rx} {ry} 0 1 0 {-2 * rx} 0"
    ring2 = f"M {cx - 205} {cy} a 205 {55} 0 1 0 410 0 a 205 {55} 0 1 0 -410 0"
    shooting = []
    for i, (x, y, dur, begin) in enumerate([(700, 20, 7, 0), (950, 70, 9, -3), (520, 10, 11, -6), (1100, 30, 8, -5)]):
        shooting.append(
            f'<g opacity="0"><line x1="0" y1="0" x2="-90" y2="-34" stroke="url(#trail)" stroke-width="1.6" stroke-linecap="round"/>'
            f'<circle r="1.8" fill="#fff"/>'
            f'<animateTransform attributeName="transform" type="translate" values="{x},{y};{x - 380},{y + 140}" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0;0" keyTimes="0;0.05;0.2;0.3;1" '
            f'dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></g>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 360" width="1200" height="360">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#04030d"/><stop offset="0.55" stop-color="#0b0620"/><stop offset="1" stop-color="#150a33"/>
    </linearGradient>
    <radialGradient id="neb1" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#8a0bef" stop-opacity="0.50"/><stop offset="1" stop-color="#8a0bef" stop-opacity="0"/></radialGradient>
    <radialGradient id="neb2" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#4fb0f5" stop-opacity="0.38"/><stop offset="1" stop-color="#4fb0f5" stop-opacity="0"/></radialGradient>
    <radialGradient id="neb3" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="#ff6ac1" stop-opacity="0.18"/><stop offset="1" stop-color="#ff6ac1" stop-opacity="0"/></radialGradient>
    <linearGradient id="q" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#8a0bef"/><stop offset="1" stop-color="#4fb0f5"/></linearGradient>
    <linearGradient id="title" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="#a8d4ff"/></linearGradient>
    <linearGradient id="trail" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset="1" stop-color="#fff" stop-opacity="0.9"/></linearGradient>
    <radialGradient id="planet" cx="0.35" cy="0.35" r="0.8"><stop offset="0" stop-color="#bfe3ff"/><stop offset="1" stop-color="#4f46e5"/></radialGradient>
    <filter id="glow" x="-30%" y="-30%" width="160%" height="160%"><feGaussianBlur stdDeviation="6" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  </defs>

  <rect width="1200" height="360" fill="url(#bg)"/>
  <ellipse cx="180" cy="330" rx="520" ry="260" fill="url(#neb1)"/>
  <ellipse cx="1010" cy="40" rx="470" ry="230" fill="url(#neb2)"/>
  <ellipse cx="700" cy="360" rx="360" ry="140" fill="url(#neb3)"/>

  <g>
    {star_field(rng, 1200, 360, 170, 46)}
  </g>

  {chr(10).join(shooting)}

  <g transform="rotate({rot} {cx} {cy})" fill="none">
    <path d="{ring}" stroke="#a8d4ff" stroke-opacity="0.18" stroke-width="1"/>
    <path d="{ring2}" stroke="#b45cff" stroke-opacity="0.22" stroke-width="1" stroke-dasharray="3 7"/>
    <circle r="7" fill="url(#planet)" filter="url(#glow)">
      <animateMotion dur="26s" repeatCount="indefinite" path="{ring}"/>
    </circle>
    <circle r="3.2" fill="#ff9ad5">
      <animateMotion dur="14s" begin="-4s" repeatCount="indefinite" path="{ring2}"/>
    </circle>
  </g>

  <circle cx="{cx}" cy="{cy}" r="150" fill="url(#neb1)">
    <animate attributeName="r" values="135;160;135" dur="5s" repeatCount="indefinite"/>
  </circle>
  <g transform="translate({cx - 115} {cy - 128}) scale(0.1) translate(-851 -716)" filter="url(#glow)">
    <path d="{logo_path()}" fill="url(#q)"/>
  </g>

  <g font-family="'Inter','Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif">
    <text x="470" y="178" font-size="92" font-weight="800" letter-spacing="14" fill="url(#title)">QUERYA</text>
    <text x="474" y="222" font-family="'JetBrains Mono','Fira Code',monospace" font-size="16" letter-spacing="5" fill="#9fb3d9">LIGHTWEIGHT TOOLS FOR WORKING WITH DATA</text>
    <text x="474" y="256" font-family="'JetBrains Mono','Fira Code',monospace" font-size="12" letter-spacing="2" fill="#6c7aa6">OPEN SOURCE  •  PRIVATE BY DESIGN  •  BUILT FOR ENGINEERS</text>
  </g>
</svg>
'''


def card(slug, tag, name, line, stack, accent, stars, downloads, seed):
    rng = random.Random(seed)
    right_sub = f"{compact(downloads)} DOWNLOADS" if downloads else "OPEN SOURCE"
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 124" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07061a"/><stop offset="1" stop-color="#120a2c"/></linearGradient>
    <radialGradient id="glow" cx="0.5" cy="0.5" r="0.5"><stop offset="0" stop-color="{accent}" stop-opacity="0.28"/><stop offset="1" stop-color="{accent}" stop-opacity="0"/></radialGradient>
  </defs>
  <style>
    .tag {{ font-family: 'JetBrains Mono','Fira Code',monospace; font-size: 10.5px; font-weight: bold; letter-spacing: 1px; fill: {accent}; }}
    .name {{ font-family: 'Inter','Segoe UI',-apple-system,Arial,sans-serif; font-size: 26px; font-weight: 800; fill: #f3f5ff; }}
    .line {{ font-family: 'JetBrains Mono',monospace; font-size: 12px; fill: #98a3c7; }}
    .stack {{ font-family: 'JetBrains Mono',monospace; font-size: 9.5px; font-weight: bold; letter-spacing: 1px; fill: #5a6590; }}
    .lbl {{ font-family: 'JetBrains Mono',monospace; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; fill: #7a86b0; }}
    .val {{ font-family: 'Inter','Segoe UI',Arial,sans-serif; font-size: 28px; font-weight: 800; fill: {accent}; }}
    .sub {{ font-family: 'JetBrains Mono',monospace; font-size: 9px; font-weight: bold; letter-spacing: 0.5px; fill: #6a76a0; }}
  </style>
  <rect width="850" height="124" rx="10" fill="url(#bg)" stroke="#241a4a" stroke-width="1.2"/>
  <ellipse cx="760" cy="20" rx="170" ry="90" fill="url(#glow)"/>
  <g>{star_field(rng, 850, 124, 26, 8)}</g>
  <rect x="0" y="14" width="4" height="96" rx="2" fill="{accent}"/>
  <text x="36" y="30" class="tag">[{escape(tag)}]</text>
  <text x="36" y="64" class="name">{escape(name)}</text>
  <text x="36" y="87" class="line">{escape(line)}</text>
  <text x="36" y="108" class="stack">{escape(stack)}</text>
  <line x1="660" y1="24" x2="660" y2="100" stroke="#241a4a" stroke-width="1"/>
  <text x="684" y="36" class="lbl">STARS</text>
  <text x="684" y="72" class="val">★ {stars}</text>
  <text x="684" y="94" class="sub">{right_sub}</text>
</svg>
'''


def stats_svg(items):
    rng = random.Random(11)
    tile_w = 850 / len(items)
    tiles = []
    for i, (label, value, sub, color) in enumerate(items):
        x = i * tile_w + 34
        tiles.append(
            f'<text x="{x:.0f}" y="62" class="lbl">{escape(label)}</text>'
            f'<text x="{x:.0f}" y="104" class="val" fill="{color}">{escape(str(value))}</text>'
            f'<text x="{x:.0f}" y="126" class="sub">{escape(sub)}</text>')
        if i:
            tiles.append(f'<line x1="{i * tile_w:.0f}" y1="40" x2="{i * tile_w:.0f}" y2="130" stroke="#241a4a"/>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 850 160" width="100%" height="100%">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#07061a"/><stop offset="1" stop-color="#150a33"/></linearGradient>
    <linearGradient id="rule" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#8a0bef"/><stop offset="1" stop-color="#4fb0f5"/></linearGradient>
  </defs>
  <style>
    .hd {{ font-family: 'JetBrains Mono',monospace; font-size: 10.5px; font-weight: bold; letter-spacing: 2px; fill: #7a86b0; }}
    .lbl {{ font-family: 'JetBrains Mono',monospace; font-size: 10px; font-weight: bold; letter-spacing: 1.5px; fill: #7a86b0; }}
    .val {{ font-family: 'Inter','Segoe UI',Arial,sans-serif; font-size: 40px; font-weight: 800; }}
    .sub {{ font-family: 'JetBrains Mono',monospace; font-size: 9px; font-weight: bold; letter-spacing: 0.5px; fill: #6a76a0; }}
  </style>
  <rect width="850" height="160" rx="10" fill="url(#bg)" stroke="#241a4a" stroke-width="1.2"/>
  <g>{star_field(rng, 850, 160, 40, 10)}</g>
  <text x="34" y="26" class="hd">MISSION TELEMETRY</text>
  <rect x="34" y="34" width="60" height="2" rx="1" fill="url(#rule)"/>
  {''.join(tiles)}
</svg>
'''


def main():
    ASSETS.mkdir(exist_ok=True)
    repos = [r for r in api(f"/orgs/{ORG}/repos?type=public")
             if not r["fork"] and not r["archived"] and r["name"] != ".github"]
    by_name = {r["name"]: r for r in repos}

    downloads, stars, people, latest = {}, 0, {}, None
    for r in repos:
        stars += r["stargazers_count"]
        total = 0
        for rel in api(f"/repos/{ORG}/{r['name']}/releases"):
            total += sum(a["download_count"] for a in rel["assets"])
            if r["name"] == "Querya-Desktop" and latest is None and not rel["prerelease"]:
                latest = rel["tag_name"]
        downloads[r["name"]] = total
        for u in api(f"/repos/{ORG}/{r['name']}/contributors"):
            if is_bot(u):
                continue
            p = people.setdefault(u["login"], {"url": u["html_url"], "n": 0})
            p["n"] += u["contributions"]

    (ASSETS / "banner.svg").write_text(banner())
    for i, (slug, repo, tag, name, line, stack, accent) in enumerate(PROJECTS):
        r = by_name.get(repo, {})
        (ASSETS / f"project-{slug}.svg").write_text(
            card(slug, tag, name, line, stack, accent,
                 r.get("stargazers_count", 0), downloads.get(repo, 0), seed=100 + i))

    (ASSETS / "stats.svg").write_text(stats_svg([
        ("STARS", compact(stars), "ACROSS ALL REPOSITORIES", "#fbbf24"),
        ("DOWNLOADS", compact(sum(downloads.values())), "ALL RELEASES, ALL VERSIONS", "#b45cff"),
        ("CREW", len(people), "HUMAN CONTRIBUTORS", "#4fb0f5"),
        ("LATEST", latest or "-", "QUERYA DESKTOP", "#5eead4"),
    ]))

    ranked = sorted(people.items(), key=lambda kv: -kv[1]["n"])
    cells = "\n".join(
        f'    <td align="center" width="110"><a href="{p["url"]}">'
        f'<img src="https://github.com/{login}.png?size=140" width="72" height="72" alt="{login}" /><br/>'
        f'<sub><b>{login}</b></sub></a><br/><sub>{p["n"]} commits</sub></td>'
        for login, p in ranked)
    block = f'{START}\n<table align="center">\n  <tr>\n{cells}\n  </tr>\n</table>\n{END}'
    text = README.read_text()
    text = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: block, text, flags=re.S)
    README.write_text(text)
    print(f"stars={stars} downloads={sum(downloads.values())} crew={len(people)} latest={latest}")


if __name__ == "__main__":
    main()
