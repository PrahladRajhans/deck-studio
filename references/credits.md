# Sources, credits and the positives matrix

Ideas were studied and re-implemented; no code was copied. All code in `scripts/` (including the HTML
draft builder) and `assets/html-stage/` is original to this skill. Anthropic's pptx skill declares its own
licence terms in its `LICENSE.txt`; ai-awesome showed no licence file when studied. From both, only ideas
were taken.

## Positives matrix: what each source does best and where it lives here

| Source (licence) | Positives taken | Where in deck-studio |
|---|---|---|
| **anthropics/skills `pptx`** (licence in its LICENSE.txt; ideas only) | content-informed palette; one dominant colour + one accent; a repeated visual motif (never a stripe); every slide gives the eye a reason to look (adapted here as a purpose test, not decoration); stat callouts; safe-font list and QA-unreliable fonts; never Aptos; avoid accent lines under titles, edge stripes, centred body, same layout repeated, default cream; the visual-QA defect list; first render always has problems; fresh-eye subagent; placeholder grep patterns | visual-language §1, §3, §6, §7, §9; qa §1, §5; builder font map; lint placeholder regex |
| **office-kit/pptx** (MIT) + its `consulting-deck-design` skill | document vs talk modes that deliberately disagree; assertion tests; talk rules (no agenda, question dividers, step-by-step reveal, staging devices, mixed headline forms, timing per body slide, close with action); three background modes; gradient covers; letter-prefixed governing thoughts; running agenda spine; left-rail framework layout; multi-column with vertical rules; pull quotes; glyph badges instead of custom icons; highlight one grey the rest; provenance tags; numbered footnotes separate from sources; never two scales on one axis; annotations beside charts, not on them; numeric self-consistency as the strongest signal; vary citation formats; no invented institutes; non-uniform case studies; phrasing diversity; cards share height; targets as series; fact ledger across pages; the fresh-eye review prompt and triage | decision-trees T2; writing §1-§2, §6; frameworks §4-§5; slide types `framework`, `columns`, `quote`, `agenda`; cover `gradient`; `letter`, `tag`, `footnotes`; lint `repeated_phrase`; qa §4-§5 |
| **PeterKalmstrom/claude-powerpoint-skill** (MIT) | spec + plan/check loop; notes written first (say / assumptions / sources); never invent facts beyond the brief; deck-level sources; the ask states reasons and cost; success has a number; compute derived figures; invented goals must add up; objection answers = claim, proof, action; chart a series again only for a different relationship; summaries state conclusions; audience persona (who, goal, setting, accessibility, tolerance); cognitive-load limits (≤ 7 bullets, ≤ 6 tiles, ≤ 55-char headlines, ≤ 75-char lines, chapter break every 7-10 slides); five-second test; 20 directions in four tone groups; spacing steps and 3× group gaps; chart and table rules; showcase-first; room-depth type floors; presenter prep (timing markers, Q&A panic sheet, handout); lint codes | facts model + checks; notes format; builder warnings (ask number/cost, FAQ fragments, same data twice); frameworks §1, §3, §5; writing §4-§5; direction index; qa §7 |
| **Rich627/slides-skill** (MIT) | JSON spec where the renderer owns layout; storyline skeletons by purpose (class report, pitch, team update, lecture, workshop, portfolio, exec status); visible caveats; references slide mapped to sources; dark slides bracket the story; authored line breaks | spec-driven builder; deck-skeletons B2, D3, E1-E3, E6; `references` type |
| **johnnyknocke/pptx-from-layouts-skill** (MIT) | visual-type decision order (sequence → comparison → parallel → data contrast → quote → table → hero → bullets); detection keywords; content-length limits per type; `data-contrast` and `story-card` types; edit vs regenerate; anti-patterns (no tables for processes, no bullets for comparisons) | decision-trees T6 (extended to 42 rows); slide-library limits; `data_contrast`, `image_full` |
| **Julien339/pptx-builder-skill** (MIT) | pick the style before building; a gallery of named styles; shape language (corner radius + motif) as part of identity; adapt to a user's template by resolving palette, radius and motif first; consistent icon set; test one slide type before scaling | direction tokens `radius`, `card`; visual-language §6; preview_directions; showcase-first |
| **CodeHalwell/power-pptx** (MIT) | space-aware authoring: measure text with font metrics before save; lint after; clear theme shadows; corner radius by absolute size; arrows with real heads; modern compositions (bento, annotated chart, product UI, editorial); HTML/SVG capture for visuals PowerPoint lacks, with an honest editability note | fit_size + floors; `_drop_style`; card radius; route G chart images; route F; editability notes |
| **zarazhangrui/frontend-slides** (MIT) | show, don't tell: three visual previews (safe, bold, wildcard); density modes; fixed 16:9 stage that never reflows; reduced motion; mood → style mapping; a style index with formality, density, best-for, avoid-for; anti-AI-slop list (fonts, purple gradients, identical cards, everything centred); preview authenticity (no internal labels on slides) | preview_directions.py; T8 mood table; direction metadata; HTML stage template; visual-language §9 |
| **AI-Business-Tools/claude-code** `slides-content` + `beamer` (MIT) | source → summary → slides; academic vs general summaries; structure presets (MBA, teaching, faculty, professional, consulting workshop, working deck); rhetoric balance (logos/ethos/pathos) per context; register (business glosses terms vs technical); devil's advocate / limitations slide; one slide per distinct finding; audit rules (no soft language for defects, every slide individually); version snapshots per edit round | storyline §6; frameworks §2; writing §3; qa §6 |
| **ai-awesome/skill-create-slides** (no licence: ideas only) | four presentation styles (executive briefing, peer sharing, public explainer, educational) with narratives and chapter structures; chapter summary tables; "think about it" question slides; progressive disclosure | decision-trees T3-T4; deck-skeletons E1; `question` type |
| **BeHuman and Unslop skills** (the user's own; built on Wikipedia's "Signs of AI writing" field guide, WikiProject AI Cleanup) | kill-list vocabulary; negative parallelism; rule-of-three padding; significance "-ing" tails; vague attribution; false ranges; puffery; em-dash density; title case and bold-label bullets; chatbot residue; "add soul" (opinions, specifics, rhythm, first person); don't overcorrect; density not thoughtcrime | references/human-voice.md (adapted to slides: fragments allowed, slide-level tells added); `ai_tells` / `deck_voice` in `_common.py`; lint `style_review`, `style_rhythm`; builder `style` prompts |
| **tosea.ai "Best Claude Code skills for PowerPoint 2026"** (same article as the Medium piece) | landscape and trade-offs between skills | selection of what to borrow |
| **Gamma Design Playbook** (own study, Nov 2026: ~546 Gamma templates classified from descriptions, Mandate verified by generation; ~1,550 Canva templates sampled, 8 inspected; 23 Manus samples) | The Deck Framework (Plan → Decide → Select → Create → Polish, with gates; extended here into draft → approve → finalise); 11 use-case themes; Mandate grammar; read-back failures; families and skins; quick picks; signature moves; Canva and Manus lessons | frameworks; use-cases; routes C-D; visual-language §10, §12 |

## External references checked online (Nov 2026)

- Sequoia Capital business plan / pitch sections: purpose, problem, solution, why now, market size,
  competition, product, business model, team, financials (via alexanderjarvis.com summary).
- Y Combinator seed deck guidance (Aaron Harris, YC blog): title, problem, solution, traction,
  insights, business model, market, team, ask; focus on narrative, clarity, simple design.
- Kevin Hale (YC), "How to design a better pitch deck": legible, simple, obvious.
- Guy Kawasaki's 10/20/30 rule: 10 slides, 20 minutes, 30pt minimum (via Microsoft Learn archive).
- Nancy Duarte, "The secret structure of great talks": what is ↔ what could be, call to action,
  new bliss; the audience is the hero.
- Gene Zelazny, *Say It With Charts*: five comparisons (component, item, time series, frequency
  distribution, correlation) (via bissantz.de summary).
- Barbara Minto's pyramid principle and SCQA (as operationalised in office-kit's sources).

## Not studied

Pinterest: blocked by a login wall in the browser pane (Nov 2026); it needs the user's own
sign-in. Nothing in this skill claims to come from Pinterest.

## Review history

- **Self-review rounds (Nov 2026)**: two critique-and-fix rounds on the playbook and skill; render,
  lint and contrast fixes; HTML-first workflow; human-voice layer.
- **External review by ChatGPT (Nov 2026, two passes over the repository at commit 794c98d)**.
  Adopted after checking each finding against the code and examples:
  - five contradictions in the bundled examples (headline vs exhibit, count vs list, scope vs data,
    a promise not kept, an unsupported payback claim), all fixed;
  - arithmetic helpers that could silently drop data or turn "not reached" into a year, fixed;
  - validation that missed nested numbers, now `spec_io.py` with an evidence register, claim
    types and a `--strict` release gate;
  - an explicit fidelity contract per final route and a destination capability table;
  - semantic review separated from style review; style findings recast as editorial prompts with
    technical exemptions and `voice_ok`;
  - universal rules turned into defaults with exceptions (agenda, reveal, threes, repetition,
    signature moves, dates, governing thought, review quotas, citation variety, rhetoric
    percentages);
  - contrast lint at 4.5:1 for normal text, font-substitution reporting, shared timing, negative
    stacked charts, CI that fails on fit errors and renders the PPTX, the draft path decoupled from
    python-pptx, domain packs, a custom-slide path, revised imagery rules, unit tests and benchmark
    briefs.
  Not adopted, with reasons: converting the approved HTML itself into PPTX (both builders render one
  spec with matching layouts, which preserves more than a conversion would; the gap is disclosed in
  the fidelity contract); starting from 20-30 layout families (44 types already exist and are
  tested); a bundled SVG icon family (deferred until a licence-clean set is chosen).
- **Further references cited in that review and used here**: the assertion-evidence approach to
  slide design (Michael Alley, Penn State) for claim-plus-evidence titles; Microsoft's PowerPoint
  accessibility guidance (alt text, reading order, contrast, slide titles) for the QA accessibility
  checks.


- **Evidence-gate hardening (Nov 2026)**: subsequent implementation and regression tests close
  documented provenance and placeholder bypasses; `CHANGELOG.md` records behavior, migration and
  verification limits. Claim inventories record semantic review rather than claiming to prove truth.

- **Creative-direction revision (Nov 2026)**: strengthen concept-first exploration, composition,
  narrative rhythm and positive presenter voice; add a full-stage custom HTML path and a fictional
  worked example. These are proposed authoring practices and tested renderer capabilities, not a
  measured claim that all future decks will be more creative. See creative-direction.md and CHANGELOG.md.

- **Workflow and component revision (14 Nov 2026)**: evaluate external review claims against this
  repository, consolidate stage routing, keep assurance proportional to claim consequence and add
  fixed-packet execution tests. Reviewer suggestions are hypotheses, not source-code evidence or
  proof of better output. See tests/evaluations/2026-11-14-revision-plan.md for actual verification.
- **Feather icons**: twelve unmodified SVGs from feathericons/feather, pinned at
  3dc050d97405062eba78aa57115c0a15c63abdaa. Copyright Cole Bemis; MIT license is
  bundled at assets/icons/feather/LICENSE. See that directory's README for source and usage. This
  supersedes the earlier review's deferral; it does not rewrite the historical decision.

## Primary guidance checked for the completeness audit (14 November 2026)

- Anthropic, [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/research/equipping-agents-for-the-real-world-with-agent-skills): supports moving task-specific detail into referenced files and evaluating realistic executions. This supports selective loading, not deleting useful context or treating a line count as a proven model limit.
- W3C, [Understanding SC 1.4.3 Contrast (Minimum)](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html): AA text reference is 4.5:1, or 3:1 for large text. These ratios inform checks; they do not certify a presentation's overall accessibility.
- Microsoft, [Make PowerPoint presentations accessible](https://support.microsoft.com/en-us/accessibility/powerpoint/make-your-powerpoint-presentations-accessible-to-people-with-disabilities): include meaningful alt text and inspect reading order using the target application's accessibility tools. Pixel inspection alone cannot establish screen-reader usability.
- UK Analysis Function, [Colours in charts](https://analysisfunction.civilservice.gov.uk/policy-store/data-visualisation-colours-in-charts/): reinforce distinctions with labels and meaningful encodings rather than relying only on colour. The skill's RAG status text and ordinal fractions reflect this principle.
- ONS, [Showing uncertainty in charts](https://service-manual.ons.gov.uk/data-visualisation/guidance/showing-uncertainty-in-charts): show uncertainty when it changes interpretation, explain its meaning and avoid misleading comparisons. The skill keeps scenario ranges distinct from statistical intervals. This is not a blanket ban on technical terminology or every error-bar style in scientific presentations.

- Anthropic Help Center, [How to create custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills): package a folder matching the skill name as the ZIP root. This motivates the verified release ZIP instead of the generic GitHub source archive. Upload validation is distinct from execution inside Claude.
