# Routes: where the deck gets built

Every new deck goes through route E (the HTML draft) first. Routes A-D and F are the final
builds, used only after the user approves the draft or explicitly skips it (SKILL.md, "Draft
first"). Editing an attached deck goes straight to its own format (route B, editing).

## E. HTML draft (`scripts/build_html.py`): always first

Why: a draft in HTML takes seconds and a small fraction of the tokens of a PPTX, Gamma or Canva
build, and the look changes with one field. Settle content, visuals and the slide skeleton here.

1. `build_html.py spec.json -o out/deck.html` renders the same spec the PPTX builder uses: all 44
   slide types, all 22 directions, the facts model, checks and tokens. It also prints the
   builder's warnings and the `voice` lines (human-voice.md).
2. `render_html.py out/deck.html out/render` takes screenshots of every slide (Playwright) and a
   contact sheet. Text that cannot fit at the floor sizes is flagged on the slide in red and
   reported with exit code 3.
3. Show the user the HTML file (it previews inline and opens in any browser) and the contact
   sheet. In the browser, arrows move, N shows notes, G shows the grid, P prints a PDF.
4. Iterate: edit the spec, rebuild, re-render. To compare looks, run `preview_directions.py`
   (HTML by default).

Fidelity: the draft uses the direction's tokens, the same layouts and the same Office fonts, with
metric-compatible web fallbacks (Carlito, Caladea, Liberation). Expect the final PPTX to match it
closely but not pixel for pixel. Native charts, tables and fitting are measured again by the PPTX
builder, so final QA always runs on the final file. `html_fonts` (spec.md) swaps in web fonts.
Use it only when the HTML itself is the final format, or when the final tool re-picks fonts
anyway (Gamma, Canva); otherwise the draft would promise a look the PPTX can't deliver.

## A. Claude Slides artifact (claude.ai)

After approval, when the session lists a Slides artifact type and the user named no file format,
build there:
the user gets an editable, shareable deck that exports to .pptx/PDF. Everything in this skill
still applies: ghost deck and Gate 1 first, anatomy per slide, one accent, the facts model
(keep it in a scratch JSON and compute figures with a few lines of Python before writing them
in), notes-first, then render/inspect via the type's own preview and fix. Follow the type's own
instructions for the data format; translate a direction's tokens into its theme.

## B. PPTX builder (`scripts/build_deck.py`)

After approval: for a .pptx request, offline submission, Google Slides (it opens .pptx), or
whenever the numbers must tie out. The approved draft's spec builds as-is. See `spec.md`. Exit codes: 0 built · 2 spec or fact-check error (nothing
written) · 3 built but some text could not fit within floors (shorten or split, never shrink).

Commands: `--schema` (fields), `--outline` (Gate 1 headline track), `--direction X --only 1,4`
(previews), `-o out.pptx`. Then `render.py`, `lint_deck.py`.

Need a layout the builder lacks (a map, an S-curve with phase bands, an org chart): build the deck,
open it with python-pptx, add shapes on the same grid with the direction's tokens, re-render,
re-lint. For chart forms PowerPoint lacks, use route G.

### Editing someone's existing deck (keep the look vs restyle)

| | Keep the look (brand, template, others keep editing) | Restyle (the design is weak; content matters) |
|---|---|---|
| Steps | copy the file → python-pptx edits in runs (formatting kept) → lint + render before and after → report what changed | extract text, numbers and notes (`python -m markitdown deck.pptx` or python-pptx) → write a spec → build → compare old vs new: every word and figure kept or moved to notes |
| Never | overwrite people's edits to a deck without asking; drop slides silently | invent content to fill the new layouts |

Version before any destructive edit: `deck_v01.pptx`, `deck_v02.pptx`.

## C. Gamma (connector)

After approval: send the approved draft's titles, figures and notes as the prompt (below).
What works (verified): `generate_from_template` with official template IDs on a paid plan;
reading/duplicating official templates returns 404. ~20 credits per card. Output fabricates
sources and numbers → always read back (`read_gamma`/outline) and fix with `edit_gamma`.

Prompt recipe (put all of it in the prompt):
1. Today's date. 2. The ghost-deck titles, in order, as the slide list. 3. The real figures with
units and sources, and "use only these numbers". 4. Audience and what they must decide.
5. Slide count, stating whether it includes the cover. 6. Text density (brief/medium/detailed).
7. Image source and style (or none for analytical slides). 8. "British English" (or Indian).
9. "Never invent source names or statistics; where a source is missing write
'Source: to be added'." 10. "Each slide title is a full-sentence insight."

Quick picks (template IDs from Gamma search, Nov 2026):

| Need | First choice | Alternative | Skin |
|---|---|---|---|
| Case competition final | Mandate `fwia89dbl14eg2r` | Casebook `sxyged9psst763s` | Consultant / Slate |
| Recommendation between options | Shortlist `hq45urii6lh45g9` | Boardroom `kamqk0xzqjwec9y` | family variant |
| Client project readout | Readout `gdglld4ukvtx3pp` | Sightline `f0d3ggfiuh1imv4` | Founder / Pearl |
| Classroom case analysis | Case Method `3hdcs9g7xt11y5a` | Consultant `ngp9geacbj3n4yo` | Chimney Smoke |
| Interview / personal story | Final Round `h67xxgfhtmahy3e` | Postmark `wg1x345zo0b5wk8` | Editoria / Linen |
| Venture or incubator pitch | Silicon Savannah `ztvprkwafjsxc4g` | Moonshot `shn45j3aik0e0pb` | Aurora / Founder |
| Brand or marketing case | Upswing `xski90vc8kufvl4` | Mosaic `hysatb92fqwhrne` | Gamma / Coral Glow |
| Metrics or project update | Daybook `5gq3jxkshjn70cp` | The Quiet Deck `tfkcig75f7si2wt` | Commons / Sage |

IDs can go stale: if one is rejected, `search_templates` again or use a workspace template.
Families, skins and the 11 themes: `use-cases.md`; full catalogue: the user's "Gamma Design
Playbook" doc.

Read-back checklist after every generation (the four failures seen with Mandate):
1. Source lines: any source you didn't supply is invented → replace with the real one or
   "Source: to be added".
2. Tie-out: every chart and table against the facts and against each other.
3. Dates: roadmap starts after today and matches the launch date.
4. Card count: did it add a cover or closer you didn't ask for?
Then fix card by card with `edit_gamma` (cheaper than regenerating; keeps what worked), and
`export_gamma` for PPTX/PDF. Say the credit cost before a large run (~20 credits a card measured).

Checking a Gamma or Canva export: the cloud workspace cannot download Gamma or Canva export links
(network allowlist, tested Nov 2026), so ask the user to download the .pptx and attach it, then run
`lint_deck.py` and `lint_deck.py --figures` on it and render it like any other deck.

Learn each template once: the first time a template is used, record its real slide layouts in the
Gamma Design Playbook, so the playbook gets more precise with use.

## D. Canva (connector)

After approval. The connector can read and edit the user's own designs, generate new designs with Canva AI,
resize, and export to PPTX/PDF/images. It cannot browse Canva's public template library, and this
account has no Brand Kits or Brand Templates. Workflow: user opens a Canva template and clicks "Customize this template" → you find
it with `search-designs` → read it → edit text/images with the edit tools (load the
canva:edit-design skill) → export. Impose the grammar: action titles, numbered exhibit, so-what,
source line. Best for co-edited, event, social and photo-led decks.

## F. HTML as the final format

When the approved deck stays HTML (a projected talk, a link to share, no PowerPoint editing
needed), the route E file is the deliverable. Optional `html_fonts` gives it distinctive web
fonts (visual-language.md §11). Then check two things with screenshots: 16:9 and one phone size.
Nothing should overflow or overlap.
- To publish, put it up as an artifact for a link, or send the file.
- Say it is not editable in PowerPoint; route B can still build the .pptx from the same spec.
- For motion or layouts beyond the 44 types, start from `assets/html-stage/stage-template.html`
  and keep its tokens and stage.

## G. Chart images (`scripts/chart_images.py`)

Mekko, slope, dumbbell, heatmap and bullet charts in a direction's colours, as PNG for an `image`
slide. Use when the chart form carries the insight (a market map, a two-period shift); keep the
numbers in `facts`; always alt text; state that the chart is a picture.

## H. Showing directions (`scripts/preview_directions.py`)

Renders the chosen slides of a spec in several directions and writes one labelled comparison
sheet. It uses HTML by default (fast, the draft stage); `--pptx` previews the native build at the
finalise stage. Default to three: one safe for the room, one bolder, one wildcard.

## I. Choosing the final format (at the approval gate)

| What matters most | Route |
|---|---|
| Precision and numbers | B (or A) |
| Visual storytelling | C |
| The team already lives in Canva | D |
| A projected talk or a link, with no editing in PowerPoint | F |

- **Hybrid**: core in A/B, opener and closer in C.
- **Unsure and the stakes are high**: build the core in B. It is the only route where every
  number is asserted inside the final file.
- **Recommend one**: give one line of reason, and let the user decide.
