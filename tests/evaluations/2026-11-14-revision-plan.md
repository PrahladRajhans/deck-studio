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

Updated at completion with exact commands, outcomes, known limits and the pull-request link.
Passing tests cannot guarantee every future model-generated deck or source claim is correct.
