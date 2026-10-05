#!/usr/bin/env python3
"""
check_published.py - is the published website the same as this folder?

    python tools/check_published.py https://<user>.github.io/ai-for-architecture/
    python tools/check_published.py <url> --module 2        only Module 2 pages
    python tools/check_published.py <url> --module 0.1      only lesson 0.1

Builds the site from this folder (engine/build.py), then downloads every
matching page from the published site and compares the readable text of
each page (markup and whitespace are ignored, so only real content
differences are reported). Prints one line per page and a verdict.
"""
import argparse, difflib, html, os, re, subprocess, sys, urllib.error, urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")


def text_of(page):
    page = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", page)
    page = re.sub(r"(?s)<[^>]+>", "\n", page)
    lines = (re.sub(r"\s+", " ", html.unescape(l)).strip() for l in page.splitlines())
    return [l for l in lines if l]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "check-published", "Cache-Control": "no-cache"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "replace")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="address of the published site, e.g. https://you.github.io/ai-for-architecture/")
    ap.add_argument("--module", default="", help="2 = Module 2, 0.1 = lesson 0.1 (default: every page)")
    ap.add_argument("--no-build", action="store_true", help="compare the existing site/ folder without rebuilding")
    a = ap.parse_args()
    base = a.url if a.url.endswith("/") else a.url + "/"

    if not a.no_build:
        subprocess.run([sys.executable, os.path.join(ROOT, "engine", "build.py")], check=True,
                       stdout=subprocess.DEVNULL)
    prefix = a.module.replace(".", "-") + "-" if a.module else ""
    pages = sorted(f for f in os.listdir(SITE) if f.endswith(".html") and f.startswith(prefix))
    if not pages:
        sys.exit(f"  No pages in site/ start with '{prefix}'.")

    same, differ, missing = [], [], []
    for name in pages:
        local = text_of(open(os.path.join(SITE, name), encoding="utf-8").read())
        try:
            remote = text_of(fetch(base + name))
        except urllib.error.HTTPError as e:
            missing.append(name); print(f"  MISSING   {name}   (published site answers {e.code})"); continue
        except Exception as e:
            sys.exit(f"\n  Could not reach {base + name}\n  {e}\n")
        if local == remote:
            same.append(name); print(f"  same      {name}")
        else:
            differ.append(name)
            d = [l for l in difflib.unified_diff(remote, local, "published", "this folder", n=0, lineterm="")
                 if l[:1] in "+-" and not l.startswith(("+++", "---"))]
            print(f"  DIFFERENT {name}   ({len(d)} changed lines; first: {d[0][:90] if d else ''})")

    print("\n  " + "-" * 60)
    print(f"  {len(same)} same, {len(differ)} different, {len(missing)} missing on the published site")
    if differ or missing:
        print("  The published site is NOT the current version. Run publish-site.bat,\n"
              "  commit and push in GitHub Desktop, wait a minute, and run this again.")
    else:
        print("  The published site matches this folder.")
    return 1 if differ or missing else 0


if __name__ == "__main__":
    sys.exit(main())
