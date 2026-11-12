# Visual language

## 1. Art directions (22; tokens in `scripts/_common.py`)

Each direction = colour tokens + type pair + shape language (corner radius, card style) + default
frame + cover style + metadata for selection. Override any token with `theme {}`; override the
frame with `frame`, the cover with `style` on the cover slide.

| Direction | Tone | Formality | Mood | Type (head / body) | Shape | Best for | Avoid for |
|---|---|---|---|---|---|---|---|
| consulting-navy | formal | high | structured, answer-first | Cambria / Calibri | sharp, tint | case comps, readouts, SteerCos | personal stories |
| boardroom-oxblood | formal | high | senior, measured | Cambria / Calibri | sharp, border | board asks, IC, law, finance | youth audiences |
| mono-ink | formal | high | austere, academic | Cambria / Calibri | sharp, border, clean | research, thesis, policy | energetic launches |
| public-sector | formal | high | plain, high contrast | Arial / Arial | sharp, clean | government, NGOs, big halls | luxury |
| finance-emerald | formal | high | trustworthy, banking | Cambria / Calibri | small radius, border | banking, investors, valuation | consumer marketing |
| editorial-warm | refined | medium | warm, human, rigorous | Cambria / Calibri | editorial frame | interviews, stories, memorable case decks | dashboards |
| forest-sage | refined | medium | calm, natural | Cambria / Calibri | soft radius | sustainability, health, teaching, FMCG | nightlife |
| gallery-white | refined | medium | lots of air, few words | Bookman Old Style / Calibri | clean, minimal cover | portfolios, talk openers | dense readouts |
| nordic-calm | refined | medium | soft, considered | Calibri / Calibri | rounded, clean | people/HR, culture, offsites | hard sales |
| terracotta-editorial | refined | medium | warm editorial | Century Schoolbook / Calibri | rounded, split cover | hospitality, food, lifestyle, NGOs | finance |
| luxe-noir | refined | high | black and gold | Palatino Linotype / Calibri | editorial | luxury, awards, galas | public sector |
| heritage-india | refined | medium | indigo + marigold, no clichés | Cambria / Calibri | border, editorial | Indian brand cases, cultural events, Bharat stories | global tech launches |
| modern-teal | bold | medium | product-clean | Calibri / Calibri | rounded, shadow, gradient cover | product, tech, QBRs, SaaS | heritage brands |
| bold-signal | bold | medium | one loud colour | Arial / Arial | sharp, clean | pitches, manifestos, one-number stories | sombre topics |
| dark-stage | bold | medium | keynote on dark | Calibri / Calibri | rounded, clean | keynotes, AI/tech talks | printing |
| electric-launch | bold | low | energetic launch | Arial / Calibri | rounded, shadow | launches, demo days, hackathons | governance |
| blueprint | bold | medium | technical drawing | Arial / Arial | sharp, clean | engineering, systems | HR, consumer |
| night-terminal | creative | low | console green | Courier New / Arial | sharp, clean | dev talks, security | non-technical execs |
| poster-yellow | creative | low | loud poster | Arial / Arial | sharp, minimal cover | manifestos, campaigns, recruitment | sensitive topics |
| coral-studio | creative | low | playful, design-led | Arial / Calibri | very rounded, shadow | marketing, social, D2C | audits |
| pastel-friendly | creative | low | soft, friendly | Arial / Calibri | very rounded, shadow | education, wellness, club socials | finance |
| campus-bright | creative | low | high-energy, youthful | Arial / Calibri | rounded, gradient cover | club events, fests, orientation | investors |

Selection: decision-trees.md T8. Preview before committing: `preview_directions.py`.
Font QA: compatible clones may be available (Carlito, Caladea, Liberation and TeX Gyre).
Run `env_check.py` in the actual environment before trusting measurements; Palatino via Pagella is
close, not identical (`fonts_qa: approximate` on luxe-noir: leave ~10% slack). Never default to Aptos,
Georgia, Trebuchet, Garamond, Impact or Arial Black for body text: their QA substitutes have
different widths (Anthropic pptx skill). Use them only if the user asks, with slack.

## 2. Frames and covers

| Frame | What it does | Use for |
|---|---|---|
| classic | tracked-caps kicker, title, full-width neutral hairline | consulting, long document decks |
| clean | kicker, title, no rule, more air | modern, creative, talk |
| editorial | accent kicker, larger serif title, no rule | stories, research narratives |
| rail | section label rotated in the left margin, hairline kept | long documents needing quiet wayfinding |

Covers: `field` (solid dark), `gradient` (diagonal dark → second stop; reads less like a template;
office-kit's consulting reference), `split` (dark panel + real photograph or the key figure),
`minimal` (light; big title; figure in accent). Dividers follow the gradient when the cover does.
Talk-mode dividers carry only the question.

The rule-under-headline question (sources disagree): Anthropic's skill calls accent lines under
titles an AI tell; office-kit's McKinsey comparison found a thin full-width rule under the headline
is the default in long external decks. Resolution: never a short coloured bar under a title; a
full-width neutral hairline only in the `classic`/`rail` frames; no rule in `clean`/`editorial`.

## 3. Colour

- One primary (structure: covers, headers, main series), one accent (meaning: the answer, the
  recommended option, the problem), neutrals for everything else. If everything is accented,
  nothing is. Semantic green/red only for good/bad deltas and status, sparingly (in the McKinsey
  reference red appeared on two slides of 68).
- Dominance over equality: one colour carries 60-70% of the visual weight (Anthropic).
- Highlight one, grey the rest in every chart and diagram.
- Three background modes, each with a job: white (exhibits), light panel (commentary, so-what,
  side panels), dark (cover, dividers, agenda spine, framework rail). Don't invent a fourth.
- Contrast: body text ≥ 4.5:1, large text ≥ 3:1 (WCAG AA). The builder flips text to ink or white
  when a fill is too light or dark for it; lint reports what remains.
- Don't default to cream/beige grounds for a generic deck (Anthropic); the warm directions use them
  on purpose for stories and editorial registers.
- Don't rely on colour alone: label the highlighted bar, use chips with words.

## 4. Type

| Text | Document | Talk | Teaching / big room |
|---|---|---|---|
| Title | 25pt (floor 20); editorial 28pt | 30pt+, ≤ 55 chars | 32pt+ |
| Body | 14-16pt, floor 12 | 18pt floor | 22pt+ (room depth: ≤ 20 ft 14pt, 30 ft 18pt, 50 ft 24pt, further 28pt; Kalmstrom) |
| Tables, axis labels | 12-13pt, floor 11 | 16pt+ | 18pt+ |
| Source, footnotes, page | 9-10pt | 10pt+ | 12pt+ |
| Hero number | 96-110pt | 110pt+ | 120pt+ |

Treat the floors as starting ranges, then test on representative slides: room size, screen,
script and density all move the right size.

**Fonts are a deployment constraint, not just a pairing.** Pick for readability, brand fit,
language and glyph coverage (₹, Devanagari, accents) and reliable rendering. Before trusting fit,
run `env_check.py`: it shows which file each font is measured with (metric clone, close clone or
substitute). When substitution happens anywhere (here, in the browser, on the machine that opens
the deck), recheck wrapping, table alignment and chart labels. Use tabular figures in tables.
Embedding a font in the PPTX depends on its licence; when unsure, stay with fonts the destination
has. A familiar font with clear hierarchy beats a distinctive one that breaks the deck: don't
reject a font only because it is common.

Two typefaces max (a third only for code). Three sizes per slide. Left-align body; centre only
single lines (covers, big numbers, quotes). Authored line breaks at meaning boundaries; no 1-3
character last lines.

## 5. Grid and spacing

16:9 at 13.333 × 7.5 in (960 × 540 pt). Margins 0.6 in. Kicker 0.38 in; title from 0.7 in; rule
~1.5 in; body 1.75 → 6.78 in (→ 6.0 with a so-what); source 6.84 in; footer and page 7.14 in.
Spacing steps 4 · 8 · 16 · 24 · 36 · 56 pt; gaps between groups ≈ 3× gaps within a group
(Kalmstrom). Keep one left edge for every title and body. Cards in a row share top edge and height.

## 6. Shape language

Corner radius and card style are part of a direction's identity (Julien339): sharp + tint
(consulting), sharp + border (boardroom, finance), small radius (editorial), rounded + shadow
(SaaS, launch), very rounded + shadow (friendly, playful). Don't mix languages in one deck.
Shadows: at most one or two elevated surfaces per slide, subtle (the builder's `shadow` cards).

## 7. Imagery and icons

- Purpose test: add a visual element only when it explains, evidences, identifies or orients.
- Real photographs of the actual subject > simple glyph badges > nothing > generic stock or AI art.
  Crop, never stretch; alt text always; credit lines and permitted use recorded for assets you did
  not make.
- Screenshots, source figures, historical documents and product interfaces are fine when they are
  the evidence: add a readable label, the source and alt text that explains them. Authored slide
  text stays editable, never flattened into a picture.
- Keep apart, and label: documentary photos vs illustrations, real interfaces vs mockups, technical
  diagrams vs decoration, verified charts vs illustrative ones. A clearly labelled conceptual
  illustration is fine; AI imagery presented as a real facility, person, customer, product or
  result never is. Never photos of public figures pulled from the web.
- Icons: glyph badges (▲ ▼ ✓ ✗ ★ → ! ◎ ●) in a filled circle render in every Office font; no emoji
  (they render inconsistently). `columns` and `cards` take `icon` names: up, down, check, cross,
  star, arrow, warn, plus, minus, question, dot, diamond, money, rupee, percent, time, target.
- One visual motif repeated across the deck (rounded photo frames, glyph badges, the highlight bar):
  never a decorative colour stripe (Anthropic).
- A richer icon set (one consistent SVG family with semantic names, stroke weight, size rules and
  licence notes) is not bundled yet; until it is, use glyph badges or none rather than mixing icon
  styles from different sources.

**Theme, composition and visual language are different levers.** A direction sets the theme
(colours, fonts, corners). Composition decides what dominates and where information sits; visual
language decides whether the deck speaks through photography, diagrams, typography, documents or
real work (campaign creative, interface screens, site photos). Narrative rhythm decides how density
and emphasis change across the deck. When a deck needs a genuinely different feel, change
composition and visual language, not just the palette; use `custom` slides for compositions the
standard types can't make.

## 8. Charts and tables

- The headline states what the chart means; the chart proves it.
- Units in the exhibit label or axis; axis at zero for bars; say so if a line axis is not.
- Data labels on single-series bars, columns, pie/doughnut; off for dense lines; legend only for
  multi-series (right side; a top or bottom legend steals height). Direct labels beat legends.
- One series in the primary, the subject in the accent, comparison in grey.
- Target as a dashed constant series (`target`), never a line shape laid over the chart.
- Never two scales on one axis; split into two charts (builder warns).
- Doughnut/pie only for ≤ 4 parts summing to a whole, explicit colours per slice.
- Tables: one header row, units in the header, numbers right-aligned with consistent decimals,
  thin horizontal rules (no grid), `total_row`, at most one highlighted row, ≤ 2-line cells.

## 9. Anti-patterns (AI-slop and amateur tells)

Layout: everything centred; the same layout slide after slide; identical card grids everywhere;
a "pretty" slide with nothing to say; visuals added only to fill space; four thin boxes on a talk
slide. Decoration: accent bars under titles, edge stripes, header/footer bars, purposeless drop
shadows, glassmorphism, glows, gradients on every slide, AI stock art, emoji icons. Colour: purple
gradient on white, generic indigo #6366F1, rainbow categorical charts, three accents fighting.
Type: Inter/Roboto/Arial as display in HTML decks (in PPTX the safe fonts are deliberate);
centred body text; 14pt body under a 16pt title (no hierarchy). Content: topic-label titles,
numbers that disagree, invented sources or fictional institutes, uniformly-shaped case studies,
the same closing clause on every slide, a "Thank you" close with no ask.

## 10. Signature moves (use them when the material supports them; never manufacture one)

One signature exhibit the room will describe afterwards (a sharp waterfall, a mekko, a
one-number slide) · a human hook (a real person, quote or moment, not a market statistic) · one
number to remember · unexpected but credible styling (consulting grammar on a warm editorial or
heritage skin) · a crisp ask (what, who, by when, cost, the number it moves) · personal voice in
personal decks · a build-up diagram revealed over 3-5 talk slides.

## 11. HTML font pairs (only when HTML is the final format; Google Fonts are fine there)

Drafts use the direction's own fonts so they predict the final PPTX. When the approved deck stays
HTML (routes.md §F), set `"html_fonts": {"heading": "Fraunces", "body": "Work Sans", "url":
"<Google Fonts css2 URL>"}` in the spec. Those web fonts then lead, with the direction's fonts as
fallback.

| Feel | Display / body | Tokens to start from |
|---|---|---|
| Warm editorial | Fraunces / Work Sans | editorial-warm |
| Quiet luxury | Cormorant Garamond / IBM Plex Sans | luxe-noir |
| Bold poster | Archivo Black / Space Grotesk | bold-signal, poster-yellow |
| Modern product | Manrope / Manrope | modern-teal, electric-launch |
| Swiss / research | Inter Tight / Inter (body only) | mono-ink |
| Playful | Plus Jakarta Sans / Plus Jakarta Sans | coral-studio, pastel-friendly |
| Engineering | JetBrains Mono / IBM Plex Sans | night-terminal, blueprint |
| Heritage | Playfair Display / Mukta (Devanagari-ready) | heritage-india |

(Pairs adapted from frontend-slides' font table plus our own; verify the families on Google Fonts
before use.)

## 12. Lessons from the template libraries (Gamma Design Playbook)

- Gamma Mandate (verified by a 7-card generation, Nov 2026): tracker, action title, hairline,
  numbered exhibits with native charts, ledger table with the client row tinted, recommended option
  in the accent, so-what boxes, source lines, Gantt with owners, notes, running footer. That grammar
  is what the builder's `classic` frame encodes. Its failures (invented sources, exhibits that did
  not tie out, a roadmap starting before today, an extra cover card) are why the facts model, the
  date check and the read-back checklist exist.
- Canva gives the look, not the argument (topic titles, decorative placeholder charts, no exhibit
  numbers, so-what or sources): borrow the look, impose the grammar.
- Manus composes every slide with a diagram (copy that) but shows density without hierarchy,
  generic invented numbers, no sources and AI-looking imagery (don't).
