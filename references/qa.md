# QA: checks, balances, reviews

QA runs twice:
- **On the HTML draft** (Stage 5): render_html → look → semantic review → checklists → style
  prompts → fresh eyes (high stakes) → fix → show the user.
- **On the final file** (Stage 6): strict build → reconcile against the approved draft → render →
  lint → look → fix.

Four kinds of quality are checked separately, and one never compensates for another: factual
fidelity (numbers, sources, claim strength), argument (does the story hold), presentation (fit,
legibility, hierarchy) and voice. A beautiful deck with an unsupported claim fails.

A first render is never clean; assume problems and hunt for them.

## 1. Render and look (every deck, every slide)

- **Draft**: `render_html.py deck.html out/` gives a contact sheet and one PNG per slide. A slide
  whose text cannot fit at the floor sizes carries a red "DOES NOT FIT" badge and is listed (exit
  3). Treat it as an error.
- **Final PPTX**: `render.py deck.pptx out/` gives the same contact sheet and per-slide PNGs.

Read the sheet for rhythm (dense/light alternation, accent discipline, consistent edges), then every
slide at full size, one at a time, not by spot-checking a representative; dense, flagged and
consequential slides get the closest look. Defect list (Anthropic pptx skill + our runs):

- Text overflow or cut off at a box or the slide edge (check this first)
- Overlaps: text through shapes, labels colliding in charts, diagrams or Gantts
- Source lines or footers colliding with content
- Gaps < 0.3 in between blocks; uneven gaps (crowded here, empty there); margins < 0.5 in
- Half-empty slides; cards much taller than their content; a lone word on a last line
- Columns or cards not aligned; titles that move between slides
- Low-contrast text or icons; colour carrying meaning alone
- Decoration left mispositioned after text changed (an underline sized for one line, now two)
- Leftover placeholders; images stretched or missing alt text
- Charts: legend overlaps, labels clipped, axis not at zero without a note, two scales on one axis

Fit is only as good as the fonts used to measure it. `env_check.py` lists, per font, whether a
metric-compatible clone was found (Calibri, Cambria, Arial, Times, Bookman, Century Schoolbook,
Courier), a close one (Palatino) or a substitute; the builders print a `note` when they measured
with a substitute. The machine that finally opens the deck may substitute again: check wrapping
there, and report which application rendered what you inspected.

## 2. Lint (`lint_deck.py`, any .pptx)

| Code | Sev | Meaning → fix |
|---|---|---|
| placeholder | error | [TBD], [CONFIRM], [IMAGE NEEDED], lorem, xxx, "click to add" left on a slide |
| offslide_shape | warn | shape past the slide edge (rotation-aware) |
| text_overflow | warn | text needs more height than its box (font-metric estimate) |
| body_below_floor | warn | body < 12pt, small print < 9pt |
| text_overlap | warn | two text boxes overlap |
| low_contrast | warn | text vs what is behind it below 4.5:1 (3:1 for ≥ 18pt, or ≥ 14pt bold) |
| duplicate_titles | warn | two slides share a title |
| too_many_bullets | warn | > 7 paragraphs in a box |
| title_is_label | info | document title is a topic, not a claim |
| long_talk_title | info | talk headline > 60 characters |
| figure_without_source | info | numbers with no source on the slide or in notes |
| missing_notes | info | no speaker notes |
| missing_alt_text | info | chart or picture without alt text, or alt text that is just a filename |
| palette | info | > 4 saturated colours on one slide |
| half_empty | info | content ends above 60% of the slide |
| same_chart_data | info | two slides chart the same numbers |
| repeated_phrase | info | a 3-word phrase on 4+ slides (formula phrasing; technical terms may legitimately repeat) |
| number_ledger | info | the same label carries different numbers on different slides |
| word_budget | info | talk slide over 50 visible words |
| style_review | warn | stock phrasing, "not just X but Y", ", ensuring…" tails, vague sources, em dashes, emoji: an editorial prompt, not proof of AI authorship (human-voice.md). Fix, or keep on purpose |
| style_rhythm | info | every list in threes, every title the same shape or opening word |

`lint_deck.py deck.pptx --figures` prints every figure per slide: the tie-out worksheet for decks
that were not built from a facts model (Gamma, Canva, a teammate's file). Reconcile each line.
Both builders print the validation from `spec_io.py` (`check` lines in drafts, `error` lines with
`--strict`): hand-typed figures anywhere in visible text, literal numbers in chart and table data,
placeholders, unclassified facts, unverified evidence; plus `note` lines for title counts that don't
match their lists, illustrative facts and custom slides. They also print `style` prompts and these
warnings: label titles, missing sources and notes, the same type three times running, agenda in talk
mode, an ask without a number or cost, FAQ fragments, risks without mitigation, recommended option
not top-scored, dual-scale series, the same data charted twice, big numbers without proof points,
and measurement with a substitute font.

## 3. Semantic review (every deck; separate from style)

Natural wording, valid arithmetic and a supported argument are three different things; the first
two can pass while the third fails. Read each slide and answer:

1. **Headline vs exhibit**: does the title follow from what the exhibit shows? ("Online overtakes
   general trade" fails when the chart ends at 34% vs 37%.)
2. **Scope**: does a claim about "every region" or "all customers" hold for every row of the data?
3. **Counts and promises**: "three limits" lists three; the opening's promises ("three stories")
   are kept; the notes don't refer to content that was cut.
4. **Claim strength**: association is not stated as causation; targets are not stated as
   forecasts; "pays back" needs the margin economics, not just volumes.
5. **Recommendation**: it follows from the analysis shown, and the scorecard agrees with it.
6. **Changes**: a rewrite, a style fix or a generator didn't add an implication the evidence
   doesn't support.

Record each failure with slide, claim, evidence and fix. `spec_io.py` catches count mismatches and
many numerical provenance gaps; claim inventories record review decisions. Source support,
claim coverage and the rest still need reading. A clean validator report is not a truth certificate.

## 3a. Creative quality (before approval)

Use creative-direction.md §8. Look for a subject-specific organising idea on substantive slides,
visible relationships, intentional reading order and an earned memorable moment where appropriate.
Check that the language expresses this presenter's point of view. If slides are generic, try a
different composition before polishing the theme. A strong table or repeated comparison layout
may be the best answer; never trade fidelity for novelty.

## 4. The ten-point check (every deck)

1. **Title test**: the titles alone tell the story (document) or the plot (talk).
2. **So-what test**: each slide answers "so what?" on its face.
3. **Tie-out**: every number agrees across summary, charts, tables, notes; headline counts match
   the items drawn.
4. **Source check**: no invented sources; every external figure traceable; gaps visible.
5. **Date check**: proposed activity starts after today and matches the launch dates in the text; retrospective or in-progress items are labelled.
6. **Squint test**: blur your eyes; the eye lands on the answer first. Five-second test: show a
   slide for five seconds; what is remembered should be the title's claim.
7. **Consistency**: fonts, grid, colours, number formats, exhibit numbering, capitalisation, terms.
8. **Look and voice check**: no generic AI imagery, glows, decorative stripes, filler icons,
   uniform case studies, repeated closing clauses. Every `style` prompt fixed or kept on purpose (`voice_ok`). Read three
   slides aloud as the presenter: would a person say this to this room? (human-voice.md)
9. **Criteria map**: every judging criterion or interview question has a slide.
10. **Time test**: a timed read-aloud of the notes fits the slot with room for questions.

## 5. Mode-specific final checks

Document: the answer is first; every non-exempt title passes both assertion tests; peers share a
form; evaluative words are backed on the same slide; later slides add rather than restate; the
summary claims nothing the body contradicts; the last body slide asks for a decision or action.

Talk: no slide over one headline + 3-4 lines; no two figures or two emphases on a slide; questions lead to a useful explanation, task or explicit investigation; revisiting a question
adds understanding rather than merely repeating it;
an agenda only if it orients, and the reveal (answer first or progressive) chosen on purpose;
headline forms fit their roles; retain repetition when it supports comparison or learning;
the abstract's promises are all paid off; the time estimate fits the slot.

Look: nothing below the floors; cover and close suit the selected style; use a key figure only when the argument has one; one
primary and one accent, each accent marks the answer or the problem; cards in a row share height;
every chart has its unit and a zero baseline (or a note); table numbers right-aligned.

## 6. Fresh-eye review (high-stakes decks)

Run it on the draft PNGs before asking for approval, so the findings change the cheap version.
Give a separate agent only the rendered PNGs (or the .pptx), the slide count and the kind of deck.
Do not tell it how the deck was made or what you are proud of. Prompt:

> You are reviewing a {KIND: deck to be presented live | deck to be read and decided from} of {N}
> slides, for {AUDIENCE}, who must {DECISION}. You have not seen how it was made. Read every slide
> in order; do not skim or infer from a sample.
> 1. Language: list every phrase a native reader would stumble on: unnatural endings, compressed
> jargon, undefined abbreviations, inconsistent terms, uneven bullet endings, phrasing that feels
> AI-written.
> 2. Logic: read only the titles top to bottom. Where does the story jump, double back, repeat, or
> reach a conclusion without its premise?
> 3. Breaks: counts in titles that don't match the body; titles that disagree with their charts;
> unbacked evaluative words; slides that rehash earlier ones; promises the opening makes that the
> body doesn't keep; the same quantity with different values on different slides; the same
> mechanism described differently; a closing that contradicts the body; numbers without sources;
> claims stronger than their evidence (causation from correlation, "all" from some).
> 4. Look: anything cramped, clipped, overlapping, too small, low-contrast, unbalanced or half-empty.
> For each finding give: slide number, the exact text, what is wrong, a suggested rewrite. End with
> up to five evidenced fixes in priority order. Report only problems you can point to on a slide; if you find
> none in a category, say "none found". Do not praise.

Triage every finding in a table: slide · finding · type · adopt / reject (reason) / ask the user.
Show the user any finding that would change meaning or structure. Apply the adopted ones, rebuild,
re-render, re-lint. One round is the default; report findings / adopted / remaining in three lines
and ask before another round.

## 7. Audit discipline

- No soft language for defects: "slightly tight" or "nearly overlapping" means fix it.
- Every slide individually; archetype bugs are type-specific (a legend bug hits every doughnut,
  a footer bug every rail slide). Render at least one slide of every type you used.
- Three fixes on the same defect without success: change the slide type or split the content.
- Record what you inspected, what changed and which renderer you used.
- Draft rounds: keep the spec under version (spec_v01.json, spec_v02.json) so any round can be
  rebuilt; the HTML is always regenerated from the spec, never hand-edited (custom compositions live
  in the spec as `custom` slides, so the HTML regenerates too). Preserve any custom PPTX
  reconstruction script alongside the spec and rerun it after each rebuild.
- Revisions: change what was asked and nothing else; diff the spec (or the slide text) before and
  after and confirm unrelated slides are untouched.
- Version before destructive edits (deck_v01.pptx, deck_v02.pptx); never overwrite the user's
  edits to a generated deck without asking.

## 8. Presenter prep (when there is a live talk)

1. Timing: `minutes` in the spec writes `[~N sec]` per slide; rehearse with a stopwatch; mark one
   or two checkpoints ("if past this divider at 9 minutes, skip slide 14").
2. Q&A sheet: the 15-25 hardest questions, each with a 2-4 sentence sourced answer, built from the
   notes (every challengeable claim becomes a question); a last-resort line for the unanswerable.
3. Handout: export notes pages or a PDF; a contact sheet of the deck for the dress rehearsal.
4. Room: check projector, clicker and fonts on the actual machine; raise the type floor for big rooms.
