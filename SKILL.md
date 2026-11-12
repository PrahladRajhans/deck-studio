---
name: deck-studio
description: Master presentation skill. Plans, drafts and QAs any deck (consulting readouts, case competitions, board asks, pitches, interviews, classes, research, marketing, events) as a fast HTML draft first, then builds the approved version as editable PPTX, Slides, Gamma, Canva or HTML. Use for any deck or slide task, including reviewing or fixing one.
---

# Deck Studio

One method for every deck, whatever the room:

**Plan → Decide → Select → Draft (HTML) → Review and iterate → [user approves] → Finalise**

Each stage closes with a gate. Weak decks fail in planning, not design, so no layout opens before
Gate 1. Content, visuals and the slide skeleton are settled in a cheap HTML draft. The expensive
final build (PowerPoint, Slides, Gamma or Canva) happens once, after the user says go.

What this skill brings together:
- the Gamma Design Playbook (Gamma, Canva and Manus studies; The Deck Framework);
- the best of ten public PowerPoint skills (`references/credits.md`);
- classic references (Minto, Duarte, Zelazny, Sequoia, YC, Kawasaki);
- the BeHuman/Unslop human-voice rules.

Tooling: one JSON spec with a facts model drives everything. From it you can build:
- an HTML draft deck (`build_html.py`);
- a native PPTX (`build_deck.py`: 44 slide types, 11 chart kinds, 22 art directions, 4 frames,
  4 cover styles).

There are also renderers for both, a linter for any .pptx, a direction previewer, and chart
images for chart forms PowerPoint lacks.

## Truth rules (non-negotiable)

1. **Never invent anything.** No made-up number, source, institute, quote, logo, photo or person.
   - A gap stays visible: "Source: to be added" on the slide, or `[CONFIRM: …]` / an `assumptions`
     line in the notes.
   - Illustrative figures are labelled illustrative on the slide.
2. **Every number that appears twice comes from one place** (`facts`).
   - Derived figures are computed, not typed.
   - `checks` assert every claim the argument rests on.
   - Decide once whether a figure is an increment or an absolute.
3. **Check today's date.** Plans start after it.
4. **Read back generator output.** Anything Gamma, Canva AI or another generator produces is read
   back and checked before the user sees it, because generators invent sources and numbers.
5. **Report honestly** what was checked and what was not.

## Draft first, finalise on approval (the working rule)

- **Draft in HTML.** Every new deck starts as an HTML draft built from the spec (`build_html.py`).
  It costs a fraction of the tokens and time of a PPTX, Gamma or Canva build. It also changes look
  with one field (`direction`), so the user can iterate freely.
- **Build the final format only after a clear go-ahead.** That means PPTX, a Slides artifact,
  Gamma or Canva, and the go-ahead is the user approving the draft ("looks good, make the
  PowerPoint"). Naming a format up front ("I need a pptx") sets the final target; it is not
  approval. Say so, and draft first.
- **Explicit skip.** The user can skip drafting ("skip the draft", "just give me the file now").
  That request is the go-ahead.
- **Edits stay in format.** Editing a deck the user attached stays in that deck's format
  (routes.md §B, editing). There is no draft stage for edits.
- **Unattended runs.** When the user is away or the run is scheduled, build and QA the draft, say
  what is waiting for approval, and stop. Never build the final format unattended.
- **Same spec, no rework.** The approved spec is the input to the final build, so iteration costs
  nothing at the end.

## The flow

### Stage 1 · Plan (frameworks.md §1-2)
1. Fill the brief canvas: audience, decision (one verb), setting, mode, time, governing thought
   (one sentence), success metric, evidence in hand, judging criteria, constraints, accessibility,
   tone, final format if named.
2. Ask only what you cannot infer: once, at most 3 questions (decision-trees.md T11). Otherwise
   state your assumptions and proceed.
3. Write the **ghost deck**: titles only, in order.

**Gate 1 · headline test.**
- The titles alone tell the story (document) or the plot (talk).
- Document titles pass two tests: "a sceptic could disagree" and "hide the body, the point
  survives".
- `build_deck.py spec.json --outline` prints the headline track.

### Stage 2 · Decide (decision-trees.md T2-T5, storyline.md, deck-skeletons.md)
- **Mode.**
  - Document: read and decided from; answer first; dense allowed; ≥ 12pt.
  - Talk: presented; revealed step by step; no agenda; question dividers; ≤ 40 words a slide;
    ≥ 18pt; close with an action.
- **Archetype**, from what the room must do: recommendation · pitch · personal story · review ·
  explainer · research readout · change/workshop · marketing plan · event · options-first.
- **Structure**:
  - pyramid/SCQA (senior, deciding);
  - sparkline (live, sceptical);
  - problem-agitate-solve;
  - chapters (people);
  - question-method-findings (research);
  - scorecard-moved-risks-asks (status).
- **Skeleton**: start from the nearest of the 40+ in deck-skeletons.md; cut what the story
  doesn't need.
- **Length**:
  - document: one slide per claim;
  - talk: ≈ 30-45 s per body slide;
  - business: ≈ 1.5-2 min per content slide;
  - pitch: ≈ 10/20/30.
  - Set `minutes` for timing notes.

**Gate 2.** Every title serves the spine. Anything else goes to the appendix or goes.

### Stage 3 · Select (decision-trees.md T8-T10; visual-language.md)
**Direction** (T8) is formality × energy × brand × medium.

| Room | Safe | Bolder | Wildcard |
|---|---|---|---|
| Case comp / client readout | consulting-navy | editorial-warm | heritage-india |
| Board / IC / finance | boardroom-oxblood | finance-emerald | mono-ink |
| Pitch / demo day / launch | electric-launch | bold-signal | dark-stage |
| Interview / personal story | editorial-warm | nordic-calm | gallery-white |
| Research / thesis / policy | mono-ink | public-sector | forest-sage |
| Teaching / peer session | forest-sage | pastel-friendly | campus-bright |
| Marketing / brand / food / lifestyle | coral-studio | terracotta-editorial | poster-yellow |
| Club event / fest / recruitment | campus-bright | poster-yellow | pastel-friendly |
| Tech / engineering | dark-stage | blueprint | night-terminal |
| Luxury / awards / gala | luxe-noir | boardroom-oxblood | gallery-white |

- **Show, don't tell.** When the look is open, run
  `preview_directions.py spec.json --directions a,b,c --slides 1,4` (HTML, seconds) and let the
  user pick.
- **Brand to follow**: use the nearest direction plus `theme` overrides.
- **Frame**: classic (consulting) · clean (modern, talk) · editorial (stories) · rail (long
  documents).
- **Cover**: gradient · field · split (with a real photo) · minimal.
- **Imagery**: real photographs or nothing. Never AI faces, web photos of public figures,
  stretched images, or text baked into pictures.
- **Final format**: note the likely final format (T1); it is confirmed at the approval gate.

**Gate 3.** One line on why this direction, frame and imagery fit this room.

### Stage 4 · Draft (HTML)
1. **Notes first.** For each slide, write 2-5 spoken sentences, then assumptions, sources and
   likely questions.
2. **Pick each slide's type by the shape of its evidence** (decision-trees.md T6; first match
   wins). Never the same type three times running; chart a series once.

   | Evidence | Type |
   |---|---|
   | a decision | `ask` |
   | one number | `big_number` |
   | two numbers in tension | `data_contrast` |
   | metrics vs plan | `kpi` |
   | a trend | line/column `chart` |
   | a bridge | `waterfall` |
   | ranges | `range` |
   | a ranking | sorted bar |
   | composition | stacked bar |
   | two variables | `scatter` / `matrix` |
   | a market map | mekko image |
   | before/after | `before_after` |
   | weighted options | `options` |
   | 2-3 alternatives | `compare` |
   | steps | `process` |
   | a loop | `cycle` |
   | narrowing | `funnel` |
   | hierarchy | `pyramid` |
   | a centre and its enablers | `hub` |
   | root causes | `issue_tree` |
   | position | `swot` |
   | overlap | `venn` |
   | a plan with owners | `timeline` |
   | dates | `milestones` |
   | now/next/later | `roadmap` |
   | next steps | `actions` |
   | risks | `risks` |
   | an experience | `journey` |
   | precise figures | `table` |
   | parallel ideas | `columns` / `cards` |
   | a thesis | `framework` |
   | one idea | `statement` |
   | a voice | `quote` |
   | people | `team` |
   | plans or price tiers | `pricing` |
   | objections | `faq` |
   | a question | `question` |
   | proof by picture | `image` / `image_full` / `gallery` |
   | code | `code` |
   | nothing fits | `bullets` (≤ 6, and ask why) |

3. **Build order**: content slides → exec summary (rows `ref` slide ids) → agenda/dividers →
   cover and close → appendix.
4. **Anatomy** (document slides), in order:
   - kicker;
   - assertion title;
   - exhibit label with unit;
   - one exhibit;
   - side panel (why);
   - so-what (the only accent besides the highlighted data);
   - footnotes, source, page.
   - Highlight one element, grey the rest.
5. **Write in a human voice** (references/human-voice.md). Specific facts, the room's own words,
   uneven rhythm, no stock AI phrasing, no em dashes on slides.
6. **Build the draft**: `build_html.py spec.json -o out/deck.html`. Read every `check`, `warn` and
   `voice` line.

**Gate 4.** Every content slide passes the anatomy. Every number comes from `facts`. Every voice
hit is fixed or kept on purpose.

### Stage 5 · Review and iterate (qa.md; never skip)
1. `render_html.py out/deck.html out/render`. Look at the contact sheet for rhythm, then at every
   slide full size. A "does not fit" flag is an error: shorten or split, never shrink.
2. Run the ten-point check (qa.md §3), the mode check, and the voice read-aloud.
3. Show the user the draft (the HTML file plus the contact sheet). Use one line on what the deck
   argues and a short list of open gaps, then ask for changes.
4. **Iterate.** Edit the spec, rebuild, re-render, re-check, show again. Content and structure
   come first, then look. Small rounds are fine; the draft is cheap.
5. **High stakes**: run a fresh-eye reviewer agent on the draft PNGs (qa.md §5) before asking for
   approval.

**Gate 5 · approval.**
- The user approves the content, visuals and skeleton (or explicitly skips drafting).
- Ask once which final format they want, with your recommendation (decision-trees.md T1):
  PPTX · Slides artifact · Gamma · Canva · keep the HTML.

### Stage 6 · Finalise (only after Gate 5)
1. **Build the approved spec** in the chosen format (routes.md). PPTX:
   `build_deck.py spec.json -o out/deck.pptx`. Gamma, Canva and Slides take the approved titles,
   figures and notes as their input.
2. **QA the final format again.** Fonts and fit differ between renderers, so check the real file.
   - PPTX: run `render.py`, then `lint_deck.py` (zero errors; each warn fixed or consciously
     accepted), then look at every slide.
   - Gamma or Canva: do the read-back checklist (routes.md §C-D).
3. **Loop until clean.** Fix → rebuild → re-render → re-lint until a full pass finds nothing new.
   Three failed fixes on one defect → change the slide type or split.

**Deliver.** Send:
- the file and its contact sheet;
- one line on what the deck argues;
- the open gaps (sources to add, assumptions to confirm);
- one next step (rehearsal notes, an appendix, a talk-mode cut, a Q&A sheet).

## Commands

```bash
S=<skill dir>/scripts
python3 $S/build_deck.py --schema                        # every slide type and field (shared by both builders)
python3 $S/build_deck.py spec.json --outline             # Gate 1 headline track
# draft (stages 4-5)
python3 $S/build_html.py spec.json -o out/deck.html      # exit 2 = spec/fact error
python3 $S/render_html.py out/deck.html out/render       # PNGs + contact sheet; exit 3 = text does not fit
python3 $S/preview_directions.py spec.json --directions consulting-navy,editorial-warm,bold-signal --slides 1,4 -o out/prev
# finalise (stage 6, after approval)
python3 $S/build_deck.py spec.json -o out/deck.pptx      # exit 2 = spec/fact error, 3 = text doesn't fit
python3 $S/render.py out/deck.pptx out/render-pptx       # LibreOffice render + contact sheet
python3 $S/lint_deck.py out/deck.pptx [--mode talk] [--figures]   # any .pptx, including Gamma/Canva exports
python3 $S/chart_images.py chart.json -o out/mekko.png --direction consulting-navy   # mekko, slope, dumbbell, heatmap, bullet
```

**Spec essentials** (spec.md):
- deck level: `direction`, `mode`, `frame`, `footer`, `sources`, `minutes`, `facts`, `checks`,
  `slides`;
- text tokens `{=expr|fmt}`, data values `"=expr"`;
- markup `**bold**`, `^^accent^^`;
- slide extras: `id`, `kicker`, `letter`, `subtitle`, `exhibit`, `so_what`, `source`, `tag`,
  `footnotes`, `notes {say, assumptions, sources, qa}`.

Worked examples are in `assets/examples/`.

**Requirements**:
- Drafts: Python and Playwright with Chromium, which is pre-installed in Claude's workspace.
- PPTX: python-pptx and Pillow; rendering needs LibreOffice and poppler; chart images need
  matplotlib.
- Install: `pip install python-pptx pillow matplotlib --break-system-packages`;
  `apt-get install -y libreoffice poppler-utils`.

If `scripts/` is missing (the skill was saved without its bundle), say so once and suggest
uploading the full deck-studio.zip. Meanwhile, hand-write the draft from
`assets/html-stage/stage-template.html` (or apply every rule here with the pptx skill once the
user approves).

## Anti-patterns

- **Process**: building the PowerPoint before the content is agreed.
- **Titles and structure**: topic-label titles in document decks · agendas and upfront answers in
  talks · a "Thank you" close with no ask.
- **Layout**: walls of bullets · the same layout repeated · four thin boxes on a talk slide ·
  centred body text · text below the floors to make it fit.
- **Decoration**: accent bars under titles, edge stripes, glows, gradients everywhere, stock AI
  art, emoji icons.
- **Colour and charts**: three accents fighting · rainbow charts · two scales on one axis.
- **Truth**: numbers that disagree · invented sources or institutes.
- **Voice**: AI voice (leverage, unlock, seamless, "not just X but Y", ", ensuring…", every list in
  threes) · uniform case studies · the same closing clause on every slide.

## Signature moves (at least two per deck)

- one signature exhibit;
- a human hook;
- one number to remember;
- credible-but-unexpected styling (consulting grammar on a warm or heritage skin);
- a crisp ask (what, who, by when, cost, the number it moves);
- personal voice;
- a build-up diagram across talk slides.

## Reference map

| Need | File |
|---|---|
| Final format, mode, archetype, structure, length, slide type, chart, direction, frame, imagery; when to ask | references/decision-trees.md |
| Brief canvas, decision structures, selection, skeleton, checks and balances, review rounds | references/frameworks.md |
| 40+ deck skeletons (consulting, reviews, pitches, careers, teaching, research, marketing, events) | references/deck-skeletons.md |
| All 44 slide types: use / avoid / limits | references/slide-library.md |
| 22 directions, frames, covers, colour, type, grid, shape, imagery, charts, anti-slop, HTML pairs | references/visual-language.md |
| Headlines, talk rules, body text, numbers, notes, sources, mode conversion | references/writing.md |
| Sounding human: word and phrase tells, slide tells, what to put in, rewrite drills | references/human-voice.md |
| Story craft, case comps, interviews, source → slides | references/storyline.md |
| 11 use-case themes → archetype, direction, Gamma pick | references/use-cases.md |
| Routes: HTML draft, Slides artifact, PPTX, editing decks, Gamma, Canva, chart images, previews | references/routes.md |
| Spec format and the facts model | references/spec.md |
| QA: draft and final render, lint codes, ten-point check, mode checks, fresh-eye prompt, presenter prep | references/qa.md |
| Sources, credits, the positives matrix | references/credits.md |
