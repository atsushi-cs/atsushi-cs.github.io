# Portfolio Site — Design

## Goal
A simple static portfolio for Allan Tsay showcasing CS coursework and game projects, hosted on GitHub Pages.

## Tech
- Plain HTML + one shared CSS file. No JavaScript, no build step, no dependencies.
- Deployed via GitHub Pages from the `main` branch root.

## File structure
```
index.html
courses/cs184.html
courses/cs162.html
courses/cs170.html
courses/cs189.html
css/style.css
images/cs184/   (user adds assignment images)
images/games/   (user adds game screenshots)
```

## Main page (`index.html`)
1. **Intro** — name heading + short drafted paragraph: Allan Tsay, 4th-year Computer Science major; interests taiko, baseball, volleyball, gaming.
2. **Coursework** — list of courses with term labels:
   - Linked to detail pages: CS 184 Computer Graphics (Fall 2026), CS 162 Operating Systems (Fall 2026), CS 189 Intro to Machine Learning (Spring 2026), CS 170 Efficient Algorithms and Intractable Problems (Fall 2025).
   - Listed without a page: CS 61A, CS 61B, CS 61C, CS 70 (no terms given; none shown).
3. **Game Projects** — one card: "Beetle Fighter" (placeholder title), Unity, bug-themed Street Fighter–style fighter with beetle-inspired characters; screenshot slot (`images/games/`) and link slot.
4. **Contact** — present in markup but commented out until the user supplies links.

## Course pages (shared layout)
- Header with "← Back to home" link, course code + name, term.
- Course-specific content (below).
- **Course Overview** section at the bottom: 2–3 sentence drafted summary of the course, editable.

| Page | Content above overview |
|---|---|
| CS 184 | One section per assignment: title, short writeup, image gallery. Placeholder slots labeled for images in `images/cs184/`. |
| CS 162 | "Project writeups coming soon" note + empty project section template (commented). |
| CS 170 | None (overview only). |
| CS 189 | SushiGPT section: "What it is" and "What I learned" with `TODO` placeholder text. |

## Style
- Minimal, single readable column (~720px max), system font stack.
- Colors as CSS custom properties; dark mode via `prefers-color-scheme`.
- Responsive: works at phone width, no horizontal scroll; image galleries use a wrapping grid.
- Missing images render as a labeled dashed placeholder box, not a broken image.

## Placeholders the user fills in later
All marked with `TODO` in HTML: CS 184 assignment writeups/images, CS 162 project writeups, SushiGPT details, game title/screenshot/link, contact links.

## Verification
- Every page opens without errors; all internal links resolve (checked by script).
- Layout checked at desktop and ~375px widths.
