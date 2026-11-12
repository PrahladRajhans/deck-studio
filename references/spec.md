# Spec reference (`build_html.py` drafts, `build_deck.py` final PPTX)

One spec drives both builders: the HTML draft during iteration and the native PPTX after approval.
Loading, facts, checks, tokens and validation live in `scripts/spec_io.py` and behave identically in both. Run
`python3 scripts/build_deck.py --schema` for the authoritative field list (44 slide types plus `custom`,
11 chart kinds). This page explains how to use it well. Worked examples in `assets/examples/`:
`case-comp.json` (document, recommendation, every number from `facts`), `personal-story.json`
(talk, interview), `showcase-new-types.json` (every newer type on one grid), `stress-all-types.json`
(regression), plus `*-preview.png` renders. Which type for which content: slide-library.md and
decision-trees.md T6.

## Skeleton

```json
{
  "title": "Deck title (metadata)",
  "direction": "consulting-navy",
  "mode": "document",
  "frame": "classic",
  "minutes": 12,
  "footer": "Team Name · Competition · Round",
  "sources": ["Deck-level sources: shown in notes of slides that have figures but no own source"],
  "facts": { "rev": [0.6, 1.8, 3.5], "budget": 1.2, "profit": "=vsub(rev, cost)" },
  "checks": ["max(rev) > 0", "peak_draw <= budget"],
  "slides": [ { "type": "cover", "title": "..." }, ... ]
}
```

Optional deck keys: `brief` (the brief canvas and voice brief; ignored by the builders, kept for
reasoning), `fact_meta`, `evidence`, `voice_ok` (below), `html_fonts` (`{heading, body, url}`: web
fonts for an HTML final only; visual-language.md §11), `theme` (token overrides for a brand),
`number_kickers`, `title_rule`.

Optional slide keys besides the visible fields: `role` (recommendation, evidence, teaching,
investigation, workshop, transition, closing; writing.md §1) and `question` (the audience question
the slide answers) for planning and review; `data_status` and `voice_ok` (below).

## Evidence register, claim types and the release gate

```json
"facts":     { "share_2026": 34, "target_orders": 5000, "conv": "=orders/carts*100" },
"fact_meta": { "share_2026":    {"kind": "observed", "evidence": "panel26"},
               "target_orders": {"kind": "target"} },
"evidence":  { "panel26": {"source": "Retail panel, Q2 2026 report", "locator": "Table 4, p. 12",
                           "status": "verified", "kind": "observed"} }
```

- `fact_meta.kind` for every raw fact: `observed`, `estimate`, `forecast`, `assumption`, `target`
  or `illustrative`. Derived (`"=expr"`) facts are `calculated` automatically. Observed facts name
  an `evidence` entry.
- `evidence` entries record `source`, `locator` (page, table, cell, URL) and `status`: `verified`
  (the source exists and supports the claim's wording, scope, period and certainty), `unverified`
  or `missing`. Never mark an entry verified that you have not checked.
- A slide whose numbers are typed rather than drawn from facts declares `data_status`: `sourced`
  (needs a `source` line) or `illustrative` (needs an Illustrative tag or footer).
- `voice_ok`: words or phrases kept on purpose despite a style prompt (deck or slide level).

`spec_io.py spec.json` reports what would block a final build; the builders print the same as
`check` lines. `--strict` (Stage 6) turns these into errors and refuses to build: hand-typed figures
in any visible text, literal numbers in chart, KPI, funnel or scorecard data, placeholders, facts
without a kind, observed facts without evidence, and evidence that is not verified, all unless the
slide declares `data_status`. Administrative numbers (page numbers, matrix positions, timeline
period indexes, highlights) are exempt. Count mismatches between a title ("Three limits") and its
list, illustrative facts and custom slides are reported as notes for the semantic review.

## The facts model (why the numbers always agree)

- `facts` holds raw inputs (numbers or lists) and derived values (`"=expr"`). Derived facts may
  use earlier facts. Evaluated with a safe whitelist: arithmetic, comparisons, indexing,
  `sum min max len abs round avg wavg approx pct cagr cumsum share vadd vsub first_at_least reached
  logistic rng all any list`.
- Easy to confuse: `pct(a, b)` is the percentage change from a to b; `share(part, whole)` is part as
  a percentage of whole; `cagr(first, last, years)` is compound annual growth.
- The helpers refuse silent errors: `vadd`, `vsub` and `wavg` reject lists of different lengths;
  `wavg` rejects zero or negative weights; `first_at_least` returns "not reached" (None) when the
  threshold never arrives, which cannot be used as an index, in arithmetic, a comparison or on a
  slide. Guard it: `"checks": ["reached(payback)"]`, or branch the wording.
- `checks` are expressions that must be true; any false check stops the build (exit 2) with the
  failing line. Write one for every claim the argument rests on.
- In any string: `{=expr|fmt}` → formatted value (`{=rev[2]|.1f}`, `{=users|,}`,
  `{=pct(a,b)|+.0f}%`, `{=years[payback]}`). As a whole value, `"=expr"` → number or list
  (`"values": "=rev"`, `"highlight": "=turn"`).
- Useful derivations: `profit = vsub(vsub(rev, cost), opex)`, `cum = cumsum(profit)`,
  `peak_draw = -min(cum)`, `turn = first_at_least(profit, 0)`, `payback = first_at_least(cum, 0)`,
  `score_b = wavg(sc_b, weights)`, `growth = cagr(rev[0], rev[3], 3)`.

## Slide-writing tips per type

- `cover`: title is the answer (document mode) or the promise (talk mode); `figure` = the one
  number to remember.
- `exec_summary`: 3–5 rows, each a claim + one-line evidence; `ref` = the `id` of the slide that
  proves it (page number filled in automatically); highlight the recommendation row.
- `agenda`: reuse between sections with `active` set to light up the current chapter.
- `chart` kind `waterfall`: `values` = start total then deltas (and later totals), `totals` =
  indexes drawn as absolute bars, e.g. `"values": [4.2, 1.1, -0.6, -0.3, 4.4], "totals": [4]`.
  Increases grey, decreases muted, totals primary, `highlight` in the accent; labels show +x and
  (x). The bridge must stay above zero.
- `chart`: `highlight` the bar that carries the title's point; side panel says why; `so_what`
  says what it means for the decision; `number_format` like `0.0`, `0%`, `#,##0`.
- `options`: criteria with weights, scores 1–5; totals are computed; `recommended` index must be
  the top scorer or the builder warns (it will not let a scorecard contradict the pitch).
- `table`: parentheses for negatives; `total_row: true` bolds and rules the last row;
  `highlight_row` for the row the title is about.
- `timeline`: `periods` across; bars `start`/`end` are period indexes; `milestone: true` for
  diamonds; highlight the critical path; `owner` per row.
- `ask`: `ask` (one sentence: what, how much), `why` (why now), `cost` (cost and impact),
  `figure` (the number it moves), `owner` ("Owner: CEO · Decision needed by 15 December").
- `statement` and `quote` may omit `title`: the claim or quote becomes the headline.
- `notes`: `say` (2–5 spoken sentences), `assumptions` (to confirm), `sources`, `qa` (likely
  questions with short answers).

## Slide-level extras

- `letter: "A"` → "A:" in the accent before the title (a chapter's key exhibits).
- `tag: "Illustrative"` → small bordered tag on the source line.
- `footnotes: ["CAGR on 2026 base"]` → numbered notes above the source; mark claims with ¹ ² ³.
- `^^word^^` in any text → that word in the accent (once per slide at most); `**word**` → bold.
- `frame` per slide overrides the deck frame (rare).
- Deck `minutes` → `[~N sec]` at the top of each slide's notes.

## Builder guarantees

Text is measured with real font metrics and stepped down to fit, never below the floors
(title 20pt, body 12pt, talk-mode body 18pt); if it still can't fit, it warns and exits 3.
Charts and tables are native and editable. Pictures are cropped, never stretched. Every chart and
picture gets alt text. Shapes carry no inherited shadows. Text that would sit on a fill (or slide
background) without enough contrast flips to ink or white (4.5:1 body, 3:1 large text). Notes
separate the spoken script from presenter-only reference. Validation (above) flags numbers that
bypass the facts model anywhere on a slide, and `--strict` blocks them. The builders print a note
when text was measured with a substitute font. Warnings flag label titles, missing
sources and notes, the same type three times running (a prompt, not a ban), agenda in talk mode, asks without a number
or cost, FAQ fragments, risks without mitigation, scorecards that contradict the recommendation,
dual-scale series and the same data charted twice.
