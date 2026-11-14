# Deck Studio

A shared Claude and ChatGPT skill for making presentations: consulting readouts, case competitions, board asks,
pitches, interviews, classes, research readouts, marketing plans and events.

Its working rule: **settle content, visuals and the slide skeleton in a fast HTML draft, and build
the PowerPoint (or Slides, Gamma, Canva) only after the user approves.**

```
Intake → Storyline → Creative direction → Draft (HTML) → Review and iterate → [user approves] → Finalise
```

Deck Studio first offers a choice when a presentation request does not already specify whether
to use it. Selecting the skill explicitly counts as consent. The choice carries through the current
deck and revisions; it is separate from approving the HTML draft before final production.

`SKILL.md` is the shared entry point. Everything else is loaded when needed.

For distinctive decks, develop the concept before selecting a theme. The creative-direction
reference helps the model make relationships visible, explore different compositions, pace the story
and write in the presenter's voice. Standard types are a toolbox; custom HTML compositions can
use the whole stage, with explicit final-format reconstruction limits.

## Download for Claude and ChatGPT

[Download the latest verified upload ZIP](https://github.com/PrahladRajhans/deck-studio/releases/latest/download/deck-studio.zip).
The package contains one `deck-studio/` folder matching the skill name, with the complete references,
scripts, examples, source packets, context and changelog. It is published only after main passes the
smoke workflow. GitHub's generic Code ZIP uses a different folder name, so use the release package
for direct upload. Use the same release ZIP for both supported skill importers:

| Host | Installation |
|---|---|
| Claude | Customize → Skills → create/upload a skill, then enable it |
| ChatGPT with native Skills available | Plugins → Skills → Create → Upload from your computer |
| ChatGPT without native Skills access | A dedicated GPT/Project can use adapted instructions and references, but attaching this ZIP does not install a native skill |

Product availability, account permissions, upload scanning and code-execution access still apply.
Current OpenAI guidance lists eligible Business, Enterprise, Healthcare and Edu users, subject to
workspace settings and product availability. Check the current documentation if the UI differs:
[ChatGPT Skills](https://help.openai.com/en/articles/20001066-skills-in-chatgpt) and
[Claude Skills](https://support.claude.com/en/articles/12512180-use-skills-in-claude).
Native skill installation is separate on each host; do not assume cross-product synchronisation.
The user reports successful use of the previous release in Claude. This cross-host revision has
automated source/package and builder checks, not an in-application certification for either host.

Try “prepare a PowerPoint”, “prepare a deck” or “make slides”: Deck Studio should offer the
choice before applying its method. Say “use Deck Studio” to proceed directly, or “without Deck
Studio” to use the usual workflow. Matching and consent are model instructions, not a guaranteed
platform popup. Metadata can be read for discovery before consent. An installed but disabled skill
cannot be expected to offer itself. The additional OpenAI metadata keeps implicit discovery enabled.

The shared core preserves the creative method, human-language guidance, chart and visual rules,
examples and builders. The [ChatGPT adapter](references/host-chatgpt.md) and
[Claude adapter](references/host-claude.md) handle available tools, previews and file delivery.
Installation does not supply missing rendering dependencies or access to external services.

For future releases, detect capabilities rather than model names, keep host changes in these thin
adapters, retain versioned source-verified releases, and recheck activation and output quality after
material host/model updates. No package can guarantee compatibility with every future product.

To reproduce locally: `python3 scripts/package_skill.py --out out/deck-studio.zip`.
The generated bundle manifest records source-file checksums; verification compares every packaged
file with its source. Checksums detect byte changes, not factual accuracy or publisher identity.

## What's in the repo

| Path | What it is |
|---|---|
| `SKILL.md` | Concise stage router, selective reference loading and approval gates |
| `licence.txt` | MIT licence, Copyright (c) 2026 Prahlad Rajhans; bundled third-party notices remain in place |
| `agents/openai.yaml` | OpenAI interface metadata and implicit-discovery policy; consent remains in the shared entry point |
| `references/host-chatgpt.md`, `references/host-claude.md` | Host-specific execution, preview and delivery guidance |
| `references/visual-components.md` | Visual grammar, icons, richer tables/processes, scenario charts and named alignment annotations |
| `references/evidence-policy.md` | Risk-based assurance, inherited provenance and unused research history |
| `references/workflow.md` | Commands, timings, fallback controls and destination limits |
| `references/creative-direction.md` | Concept development, creative moves, sequence, voice and distinctiveness review |
| `references/domain-packs.md` | What consulting, finance, marketing, energy, science/health, technology, policy and teaching decks must prove |
| `references/decision-trees.md` | T0-T11: job type, final format, mode, use case, structure, length, slide type, chart form, direction, frame, imagery, when to ask |
| `references/frameworks.md` | Brief canvas, decision structures, checks and balances |
| `references/deck-skeletons.md` | 40+ deck skeletons by situation |
| `references/slide-library.md` | The 44 slide types: use, avoid, limits |
| `references/visual-language.md` | 22 art directions, frames, covers, colour, type, grid, imagery, charts, anti-slop |
| `references/writing.md` | Headlines, talk rules, body text, numbers, notes, sources |
| `references/human-voice.md` | How to make slide text sound human, not AI-written |
| `references/storyline.md` | Story craft, case comps, interviews, turning a source into slides |
| `references/use-cases.md` | 11 use-case themes mapped to archetype, direction and Gamma template |
| `references/routes.md` | Fidelity contract per route, destination capabilities, HTML draft, Slides artifact, PPTX, templates, Gamma, Canva |
| `references/spec.md` | The JSON spec, the facts model, the evidence register and the strict release gate |
| `references/qa.md` | Render, lint codes, ten-point check, mode checks, fresh-eye review prompt, presenter prep |
| `references/credits.md` | Sources and what was taken from each |
| `scripts/spec_io.py` | Loads and validates a spec (no PowerPoint dependency); `--strict` is the release gate |
| `scripts/env_check.py` | Which fonts the fit measurement really uses; which renderers are available |
| `scripts/build_html.py` | Spec → self-contained HTML draft deck |
| `scripts/render_html.py` | Screenshots every draft slide, makes a contact sheet, flags text that does not fit |
| `scripts/build_deck.py` (+ `slides_extra.py`, `_common.py`) | Spec → native, editable PPTX |
| `scripts/render.py` | PPTX → PNGs and a contact sheet (LibreOffice) |
| `scripts/lint_deck.py` | Lints any .pptx, including Gamma and Canva exports |
| `scripts/preview_directions.py` | The same slides in several art directions, side by side |
| `scripts/chart_images.py` | Mekko, slope, dumbbell, heatmap, bullet, tornado and sensitivity charts as images |
| `assets/examples/*.json` | Worked example specs (all fictional or illustrative data) |
| `assets/examples/drafts/` | HTML drafts built from those specs, with contact sheets |
| `assets/creative-examples/queue-review.json` | A fictional concept-led HTML example with an exact counted display and a proposed test |
| `assets/html-stage/stage-template.html` | Hand-built HTML stage for layouts beyond the 44 types |
| `tests/smoke_test.sh` | Builds every example (draft and strict PPTX), renders both, lints, runs unit tests; run by GitHub Actions on each push |
| `tests/test_core.py` | Unit tests: arithmetic edge cases, validation, style exemptions, builder independence |
| `tests/fixtures/` | Fixed evidence packets for reproducible evaluation |
| `assets/benchmarks/` | Authored benchmark regression decks, including a draft-only missing-evidence case |
| `assets/forward-tests/` | Independently generated Codex drafts, not proof of Claude execution |
| `tests/benchmark-briefs.md` | Ten contrasting briefs and a scoring rubric for judging the skill's output |

## Try it

```bash
pip install -r requirements.txt
python -m playwright install chromium            # for the HTML draft renderer
# For PPTX rendering: LibreOffice and poppler (apt-get install -y libreoffice poppler-utils)

python3 scripts/build_html.py assets/examples/case-comp.json -o out/case-comp.html  # draft
python3 scripts/build_html.py assets/examples/case-comp.json --strict -o out/final.html  # after approval
python3 scripts/render_html.py out/case-comp.html out/render      # PNGs + contact-sheet.png
python3 scripts/spec_io.py assets/examples/case-comp.json --strict  # release gate
python3 scripts/build_deck.py assets/examples/case-comp.json --strict -o out/case-comp.pptx
python3 scripts/lint_deck.py out/case-comp.pptx
bash tests/smoke_test.sh                                          # everything, every example
```

Open any file in `assets/examples/drafts/` in a browser. Arrow keys move between slides, N shows
speaker notes, G shows all slides as a grid, P prints a PDF.

Changes and migration notes: [CHANGELOG.md](CHANGELOG.md).

Latest validation and limitations: [revision ledger](tests/evaluations/2026-11-14-revision-plan.md) and
[independent execution notes](tests/evaluations/2026-11-14-forward-test.md). Earlier
[creative planning checks](tests/evaluations/2026-11-12-creative-plans.md) remain historical evidence.

Feedback coverage and preservation audit: [what was adopted, retained or declined](tests/evaluations/2026-11-14-feedback-coverage.md).
Additional samples cover fair option judgements, per-order contribution and cash-flow teaching.
For the expressive brand's native editable reconstruction:

```bash
python3 assets/forward-tests/rebuild_brand.py -o out/brand-native.pptx
python3 scripts/render.py out/brand-native.pptx out/render-brand-native
python3 scripts/lint_deck.py out/brand-native.pptx
```

The recipe targets that specific concept and shares its resolved copy, sources and notes. It is not
a general HTML converter. Build a corresponding native recipe for other custom designs.

Execution and reference checks: `python3 scripts/check_links.py`; feature readiness:
`python3 scripts/env_check.py --json`. Select route prerequisites with `--require` rather than
requiring every optional package for every task. Recovery budgets and explicit pause/stop outcomes
are in references/workflow.md. Renderer timeouts report failure; they never certify an incomplete
output. POSIX subprocess groups are cleaned up; target applications/model behavior still need review.

Latest execution/linkage closure: [findings, fixes and verification limits](tests/evaluations/2026-11-14-closed-loops.md).

## For reviewers

Useful questions to review against:

1. **Consistency.** Does any file contradict `SKILL.md` or another reference?
2. **Loops and dead ends.** Is there a point where a model following the instructions would get
   stuck, loop, or have two equally valid next steps with no rule to choose?
3. **The approval gate.** Is it always clear when the final PowerPoint/Gamma/Canva build may happen,
   including when the user names a format up front, when they say "skip the draft", and when no
   one is there to answer?
4. **Coverage.** What is missing for consulting, pitch, MBA, marketing, formal and creative decks?
5. **Human voice.** Do the rules in `human-voice.md` (and the checks in `_common.py`) ban anything a
   real deck needs, or miss common AI tells?
6. **Truth.** Can a number or source still slip onto a slide without going through `facts`, a
   declared `data_status` or a visible "to be added" gap? (`spec_io.py --strict` is meant to stop it.)

`references/credits.md` ends with the review history: what earlier reviews found, what was adopted,
and what was not, with reasons.

The skill was written for Claude, with its scripts running in Claude's workspace. Example data is
fictional or labelled illustrative.

## Licence

Deck Studio is licensed under the [MIT License](licence.txt), copyright © 2026 Prahlad Rajhans.
Bundled third-party material retains its own notices, including the
[Feather icon licence](assets/icons/feather/LICENSE). The project licence does not replace those
notices or reattribute their authorship. Runtime dependencies retain their respective licences.
