#!/usr/bin/env python3
"""Refresh org-wide stats and the contributors block of profile/README.md.

Reads every public, non-fork repository of the organization through the
GitHub API (token from GITHUB_TOKEN), writes shields.io endpoint JSON files
to profile/stats/ and rewrites the block between the CONTRIBUTORS markers.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

ORG = "QueryaHub"
ROOT = Path(__file__).resolve().parent.parent
PROFILE = ROOT / "profile"
BOT_LOGINS = {"actions-user", "github-actions", "dependabot", "renovate"}
START, END = "<!--CONTRIBUTORS:START-->", "<!--CONTRIBUTORS:END-->"


def api(path):
    """GET a GitHub API path, following pagination, returning a flat list."""
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


def is_bot(user):
    login = user["login"].lower()
    return user.get("type") == "Bot" or login.endswith("[bot]") or login in BOT_LOGINS


def badge(path, label, message, color):
    (PROFILE / "stats").mkdir(exist_ok=True)
    payload = {"schemaVersion": 1, "label": label, "message": str(message), "color": color}
    (PROFILE / "stats" / path).write_text(json.dumps(payload) + "\n")


def compact(n):
    return f"{n / 1000:.1f}k".replace(".0k", "k") if n >= 1000 else str(n)


def main():
    repos = [r for r in api(f"/orgs/{ORG}/repos?type=public")
             if not r["fork"] and not r["archived"] and r["name"] != ".github"]

    stars = sum(r["stargazers_count"] for r in repos)
    downloads = 0
    people = {}
    for r in repos:
        for rel in api(f"/repos/{ORG}/{r['name']}/releases"):
            downloads += sum(a["download_count"] for a in rel["assets"])
        for u in api(f"/repos/{ORG}/{r['name']}/contributors"):
            if is_bot(u):
                continue
            p = people.setdefault(u["login"], {"url": u["html_url"], "n": 0})
            p["n"] += u["contributions"]

    badge("stars.json", "stars", compact(stars), "f5c542")
    badge("downloads.json", "downloads", compact(downloads), "8a0bef")
    badge("contributors.json", "contributors", len(people), "4fb0f5")

    ranked = sorted(people.items(), key=lambda kv: -kv[1]["n"])
    cells = "\n".join(
        f'  <a href="{p["url"]}" title="{login}">'
        f'<img src="https://github.com/{login}.png?size=120" width="64" height="64" alt="{login}" /></a>'
        for login, p in ranked
    )
    block = f'{START}\n<p align="center">\n{cells}\n</p>\n{END}'

    readme = PROFILE / "README.md"
    text = readme.read_text()
    text = re.sub(f"{re.escape(START)}.*?{re.escape(END)}", lambda _: block, text, flags=re.S)
    readme.write_text(text)
    print(f"stars={stars} downloads={downloads} contributors={len(people)}")


if __name__ == "__main__":
    main()
