# Portfolio Site — Design

## Goal
A simple static portfolio for Allan Tsay showcasing CS coursework and game projects, hosted on GitHub Pages.

## Tech
- Plain HTML + one shared CSS file. No JavaScript, no build step, no dependencies.
- Deployed via GitHub Pages from the `main` branch root.

## File structure
```
index.html
projects.html
about.html
resume.pdf
courses/cs184.html
courses/cs162.html
courses/cs170.html
courses/cs189.html
css/style.css
images/cs184/   (user adds assignment images)
images/games/   (user adds game screenshots)
```

## Main page (`index.html`)
Kept deliberately short; details live on the Projects and About pages.
1. **Intro** — name, tagline, two-sentence summary, GitHub/LinkedIn logo links and a Résumé link (`resume.pdf`).
2. **Projects** — two featured projects (sushiGPT, Beetle Fighter) with one-line blurbs, plus "All projects →".
3. **Coursework** — the four courses with detail pages, plus a link to About.

## Projects page (`projects.html`)
sushiGPT summary (links to the CS 189 page), the Beetle Fighter card, and systems/graphics projects (RISC-V emulator, Pintos, rasterizer).

## About page (`about.html`)
Longer intro and hobbies, résumé link, Experience, Leadership, Skills, and courses without detail pages (CS 61A, 61B, 61C, 70).

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
