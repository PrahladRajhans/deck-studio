# Revision plan and verification ledger — 14 November 2026

Base: main `315d1076a43ef9a950b8a6cc9383f6d27e616891`. Preserve HTML-first user approval,
existing examples and native editability. Work is isolated until tests and renders pass.

## Checkpoints

1. Routing and workflow
   - Short entry point, explicit stage-specific loading, one theme-selection table.
   - Intake establishes provisional destination; storyline audit follows mode/structure decisions.
   - Independent outline/schema commands; preserve old CLI compatibility.
2. Evidence and usability
   - Check evidence/facts reachable from delivered content; retain unused gaps as advisory history.
   - Inherit provenance through fact dependencies without treating arithmetic as semantic proof.
   - Optional brief/standard/high assurance documentation, chosen by claim consequence.
   - Keep contradiction, placeholder, numerical, illustrative-label and source-honesty rules.
3. Visual system and components
   - Visual grammar, image/art direction, shape/diagram semantics, optical alignment and layering.
   - Bundle one pinned, licensed icon family with HTML and PNG export.
   - Extend existing tables/processes; add tornado and sensitivity chart helpers, unit-economics recipes.
   - Targeted alignment groups and narrowly declared intentional overlaps; no global collision waiver.
   - Explicit slide timing overrides, fallback complexity weights; parity for fallback HTML controls.
4. Evaluation and publication
   - Fixed source packets for executive, marketing-confounding, incomplete-evidence and expressive briefs.
   - Unit regressions, old/new HTML and PPTX builds, rendering, lint, source readback and changelog.
   - Independent task executions and visual inspection; record renderer/model/environment honestly.
   - Run inside Claude only if a callable authorised Claude environment exists. Otherwise provide
     exact packets and record target-Claude verification as pending, not as passed.

## Baseline

- Exact local blob comparison against remote main: no mismatches.
- 42 local unit tests: 40 passed, 2 dependency-related skips.
- Local Python lacks PPTX/Pillow/Playwright/matplotlib; no Claude CLI or LibreOffice found.
- GitHub Actions supplies render dependencies. Its result is required before publication to main.

## Completion ledger

- Routing: SKILL.md reduced from the prior 400-line entry point to 163 lines. Detailed command,
  provenance and visual rules live in selectively loaded references. Destination is provisional at
  intake; mode and structure precede the storyline audit. Legacy builder CLI remains available.
- Evidence: source references inherit through fact dependencies; semantic claim status and analytical
  basis are still checked. Unused research gaps are advisory, never silently deleted. Brief assurance
  requires supplied evidence; high assurance retains explicit claim review. Placeholder, illustrative
  authorization, classification and numerical regression tests remain in the suite.
- Visuals: semantic RAG/Harvey cells and base markers remain native table content; process metrics
  remain editable text. Bundled MIT Feather SVGs become offline HTML icons and PNGs inside PPTX.
  Status hues retain their meaning across themes, and icon foregrounds follow actual badge contrast.
  Tornado and sensitivity helpers explicitly describe scenarios, base cases and conditional scope.
- Geometry/runtime: alignment checks use actual named boxes; overlap exceptions apply only to one
  documented pair. Malformed annotations warn instead of crashing. Timings reject nonfinite values;
  explicit rehearsal timings take priority. Manual fallback supports notes, grid, sandbox navigation
  and card counts derived from actual content. Full-stage custom headings respect container fonts.
- Human voice: positive presenter register remains the starting point; recurring legitimate terms
  need no per-word records. Copy review parses visible custom HTML, excluding reconstruction notes,
  attributes and hidden templates. Repeated custom slide types are not mistaken for repeated layouts.

## Independent execution and review

A separate Codex agent generated executive, marketing and brand drafts from fixed packets before
reading the authored benchmark solutions. The retained specs are assets/forward-tests; the agent's
original report is 2026-11-14-forward-test.md. Another agent reviewed source changes and reproduced
edge cases. Neither executor was Claude.

Concrete findings adopted: invisible icons, stale workflow cross-references, malformed annotation
crashes, nonfinite timing acceptance, custom-copy false positives, theme-font leakage, RAG amber
following theme-blue, and tornado endpoint crowding. Fixes have relevant tests and/or rendered review.

The source packet contains hypothetical data, explicitly labelled illustrative. Verification of that
packet establishes faithful use of supplied inputs, not evidence about a real company or event.
The incomplete-evidence specimen remains a draft and is deliberately rejected by strict production.

## Validation record

- Local: 67 unit tests, 61 passed and six renderer-dependent skips. `git diff --check` clean.
- Full CI checkpoint: run 43586029474 passed 65 tests with no skips plus all smoke builds/renders.
- Independent-execution checkpoint: run 43586247059 passed the complete smoke workflow. Its artifact
  contains 18 HTML decks / 132 HTML slide renders, 13 PPTX files / 111 PPTX slide renders and four
  image charts. Strict missing-evidence output was refused without writing a final file.
- Subsequent semantic-colour/label-spacing checkpoint: run 43586475518 passed the full workflow.
- Final runtime commit: 1f79cc422c09d23ff66a5a8c50019ec6ae294bbc. Run 43586650290 passed all 67 tests without skips and the complete smoke workflow.
  Final artifacts were inspected: custom Arial headings, amber status, icon visibility and tornado
  endpoint spacing now match their intended behavior.
  https://github.com/PrahladRajhans/deck-studio/actions/runs/43586650290

Commands: `python3 -m unittest discover -s tests -p 'test*.py' -q`,
`bash tests/smoke_test.sh out/smoke`, and independent `spec_io.py --strict`, `--outline`,
`build_html.py`, browser rendering, native PPTX build, LibreOffice rendering and lint.
CI runs Python 3.12 with Chromium, installed Office-compatible fonts, CairoSVG, LibreOffice and poppler.

Rendered review covered new component/benchmark contact sheets, independent executive/marketing/brand
sequences, scenario charts, and representative dense/custom slides at individual-slide size. Component
fixtures exercise capabilities; their sparse template composition is not evidence of creative quality.
The independent festival draft develops a coherent printshop/poster identity; the executive draft
shows five-year undiscounted savings merely matching upfront cost; marketing leaves incremental
campaign credit unassigned. These are useful qualitative observations, not a measured improvement
against a prior-model baseline. Final typography and tornado spacing are rechecked in final artifacts.

## Limits and follow-up

- Actual Claude execution is pending: no callable Claude environment was available. Use the fixed
  packets unchanged in Claude, retain its generated spec and rendered deck, and judge each rubric
  dimension separately. Do not describe Codex forward tests as Claude tests.
- Custom HTML examples are draft-route tests. Automatic custom-to-native-PPTX conversion is not
  claimed; final editable reconstruction requires its own implementation and inspection.
- Chromium/LibreOffice results do not certify every PowerPoint version, plugin destination, font
  environment or future model output. Source semantics still need human/model judgement.
- No mathematical guarantee of error-free future decks is possible. This record states what was
  actually tested, what failed and was repaired, and what remains untested.

Publication: pull request https://github.com/PrahladRajhans/deck-studio/pull/2. Documentation-only
completion records follow the tested runtime commit; CI also checks the final PR head before merge.
