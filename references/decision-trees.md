# Decision trees

Walk these in order: T0 → T1 (provisional) → T2 → T3 → T4 → T5 at the start of a deck; T6 → T7 for every
content slide; T8 → T9 → T10 once per deck, after developing the concept (creative-direction.md). Each tree ends in a concrete choice. When two branches
fit, use the audience's task, evidence and destination to choose; do not let row order decide.
When none fits, explain the gap and ask only if it prevents useful progress.

---

## T0 · What kind of job is this?

```
Is there an existing deck or file?
├─ No → NEW DECK → T1
└─ Yes
   ├─ "Review / critique / check it"           → REVIEW: lint_deck.py + render + qa.md checks; report, change nothing
   ├─ "Fix / tidy / update numbers", keep look → EDIT IN PLACE: python-pptx on their file, keep template;
   │                                             lint + render before and after (routes.md §B)
   ├─ "Make it better / restyle / rebuild"     → RESTYLE: extract content → write a spec → HTML draft →
   │                                             approval → rebuild (T1); nothing dropped (moved text goes to notes)
   ├─ "Turn this report / paper / doc into slides" → SOURCE → SUMMARY → SLIDES (storyline.md §6)
   └─ "Convert talk deck ↔ document deck"      → re-run T2 and storyline.md §2 / §7 rules; draft the
                                                 converted deck in HTML like a new deck
```

## T1 · Final format (provisional at intake, confirmed at the approval gate)

Every new deck is drafted in HTML first (`build_html.py`); this tree picks what the APPROVED draft
becomes. Build it only after the user's go-ahead (SKILL.md, "Approval and preservation").

```
Is this an edit of a deck the user attached?
├─ Yes, in-place changes → edit in its own format (routes.md §B); no HTML draft
├─ Yes, substantive restyle/rebuild → HTML draft and approval before rebuilding
└─ No → draft in HTML, iterate, get approval, then:
   Did the user name a format or tool?
   ├─ ".pptx / PowerPoint / editable file"      → PPTX BUILDER
   ├─ "Gamma"                                    → GAMMA (routes.md §C)
   ├─ "Canva"                                    → CANVA (routes.md §D)
   ├─ "Google Slides"                            → PPTX BUILDER (Google Slides opens .pptx); say so
   ├─ "web / link / HTML / animated"             → KEEP THE HTML (routes.md §F)
   └─ nothing named → recommend one at the approval gate:
      ├─ In claude.ai and a Slides artifact type is listed → SLIDES ARTIFACT (apply this skill's rules)
      ├─ Numbers must tie out, consulting exhibits, submission file → PPTX BUILDER
      ├─ Image-led storytelling, link to share  → GAMMA (with read-back checklist)
      ├─ Team edits in Canva / event & social assets  → CANVA
      ├─ Projected talk, link to share, no editing needed → KEEP THE HTML
      └─ Unsure and stakes are high → PPTX BUILDER (validates the specification before building; reconcile the exported file afterwards)
Hybrid is allowed: analytical core in the builder, narrative opener/closer in Gamma or HTML.
```

Tell the user the route's fidelity class with the recommendation (routes.md: faithful
reconstruction, controlled adaptation, or redesign), and check the destination's capabilities
before approving effects it can't reproduce.

## T2 · Document mode or talk mode?

```
Will someone present it live?
├─ No (emailed, read ahead, judged on paper, handout, board pack, pre-read) → DOCUMENT
├─ Yes, and it will ALSO be circulated afterwards                          → DOCUMENT first,
│                                                   then cut a TALK version (storyline.md §7)
└─ Yes, presented only
   ├─ Audience must decide something in the room (board, IC, client SteerCo)  → DOCUMENT density,
   │                                                                          talk-size type (≥16pt)
   └─ Audience must learn / feel / be persuaded (keynote, class, pitch, interview) → TALK
If the brief does not settle it and the user is present, ask once.
```

| | Document | Talk |
|---|---|---|
| Answer | usually first for decisions | answer first or progressive reveal, by purpose |
| Titles | full-sentence assertions | mixed forms: claims, questions, short labels when a figure is the star |
| Agenda | when it supports navigation | when it orients; useful for teaching and workshops |
| Words per slide | dense allowed | ≤ 40 visible words, one idea |
| Body text | ≥ 12pt | ≥ 18pt (22pt+ teaching, 24pt+ big rooms) |
| Notes | sources, assumptions, Q&A | the script, word for word |
| Close | decision + next action | call to action |

## T3 · Which use case → which archetype? (full table: use-cases.md)

```
What must the room DO after the deck?
├─ Approve / decide / fund        → RECOMMENDATION (case comp, client readout, board ask, IC memo)
├─ Invest / join / buy            → PITCH (venture, demo day, sales pitch, partnership)
├─ Hire / remember the person     → PERSONAL STORY (interview, intro, award, portfolio)
├─ Know where things stand        → REVIEW (QBR, status, ops review, ELP check-in)
├─ Learn / be able to do          → EXPLAINER (lecture, training, peer teaching, onboarding)
├─ Understand a finding           → RESEARCH READOUT (thesis, white paper, survey results)
├─ Change how they work           → CHANGE / WORKSHOP (town hall, new process, offsite)
├─ Buy into a campaign / brand    → MARKETING PLAN (campaign, launch, brand strategy)
├─ Feel part of something         → EVENT (club, fest, farewell, celebration)
└─ Choose between options         → OPTIONS-FIRST (criteria → scorecard → case for the winner)
```

## T4 · Which story structure?

```
Is the audience senior, time-poor, deciding?          → PYRAMID / SCQA: answer first, the distinct reasons (2-5), evidence
Is the audience neutral-to-sceptical, live?           → SPARKLINE (Duarte): what is ↔ what could be, CTA, new bliss
Is it a problem the room already feels?               → PROBLEM-AGITATE-SOLVE: their pain → why it persists → fix
Is it a journey or a person?                          → CHAPTERS: one deep story or a few short ones, each with a lesson
Is it a finding from research?                        → QUESTION-METHOD-FINDINGS-IMPLICATIONS-LIMITS
Is it teaching?                                       → WONDER-EXPLORE-DISCOVER-PRACTISE-REFLECT
Is it a status update?                                → SCORECARD → WHAT MOVED → RISKS → ASKS
Is it options?                                        → CRITERIA → OPTIONS → SCORECARD → RECOMMENDATION → RISKS
Is it a pitch?                                        → Sequoia/YC order (deck-skeletons.md), traction early if strong
```

## T5 · How many slides, how long?

- Document deck: one slide per claim the storyline needs; never pad, never cut a supported point.
- Talk deck, rule of thumb seconds per body slide (office-kit measurements of one speaker; replace
  with the user's own): lightning (5 min) ~30 s · 15-min slot ~30 s · 40-min conference ~37 s ·
  non-expert audience ~45 s. Dividers and cover ~8 s each. Plan for slot minus 5 minutes if Q&A
  is inside it.
- Business presentation default: 1.5-2 min per content slide (Gamma Design Playbook).
- Pitch: 10 slides / 20 minutes / 30pt+ type is Kawasaki's 10/20/30 rule; YC seed decks favour
  fewer, simpler slides.
- Set `minutes` in the spec; the builder writes `[~N sec]` at the top of each slide's notes.

---

## T6 · Which slide type? (the exhibit chooser; run per slide)

Start from the audience's question for this slide and the relationship that answers it. The table
generates candidates: detection words help you notice the shape of the content, they don't decide.
When two rows fit, pick the form that makes the answer easiest to see without hiding variation or
uncertainty, and say why in a line (a trend could also be a cohort comparison or a distribution).
Use a table when exact lookup is the job, and a sentence when a visual adds nothing.

| # | Question about the content | Words that signal it | Slide type |
|---|---|---|---|
| 1 | Is it the decision being asked for? | approve, fund, decide, mandate | `ask` |
| 2 | Is it one number that carries the point? | "x%", "1 in 9", record, doubled | `big_number` |
| 3 | Two numbers in tension? | but, while, despite, vs | `data_contrast` |
| 4 | A few headline metrics vs plan? | scorecard, KPIs, vs plan | `kpi` (deltas) |
| 5 | Change over time? | trend, grew, since, YoY | `chart` line (≥ 6 points) / column (≤ 8) |
| 6 | A bridge between two totals? | from X to Y, drivers, walk | `chart` waterfall |
| 7 | Ranges by method or scenario? | valuation, range, low-high | `chart` range (football field) |
| 8 | Ranking? | top, largest, leaders | `chart` bar, sorted |
| 9 | Composition? | share, mix, split | stacked bar (or doughnut ≤ 4 parts) |
| 10 | Two variables per item? | vs, correlation, cost vs value | `chart` scatter or `matrix` |
| 11 | Market structure by segment and size? | market map, share by region | chart image `mekko` |
| 12 | Before vs after a change? | used to, now, redesign | `before_after` / chart image `slope` |
| 13 | Gap to target per item? | target, gap, progress | chart image `dumbbell` / `bullet` |
| 14 | Options against weighted criteria? | options, criteria, scorecard | `options` |
| 15 | 2-3 alternatives side by side? | option A/B, pros/cons, us vs them | `compare` |
| 16 | Steps in order? | step, phase, then, process | `process` |
| 17 | A loop that reinforces itself? | flywheel, cycle, virtuous | `cycle` |
| 18 | Stages that narrow? | funnel, conversion, drop-off | `funnel` |
| 19 | A hierarchy or foundation? | levels, base, pyramid, needs | `pyramid` |
| 20 | One centre with enablers around it? | pillars, enablers, ecosystem | `hub` |
| 21 | A question broken into causes (MECE)? | why, drivers, root cause | `issue_tree` |
| 22 | Internal/external position? | SWOT, strengths, threats | `swot` |
| 23 | Overlap of sets is the point? | sweet spot, intersection | `venn` |
| 24 | Positioning on two axes? | 2x2, map, priority | `matrix` |
| 25 | Plan with owners over time? | roadmap, Gantt, workstreams | `timeline` |
| 26 | A few dated milestones? | by March, launch date | `milestones` |
| 27 | Now / next / later? | roadmap, horizons | `roadmap` |
| 28 | Who does what by when? | next steps, owners | `actions` |
| 29 | What could go wrong? | risks, mitigation | `risks` (register) or `matrix` (heat 2x2) |
| 30 | A user's experience over stages? | journey, touchpoints, pain points | `journey` |
| 31 | Precise figures in rows and columns? | P&L, table, breakdown | `table` |
| 32 | Parallel ideas, each with an icon? | pillars, principles, 3 things | `columns` (open) or `cards` (boxed) |
| 33 | A thesis plus its supports? | our strategy, thesis, framework | `framework` (dark rail) |
| 34 | One big idea, no list? | the point is, simply | `statement` |
| 35 | A real person's words? | said, told us, quote | `quote` |
| 36 | People? | team, founders, speakers | `team` |
| 37 | Prices or packages? | plans, tiers, pricing | `pricing` |
| 38 | Objections? | but what about, FAQ, concerns | `faq` |
| 39 | A question for the room? | quiz, poll, think about it | `question` |
| 40 | Proof by picture? | photo, product, before/after shots | `image` / `image_full` / `gallery` |
| 41 | Code, prompt, command? | code, prompt, config | `code` |
| 42 | A tailored composition explains or expresses the idea better | spatial explanation, documentary detail, typographic idea | `custom` (full-stage if useful), with native reconstruction plan |
| 43 | Parallel text is the clearest answer | short parallel statements | `bullets` (≤ 6); no need to manufacture a diagram |

Overrides:
- Talk mode avoids document devices on one slide (four thin cards, hubs with 8 spokes): split into
  several slides or a build-up sequence instead.
- Same type three slides running: fine when the slides compare like with like (the reader learns the
  layout once); change it when the communication task changes. The builders flag it as a prompt.
- Chart a data series again only when the second view shows a different relationship; summaries
  state conclusions in words or KPIs.
- Nothing fits without distorting the idea → `custom` slide on the deck's tokens (slide-library.md).

## T7 · Which chart form? (Zelazny's five comparisons + the extras)

| Comparison (Zelazny) | Question | Best form | Avoid |
|---|---|---|---|
| Component | what share of the whole? | 100% stacked bar; doughnut only ≤ 4 parts | pie with 6+ slices, 3D |
| Item | how do items rank? | horizontal bar, sorted, one highlighted | rainbow colours |
| Time series | how does it change? | column (few periods) or line (many) | dual axes |
| Frequency distribution | how many fall in each range? | histogram (column, no gaps) | smoothed curves without data |
| Correlation | do two variables move together? | scatter; paired bars if few items | line between unrelated points |
| Bridge | what explains the change? | waterfall | stacked columns |
| Range | where does it lie? | range bars (football field) | error-bar clutter |
| Structure × size | who holds what share of which segment? | mekko (image) | nested pies |
| Two-period change by item | who moved most? | slope (image) | clustered bars with 8 pairs |
| Progress to target | how close? | bullet or dumbbell (image) | gauges |
| Distribution with spread | does the average hide variation? | histogram, box plot or the individual points (image or `custom`) | an average alone |
| Dependencies | what must happen before what? | dependency or network diagram (`custom`); `timeline` only if order is all that matters | a Gantt that hides the links |
| Location | does geography explain it? | map (image), only when place carries the argument | a map as decoration |
| Mechanism | how does it work? | annotated schematic (image or `custom`), labelled as technical evidence | decorative illustration |
| Exact lookup | what is the value for X? | `table`, numbers right-aligned | a chart nobody can read values from |

Hygiene for every chart: headline says what it means; units in the exhibit label or axis; axis at
zero for bars (say so on the slide if a line axis is not); direct labels instead of legends when
possible; highlight one thing, grey the rest; never two scales on one axis (split the chart).

## T8 · Which art direction? (full index: visual-language.md §1)

```
1. Formality the room expects?  high → formal or refined group · medium → refined or bold · low → bold or creative
2. Energy the content needs?    calm → refined · confident → formal/bold · loud → bold/creative
3. Brand to follow?             yes → nearest direction + `theme` overrides (primary, accent, fonts)
4. Medium?                      projected in a dark hall → dark-stage / blueprint · printed → light grounds only
5. Stand out without risk?      consulting grammar + editorial-warm / terracotta-editorial / heritage-india
6. Not sure?                    preview three: one safe, one bolder, one wildcard (preview_directions.py)
```

| Room | First pick | Second | Wildcard |
|---|---|---|---|
| Case competition final | consulting-navy | editorial-warm | heritage-india (Indian brand case) |
| Board / IC / investment ask | boardroom-oxblood | finance-emerald | mono-ink |
| Client readout | consulting-navy | modern-teal | gallery-white |
| Startup pitch / demo day | electric-launch | bold-signal | dark-stage |
| Interview / personal story | editorial-warm | nordic-calm | gallery-white |
| Research / thesis | mono-ink | forest-sage | gallery-white |
| Teaching / peer session | forest-sage | pastel-friendly | campus-bright |
| Marketing / brand | coral-studio | terracotta-editorial | poster-yellow |
| Club event / fest | campus-bright | poster-yellow | pastel-friendly |
| Tech / engineering talk | dark-stage | blueprint | night-terminal |
| Government / NGO / big hall | public-sector | forest-sage | mono-ink |
| Luxury / awards / gala | luxe-noir | boardroom-oxblood | gallery-white |

## T9 · Frame and cover

- Frame: `classic` (kicker, title, hairline) for consulting and long document decks; `clean` for
  modern, talk and creative decks; `editorial` (larger serif title, accent kicker, no rule) for
  stories and research narratives; `rail` (rotated section label in the margin) for long documents
  that need wayfinding without a top tracker.
- Cover: `gradient` for formal decks that should not look like a template; `field` (solid) for
  restrained; `split` with a real photograph for brand, people and place stories; `minimal` (light)
  for research, gallery-like and poster decks. The cover carries the key figure when the deck has one.

## T10 · Imagery

```
Does the image explain, evidence, identify or orient? If it only fills space, leave it out.
Do you have real photographs of the actual thing (product, place, people, event)?
├─ Yes → use them: image_full for the hook, split cover, gallery for evidence; credit and alt text
└─ No
   ├─ Is it a screenshot, source figure or document that IS the evidence? → use it as is; add a readable
   │   label, the source and alt text that explains it (authored slide text stays editable)
   ├─ Is the point a number or a structure? → no image; the exhibit is the visual
   ├─ Is the slide abstract (vision, values)? → a typographic statement or quote beats stock art
   ├─ Would a conceptual illustration help? → only if clearly labelled as illustrative
   └─ Is an image truly needed? → ask the user for one, or leave [IMAGE NEEDED: what] (it fails lint)
Keep apart: documentary photos vs illustrations, real interfaces vs mockups, technical diagrams vs
decoration, verified charts vs illustrative ones.
Never: AI-generated imagery presented as a real facility, person, customer, product or result;
photos of public figures pulled from the web; stretched images (the builder crops); authored slide
text flattened into a picture.
```

## T11 · When to ask the user, when to proceed

- Ask (one round, ≤ 3 questions) when a wrong guess is expensive: the audience and the decision,
  the mode if unclear, real numbers you do not have.
- Proceed and state the assumption when the guess is cheap: direction (show previews instead),
  slide count, minor wording, the order inside a section.
- Never fill a gap with an invented fact; leave a visible placeholder (it fails lint until fixed).
- Always ask before the final build: the approval gate (Gate 5) is a question, even when the
  final format was named at the start. The only exceptions are an explicit "skip the draft" and
  edits to an attached deck. If nobody is there to answer, stop at the draft.
