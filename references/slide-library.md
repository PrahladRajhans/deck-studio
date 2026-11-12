# Slide library (44 types plus `custom`)

For each type: use it when / avoid it when / content limits / notes. Field reference:
`build_deck.py --schema`. Visual reference: `assets/examples/*-preview.png` and the showcase spec
`assets/examples/showcase-new-types.json` (every type rendered on one grid).

Global limits (Kalmstrom, johnnyknocke, office-kit): ≤ 7 bullets or ≤ 6 tiles per slide · 4-5 items
per visual group · document titles ≤ 2 lines (~15 words) · talk titles ≤ 55 characters · line length
≤ 75 characters · card body ≤ ~60 characters per bullet · process step ≤ ~50 characters ·
timeline/milestone label ≤ ~30 characters · statement ≤ ~100 characters · one emphasis per slide.
Over the limit (the overflow rule): first remove redundancy, then restructure, split, or move supporting
detail to the notes or an appendix. Reduce type only within the floors. Never hide overflow or silently
drop evidence. The HTML draft flags any slide whose text cannot fit or falls below 9pt.

Every type carries a semantic contract as well as a geometric one: a `compare` uses the same criteria,
units and time horizon on both sides; a `waterfall`'s steps reconcile to its totals; an `options`
scorecard uses weights the user agreed (never invented ones); a `process` arrow means a real sequence;
a `big_number` has its denominator and period. A balanced-looking slide that breaks its contract
misleads.

## Openers, structure, closers

| Type | Use when | Avoid when | Notes |
|---|---|---|---|
| `cover` | always | — | Title = answer (D) or promise (T). `figure` = the one number. Styles: field, gradient, split (+ photo), minimal |
| `exec_summary` | document decks of 6+ slides | talk mode | 3-5 rows, one per chapter, same order as the body; `ref` gives live page numbers; write it last |
| `agenda` | long document decks | talk mode (builder warns) | reuse per chapter with `active` = running spine |
| `divider` | every 3-6 body slides in long decks | two in a row | talk mode: only the audience's next question; the next slide starts answering it |
| `framework` | a thesis with 3-4 supports | data slides | dark left rail; use for the chapter's key idea, not everything |
| `statement` | one idea to land | lists | claim may be the headline (no title) |
| `quote` | a real voice | invented or paraphrased quotes | verbatim only; attribution with role |
| `question` | quiz, poll, "think about it", talk hook | document decks | answer on the next slide, never on the same one |
| `closing` | always | "Thank you" alone | repeats the key figure next to the ask or the action |

## Numbers

| Type | Use when | Avoid when | Notes |
|---|---|---|---|
| `big_number` | one number carries the slide | the number needs a trend | add 2-3 proof points or context (builder warns otherwise) |
| `data_contrast` | two numbers in tension | more than two | the gap is the story; highlight the problem side |
| `kpi` | 2-4 metrics vs plan | the same series is charted later as a trend (say it once) | `delta` chips: green/red by `good`; scorecard slides state conclusions, detail slides chart |
| `chart` | evidence over categories or time | decoration | kinds: column, bar, line (+`smooth`, `target`), stacked, stacked_bar, area, doughnut/pie (≤ 4 parts), waterfall, range, scatter. Highlight one, grey the rest |
| `table` | precise figures | a trend (use a chart) | numbers right-aligned, units in header, `total_row`, `highlight_row`, ≤ 2-line cells |
| `options` | choosing between options on weighted criteria | 2 options with no criteria (use `compare`) | totals computed; builder warns if the recommended option is not top |

Chart images (`scripts/chart_images.py`, placed with `image`): mekko (market map), slope (two-period
change), dumbbell (gap to target), heatmap (performance grid), bullet (progress vs target). Pictures,
not editable data: keep the numbers in `facts`, give alt text, say so if editability matters.

## Diagrams

| Type | Use when | Avoid when | Limits |
|---|---|---|---|
| `process` | ordered steps | a loop (use cycle) | 3-6 steps, short heads; centred when bodies are short |
| `cycle` | a self-reinforcing loop (flywheel) | linear steps | 3-6 steps; `center` names the loop |
| `funnel` | narrowing stages with conversion | stages that don't narrow | 3-6 stages; numeric values compute conversion |
| `pyramid` | hierarchy or foundation | equal items | 3-5 levels, top = the point |
| `hub` | one centre, enablers around | sequence | 3-8 spokes; talk mode: ≤ 5 |
| `issue_tree` | MECE breakdown of a question / root cause | storytelling openers | 2-4 branches, 1-3 leaves each |
| `matrix` | positioning on two axes; risk heat map | more than ~10 items | label quadrants with actions |
| `swot` | internal/external position | as the conclusion (it is an input) | 2-4 bullets per box; highlight the quadrant that matters |
| `venn` | overlap is the point (sweet spot) | more than 3 sets | 2-3 sets; name the overlap |
| `journey` | a user's experience over stages | a process without people | 3-6 stages; `feeling` -1..1 draws the emotion line |

## Compare and plan

| Type | Use when | Avoid when | Notes |
|---|---|---|---|
| `compare` | 2-4 alternatives, same rows | weighted criteria (use options) | panels sized to content |
| `columns` | 2-4 parallel ideas with glyph badges | boxed cards look heavy | open layout, vertical rules (office-kit multi-column) |
| `cards` | 2-4 parallel ideas, boxed | talk mode (four thin cards) | equal heights by construction |
| `before_after` | a change | three states | optional images per side |
| `pricing` | plans / packages | non-commercial decks | one `recommended` tier raised |
| `timeline` | workstreams over periods, owners | 2-3 dates (use milestones) | Gantt with milestones; highlight the critical path |
| `milestones` | 3-6 dated points | detailed plans | state done / now / next |
| `roadmap` | now / next / later or quarters | dated commitments | 3-4 lanes |
| `actions` | next steps with owners and dates | vague intentions | status chips: done, on_track, at_risk, late, not_started |
| `risks` | risk register | no mitigations (builder warns) | likelihood/impact dots H/M/L, mitigation, owner |
| `ask` | the decision | no cost or number (builder warns) | what, why now, cost and impact, owner, figure |

## People, proof, pictures, other

| Type | Use when | Avoid when | Notes |
|---|---|---|---|
| `team` | people matter (pitch, intro) | long bios | photo circles or initials; one line of proof each |
| `faq` | objections and answers | fragments | each answer: claim, proof, action (≥ 6 words; builder warns) |
| `image` | proof by picture + 3 points | stock filler | crop not stretch; alt text required |
| `image_full` | the human hook, a place, a product in use | text-heavy points | scrim keeps text legible; credit line |
| `gallery` | 2-6 pictures with captions | unrelated images | portfolios, events, product range |
| `code` | code, prompt, command | executives who don't code | monospaced on a dark panel + 2-3 points |
| `bullets` | nothing else fits | more than 6 items | ask first why no exhibit fits |
| `references` | sources slide | invented sources | numbered; consistent, complete citations (publisher, title, date, locator) |
| `custom` | no type fits without distorting the idea (a map, a dependency network, an annotated schematic) | a standard type would do | `html` body on the deck's CSS tokens, reproducible from the spec; say why no type fits; the PPTX needs a hand build of the slide (placeholder fails lint until done) |

## Variants worth knowing

- Governing-thought letters: `letter: "A"` on a chapter's key exhibits (office-kit, McKinsey reference).
- Provenance: `tag: "Illustrative"` or `"Non-exhaustive"` on samples and maps.
- Footnotes: `footnotes: [...]` with ¹ ² ³ in the claim; keep them separate from the source line.
- Accent words in titles: `^^7x^^` (once per slide at most).
- Talk build-up: show a diagram growing over 3-5 slides (duplicate the slide, add one element each).
- False ending and reversal, objection-then-rebuttal, an honest limitation slide: staging devices
  for talks (office-kit); use them when real material supports them, never manufactured.
