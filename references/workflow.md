# Production reference

## Host capabilities

After the activation choice in SKILL.md, use host-chatgpt.md or host-claude.md for previews and
file delivery. Resolve paths from the installed skill root and check the chosen route's actual
capabilities. A model upgrade or successful skill upload does not establish runtime readiness.
Keep this shared pipeline and its checks unchanged when adapting to another host.

## Commands

Use the independent specification tooling for early planning. Existing build_deck.py --schema and
--outline remain compatible but import PowerPoint dependencies.

```bash
S=<skill-directory>/scripts
python3 "$S/spec_io.py" --schema
python3 "$S/spec_io.py" spec.json --outline
python3 "$S/spec_io.py" spec.json
python3 "$S/spec_io.py" spec.json --strict
python3 "$S/env_check.py"
# HTML draft
python3 "$S/build_html.py" spec.json -o out/deck.html
python3 "$S/render_html.py" out/deck.html out/render-html
# Final production, after approval or an explicit skip
python3 "$S/build_html.py" spec.json --strict -o out/final.html
python3 "$S/build_deck.py" spec.json --strict -o out/deck.pptx
python3 "$S/render.py" out/deck.pptx out/render-pptx
python3 "$S/lint_deck.py" out/deck.pptx --spec spec.json
```

A facts/check error exits 2. Strict validation refuses blocked final builds. Native PPTX fit or
placeholder failures exit 3. HTML fit is evaluated by render_html.py, which exits 3 on reported
failures. Passing generation is not proof that the slide is readable or factually correct.

## Timing

Set `minutes` for an estimated slot, or explicit `seconds` on a slide after rehearsal. Explicit
timings take precedence. Otherwise, covers/dividers/agenda/closing receive short estimates and
remaining time is weighted by slide complexity, with a reserve. Estimates are not measured speech.
Check the total against the slot; do not silently shorten explicit rehearsal timings to fit.

## Destination and custom composition

Read only the chosen routes.md adapter. Before approving a custom composition, check that its
text, shapes, image treatment and data encoding can be reconstructed in the target. Prefer reusable
native components when they serve the idea. Keep the HTML as the reference and preserve custom
reconstruction code alongside the spec. An agreed image-based exhibit is a disclosed fallback;
full-slide rasterisation is never the default substitute for an editable deck.

The expressive brand example has an explicit native recipe:
`python3 assets/forward-tests/rebuild_brand.py -o out/brand-native.pptx`.
It validates the shared spec and preserves its copy/sources/notes with editable text and shapes.
Review the controlled layout adaptations against HTML; this recipe supports that example only.
Run the normal render/lint/readback checks before treating a reconstruction as complete.

## Fallback HTML

assets/html-stage/stage-template.html is a small manual starting point. Preserve its fixed stage,
scaling and sandbox-safe navigation. Its notes/grid controls are tested separately from the generated
runtime. It does not provide the facts model, automatic fitting or strict validation: apply those
checks manually or restore the complete script bundle. Example card counts and layouts may change
with the content; do not repeat them by habit.

## Verification and revisions

- Version before destructive edits. Preserve unrelated changes and use exact specification diffs.
- Inspect the contact sheet for sequence, then individual slides for evidence, hierarchy and defects.
- Keep material caveats and real limitations. Use narrowly documented intentional layering; never
  suppress all warnings on a slide or treat a waiver as proof of accessibility.
- After final production, reconcile order, claims, quantities, units, images, sources and notes.
- Name the renderer and target applications actually tested. A LibreOffice render does not establish
  identical behavior in every version of PowerPoint, Canva or Gamma.

## Build in an order that exposes risk early

After the ghost deck, start with consequential content exhibits and one representative dense slide.
For a section of four or more similar slides, render and inspect that first specimen before scaling
the pattern. Recheck the longest variant. Content-first production often works well: evidence core,
then summary/ask, navigation/dividers, cover/close and appendix. This is a production heuristic, not
the audience's slide order or a restriction on exploring a strong cover concept early. Rewrite the
summary after the evidence changes. Preserve relevant detail in notes or appendix rather than
silently deleting it to fit a short slide.

## Bounded recovery and explicit exits

Keep one task-level QA budget: three failed-check repair rounds or 15 minutes, whichever comes
first, unless the user specifies otherwise. Track the count in normal progress notes, not per-slide
compliance records. Initial authoring and useful concept exploration are outside this recovery count.
New layouts, routes and failed API calls share the same budget. Count a changed API recovery
attempt plus its result check as one round; discovery is limited to one refreshed lookup and one
verified alternative for that failed step, never a fresh budget. Do not restart it implicitly.

| Condition | Next step | Exit when unresolved |
|---|---|---|
| Fit/collision failure | Fix the relevant spec, rebuild and inspect; count the round | Budget exhausted: last usable draft plus exact failed slides and next decision |
| Missing evidence | Narrow or remove the claim, or request essential evidence once | Keep a labelled draft; strict final remains blocked |
| Approval missing | Show the reviewed draft and identify the pending decision | Pause; do not poll or manufacture approval |
| Dependency absent/broken | Check the required feature, attempt one appropriate setup if allowed | Report the blocked feature; retain the draft or use an authorised available route |
| External API/template rejection | One refreshed capability/template lookup, then one verified alternative | No identical retry; report blocked operation and available draft/export |
| Renderer timeout | Inspect diagnostic; one materially changed retry within remaining budget | Stop and withhold the unverified final |
| Material destination compromise | Explain the change against the approved design | Await agreement before that compromise |

`render.py` bounds each external conversion at 240 seconds and shares a 600-second conversion
budget. `preview_directions.py` bounds child commands at 240 seconds within a 900-second total.
Both accept `--timeout` and `--budget` in seconds; pass the smaller remaining task budget where
appropriate. Timeout exit is 124, with a diagnostic rather than a success claim. POSIX cleanup retains one owner across nested commands and kills
the whole stage group, including converters; Windows cleanup kills the direct child and still needs host/job supervision.
No automatic retry is hidden inside the execution helper. A local file operation or arbitrary model
trajectory is not made mathematically time-bounded by these controls.

Use `env_check.py --json` for feature readiness, or `--require html_render`, `--require pptx_build`,
`--require pptx_render`, `--require pptx_icons` or `--require chart_images` for the chosen route.
Required-feature failure exits 1. Dependency-free HTML drafting remains available when optional
PowerPoint/icon packages are missing. CairoSVG is tested by actually rasterising a bundled icon;
its Python import alone is not treated as proof that native Cairo works. Font substitution and
final application wrapping still need visual review.

Run `python3 scripts/check_links.py` after moving references or modules. CI checks internal file and
section references plus circular local imports. This is structural validation, not proof that prose
instructions have identical meaning or that a changing external service is available.
