# Spec reference (`build_html.py` drafts, `build_deck.py` final PPTX)

One spec drives both builders: the HTML draft during iteration and the native PPTX after approval.
Loading, facts, checks, tokens and validation live in `scripts/spec_io.py` and behave identically in both. Run
`python3 scripts/spec_io.py --schema` for the authoritative field list (44 slide types plus `custom`,
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

## Evidence register, claim inventories and the release gate

Run `spec_io.py spec.json --strict` before final production in **every** format. Final HTML also
supports `build_html.py spec.json --strict -o out/deck.html`. Draft mode reports blockers but
continues, so unresolved evidence can still be discussed in a visibly unfinished draft.

```json
{
  "facts": {"enrolled": 12},
  "fact_meta": {"enrolled": {"kind": "observed", "evidence": "report"}},
  "evidence": {"report": {
    "source": "User-supplied study report", "locator": "Table 1, enrolled row",
    "status": "verified"
  }},
  "slides": [{
    "type": "statement", "claim": "We enrolled {=enrolled} participants",
    "claims": [{
      "text": "We enrolled {=enrolled} participants", "kind": "observed",
      "evidence_ids": ["report"], "status": "reviewed"
    }]
  }]
}
```

- Classify raw facts as `observed`, `estimate`, `forecast`, `assumption`, `target` or
  `illustrative`. Only an `=expression` can be `calculated`. Observed facts link an evidence ID.
- Every evidence entry requires a source, a precise locator and `verified` status. Verification
  means the source was actually checked and supports the particular wording, scope, population,
  period and certainty. The validator checks the record, not the source itself.
- Record each substantive claim in the slide's `claims` list, including facts in notes and exact
  quotations. `text` must match presented wording (tokens are supported). Set `status: reviewed`
  only after semantic review. Observed claims and quotations require `evidence_ids`.
- Other claim kinds are `calculated`, `estimate`, `forecast`, `assumption`, `target`, `hypothesis`,
  `recommendation` and `illustrative`. All except illustrative claims require a `basis` explaining
  their calculation, analysis or assumptions. Match the visible wording to that classification.
- Navigation and other content making no factual assertion may use `non_factual_reason` instead
  of claims. This is a documented review decision, not an automatic assertion exemption. Do not
  use it to hide factual content. Review inventory completeness against the actual output.
- Literal figures, including ordinary counts and years, are checked even without a facts model.
  Prefer tokens and expressions. A slide using literal sourced data requires `data_status: sourced`,
  a source line **and** `evidence_ids` linked to verified entries. A citation string alone never
  establishes provenance. Code and citation metadata are exempt from numerical scanning only;
  placeholders in them still block release.
- Administrative text such as a section number may use
  `number_exceptions: [{"text": "Part 2", "reason": "Section navigation"}]`. Keep the exception
  exact and narrow; it is reviewed, not inferred. Never exempt substantive counts or dates.
- Illustrative content requires user agreement recorded as `illustrative_authorized: true`, a
  visible `Illustrative` tag or footer, and `data_status: illustrative` on wholly illustrative
  slides. Such slides describe fictional examples and may omit real-world claim evidence.
  Derived facts inherit illustrative provenance, so calculations cannot remove the label requirement.
  Both builders add a visible high-contrast badge, including on full-bleed covers and closings.
- Do not infer truth or user agreement merely from these fields. They are audit records. No prompt
  or schema guarantees zero hallucinations; source verification and semantic review remain required.
- Placeholder scanning includes quotations, references, source lines, code and speaker notes,
  independently of style exemptions. Count mismatches and custom reconstruction needs remain notes.
- `voice_ok` records editorial exceptions and does not waive any evidence or release rule.

**Migration:** older real decks may now fail strict validation. Add locators, claim inventories and
linked evidence; do not relabel real figures illustrative to silence errors. The bundled examples
are explicitly fictional layout demonstrations and have been classified accordingly.

## The facts model (shared inputs and checked calculations)

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

## Creative planning and custom composition

Keep `brief.creative_brief` and `brief.creative_plan` beside the content: audience change, tension,
distinctive material, latitude, selected concept, alternatives, rationale and intended rhythm.
They guide judgement and are not rendered or graded by the validator. See creative-direction.md.

A `custom` slide can improve explanation or expression even when standard types technically fit.
Its `html` uses the deck's tokens inside normal chrome. `full_bleed: true` uses the whole stage;
notes, a supplied source line and illustrative provenance remain in the generated HTML. Place
the visible headline inside `html`; ordinary chrome fields such as `title` become planning metadata
in this mode and cannot substitute for presented claim text. Give the
composition a clear reading order and retain legible, editable text. Full-stage HTML does not
promise automatic native PPTX conversion: record a feasible `pptx_note`, reconstruct after approval,
then compare and QA the actual file. The builder's placeholder must not be delivered as final.

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

## Builder checks and limits

Text is measured with real font metrics and stepped down to fit, never below the floors
(title 20pt, body 12pt, talk-mode body 18pt); if it still can't fit, it warns and exits 3.
Charts and tables are native and editable. Pictures are cropped, never stretched. Charts receive generated alt text; pictures need supplied alt text and warn when it is missing. Shapes carry no inherited shadows. Text that would sit on a fill (or slide
background) without enough contrast flips to ink or white (4.5:1 body, 3:1 large text). Notes
separate the spoken script from presenter-only reference. Validation (above) checks recorded numerical provenance and blocks detected gaps under
`--strict`; administrative exceptions and reviewed claim inventories still need semantic review. The builders print a note
when text was measured with a substitute font. Warnings flag label titles, missing
sources and notes, the same type three times running (a prompt, not a ban), agenda in talk mode, asks without a number
or cost, FAQ fragments, risks without mitigation, scorecards that contradict the recommendation,
dual-scale series and the same data charted twice.

## Workflow and component extensions

Choose `assurance` by claim consequence, following evidence-policy.md. Fact tokens inherit source links
through calculated dependencies; semantic review of claim strength remains necessary. Unused research
gaps remain advisory. Use `spec_io.py --schema` and `spec_io.py spec.json --outline` independently of
the PPTX libraries. Existing build_deck.py commands remain supported.

Optional per-slide `seconds` overrides estimated speaking time. `table` supports structured status and
Harvey cells plus `base_cell`; `process` supports labelled metrics; `columns` supports bundled Feather
icons. Layout annotations refer to actual named PPTX shapes. See visual-components.md for fields,
semantics and examples, and workflow.md for commands and renderer limitations.
