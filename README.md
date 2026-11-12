# Deck Studio

A Claude skill for making presentations: consulting readouts, case competitions, board asks,
pitches, interviews, classes, research readouts, marketing plans and events.

Its working rule: **settle content, visuals and the slide skeleton in a fast HTML draft, and build
the PowerPoint (or Slides, Gamma, Canva) only after the user approves.**

```
Plan → Decide → Select → Draft (HTML) → Review and iterate → [user approves] → Finalise
```

`SKILL.md` is the entry point Claude reads. Everything else is loaded when needed.

## What's in the repo

| Path | What it is |
|---|---|
| `SKILL.md` | The method: truth rules, the draft-first rule, six stages with gates, commands, anti-patterns |
| `references/domain-packs.md` | What consulting, finance, marketing, energy, science/health, technology, policy and teaching decks must prove |
| `references/decision-trees.md` | T0-T11: job type, final format, mode, use case, structure, length, slide type, chart form, direction, frame, imagery, when to ask |
| `references/frameworks.md` | Brief canvas, decision structures, selection, skeleton and anatomy, checks and balances, review rounds |
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
| `scripts/chart_images.py` | Mekko, slope, dumbbell, heatmap and bullet charts as images |
| `assets/examples/*.json` | Worked example specs (all fictional or illustrative data) |
| `assets/examples/drafts/` | HTML drafts built from those specs, with contact sheets |
| `assets/html-stage/stage-template.html` | Hand-built HTML stage for layouts beyond the 44 types |
| `tests/smoke_test.sh` | Builds every example (draft and strict PPTX), renders both, lints, runs unit tests; run by GitHub Actions on each push |
| `tests/test_core.py` | Unit tests: arithmetic edge cases, validation, style exemptions, builder independence |
| `tests/benchmark-briefs.md` | Ten contrasting briefs and a scoring rubric for judging the skill's output |

## Try it

```bash
pip install -r requirements.txt
python -m playwright install chromium            # for the HTML draft renderer
# For PPTX rendering: LibreOffice and poppler (apt-get install -y libreoffice poppler-utils)

python3 scripts/build_html.py assets/examples/case-comp.json -o out/case-comp.html
python3 scripts/render_html.py out/case-comp.html out/render      # PNGs + contact-sheet.png
python3 scripts/spec_io.py assets/examples/case-comp.json --strict  # release gate
python3 scripts/build_deck.py assets/examples/case-comp.json --strict -o out/case-comp.pptx
python3 scripts/lint_deck.py out/case-comp.pptx
bash tests/smoke_test.sh                                          # everything, every example
```

Open any file in `assets/examples/drafts/` in a browser. Arrow keys move between slides, N shows
speaker notes, G shows all slides as a grid, P prints a PDF.

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
