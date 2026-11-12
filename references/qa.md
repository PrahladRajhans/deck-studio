# QA: checks, balances, reviews

QA runs twice:
- **On the HTML draft** (Stage 5): render_html → look → checklists → voice → fresh eyes (high
  stakes) → fix → show the user.
- **On the final file** (Stage 6): render → lint → look → fix.

A first render is never clean; assume problems and hunt for them.

## 1. Render and look (every deck, every slide)

- **Draft**: `render_html.py deck.html out/` gives a contact sheet and one PNG per slide. A slide
  whose text cannot fit at the floor sizes carries a red "DOES NOT FIT" badge and is listed (exit
  3). Treat it as an error.
- **Final PPTX**: `render.py deck.pptx out/` gives the same contact sheet and per-slide PNGs. Read the sheet for rhythm (variety,
dense/light alternation, accent discipline, consistent edges), then every slide at full size, one at
a time, not by spot-checking a representative. Defect list (Anthropic pptx skill + our runs):

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

LibreOffice renders Calibri/Cambria/Arial/Times/Bookman/Century Schoolbook with metric-identical
clones, so fit is trustworthy for those; Palatino is close; others are approximate.

## 2. Lint (`lint_deck.py`, any .pptx)

| Code | Sev | Meaning → fix |
|---|---|---|
| placeholder | error | [TBD], [CONFIRM], [IMAGE NEEDED], lorem, xxx, "click to add" left on a slide |
| offslide_shape | warn | shape past the slide edge (rotation-aware) |
| text_overflow | warn | text needs more height than its box (font-metric estimate) |
| body_below_floor | warn | body < 12pt, small print < 9pt |
| text_overlap | warn | two text boxes overlap |
| low_contrast | warn | text vs what is behind it < 3:1 |
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
| repeated_phrase | info | a 3-word phrase on 4+ slides (machine tell) |
| number_ledger | info | the same label carries different numbers on different slides |
| word_budget | info | talk slide over 50 visible words |
| ai_voice | warn | stock AI words, "not just X but Y", ", ensuring…" tails, vague sources, em dashes, emoji (human-voice.md) |
| ai_rhythm | info | every list in threes, every title the same shape or opening word |

`lint_deck.py deck.pptx --figures` prints every figure per slide: the tie-out worksheet for decks
that were not built from a facts model (Gamma, Canva, a teammate's file). Reconcile each line.
Both builders (HTML and PPTX) add their own warnings at build time, including `voice` lines from
the same checks as `ai_voice` and `ai_rhythm`. The other build-time warnings are: hand-typed money, % or multiples in a deck that has
facts (the commonest contradiction: a title that disagrees with the model), label titles, missing sources, missing notes, the
same type three times running, agenda in talk mode, an ask without a number, an ask without cost,
FAQ fragments, risks without mitigation, recommended option not top-scored, dual-scale series,
the same data charted twice, big numbers without proof points.

## 3. The ten-point check (every deck)

1. **Title test**: the titles alone tell the story (document) or the plot (talk).
2. **So-what test**: each slide answers "so what?" on its face.
3. **Tie-out**: every number agrees across summary, charts, tables, notes; headline counts match
   the items drawn.
4. **Source check**: no invented sources; every external figure traceable; gaps visible.
5. **Date check**: timelines start after today and match the launch dates in the text.
6. **Squint test**: blur your eyes; the eye lands on the answer first. Five-second test: show a
   slide for five seconds; what is remembered should be the title's claim.
7. **Consistency**: fonts, grid, colours, number formats, exhibit numbering, capitalisation, terms.
8. **AI-look and AI-voice check**: no generic AI imagery, glows, decorative stripes, filler icons,
   uniform case studies, repeated closing clauses. Zero unexamined `voice` lines. Read three
   slides aloud as the presenter: would a person say this to this room? (human-voice.md)
9. **Criteria map**: every judging criterion or interview question has a slide.
10. **Time test**: a timed read-aloud of the notes fits the slot with room for questions.

## 4. Mode-specific final checks

Document: the answer is first; every non-exempt title passes both assertion tests; peers share a
form; evaluative words are backed on the same slide; later slides add rather than restate; the
summary claims nothing the body contradicts; the last body slide asks for a decision or action.

Talk: no slide over one headline + 3-4 lines; no two figures or two emphases on a slide; every
divider is answered by the next slide and fully before the next divider; no question asked twice;
no agenda or upfront summary slipped in; headline forms are mixed, no pattern three times running;
the abstract's promises are all paid off; the time estimate fits the slot.

Look: nothing below the floors; cover and close use a colour field and carry the key figure; one
primary and one accent, each accent marks the answer or the problem; cards in a row share height;
every chart has its unit and a zero baseline (or a note); table numbers right-aligned.

## 5. Fresh-eye review (high-stakes decks)

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
> mechanism described differently; a closing that contradicts the body; numbers without sources.
> 4. Look: anything cramped, clipped, overlapping, too small, low-contrast, unbalanced or half-empty.
> For each finding give: slide number, the exact text, what is wrong, a suggested rewrite. End with
> the top 5 fixes in priority order. No deck is flawless: find at least three real problems. Do not
> praise.

Triage every finding in a table: slide · finding · type · adopt / reject (reason) / ask the user.
Show the user any finding that would change meaning or structure. Apply the adopted ones, rebuild,
re-render, re-lint. One round is the default; report findings / adopted / remaining in three lines
and ask before another round.

## 6. Audit discipline

- No soft language for defects: "slightly tight" or "nearly overlapping" means fix it.
- Every slide individually; archetype bugs are type-specific (a legend bug hits every doughnut,
  a footer bug every rail slide). Render at least one slide of every type you used.
- Three fixes on the same defect without success: change the slide type or split the content.
- Record what you inspected, what changed and which renderer you used.
- Draft rounds: keep the spec under version (spec_v01.json, spec_v02.json) so any round can be
  rebuilt; the HTML is always regenerated from the spec, never hand-edited.
- Version before destructive edits (deck_v01.pptx, deck_v02.pptx); never overwrite the user's
  edits to a generated deck without asking.

## 7. Presenter prep (when there is a live talk)

1. Timing: `minutes` in the spec writes `[~N sec]` per slide; rehearse with a stopwatch; mark one
   or two checkpoints ("if past this divider at 9 minutes, skip slide 14").
2. Q&A sheet: the 15-25 hardest questions, each with a 2-4 sentence sourced answer, built from the
   notes (every challengeable claim becomes a question); a last-resort line for the unanswerable.
3. Handout: export notes pages or a PDF; a contact sheet of the deck for the dress rehearsal.
4. Room: check projector, clicker and fonts on the actual machine; raise the type floor for big rooms.
