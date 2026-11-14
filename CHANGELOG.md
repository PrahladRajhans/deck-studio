# Changelog

Record user-visible changes newest first. Each entry states the reason, behavior, compatibility
impact and validation. Add changes to the current unreleased entry until they are merged; do not
rewrite older entries to imply that later fixes already existed.

## 2026-11-14

### MIT licence and final package

- Add the standard MIT licence in licence.txt, Copyright (c) 2026 Prahlad Rajhans, as selected by
  the author. Keep the bundled Feather icon copyright/licence and other third-party notices intact.
- Require the project licence in source-verified upload ZIPs. Extend package regression checks to
  confirm attribution and third-party preservation, and reject a source bundle missing licence.txt.
- Document licence scope in the README. No creative instructions, adapters, examples, specification
  or slide-building behavior change. Existing reference, builder and package CI gates publication.

### Shared Claude and ChatGPT package

- Keep one creative method, human-voice reference collection, specification, builder pipeline and
  examples. Add small host adapters for capability discovery, HTML preview, editable production
  and file delivery; remove the renderer documentation's preinstalled-Chromium assumption.
- Offer Deck Studio for presentation, PowerPoint, deck and slide requests. Ask once before applying
  the workflow unless the user explicitly selects or declines it; preserve the choice through the
  task and revisions. Keep skill-use consent separate from the existing draft approval gate.
- Add OpenAI interface metadata with implicit discovery enabled so the choice can be offered.
  Keep the shared description concise and compatible with the stricter documented description limit.
  Include both adapters and OpenAI metadata as required, checksum-verified package contents.
- Explain native installation on supported hosts, account/runtime limitations and capability-based
  maintenance. Retain prior content and legacy commands; no spec fields or builder behavior change.
- Validation: internal reference/import checks, package readback and existing builder regression CI
  gate publication. Extend packaging regression coverage for adapter preservation and missing-adapter
  rejection. In-app tests are intentionally outside this revision; the user reports the preceding
  release works in Claude. Prompt scenarios and current primary sources are in the portability ledger.

### Bounded recovery and connected dependencies

- Bound external conversion/preview commands with per-command and shared wall-clock budgets,
  clear timeout outcomes and POSIX process-group cleanup. Run the optional PDF fallback in a bounded
  child process. Add explicit CI job limits; timeout failures cannot be reported as successful builds.
- Share a three-round/15-minute QA recovery budget across the deck, layouts and routes, with a
  stop-with-draft diagnostic outcome. Creative exploration and initial authoring remain unrestricted
  by this failure-recovery counter. User-specified budgets take precedence.
- Report actual route-specific dependencies, including CairoSVG/native Cairo icon rendering,
  Pillow, chart packages, Chromium, LibreOffice, poppler and optional PyMuPDF. Missing optional
  packages do not crash the checker or block dependency-free HTML authoring.
- Discover Gamma/Canva operations, permissions, assets, export paths and current cost estimates at
  runtime. Retain historical catalogue hints as optional context; remove account/network assumptions
  and mandatory references to uninstalled skills or an external playbook.
- Complete chart-image routing for tornado/sensitivity. Add an automatic internal-reference,
  section-pointer and local-import-cycle check. CI exercises timeout cleanup, dependency isolation,
  PDF fallback, link failures, all existing examples and package verification.



### Feedback completeness and content preservation

- Add a deterministic, source-verified Claude upload ZIP rooted at deck-studio/, matching the skill
  name. Publish a versioned download after successful main CI. Preserve the full source/context and
  add tamper/structure regression coverage; do not claim that packaging tests are Claude execution.


- Verification: native/runtime checkpoint passes 73 tests without skips, with 148 HTML and 131
  PPTX slide renders. Packaging adds the 74th test. Final-head checks, source readback and release
  download verification gate publication; detailed evidence is in the feedback coverage ledger.
- Audit both the earlier Gemini/Claude discussion and detailed actual-file feedback against code,
  references and examples. Add a recommendation-by-recommendation coverage ledger, including
  intentional rejections and remaining limits, in tests/evaluations/2026-11-14-feedback-coverage.md.
- Restore showcase-first rendering and content-first production advice lost during slimming; directly
  route writing.md and T6/T7 at the stage where needed. Preserve the concise entry point and detailed
  references, creative latitude, presenter register, evidence safeguards and HTML approval.
- Correct live-executive routing: use the tested talk renderer with answer-first structure and a
  document/appendix path for lookup detail, instead of promising document density at projection size.
- Surface sensitivity, quantified-process and contribution patterns in the main chooser. Strengthen
  topic-colon and fair-option guidance. Preserve legitimate repetition and technical language.
- Add decision-tradeoffs, unit-economics and cash-flow-teaching samples, semantic sensitivity-table
  crosshairs, optional defect/drop-off process metrics and an explicit native editable reconstruction
  recipe for the expressive brand example. Reconcile recipe copy/sources/notes and reject changed
  structures requiring layout review. General HTML-to-PPTX conversion is not claimed.
- Research primary Anthropic, W3C, Microsoft and ONS/Analysis Function guidance. Add practical
  reading-order, colour and uncertainty interpretation advice with exact sources in credits.md.



### Coherent workflow and visual grammar (2026-11-14)

- Reduce SKILL.md to a 163-line stage router. Consolidate theme selection and move production,
  evidence policy and visual component detail to references loaded for the current task.
- Establish provisional destination at intake; choose mode and structure before the storyline audit.
  Add dependency-free schema and outline commands; retain the old builder commands.
- Reuse source provenance through calculated facts, while retaining semantic claim review. Keep unused
  research gaps as advisory history. Add risk-based brief/standard/high assurance without waiving
  factual honesty, numerical checks, visible uncertainty or final placeholder blocking.
- Expand art direction, shape and diagram semantics, photography, icon consistency, optical alignment
  and purposeful layering. Bundle twelve pinned MIT Feather SVGs and license; use offline SVG in HTML
  and high-resolution transparent PNG in native editable PPTX layouts.
- Extend editable tables with labelled RAG/Harvey cells and base-case markers; extend processes with
  optional metrics. Add tornado and sensitivity image-chart helpers and unit-economics guidance.
- Add named alignment groups and pair-specific intentional-overlap annotations. No slide-wide warning
  suppression. Add explicit rehearsal timing overrides and complexity-weighted estimates.
- Respect custom composition typography without leaking theme heading fonts. Count visible custom
  copy instead of HTML attributes or reconstruction metadata; avoid treating all custom compositions
  as the same layout.
- Add sandbox-safe notes/grid controls and variable card-count support to the manual HTML fallback.
  Keep human voice guidance positive; avoid individual-word compliance records and use sentence case
  and range punctuation as contextual defaults.
- Add fixed executive, confounded-marketing, missing-evidence and brand packets, authored regression
  decks and component tests. Retain prior examples. Independent execution and renderer results are
  recorded in tests/evaluations/2026-11-14-revision-plan.md. Actual Claude execution is not claimed.

Compatibility: existing JSON specs, theme names, legacy glyphs and builder CLI remain supported.
New PPTX Feather icons require CairoSVG, added to requirements. Image-chart extensions are raster
exhibits, not editable charts; native decision tables and process text remain editable.


## 2026-11-12

### Creative direction and presenter voice

- Develop a subject-specific concept before selecting palette and typography. Add concise creative
  briefs, genuinely different concept candidates, relationship-based composition prompts and a
  distinctiveness review. Keep the process lightweight and avoid extra compulsory approval gates.
- Treat the layout library as a toolbox. Permit custom composition for explanatory or expressive
  value, not only after every standard type fails. Add a full-stage custom HTML option that retains
  sources, notes and provenance, with explicit native PPTX reconstruction requirements.
- Replace rigid composition and storytelling prescriptions with purpose-based defaults. Preserve
  factual, accessibility, readability and destination constraints; do not substitute novelty for proof.
- Strengthen positive voice development: presenter judgement, authentic samples, pivotal-title
  alternatives and contextual editing. Do not simulate humanity with invented detail, slang, errors
  or forced sentence variation. Keep technical terms, quotations and useful repetition.
- Add a fictional queue-review example with a spatial handoff concept, accurately counted units,
  an explicitly unproven intervention and an exact lookup table. CI builds and renders it as HTML;
  it is not advertised as automatically converted native PowerPoint.
- Expand evaluation to concept, composition, narrative sequence and presenter voice. Examples and
  passing renderer tests establish feasibility; future creative quality must be judged from outputs.


### Fixed

- Check literal figures even when `facts` is empty or absent. Ordinary counts and years, mixed
  chart arrays and numeric table cells can no longer silently bypass numerical provenance checks.
- Require sourced slide literals to link evidence IDs. A nonempty citation string alone is no
  longer sufficient. Evidence records now require precise locators as well as verification status.
- Reserve `calculated` facts for expressions, preventing raw values from acquiring that status.
- Propagate illustrative provenance through derived calculations. Missing visible labels and
  missing recorded user agreement now block final release rather than produce advisory notes.
- Ensure illustrative provenance badges appear in HTML and native PPTX, including full-bleed
  covers and closing slides that omit ordinary footers.
- Scan quotations, references, source lines, code, deck sources and notes for placeholders independently of
  editorial exemptions, including the documented "Source: to be added" gap marker. Custom HTML scans its text without mistaking CSS dimensions for data.
- Keep administrative number exceptions narrow and documented; an exception for a standalone
  digit does not remove that digit from larger substantive quantities.

### Added

- Per-slide reviewed claim inventories with exact presented wording, claim type and supporting
  evidence or analytical basis. Navigation-only slides can record a non-factual reason instead.
- `build_html.py --strict`, which refuses blocked final HTML before writing it. Draft generation
  remains available with reported blockers. Require the shared strict gate for every final route.
- Adversarial regression coverage and positive examples for evidence, quotations, calculations,
  illustrative labels, semantic review records and HTML release behavior.

### Changed

- Align agenda, reveal, repetition, restyling and text-only guidance across references. Retain the
  HTML-first approval workflow, with in-place edits distinguished from substantive rebuilding.
- Describe validation as checking pre-build records, not embedding assertions in the delivered
  PowerPoint or proving the truth of natural-language claims.
- Require custom PPTX reconstruction scripts to be kept beside the specification for later builds.
- Mark bundled layout examples explicitly illustrative and retain their fictional status. They
  are not evidence of real-world findings. CI now builds HTML examples in strict mode too.
- Remove the unsupported claim that audiences reliably recognize and discount machine-written
  text within seconds; evaluate clarity, specificity and presenter fit instead.

### Compatibility and limits

- Existing real decks may fail strict validation until evidence locators, linked evidence IDs and
  claim inventories are added. Do not classify real data as illustrative to avoid this migration.
- Verification status and user agreement fields are audit records. The validator cannot prove
  source authenticity, source support or completeness of a reviewed claim inventory. Check
  those during semantic review and reconcile the actual exported content before delivery.
- Draft and final render review remain separate requirements. Tests of generation are not proof
  of readability, visual fidelity or final-application behavior.

### Validation

- Local Python unit and adversarial tests pass; the browser sandbox test is skipped when
  Playwright is unavailable. All nine bundled decks pass strict specification validation and HTML
  generation. Check the associated pull request for the exact test count and CI results.
- Fresh browser and PowerPoint renders were not available in the local review environment.
  GitHub Actions installs their dependencies and runs the full existing smoke workflow.

## Earlier changes

These entries summarize existing history; they do not assign retrospective version numbers.

### 2026-11-12 — Sandboxed HTML previews (`cb30786`)

- Guard URL-history updates so sandboxed `about:srcdoc` previews can navigate without a
  `replaceState` security error; add a browser regression test.

### 2026-11-12 — First external-review changes (`640aca9`)

- Add the initial evidence register and strict gate, repair example contradictions and arithmetic
  helpers, decouple HTML loading from PowerPoint, and expand domain, fidelity and QA guidance.
- This gate had bypasses addressed in the unreleased entry above.

### 2026-11-12 — Initial repository (`794c98d`)

- Introduce the HTML-first presentation workflow, shared specification, native PPTX builder,
  reference library, examples and smoke tests.
