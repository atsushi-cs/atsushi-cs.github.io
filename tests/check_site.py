#!/usr/bin/env python3
"""Static checks for the portfolio site. Run: python3 tests/check_site.py"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE_PAGES = ["cs184", "cs162", "cs170", "cs189"]
PAGES = ["index.html"] + [f"courses/{c}.html" for c in COURSE_PAGES]
UNLINKED_COURSES = ["CS 61A", "CS 61B", "CS 61C", "CS 70"]


class Page(HTMLParser):
    """Collects links, title, viewport meta, h2 headings, and visible text.

    HTMLParser skips comment contents, so commented-out TODO markup is ignored.
    """

    def __init__(self):
        super().__init__()
        self.refs = []
        self.title = ""
        self.has_viewport = False
        self.h2s = []
        self.text = ""
        self._in = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("href", "src"):
            if a.get(key):
                self.refs.append(a[key])
        if tag == "meta" and a.get("name") == "viewport":
            self.has_viewport = True
        if tag in ("title", "h2"):
            self._in = tag
            if tag == "h2":
                self.h2s.append("")

    def handle_endtag(self, tag):
        if tag == self._in:
            self._in = None

    def handle_data(self, data):
        self.text += data
        if self._in == "title":
            self.title += data
        elif self._in == "h2":
            self.h2s[-1] += data


def parse(path):
    page = Page()
    page.feed(path.read_text(encoding="utf-8"))
    return page


def check_links(rel, path, page, errors):
    for ref in page.refs:
        if ref.startswith(("http://", "https://", "mailto:", "#")):
            continue
        if ref.startswith("/"):
            errors.append(f"{rel}: root-absolute link {ref!r} breaks on GitHub Pages project sites")
            continue
        target = (path.parent / ref.split("#")[0]).resolve()
        if not target.is_file():
            errors.append(f"{rel}: broken link {ref!r}")


def check():
    errors = []
    pages = {}
    for rel in PAGES:
        path = ROOT / rel
        if not path.is_file():
            errors.append(f"{rel}: missing")
            continue
        html = path.read_text(encoding="utf-8")
        # Without whitespace, screen readers read "CS 184Computer Graphics".
        for match in re.findall(r'<span class="code">[^<]*</span>(?=\S)', html):
            errors.append(f"{rel}: no space after {match!r}")
        page = pages[rel] = parse(path)
        if not page.title.strip():
            errors.append(f"{rel}: empty <title>")
        if not page.has_viewport:
            errors.append(f"{rel}: missing viewport meta")
        check_links(rel, path, page, errors)

    index = pages.get("index.html")
    if index:
        for c in COURSE_PAGES:
            if f"courses/{c}.html" not in index.refs:
                errors.append(f"index.html: no link to courses/{c}.html")
        for name in UNLINKED_COURSES + ["Allan Tsay"]:
            if name not in index.text:
                errors.append(f"index.html: missing text {name!r}")
        for heading in ("Coursework", "Game Projects"):
            if heading not in [h.strip() for h in index.h2s]:
                errors.append(f"index.html: missing <h2>{heading}</h2>")

    for c in COURSE_PAGES:
        rel = f"courses/{c}.html"
        page = pages.get(rel)
        if not page:
            continue
        if "../index.html" not in page.refs:
            errors.append(f"{rel}: no back link to ../index.html")
        if not page.h2s or page.h2s[-1].strip() != "Course Overview":
            errors.append(f"{rel}: last <h2> must be 'Course Overview'")

    css = ROOT / "css/style.css"
    if not css.is_file() or "prefers-color-scheme: dark" not in css.read_text(encoding="utf-8"):
        errors.append("css/style.css: missing or has no dark-mode block")

    return errors


if __name__ == "__main__":
    errs = check()
    for e in errs:
        print("ERROR:", e)
    if errs:
        sys.exit(1)
    print(f"OK: {len(PAGES)} pages checked")
