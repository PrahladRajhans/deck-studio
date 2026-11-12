---
name: deck-studio
description: Master presentation skill. Plans, drafts and QAs any deck (consulting readouts, case competitions, board asks, pitches, interviews, classes, research, marketing, events) as a fast HTML draft first, then builds the approved version as editable PPTX, Slides, Gamma, Canva or HTML. Use for any deck or slide task, including reviewing or fixing one.
---

# Deck Studio

One method for every deck, whatever the room:

**Plan → Decide → Select → Draft (HTML) → Review and iterate → [user approves] → Finalise**

Each stage closes with a gate. Weak decks fail in planning, not design, so no layout opens before
Gate 1. Content, visuals and the slide skeleton are settled in an HTML draft that is quick to
change. The final build (PowerPoint, Slides, Gamma or Canva) happens once, after the user says go.

What this skill brings together:
- the Gamma Design Playbook (Gamma, Canva and Manus studies; The Deck Framework);
- the best of ten public PowerPoint skills (`references/credits.md`);
- classic references (Minto, Duarte, Zelazny, Sequoia, YC, Kawasaki, assertion-evidence);
- the BeHuman/Unslop human-voice rules;
- two rounds of external review.

Tooling: one JSON spec with a facts model drives everything. From it you can build:
- an HTML draft (`build_html.py`);
- a native PPTX (`build_deck.py`: 44 slide types plus `custom`, 11 chart kinds, 22 art
  directions, 4 frames, 4 cover styles).

There are also:
- a validator with a strict release gate (`spec_io.py`);
- renderers for both formats;
- a linter for any .pptx;
- a direction previewer;
- chart images for chart forms PowerPoint lacks;
- an environment check for fonts and renderers.

## Truth rules (non-negotiable)

1. **Evidence before assertion.**
   - Every substantive factual claim rests on supplied material or a verified source. Record where:
     file and page, section, cell, or URL.
   - Verify both that the source exists and that it supports the claim's wording, scope,
     population, period and certainty. A plausible source name is not evidence.
   - When evidence is missing, ask for it, drop the claim, or mark the gap visibly
     ("Source: to be added", `[CONFIRM: …]`).
   - Never invent a number, source, institute, quote, logo, photo or person.
2. **Keep claim types apart.** Observed facts, calculations, estimates, forecasts, assumptions,
   targets, recommendations and illustrative examples stay distinguishable (`fact_meta`,
   `data_status`).
   - Don't turn association into causation, a target into a forecast, or a partial finding into a
     universal one.
   - Illustrative figures need the user's agreement and a visible label.
3. **One place for every number.** Substantive figures live in `facts`. Derived figures are
   computed, not typed. `checks` assert every claim the argument rests on. Decide once whether a
   figure is an increment or an absolute.
4. **Check today's date.** Proposed activity starts after it. Retrospective and in-progress
   timelines are labelled as such.
5. **Read back generator output.** Anything Gamma, Canva AI or another generator produces is read
   back and reconciled against the approved spec before the user sees it.
6. **Report honestly** what was checked and what was not. Never call a deck verified while a
   required check is incomplete.

## Draft first, finalise on approval (the working rule)

- **Draft in HTML.** Every new deck starts as an HTML draft built from the spec (`build_html.py`).
  It renders in seconds, changes look with one field (`direction`), and keeps the final build out
  of the iteration loop. The token and time saving over iterating in PPTX, Gamma or Canva is
  expected, not measured; don't quote a figure.
- **Know the destination early, build it late.**
  - Note the likely final format at Stage 3 (decision-trees.md T1), so the draft doesn't promise
    what the destination can't do (routes.md, capability table).
  - Build that format only after a clear go-ahead.
- **What approval means.** The approved draft is the design reference for the final build: slide
  order, wording, evidence, visual relationships, hierarchy and design tokens. Each route states
  what it preserves and what it adapts (routes.md, fidelity contract). Any material departure goes
  back to the user.
- **Naming a format is not approval.** "I need a pptx" sets the final target. Say so, and draft
  first.
- **Explicit skip.** "Skip the draft" or "just give me the file now" is the go-ahead.
- **Edits stay in format.** Editing a deck the user attached stays in that deck's format
  (routes.md §B). There is no draft stage for edits.
- **Unattended runs.** Build and QA the draft, say what is waiting for approval, and stop. Never
  build the final format unattended.

## The flow

### Stage 1 · Plan (frameworks.md §1-2)
1. **Fill the brief canvas**: purpose, audience, decision or action (one verb), consumption (live,
   read alone, workshop, hybrid), setting, time, domain (references/domain-packs.md), governing
   thought, success metric, evidence in hand, judging criteria, constraints (brand, template,
   final format), accessibility, tone.
2. **Fill the voice brief**: presenter stance, formality, relationship to the audience, claim
   strength, must-use terms, plus authentic writing samples when available. Infer these when the
   material makes them clear.
3. **Ask only what you cannot infer**: once, at most 3 questions (decision-trees.md T11).
   Otherwise state assumptions and proceed.
4. **List the evidence**: what you have, where it sits, what is missing.
5. **Write the ghost deck**: titles only, in order.

If no governing thought can be written yet, either:
- frame the deck around an explicit open question and an evidence plan (exploratory work), or
- say the material isn't ready and offer a one-page issue summary.

**Gate 1 · headline test.**
- The titles alone tell the story (document) or the plot (talk).
- Document titles pass two tests: "a sceptic could disagree" and "hide the body, the point
  survives".
- `build_deck.py spec.json --outline` prints the headline track.

### Stage 2 · Decide (decision-trees.md T2-T5, storyline.md, deck-skeletons.md)
- **Mode.**
  - Document: read and decided from; dense allowed; ≥ 12pt.
  - Talk: presented; ≤ 40 words a slide; ≥ 18pt; close with an action.
- **Reveal**: answer first when the room is senior, time-poor or deciding. Reveal progressively
  when the room must be brought along. Choose by purpose, not by mode.
- **Agenda**: use one when it reduces uncertainty (workshops, long sessions, teaching). For a short
  persuasive talk, question dividers usually do the job better.
- **Archetype**, from what the room must do: recommendation · pitch · personal story · review ·
  explainer · research readout · change/workshop · marketing plan · event · options-first.
- **Structure**:
  - pyramid/SCQA;
  - sparkline;
  - problem-agitate-solve;
  - chapters;
  - question-method-findings;
  - scorecard-moved-risks-asks.
  Use as many supporting arguments as there are distinct ones, not three by habit.
- **Skeleton**: start from the nearest of the 40+ in deck-skeletons.md; cut what the story
  doesn't need.
- **Length**:
  - document: one slide per claim;
  - talk: ≈ 30-45 s per body slide;
  - business: ≈ 1.5-2 min per content slide;
  - pitch: ≈ 10/20/30.
  - Set `minutes` for timing notes.

**Gate 2.** Every title serves the spine. Anything else goes to the appendix or goes.

### Stage 3 · Select (decision-trees.md T1, T8-T10; visual-language.md)
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

- **Show, don't tell.** When the look is open, preview two or three materially different
  directions on real content: one evidence-heavy slide, one comparison or explanation, and one
  opener. Run `preview_directions.py spec.json --directions a,b,c --slides 1,4,6`, let the user
  pick, then apply the choice consistently.
- **A direction is a theme, not a whole design language.** When the material calls for it, change
  composition and visual language too: real creative work in a marketing deck, documentary photos,
  annotated schematics.
- **Brand to follow**: use the nearest direction plus `theme` overrides. With a supplied template,
  profile its layouts first (routes.md §B).
- **Frame**: classic · clean · editorial · rail.
- **Cover**: gradient · field · split · minimal.
- **Imagery** (T10): real photographs, the user's own assets, or none. Screenshots and source
  figures are fine when they are the evidence. Conceptual illustration must be labelled as such.
  Never AI imagery passed off as a real facility, customer, product or result.
- **Destination**: note the likely final format and check its limits (T1; routes.md).

**Gate 3.** One line on why this direction, frame, imagery and destination fit this room.

### Stage 4 · Draft (HTML)
1. **Notes first.** For each slide, write 2-5 spoken sentences, then assumptions, sources and
   likely questions.
2. **Choose each exhibit by the audience's question, not by keyword** (decision-trees.md T6-T7):
   1. Name the question the slide answers (optional spec fields `role`, `question`).
   2. Name the relationship that answers it.
   3. Check that the evidence supports that relationship.
   4. Pick the simplest form that shows it without hiding relevant variation or uncertainty.
   5. Choose a layout that suits the destination and density.

   Detection words in T6 suggest candidates; they don't decide. When two forms are plausible, say
   in a line what the chosen one makes easier to see.
   - Use a table when exact lookup is the task. Use a sentence when a visual would add nothing.
   - Reuse a layout when slides compare like with like. Change it when the communication task
     changes. Don't vary layouts to hit a quota.
   - Chart the same data again only when the second view adds a distinct insight.
   - **Custom slides**: when every standard type distorts the idea, compose a `custom` slide from
     the deck's tokens. Say why no type fits; the PPTX then needs a hand build of that slide.
3. **Build order**: content slides → exec summary (rows `ref` slide ids) → agenda/dividers →
   cover and close → appendix.
4. **Anatomy** (document evidence slides), in order:
   - kicker;
   - assertion title at the strength the evidence justifies;
   - exhibit label with unit;
   - one exhibit;
   - side panel (why);
   - so-what;
   - footnotes, source, page.
   - Highlight one element, grey the rest.

   Teaching, transition and workshop slides may use questions or labels on purpose (writing.md
   §1).
5. **Write in the presenter's voice** (references/human-voice.md): specific facts from the
   evidence, the room's own words, accountable actors, stable terms.
   - Specificity must come from evidence. Without evidence, narrow or qualify the claim; never
     invent precision.
6. **Build the draft**: `build_html.py spec.json -o out/deck.html`. Read every `check`, `warn`,
   `note` and `style` line.

**Gate 4.**
- Every content slide passes the anatomy.
- Every substantive number comes from `facts` or a slide with a declared `data_status`.
- Every style prompt is fixed or kept on purpose (`voice_ok`).

### Stage 5 · Review and iterate (qa.md; never skip)
1. **Render**: `render_html.py out/deck.html out/render`. Look at the contact sheet for rhythm,
   then at every dense, flagged or consequential slide full size. "Does not fit" is an error:
   cut redundancy, restructure or split; reduce type only within the floors.
2. **Semantic review** (qa.md §3), separate from style:
   - Does each headline follow from its exhibit?
   - Do counts and promises match the content?
   - Does the recommendation follow from the analysis?
   - Are causal and financial conclusions actually established?
3. **Checks**: the ten-point check, the mode check, and the voice read-aloud.
4. **Show the user the draft**: the HTML file and contact sheet, one line on what the deck argues,
   and the open gaps. Then ask for changes.
5. **Iterate**: edit the spec, rebuild, re-render, re-check, show again. Content and structure
   come first, then look.
6. **High stakes**: run a fresh-eye reviewer on the draft PNGs (qa.md §6) before asking for
   approval.

**Gate 5 · approval.**
- The user approves the content, visuals and skeleton (or explicitly skips drafting).
- Confirm the final format, with your recommendation and its fidelity class (routes.md).
- `spec_io.py spec.json --strict` lists any release blockers left to resolve.

### Stage 6 · Finalise (only after Gate 5)
1. **Build with the release gate.** PPTX: `build_deck.py spec.json --strict -o out/deck.pptx`
   refuses to build while blockers remain:
   - hand-typed or unclassified numbers;
   - placeholders;
   - unclassified facts;
   - unverified evidence.
   Gamma, Canva and Slides take the approved titles, figures, notes and layout intent as their
   input.
2. **Reconcile the final file against the approved draft**: every slide, figure and claim. Note
   anything the tool added or changed. Gamma and Canva output gets the read-back checklist
   (routes.md §C-D).
3. **QA the real file.** PPTX: run `render.py`, then `lint_deck.py` (zero errors; each warn fixed
   or consciously accepted), then look at every slide. Report which application rendered it.
4. **Loop until clean.** Fix → rebuild → re-render → re-lint until a full pass finds nothing new.
   Three failed fixes on one defect → change the slide type or split.

**Deliver.** Send:
- the file and its contact sheet;
- one line on what the deck argues;
- the open gaps;
- what was and wasn't verified;
- one next step.

## Commands

```bash
S=<skill dir>/scripts
python3 $S/env_check.py                                  # fonts used for fit measurement; renderers available
python3 $S/build_deck.py --schema                        # every slide type and field (shared by both builders)
python3 $S/build_deck.py spec.json --outline             # Gate 1 headline track
python3 $S/spec_io.py spec.json [--strict]               # validation; --strict = release gate (exit 2 on blockers)
# draft (stages 4-5)
python3 $S/build_html.py spec.json -o out/deck.html      # exit 2 = spec/fact error
python3 $S/render_html.py out/deck.html out/render       # PNGs + contact sheet; exit 3 = text does not fit
python3 $S/preview_directions.py spec.json --directions consulting-navy,editorial-warm,bold-signal --slides 1,4,6 -o out/prev
# finalise (stage 6, after approval)
python3 $S/build_deck.py spec.json --strict -o out/deck.pptx   # exit 2 = blockers or fact error, 3 = text doesn't fit
python3 $S/render.py out/deck.pptx out/render-pptx       # LibreOffice render + contact sheet
python3 $S/lint_deck.py out/deck.pptx [--mode talk] [--figures]   # any .pptx, including Gamma/Canva exports
python3 $S/chart_images.py chart.json -o out/mekko.png --direction consulting-navy   # mekko, slope, dumbbell, heatmap, bullet
```

**Spec essentials** (spec.md):
- deck level: `direction`, `mode`, `frame`, `footer`, `sources`, `minutes`, `facts`,
  `fact_meta`, `evidence`, `checks`, `voice_ok`, `slides`;
- text tokens `{=expr|fmt}`, data values `"=expr"`;
- markup `**bold**`, `^^accent^^`;
- slide extras: `id`, `role`, `question`, `kicker`, `letter`, `subtitle`, `exhibit`, `so_what`,
  `source`, `data_status`, `tag`, `footnotes`, `notes {say, assumptions, sources, qa}`.

Worked examples are in `assets/examples/`; tests are in `tests/`.

**Requirements**:
- Drafts: Python and Playwright with Chromium (pre-installed in Claude's workspace). The draft path
  doesn't need python-pptx.
- PPTX: python-pptx and Pillow; rendering needs LibreOffice and poppler; chart images need
  matplotlib.
- Install: `pip install -r requirements.txt`.

If `scripts/` is missing (the skill was saved without its bundle), say so once and suggest
uploading the full deck-studio.zip. Meanwhile, hand-write the draft from
`assets/html-stage/stage-template.html`, applying every rule here.

## Defaults that are easy to get wrong

Each of these is a default with a purpose, not a ban; break it when the purpose isn't served, and
say why.

| Default | Purpose | Exception |
|---|---|---|
| Assertion titles on evidence slides | The point survives a skim | Teaching questions, transitions, workshop prompts |
| One accent, highlight one element | The eye lands on the answer | Two genuinely parallel highlights the argument needs |
| No accent bars under titles, edge stripes or glows | They read as template decoration | A brand system that requires them |
| Real photos or none | Fake imagery destroys trust | Labelled conceptual illustration; screenshots as evidence |
| Talk slide ≤ 40 words | The audience listens, not reads | A slide the presenter reads out verbatim on purpose (e.g. a quote) |
| Close with an ask or action | Decks exist to move people | Pure teaching sessions close on the takeaway |
| Distinctive devices (a signature exhibit, a human hook, one number to remember) | Memorability | Never manufactured: use them only when the material supports them |

## Anti-patterns

- **Process**: building the final format before the content is agreed.
- **Truth**: numbers that disagree · invented or unverified sources · headlines that overstate
  their exhibit · claims stronger than the evidence.
- **Titles and structure**: topic-label titles on evidence slides · a "Thank you" close with no
  ask.
- **Layout**: walls of bullets · layouts varied for variety's sake or repeated without reason ·
  four thin boxes on a talk slide · centred body text · text below the floors to make it fit.
- **Decoration**: decoration that explains nothing · stock AI art.
- **Colour and charts**: three accents fighting · rainbow charts · two scales on one axis.
- **Voice**: stock phrasing (leverage, unlock, seamless, "not just X but Y", ", ensuring…") ·
  manufactured anecdotes or rhythm · the same closing clause on every slide.

## Reference map

| Need | File |
|---|---|
| Final format, mode, archetype, structure, length, slide type, chart, direction, frame, imagery; when to ask | references/decision-trees.md |
| Brief canvas, decision structures, selection, skeleton, checks and balances, review rounds | references/frameworks.md |
| Domain conventions: consulting, finance, marketing, energy, science/health, technology, public policy, education | references/domain-packs.md |
| 40+ deck skeletons (consulting, reviews, pitches, careers, teaching, research, marketing, events) | references/deck-skeletons.md |
| All 44 slide types plus custom: use / avoid / limits / overflow | references/slide-library.md |
| 22 directions, frames, covers, colour, type and font deployment, grid, imagery, icons, charts, anti-slop | references/visual-language.md |
| Headlines by slide role, claim strength, talk rules, body text, numbers, notes, sources | references/writing.md |
| Voice brief, style prompts, what to put in, rewrite drills | references/human-voice.md |
| Story craft, case comps, interviews, source → slides | references/storyline.md |
| 11 use-case themes → archetype, direction, Gamma pick | references/use-cases.md |
| Routes, fidelity contract, destination capabilities, editing decks, Gamma, Canva, chart images, previews | references/routes.md |
| Spec format, facts model, evidence register, strict gate | references/spec.md |
| QA: render, semantic review, lint codes, ten-point check, mode checks, fresh-eye prompt, presenter prep | references/qa.md |
| Sources, credits, the positives matrix, review history | references/credits.md |
