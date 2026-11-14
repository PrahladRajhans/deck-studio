# Feedback coverage and preservation audit — 14 November 2026

Baseline for this follow-up: main a9decf9bf4c0bd18108fdac2278d8d98720bd202, after PR 2.
The user asked whether both the earlier Gemini/Claude discussion and the detailed Gemini review
were covered, and whether slimming lost meaning. This file is the review ledger, not a reference
Claude needs to preload while making a deck.

## Sources and confidence

Read the four user-supplied Gemini PDFs, including the later five-page review of ten actual files,
and the Claude analysis quoted in the conversation. The earlier reports explicitly describe unread
ZIP content or different public repositories. Their recommendations are evaluated as suggestions;
claims about other repositories are not evidence of defects in this one. The later report examines
actual files but still cannot establish runtime behavior without executing the relevant code.

Primary guidance checked on 14 November 2026: Anthropic on progressive disclosure/evaluation, W3C
on text contrast, Microsoft on presentation reading order/alt text, and ONS/Analysis Function on
colour and uncertainty. See references/credits.md for exact URLs and how each informs this skill.

## Coverage of the earlier review and Claude's analysis

| Suggestion | Disposition | Implementation or reason |
|---|---|---|
| Reduce initial context and route by stage | Implemented | SKILL is a short router; detail remains in references with a read-now/read-if-needed table |
| Narrative plan before deterministic layout | Retained | Shared spec/facts drive HTML and native PPTX; model plans the argument |
| Horizontal title audit | Retained | Gate 2 and spec_io --outline; writing.md explains purposeful title forms |
| Vertical title/body agreement | Retained | qa.md semantic review; machine checks are not proof of meaning |
| Relationship-based layout/chart selection | Retained and linked | T6/T7 directly linked at production stage; avoid-default column and targeted visual defaults |
| Stable style contract | Retained | direction/theme and the creative brief are the shared contract; no competing spec_lock needed |
| Render and inspect actual output | Retained and exercised | HTML, PPTX and native reconstruction renders in smoke workflow |
| Native editable standard charts | Retained | Existing chart kinds remain native; new image helpers are explicitly raster exhibits |
| Source, kicker and so-what anatomy | Retained as purposeful defaults | Existing anatomy remains available; expressive/teaching slides need not carry every item |
| Colour contrast | Retained and researched | 4.5:1 normal text, 3:1 large text as AA reference; status labels accompany colour |
| Failed asset retrieval fallback | Retained | Draft placeholder/typographic fallback; never invent documentary assets; resolve final placeholders |
| Real font measurements | Retained | Existing font-metric fitting is not replaced with crude character estimates |
| Forbidden-default column | Implemented as advisory | T7 Avoid column plus visual-components choices; tables remain valid for exact lookup |
| RAG and Harvey-ball decision matrix | Implemented | Structured native/HTML table cells with labels, ordinal rubric and unknown state |
| En dashes and sentence case | Implemented as editorial defaults | human-voice typography section; retain quotations, brands, acronyms and technical forms |
| Scale evidence bureaucracy by stakes | Implemented | brief/standard/high assurance by consequence; source inheritance avoids repeated provenance |
| Executive, marketing and missing-evidence benchmarks | Implemented | Fixed packets, authored specimens, independent executions and CI renders |
| Hard-banned word list | Declined | Contextual prompts retain precise technical terms and credible presenter register |
| No repeated layouts on adjacent slides | Declined | Consistent comparison/teaching can benefit from repetition; no novelty quota |
| Number in every title | Declined | Claim strength follows evidence; labels/questions can serve legitimate roles |
| Telegraphic copy by dropping articles | Declined as universal rule | Readable compression depends on presenter, audience and delivery setting |
| 7:1 headers described as AA | Corrected | W3C AA large text threshold is 3:1; stronger contrast can be desirable without mislabelling it |
| Universal Aptos/Helvetica Neue availability | Declined | Font substitution must be tested; env_check reports what is actually available |
| Split every title containing 'and' | Declined | Semantic relationship determines whether it contains multiple jobs, not a token search |

## Detailed actual-file Gemini review

| Finding/suggestion | Status after this audit | Where or judgement |
|---|---|---|
| Ghost deck before mode/structure | Fixed in PR 2 | Intake brief gate, then mode/structure/storyline and Gate 2 |
| Provisional destination too late | Fixed in PR 2 | Intake establishes final-route constraints |
| Duplicate conflicting theme tables | Fixed in PR 2 | T8 is the authoritative selector; expressive grammar remains distinct from a palette |
| Manual stage lacks N/G controls | Fixed and tested in PR 2 | Notes, grid, Escape, sandbox-safe navigation and print |
| Manual stage fixed to three cards | Fixed and tested in PR 2 | Count derived from actual children, with explicit author override |
| Live executive density/type conflict | Closed in follow-up | Route projected decision decks to existing talk mode, answer first; lookup detail in notes/appendix/document variant |
| New exec_live token with 14pt body | Not introduced | Avoid an unsupported enum or lowering readability to fit; projection profile uses tested talk renderer |
| Custom HTML native reconstruction cliff | Strengthened in follow-up | Preflight hardest native relationship before approval; explicit editable reconstruction recipe for brand.json |
| Full-slide rasterisation fallback | Not defaulted | Native text/shapes retained; disclose and agree any material image-based adaptation |
| Naming PPTX should bypass draft approval | Not adopted | Preserve user's established HTML-first workflow; explicit direct-file/skip-draft instructions authorise same-run final production |
| Tornado chart | Implemented in PR 2 and routed now | chart_images helper, T6/T7; one-input-at-a-time outcome ranges |
| Two-way sensitivity table | Implemented, crosshair strengthened | Native table/HTML base marker and row/column crosshair; separate raster helper |
| Quantified process/value chain | Implemented, extended | volume, duration, cost, conversion, defect_rate, drop_off; units and denominators explicit |
| Unit economics / margin layers | Example and recipe added | Native waterfall and table; define CM labels and fixed-cost exclusions; missing LTV never invented |
| Complexity-weighted timing | Implemented in PR 2 | Explicit rehearsal seconds win; role/complexity estimates are a fallback |
| Repetitive Topic: claim headlines | Guidance strengthened | Existing deck-wide colon prompt retained; human-voice explains subject-first writing with contextual exceptions |
| Strawman all-red alternatives/all-green winner | Guidance and example added | domain-packs fair-options section; viable strengths, unknown distinct from failure, explicit rubric |
| Repeated fact provenance | Fixed in PR 2 | Source inheritance through fact dependencies; semantic review still required for interpretive claims |

## What slimming preserved, and what was restored

A separate read-only validator compared the pre-PR-2 SKILL/frameworks files with the revised bundle.
It found no substantial loss of the creative mandate or authentic presenter voice. It identified:

- Deleted showcase-first advice: restored in SKILL Stage 4 and workflow.md. Render a representative
  dense specimen before scaling a repeated section; then inspect its longest variant.
- Partly lost production order: restored as a content-first production heuristic in workflow.md,
  distinct from audience slide order and permissive of exploring a meaningful cover concept early.
- Weaker direct access to writing.md: restored in the writing/specification stage route.
- Weaker T6/T7 access: restored in the layout-production route, with the new components in the tables.

Retained detail: storyline structures, title/notes anatomy, domain packs, deck skeletons, full slide
library, theme/frame/image language, presenter voice, strict evidence policy, destination adapters,
final reconciliation and QA. Material detail can move to notes/appendix; shortening a slide is not
permission to remove a premise, source, caveat or technical meaning. No global creative quota added.

## Additional samples and actual checks

- decision-tradeoffs.json: RAG plus Harvey/unknown assessments, viable competing advantages and a
  quantified process. A preferred option still has weaknesses. Ordinal scores do not masquerade as ROI.
- unit-economics.json: INR-per-order waterfall and defined contribution layers; no fabricated LTV.
- cash-flow-teaching.json: question, simplified profit-to-cash bridge, closing cash reconciliation,
  retrieval question and an answer in speaker notes.
- assets/forward-tests/rebuild_brand.py: deliberate native reconstruction of the specific four-slide
  expressive concept, using resolved copy, editable text/shapes, sources and original notes.
  It rejects structural changes requiring a revised recipe. It is not a general HTML converter.
- Existing examples, fixed packets and earlier regressions remain in smoke tests.

Independent review repaired a mismatched option criterion, a confusing quiz choice and an overly
broad showcase-first instruction. It also identified that chunk counts alone did not detect markup
changes. The native recipe now pins a structural/layout signature while keeping copy in the shared
spec, and tests reject both added copy and same-count structure/style changes. A malformed base-cell
regression now produces a controlled spec error rather than an indexing crash. Initial full CI caught
a cover textbox too short at the intended 90pt size; its geometry was enlarged without shrinking type.

Validation outcomes and publication are recorded below after checks, renders and source readback.

## Upload-package follow-through

Anthropic's current custom-skill instructions require the ZIP root folder to match the skill name.
GitHub's generic main archive uses deck-studio-main, so it is not the preferred direct-upload link.
package_skill.py produces deck-studio.zip with a deck-studio/ root, preserves all references,
scripts, examples, fixed packets, tests, evaluation context and changelog, and verifies every source
byte against a manifest. A regression rejects tampering. Successful main CI publishes the ZIP as a
versioned GitHub release, with a stable latest-download URL. It does not mark actual Claude execution
as passed. Workflow publication is restricted to main push after successful smoke checks.

## Remaining limits

Actual execution inside Claude is still untested. Codex executions and Chromium/LibreOffice renders
are not Claude tests or certification of every target application. The brand recipe demonstrates one
editable custom path; it does not eliminate the need to implement other custom designs deliberately.
Accessibility checks require target-application reading-order/screen-reader review when relevant.
Creative samples establish working examples, not a guarantee of artistic quality in every future deck.

## Verification and publication record

- Native/runtime checkpoint 487dcf0ee56b44cd3438d5339ffe69f8df0b4c84 passed CI run 43588787868,
  including all 73 tests without skips, old/new HTML and PPTX builds, rendering and lint.
- That artifact contains 21 HTML decks / 148 slide renders and 17 PPTX decks / 131 slide renders.
  Native reconstruction is included in the PPTX count; no whole-slide raster wrapper is used.
- New decision, contribution, teaching and native-brand lints are clean. The missing-evidence final
  still refuses output. Copy/readback checks preserve every brand text block, source and speaker note.
- Rendered contact sheets and individual dense/new native slides were reviewed. Brand reconstruction
  preserves typography, conceptual circle/rules and content hierarchy with disclosed geometric
  adaptation; the large cover type fits after its box-height repair. RAG labels remain readable;
  financial bridges and closing cash reconcile, with assumptions visible or in notes.
- Packaging adds one test, bringing the local suite to 74 (67 passed, seven renderer-dependency
  skips). The full CI environment has those dependencies. Local upload build and verify-only both
  passed, preserving source bytes and a correctly named root; package tampering is rejected.
- Final source is read back against the published Git tree. The exact final PR head must pass full
  CI before merge; final run outcomes are recorded on https://github.com/PrahladRajhans/deck-studio/pull/3.
- After merge, main's successful workflow publishes and re-downloads the release ZIP, then verifies
  it against that exact main source. The stable asset URL is
  https://github.com/PrahladRajhans/deck-studio/releases/latest/download/deck-studio.zip.
  Release publication stages the asset as a draft, repairs a missing asset on retry, and checks
  manifest schema, expected revision and every source byte before making it public/latest.
  Publication is a separately checked step; a ZIP link is not reported ready until its release exists.

Commands used: unittest discovery; tests/smoke_test.sh; spec_io --strict; both builders; Chromium
and LibreOffice renders; native brand recipe; lint; package_skill.py build and verify-only.
The changelog records the follow-up separately from the earlier PR 2 work. Claude execution remains
an explicit untested target, not hidden behind the automated test count.
