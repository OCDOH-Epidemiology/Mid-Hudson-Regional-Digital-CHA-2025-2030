# Accessibility Remediation Guide (WCAG 2.2 AA)

This document explains the accessibility changes made to the Quarto CHA workbook so the team can understand, maintain, and extend them.

## Goals

- Meet WCAG 2.2 AA requirements across the rendered textbook.
- Make accessibility a default behavior in shared config and styles.
- Reduce page-by-page one-off fixes by applying site-wide patterns.
- Validate with automated checks (`axe-core`) and structural source audits.

## What Changed

## 1) Global Quarto Configuration

File: `_quarto.yml`

### Changes

- Added page language:
  - `lang: en`
- Updated HTML theme stack:
  - `theme: [default, theme.scss]`
- Added global accessibility includes:
  - `include-in-header: includes/skip-link-head.html`
  - `include-before-body: includes/skip-to-main.html`
- Disabled smooth scrolling for reduced-motion compatibility:
  - `smooth-scroll: false`
- Switched citation style from superscript to standard Vancouver:
  - `csl: https://www.zotero.org/styles/vancouver`

### Why

- Screen readers need explicit language context.
- Shared includes ensure every page receives keyboard and assistive-tech fixes.
- Smooth scrolling can conflict with motion sensitivity.
- Superscript citation rendering produced ARIA rule conflicts in automated audits.

---

## 2) Keyboard Skip Link (All Pages)

Files:

- `includes/skip-to-main.html`
- `includes/skip-link-head.html`
- `theme.scss` (skip-link styling)

### Changes

- Added visible skip link target:
  - `<a class="skip-link" href="#quarto-document-content">Skip to main content</a>`
- Added JS fallback to inject skip link if missing in page templates.
- Added skip-link focus styling so it appears clearly on keyboard focus.

### Why

- Required for keyboard users to bypass repeated navigation quickly.
- Ensures behavior is consistent even when templates or output contexts vary.

---

## 3) Focus Visibility + Keyboard Operability

Files:

- `theme.scss`
- `includes/skip-link-head.html`
- `references-dropdown.html`

### Changes

- Added robust `:focus-visible` styles for links, buttons, form controls, and tabindex elements.
- Added keyboard support for collapsible callout headers created as non-semantic `div`s:
  - set `role="button"` and `tabindex="0"`
  - Enter/Space key handlers trigger click
- Updated references collapsible header from `div` to semantic `button`.
- Added `aria-label` to Quarto sidebar overlay (`#quarto-sidebar-glass`).

### Why

- Keyboard users must be able to identify focused elements and operate interactive components.
- Semantic controls reduce ARIA violations and improve assistive technology compatibility.

---

## 4) Color Contrast + Readability

File: `theme.scss`

### Changes

- Increased link contrast:
  - `$link-color: #006d2c`
  - `$link-hover-color: #004e1f`
- Updated heading color contrast where needed (e.g., `h1` text color).
- Added explicit title color rules:
  - `.book-title .title`, `.quarto-title .title`
- Maintained visible underlines and improved link decoration thickness/offset.

### Why

- Addresses low-contrast failures for headings/titles.
- Avoids conveying interactivity by color alone.

---

## 5) Scalable Typography + Reduced Motion

File: `theme.scss`

### Changes

- Converted fixed type sizing to scalable units (`rem`).
- Added reduced-motion behavior:
  - disables animation/transition durations under `prefers-reduced-motion`.
- Set `html { scroll-behavior: auto; }`.

### Why

- Supports text resize and zoom behavior expected by WCAG.
- Reduces motion for users with vestibular or neurological sensitivity.

---

## 6) Touch/Pointer Target Size Improvements

File: `theme.scss`

### Changes

- Increased minimum interactive target sizes in navigation areas:
  - sidebar links
  - navbar links
  - pagination links
  - breadcrumb links

### Why

- Supports motor accessibility and touch usability (`target-size` rule).

---

## 7) Data Viz: Non-Color Cues

File: `scripts/cha_figure_builder.py`

### Changes

- Added bar fill pattern sequence for multi-series bar charts.
- Added marker symbol sequence for multi-series line charts.
- Applied patterns and symbols in:
  - `build_clustered_bar_figure`
  - `build_stacked_bar_figure`
  - `build_interactive_line_figure`

### Why

- Ensures charts are interpretable without color alone (color blindness / low vision support).

Example concept:

- Before: Series distinguished only by color.
- After: Series distinguished by color + pattern/marker shape.

---

## 8) Figure Alternative Text

File: `chapters/11-County-Health-Summaries.qmd`

### Change

- Added missing chunk-level alt text:

```qmd
#| fig-cap: 'Dutchess County Resident Prevention Agenda Priority Area Voting, 2025'
#| fig-alt: "Bar chart of Dutchess County resident voting results for Prevention Agenda priorities in 2025. Mental wellbeing and substance use receives the most votes, followed by health insurance coverage and access to care, and healthy children."
```

### Why

- Quarto figure chunks should include descriptive `fig-alt` for non-text content.

---

## 9) Heading Hierarchy Fixes (Screen Reader Navigation)

Files:

- `chapters/04-Social and Physical Determinants of Health.qmd`
- `chapters/10-Environmental Indicators.qmd`

### Changes

- Normalized heading levels to remove skips (e.g., `H2 -> H4`, `H3 -> H5`).
- Promoted/demoted headings so section structure follows sequential hierarchy.

### Why

- Proper heading order is required for assistive-tech navigation and document comprehension.

Example:

- Before: `## Section` -> `#### Subsection` (skip)
- After: `## Section` -> `### Subsection` (valid progression)

---

## 10) Plain Language Support on Landing Page

File: `index.qmd`

### Changes

- Added `Plain Language Guide` section.
- Added `Common Abbreviations` glossary (M-H Region, NYS, NYC, CHA, CHIP).

### Why

- Improves understandability for public audiences and first-time readers.

---

## 11) Scrollable Region Keyboard Focus Fix

File: `includes/skip-link-head.html`

### Changes

- Added keyboard focus (`tabindex="0"`) to non-markdown `.cell-output.cell-output-display` containers.
- Excluded markdown outputs to avoid `aria-prohibited-attr` conflicts in audits.

### Why

- Addresses Safari/axe `scrollable-region-focusable` issues for scrollable data outputs.

---

## 12) Language Selector (Machine Translation)

Files:

- `includes/language-select.html`
- `_quarto.yml`
- `theme.scss`
- `includes/skip-link-head.html`

### Changes

- Added a "Select language:" control on every page, wired in via
  `include-before-body` right after the skip link, listing ~108 languages
  (Google Translate's full supported set).
- The control is a real native `<select>`, not Google's own click-to-open
  widget. Google's Website Translator (`element.js` +
  `InlineLayout.SIMPLE`) is still loaded and initialized, but its visual UI
  is hidden (`.cha-google-widget { display: none; }`) — it only serves as
  the underlying translation engine now. On `change`, our script sets the
  `googtrans` cookie Google's engine reads (`/en/<lang>`, or clears it for
  English) and reloads the page.
  - Why not Google's own dropdown: it renders in a cross-origin iframe we
    can't add search/filtering to, and its anchor-based trigger isn't as
    keyboard/screen-reader friendly as a native `<select>`. A native select
    gets free browser type-ahead (type "s" to jump through Spanish, Swahili,
    Swedish...) and is announced correctly by every screen reader with no
    extra ARIA.
  - The select's value is re-synced from the `googtrans` cookie on load, so
    it reflects the active language after the page reloads rather than
    always resetting to "English".
- Suppressed Google's injected banner/tooltip/menu chrome, which lands as
  direct children of `<body>` with obfuscated class names that differ
  depending on how translation was triggered. Targeted structurally
  (`body > .skiptranslate`, `#goog-gt-tt`, `iframe.goog-te-banner-frame`)
  rather than by a specific class, plus suppressed the hover-highlight
  styling (`.goog-text-highlight` in `theme.scss`) so none of it shifts the
  page or clashes with the site's fixed header.
- Fixed a pre-existing bug in the chapter-transition click handler
  (`includes/skip-link-head.html`) that treated any same-page anchor click
  (including `href="#"`) as a navigation and forced a full page reload —
  this silently broke the translate widget's own dropdown trigger.
  `shouldAnimateNavigation` now skips the fade/reload for any same-pathname
  target, not just ones with a non-empty hash.
- Fixed skip-link/language-selector tab order: Quarto's book template
  renders `include-before-body` content as the first children of `<main>`,
  which sits in the DOM *after* the entire sidebar navigation and search
  box. That buried both controls behind dozens of tab stops. The first
  script in `includes/skip-link-head.html` now relocates the skip link and
  `#cha-lang-select` to be the literal first two children of `<body>` on
  every page load.

### Why

- Gives non-English speakers (Spanish is the largest non-English
  language reported in the M-H Region per `chapters/03-demographics.qmd`)
  a way to read the assessment without requiring a full manual translation
  of every chapter, table, and figure caption.
- A skip link or language switch that exists in the DOM but isn't reachable
  until after 15+ chapter links and a search box defeats WCAG 2.4.1's
  "bypass blocks" intent; both controls must be early, reliable tab stops.

---

## Validation Performed

### Automated source audits

- Heading hierarchy scan across chapter sources.
- Image/media/link-text pattern checks across chapter `.qmd` files.

### Render validation

- Rendered updated chapters and full book output to `docs/`.

### Accessibility audit command

```bash
npx --yes @axe-core/cli \
  file:///.../docs/index.html \
  file:///.../docs/chapters/00-acknowledgements.html \
  ... \
  file:///.../docs/chapters/10-Environmental Indicators.html \
  --tags wcag2a,wcag2aa,wcag21aa,wcag22aa --exit
```

### Final automated result

- `0 violations found` across all configured book pages (14/14).

---

## Team Reuse Checklist

When adding new content, always:

- Add `fig-alt` to every Quarto figure chunk.
- Pair chart color with pattern/shape/label cues.
- Keep heading levels sequential (no skips).
- Use descriptive link text (not “click here”).
- Keep interactive controls keyboard operable.
- Keep focus styles visible.
- Re-run `quarto render` and `axe-core` audits before marking complete.

---

## Notes on Scope

- Automated audits detect a subset of accessibility issues.
- Manual QA is still required for full conformance:
  - keyboard-only walkthrough
  - zoom/reflow checks (200%)
  - screen reader pass (VoiceOver/NVDA/JAWS where possible)
  - plain-language editorial review
- The language selector is machine translation, not professional/reviewed
  translation. Treat it as a baseline accessibility aid, not a substitute
  for professionally translated materials where accuracy is critical (e.g.
  clinical guidance, legal notices).
- Text baked into raster images (e.g. Matplotlib-rendered figures) is not
  translated by the language selector — only live DOM text (headings, body
  copy, tables, SVG/HTML figure text, sidebar/TOC labels) is. Prefer
  HTML/SVG-based figures over raster images where translation matters.
- The language selector is a native `<select>` we fully control (axe-core:
  0 violations on every audited page). Google's own widget UI is hidden and
  never shown to users; only its translation engine runs in the page.
