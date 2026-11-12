# Changelog

Record user-visible changes newest first. Each entry states the reason, behavior, compatibility
impact and validation. Add changes to the current unreleased entry until they are merged; do not
rewrite older entries to imply that later fixes already existed.

## Unreleased

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
