# Portfolio Site Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a static portfolio site (home page + 4 course pages) for Allan Tsay, deployable on GitHub Pages.

**Architecture:** Five hand-written HTML files share one stylesheet. A stdlib-only Python script checks structure and links; a headless-Chrome screenshot pass checks layout at phone/desktop widths in light and dark mode.

**Tech Stack:** HTML5, CSS (custom properties, grid/flex), Python 3 stdlib (`html.parser`) for checks, Google Chrome headless for screenshots.

**Spec:** `docs/superpowers/specs/2026-09-27-portfolio-site-design.md`

## Global Constraints

- No JavaScript, no build step, no dependencies.
- All internal links are relative (never start with `/`) and point at explicit `.html` files, so the site works both on a GitHub Pages project subpath and from `file://`.
- Every course page ends with an `<h2>Course Overview</h2>` section and links back to `../index.html`.
- Missing images are shown as `<div class="img-slot">` placeholders — never an `<img>` pointing at a file that doesn't exist.
- Content the user fills in later is marked with an HTML `<!-- TODO: ... -->` comment; visible placeholder text reads naturally (e.g. "Writeup coming soon.").
- Colors only via CSS custom properties on `:root`, redefined under `@media (prefers-color-scheme: dark)`.
- Readable column max 720px, 16px side gutter, no horizontal scroll at 375px.

## Review Focus

1. **Hosted on a project subpath** (`https://user.github.io/portfolio/`) — a root-absolute link like `/css/style.css` would 404. Pinned by the checker's root-absolute rule (Task 1).
2. **Opened from disk via `file://`** — a link to a directory (`courses/`) shows a file listing instead of a page. Pinned by the checker's `is_file()` rule (Task 1).
3. **Phone width (375px)** — long course names must wrap, not overflow. Pinned by Task 2 screenshots.
4. **Dark mode** — text, borders, and dashed placeholder boxes must stay visible. Pinned by Task 2 dark screenshots.
5. **Images not yet added** — pages must not show broken-image icons. Pinned by the checker's broken `src` rule (Task 1) plus Task 2 screenshots.

---

### Task 1: Site pages, stylesheet, and structural checker

**Files:**
- Create: `tests/check_site.py`
- Create: `css/style.css`
- Create: `index.html`
- Create: `courses/cs184.html`, `courses/cs162.html`, `courses/cs170.html`, `courses/cs189.html`
- Create: `images/cs184/.gitkeep`, `images/games/.gitkeep`

**Interfaces:**
- Produces: `python3 tests/check_site.py` → exits 0 and prints `OK: 5 pages checked` when the site is valid; exits 1 listing each error otherwise. CSS class names used by the HTML: `container intro tagline course-list plain code term card card-body tags tag img-slot gallery assignment placeholder back page-header eyebrow links site-footer`.

- [ ] **Step 1: Write the checker**

`tests/check_site.py`:

```python
#!/usr/bin/env python3
"""Static checks for the portfolio site. Run: python3 tests/check_site.py"""
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
```

- [ ] **Step 2: Run the checker to verify it fails**

Run: `python3 tests/check_site.py`
Expected: exit 1, errors `index.html: missing`, four `courses/…: missing`, and `css/style.css: missing or has no dark-mode block`.

- [ ] **Step 3: Write the stylesheet**

`css/style.css`:

```css
:root {
  --bg: #fbfaf7;
  --surface: #ffffff;
  --text: #1f2328;
  --muted: #5d636b;
  --accent: #2b5c8a;
  --border: #e2ded6;
  --slot: #c9c4ba;
  color-scheme: light;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #15171a;
    --surface: #1d2024;
    --text: #e6e4e0;
    --muted: #9ba1a8;
    --accent: #8cb8e8;
    --border: #2d3137;
    --slot: #474c54;
    color-scheme: dark;
  }
}

*, *::before, *::after { box-sizing: border-box; }
html { -webkit-text-size-adjust: 100%; }

body {
  margin: 0;
  background: var(--bg);
  color: var(--text);
  font: 17px/1.6 system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
}

.container { max-width: 720px; margin: 0 auto; padding: 56px 16px 40px; }

h1, h2, h3 { line-height: 1.25; margin: 0 0 0.5em; }
h1 { font-size: 2.25rem; letter-spacing: -0.02em; }
h2 {
  font-size: 1.35rem;
  margin-top: 2.5rem;
  padding-bottom: 0.4rem;
  border-bottom: 1px solid var(--border);
}
h3 { font-size: 1.1rem; margin-top: 1.5rem; }
p { margin: 0 0 1em; }
a { color: var(--accent); text-underline-offset: 2px; }
img { display: block; max-width: 100%; height: auto; }

.tagline, .eyebrow, .term, .placeholder, .site-footer, figcaption { color: var(--muted); }
.tagline { margin-top: -0.25rem; }
.eyebrow {
  margin-bottom: 0.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  text-transform: uppercase;
}
.placeholder { font-style: italic; }

/* Course list */
.course-list { list-style: none; margin: 0; padding: 0; }
.course-list li {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: baseline;
  gap: 0 1rem;
  padding: 0.6rem 0;
  border-bottom: 1px solid var(--border);
}
.course-list li:last-child { border-bottom: 0; }
.course-list a { font-weight: 500; text-decoration: none; }
.course-list a:hover { text-decoration: underline; }
.code { margin-right: 0.4rem; font-weight: 700; white-space: nowrap; }
.term { font-size: 0.9rem; white-space: nowrap; }

/* Game card */
.card {
  overflow: hidden;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 10px;
}
.card > .img-slot { aspect-ratio: 16 / 9; border-width: 0 0 2px; border-radius: 0; }
.card-body { padding: 1rem 1.25rem 0.25rem; }
.card-body h3 { margin-top: 0; }
.tags { display: flex; flex-wrap: wrap; gap: 0.4rem; }
.tag {
  padding: 0.1rem 0.55rem;
  font-size: 0.8rem;
  color: var(--muted);
  border: 1px solid var(--border);
  border-radius: 999px;
}

/* Image placeholders and galleries */
.img-slot {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  padding: 1rem;
  font-size: 0.85rem;
  text-align: center;
  overflow-wrap: anywhere;
  color: var(--muted);
  border: 2px dashed var(--slot);
  border-radius: 8px;
}
.gallery {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.75rem;
  margin: 1rem 0 1.5rem;
}
.gallery figure { margin: 0; }
.gallery img { border: 1px solid var(--border); border-radius: 8px; }
figcaption { margin-top: 0.3rem; font-size: 0.85rem; }

/* Course pages */
.back { margin-bottom: 2rem; font-size: 0.95rem; }
.back a { text-decoration: none; }

.links { display: flex; flex-wrap: wrap; gap: 0.5rem 1.25rem; list-style: none; padding: 0; }
.site-footer { margin-top: 3rem; font-size: 0.85rem; }

@media (max-width: 480px) {
  .container { padding-top: 32px; }
  h1 { font-size: 1.9rem; }
}
```

- [ ] **Step 4: Write the home page**

`index.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Allan Tsay</title>
  <meta name="description" content="Allan Tsay: Computer Science coursework and game projects.">
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <main class="container">
    <header class="intro">
      <h1>Allan Tsay</h1>
      <p class="tagline">Computer Science · 4th year · UC Berkeley</p>
      <p>Hi! I'm a fourth-year Computer Science major. This site collects my coursework and projects, from graphics and operating systems to machine learning. Outside of class you'll find me playing taiko, baseball, or volleyball, or deep into a video game, which is how I ended up building one.</p>
    </header>

    <section id="coursework">
      <h2>Coursework</h2>
      <ul class="course-list">
        <li><a href="courses/cs184.html"><span class="code">CS 184</span>Computer Graphics and Imaging</a><span class="term">Fall 2026</span></li>
        <li><a href="courses/cs162.html"><span class="code">CS 162</span>Operating Systems and System Programming</a><span class="term">Fall 2026</span></li>
        <li><a href="courses/cs189.html"><span class="code">CS 189</span>Introduction to Machine Learning</a><span class="term">Spring 2026</span></li>
        <li><a href="courses/cs170.html"><span class="code">CS 170</span>Efficient Algorithms and Intractable Problems</a><span class="term">Fall 2025</span></li>
      </ul>

      <h3>Also completed</h3>
      <ul class="course-list plain">
        <li><span><span class="code">CS 61A</span>Structure and Interpretation of Computer Programs</span></li>
        <li><span><span class="code">CS 61B</span>Data Structures</span></li>
        <li><span><span class="code">CS 61C</span>Great Ideas in Computer Architecture</span></li>
        <li><span><span class="code">CS 70</span>Discrete Mathematics and Probability Theory</span></li>
      </ul>
    </section>

    <section id="games">
      <h2>Game Projects</h2>
      <article class="card">
        <!-- TODO: replace this slot with a screenshot:
        <img src="images/games/beetle-fighter.png" alt="Two beetle fighters mid-match"> -->
        <div class="img-slot">Screenshot coming soon</div>
        <div class="card-body">
          <!-- TODO: replace "Beetle Fighter" with the real title -->
          <h3>Beetle Fighter</h3>
          <p class="tags"><span class="tag">Unity</span><span class="tag">C#</span><span class="tag">Fighting game</span></p>
          <p>A Street Fighter–style fighting game set in the world of bugs, with a roster of beetle-inspired characters.</p>
          <!-- TODO: add links when ready:
          <p><a href="https://example.com/play">Play</a> · <a href="https://github.com/USERNAME/REPO">Source</a></p> -->
        </div>
      </article>
    </section>

    <!-- TODO: uncomment and fill in when ready
    <section id="contact">
      <h2>Contact</h2>
      <ul class="links">
        <li><a href="https://github.com/USERNAME">GitHub</a></li>
        <li><a href="https://www.linkedin.com/in/USERNAME">LinkedIn</a></li>
        <li><a href="mailto:EMAIL">Email</a></li>
        <li><a href="resume.pdf">Résumé</a></li>
      </ul>
    </section>
    -->

    <footer class="site-footer">© 2026 Allan Tsay</footer>
  </main>
</body>
</html>
```

- [ ] **Step 5: Write CS 184 page**

`courses/cs184.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS 184 · Allan Tsay</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <main class="container">
    <nav class="back"><a href="../index.html">← Back to home</a></nav>
    <header class="page-header">
      <p class="eyebrow">CS 184 · Fall 2026</p>
      <h1>Computer Graphics and Imaging</h1>
    </header>

    <section id="assignments">
      <h2>Assignments</h2>
      <!-- To add an image, replace an img-slot div with:
      <figure>
        <img src="../images/cs184/hw1-1.png" alt="Describe what the image shows">
        <figcaption>Short caption</figcaption>
      </figure>
      Rename the assignment titles below to match this semester's assignments. -->

      <article class="assignment">
        <h3>Homework 1: Rasterizer</h3>
        <!-- TODO: writeup for Homework 1 -->
        <p class="placeholder">Writeup coming soon.</p>
        <div class="gallery">
          <div class="img-slot">images/cs184/hw1-1.png</div>
          <div class="img-slot">images/cs184/hw1-2.png</div>
        </div>
      </article>

      <article class="assignment">
        <h3>Homework 2: MeshEdit</h3>
        <!-- TODO: writeup for Homework 2 -->
        <p class="placeholder">Writeup coming soon.</p>
        <div class="gallery">
          <div class="img-slot">images/cs184/hw2-1.png</div>
          <div class="img-slot">images/cs184/hw2-2.png</div>
        </div>
      </article>

      <article class="assignment">
        <h3>Homework 3: PathTracer</h3>
        <!-- TODO: writeup for Homework 3 -->
        <p class="placeholder">Writeup coming soon.</p>
        <div class="gallery">
          <div class="img-slot">images/cs184/hw3-1.png</div>
          <div class="img-slot">images/cs184/hw3-2.png</div>
        </div>
      </article>

      <article class="assignment">
        <h3>Homework 4: ClothSim</h3>
        <!-- TODO: writeup for Homework 4 -->
        <p class="placeholder">Writeup coming soon.</p>
        <div class="gallery">
          <div class="img-slot">images/cs184/hw4-1.png</div>
          <div class="img-slot">images/cs184/hw4-2.png</div>
        </div>
      </article>
    </section>

    <section id="overview">
      <h2>Course Overview</h2>
      <p>CS 184 covers the foundations of computer graphics: how 2D and 3D scenes are represented, transformed, and turned into images. Topics include rasterization and sampling, geometric modeling with curves and meshes, ray tracing and physically based rendering, and animation and physical simulation.</p>
    </section>

    <footer class="site-footer">© 2026 Allan Tsay</footer>
  </main>
</body>
</html>
```

- [ ] **Step 6: Write CS 162 page**

`courses/cs162.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS 162 · Allan Tsay</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <main class="container">
    <nav class="back"><a href="../index.html">← Back to home</a></nav>
    <header class="page-header">
      <p class="eyebrow">CS 162 · Fall 2026</p>
      <h1>Operating Systems and System Programming</h1>
    </header>

    <section id="projects">
      <h2>Projects</h2>
      <p class="placeholder">Project writeups coming soon.</p>
      <!-- TODO: add one block per project:
      <article class="assignment">
        <h3>Project 1: Name</h3>
        <p>What you built, how it works, and what you learned.</p>
      </article>
      -->
    </section>

    <section id="overview">
      <h2>Course Overview</h2>
      <p>CS 162 explores how operating systems manage hardware and support running programs. Topics include processes and threads, concurrency and synchronization, CPU scheduling, virtual memory, file systems, and I/O, with large team projects that extend a real teaching operating system.</p>
    </section>

    <footer class="site-footer">© 2026 Allan Tsay</footer>
  </main>
</body>
</html>
```

- [ ] **Step 7: Write CS 170 page**

`courses/cs170.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS 170 · Allan Tsay</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <main class="container">
    <nav class="back"><a href="../index.html">← Back to home</a></nav>
    <header class="page-header">
      <p class="eyebrow">CS 170 · Fall 2025</p>
      <h1>Efficient Algorithms and Intractable Problems</h1>
    </header>

    <section id="overview">
      <h2>Course Overview</h2>
      <p>CS 170 is about designing and analyzing algorithms and understanding the limits of efficient computation. Topics include divide and conquer, graph algorithms, greedy methods, dynamic programming, linear programming and network flow, and NP-completeness, along with approaches for hard problems such as approximation algorithms.</p>
    </section>

    <footer class="site-footer">© 2026 Allan Tsay</footer>
  </main>
</body>
</html>
```

- [ ] **Step 8: Write CS 189 page**

`courses/cs189.html`:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>CS 189 · Allan Tsay</title>
  <link rel="stylesheet" href="../css/style.css">
</head>
<body>
  <main class="container">
    <nav class="back"><a href="../index.html">← Back to home</a></nav>
    <header class="page-header">
      <p class="eyebrow">CS 189 · Spring 2026</p>
      <h1>Introduction to Machine Learning</h1>
    </header>

    <section id="sushigpt">
      <h2>SushiGPT</h2>
      <h3>What it is</h3>
      <!-- TODO: describe SushiGPT: the goal, the data, the model, and results -->
      <p class="placeholder">Project description coming soon.</p>

      <h3>What I learned</h3>
      <!-- TODO: replace with a list of takeaways, e.g.
      <ul>
        <li>...</li>
      </ul> -->
      <p class="placeholder">Takeaways coming soon.</p>
    </section>

    <section id="overview">
      <h2>Course Overview</h2>
      <p>CS 189 covers the theory and practice of machine learning. Topics include linear and logistic regression, classification, regularization, and the bias–variance tradeoff, as well as decision trees, neural networks, dimensionality reduction, and clustering, with an emphasis on the math behind each method and on building models from real data.</p>
    </section>

    <footer class="site-footer">© 2026 Allan Tsay</footer>
  </main>
</body>
</html>
```

- [ ] **Step 9: Add image folders**

Run: `mkdir -p images/cs184 images/games && touch images/cs184/.gitkeep images/games/.gitkeep`

- [ ] **Step 10: Run the checker to verify it passes**

Run: `python3 tests/check_site.py`
Expected: `OK: 5 pages checked`, exit 0.

- [ ] **Step 11: Verify the checker catches the Review Focus link failures**

Run:
```bash
cp index.html index.html.bak
sed -i '' 's#href="css/style.css"#href="/css/style.css"#; s#href="courses/cs170.html"#href="courses/"#' index.html
python3 tests/check_site.py; echo "exit=$?"
mv index.html.bak index.html
python3 tests/check_site.py
```
Expected: first run prints `root-absolute link '/css/style.css'`, `broken link 'courses/'`, and `no link to courses/cs170.html`, then `exit=1`; after restore, `OK: 5 pages checked`.

- [ ] **Step 12: Commit**

```bash
git add tests css index.html courses images
git commit -m "Add portfolio home page, course pages, and site checker"
```

---

### Task 2: Visual check at phone and desktop widths, light and dark

**Files:**
- Modify (only if a defect is found): `css/style.css`

**Interfaces:**
- Consumes: the pages and stylesheet from Task 1.
- Produces: screenshots in the session scratchpad (not committed).

- [ ] **Step 1: Take screenshots**

Run (set `OUT` to the session scratchpad directory):
```bash
CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
OUT="$SCRATCHPAD/shots"; mkdir -p "$OUT"
for page in index courses/cs184 courses/cs189; do
  name=$(basename $page)
  "$CHROME" --headless --hide-scrollbars --window-size=375,1800 --screenshot="$OUT/$name-phone.png" "file://$PWD/$page.html"
  "$CHROME" --headless --hide-scrollbars --window-size=1280,1400 --screenshot="$OUT/$name-desktop.png" "file://$PWD/$page.html"
  "$CHROME" --headless --hide-scrollbars --force-dark-mode --window-size=375,1800 --screenshot="$OUT/$name-phone-dark.png" "file://$PWD/$page.html"
done
ls "$OUT"
```
Expected: 9 PNG files. If Chrome is not installed, run `python3 -m http.server 8000` and ask the user to check `http://localhost:8000` at phone width in their browser's dev tools instead.

- [ ] **Step 2: Inspect each screenshot**

Open every PNG with the Read tool. Pass criteria:
- Phone: no text cut off at the right edge; long course names wrap under the course code; terms wrap onto their own line rather than overflowing.
- Dark: dark background, light text, dashed placeholder boxes and dividers visible.
- Desktop: content is a centered column ~720px wide; CS 184 gallery shows 2+ slots per row.

- [ ] **Step 3: Fix any defect in `css/style.css`, re-run Step 1, re-inspect**

Only if Step 2 found a defect. Re-run `python3 tests/check_site.py` afterwards; expected `OK: 5 pages checked`.

- [ ] **Step 4: Commit (only if CSS changed)**

```bash
git add css/style.css
git commit -m "Fix layout issues found in visual check"
```

---

## After implementation

Tell the user how to deploy: push `main` to GitHub, then in the repo's **Settings → Pages**, set Source to "Deploy from a branch", branch `main`, folder `/ (root)`.
