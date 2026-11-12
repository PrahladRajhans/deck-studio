# Frameworks: plan, decide, select, build, check

The Deck Framework (from the Gamma Design Playbook) runs as six stages with five gates. The
user's approval of a cheap HTML draft (Gate 5) sits between the work and the expensive final
build. This file gives each stage its working tool: a canvas to fill, a rule to decide, a
checklist to pass.

```
PLAN ─g1─▶ DECIDE ─g2─▶ SELECT ─g3─▶ DRAFT (HTML) ─g4─▶ REVIEW + ITERATE ─g5: user approves─▶ FINALISE ─▶ DELIVER
brief       archetype,    direction,     notes first,       render, ten-point check,     PPTX / Slides /
ghost deck  structure,    frame,         build order,       voice read-aloud, show the   Gamma / Canva /
headline    skeleton      imagery        facts model,       user, change the spec,       HTML; final QA
test                      (previews)     human voice        repeat                       on the real file
```

Why the order: content, visuals and the skeleton change most while iterating, and every change
is a one-line spec edit plus a rebuild of the draft in seconds. A PPTX, Gamma or Canva build costs
far more tokens and time and, for generators, credits. So it happens once, on settled content.

---

## 1. Planning framework: the brief canvas

Fill this before any slide exists. Write it at the top of the spec as `"brief": {...}` (the builder
ignores it; it keeps the reasoning next to the deck).

| Field | Question | Example |
|---|---|---|
| Audience | Who, what they already know (beginner / practitioner / expert) | 3 partners judging a strategy case; know the industry |
| Decision / action | One verb: approve, fund, hire, learn, adopt, celebrate | Approve a USD 1.2M entry budget |
| Setting | Live room (size, projector), video call, read alone later | 12-minute final, projected, PDF submitted before |
| Mode | Document or talk (decision-trees.md T2) | Document density, 16pt+ type |
| Time and length | Minutes; slide budget | 12 min + 8 min Q&A; 9-11 content slides |
| Governing thought | The answer in one sentence | Enter through Amazon.ae and one retailer, not own stores |
| Success metric | A number or a verb + object | Judges score feasibility ≥ 8/10 |
| Evidence in hand | Real figures, sources, quotes, photos; gaps listed | Market size (Euromonitor), 2 interviews; no CAC data yet |
| Criteria | Rubric, interview questions, client's question; each maps to a slide | Insight, feasibility, financials, creativity |
| Constraints | Format, template, brand, file size, deadline, language | 16:9, ≤ 12 slides, PDF, British English |
| Accessibility | Low vision, colour blindness, captions, non-native audience | Large hall: 24pt floor |
| Tone | Rigorous, warm, bold, playful | Rigorous with one human hook |
| Tolerance | How dense, how much motion the audience accepts | Dense OK, no animation |

If you cannot write the governing thought, stop: the material is not ready. Offer a one-page
issue summary instead of a deck.

## 2. Decision framework: from material to argument

1. **Governing thought** in one sentence, at the confidence the evidence supports.
2. **Structure** the support (pick per decision-trees.md T4):
   - *Pyramid (Minto)*: governing thought → 3 key lines (all reasons OR all steps, never mixed) →
     evidence under each. Key lines are MECE: no overlaps, no gaps a judge would spot.
   - *SCQA*: Situation (agreed facts) → Complication (what changed) → Question (what should we do?) →
     Answer. Give only the situation the reader needs.
   - *Sparkline (Duarte)*: alternate "what is" and "what could be", end with a call to action and
     the "new bliss"; the audience is the hero, the presenter the mentor.
   - *Problem-agitate-solve* for rooms that already feel the pain.
3. **Rhetoric balance** (AI-Business-Tools beamer patterns; tone, not slide allocation):

| Context | Logos | Ethos | Pathos |
|---|---|---|---|
| MBA / executive readout | 50% | 25% | 25% |
| Business-school teaching | 45% | 15% | 40% |
| Professional audience | 40% | 25% | 35% |
| Consulting workshop | 30% | 25% | 45% |
| Working deck | 55% | 25% | 20% |

   Logos = data and frameworks; ethos = method, limits, devil's advocate; pathos = stories, stakes.
4. **Devil's advocate**: write the strongest objection to the governing thought. Either it gets a
   slide (limits, risks, "what would change our mind") or the notes carry the answer.
5. **Ghost deck**: one line per slide, in order. Lines may be premises, facts or questions as well
   as answers; read in sequence they form one speech.

**Gate 1 (headline test).** Read only the titles: they tell the whole story and land the answer
(document mode) or reveal it step by step (talk mode). Every document title passes both tests:
(a) a sceptic could say "I disagree"; (b) hide the body and the title still carries the point.

## 3. Selection framework

Score each choice against the brief, not taste. Write the one-line rationale (Gate 3).

| Choice | Decide by | Tool |
|---|---|---|
| Final format (confirmed at Gate 5) | Format named? numbers must tie? image-led? team edits? | decision-trees.md T1 |
| Archetype + skeleton | What the room must do | T3, deck-skeletons.md |
| Story structure | Seniority, scepticism, live or read | T4 |
| Slide types | Shape of each piece of evidence | T6, slide-library.md |
| Chart forms | Comparison type | T7 |
| Direction | Formality × energy × brand × medium | T8, visual-language.md §1 |
| Frame + cover | Document length, register | T9 |
| Imagery | Real photographs available? | T10 |
| Density | Mode + audience tolerance | T2 table |

**Show, don't tell.** When the look is open, build 2 slides (cover + one representative content
slide) in three directions with `preview_directions.py` (HTML, seconds) and let the user pick: one safe for the
room, one bolder, one wildcard. People recognise what they want faster than they can describe it.

**Showcase first.** For a section of 4+ similar slides, build one, render it, look, then build the
rest.

## 4. Skeleton framework: build order and anatomy

Build order: content slides → executive summary (from the finished content; rows `ref` the slides)
→ agenda / dividers → cover and close → appendix (backup for every number a judge might challenge).

Slide anatomy (document content slide):

| Zone | Rule |
|---|---|
| Kicker | section name, small tracked caps; quiet wayfinding |
| Title | one full-sentence assertion, ≤ 2 lines; optional `letter` prefix for a chapter's key exhibits |
| Subtitle (optional) | scope or method in one line |
| Exhibit label | "Exhibit N · what it shows (unit)" |
| Exhibit | the one chart / table / diagram / picture that proves the title |
| Side panel (optional) | 2-3 "why" sentences beside a chart: the chart shows what, the panel why |
| So-what | the implication or decision; the accent appears here and on the highlighted data only |
| Footnotes (optional) | numbered, tied to ¹ ² ³ markers at the claim |
| Source | real source; or "Source: to be added" |
| Tag (optional) | "Illustrative" / "Non-exhaustive" when the exhibit is a sample |
| Footer + page | constant across the deck |

Talk-mode anatomy: headline that reads at a glance, one figure or 3-4 lines, nothing the audience
must squint at; the depth is in the notes.

Notes anatomy (every slide): `[~N sec]` → spoken script (2-5 sentences, point first, each figure
with its source in the sentence) → "For the presenter, not to be read out": assumptions to confirm,
sources, likely questions with short answers.

## 5. Checks and balances (built into the workflow)

| Risk | Check | Where it runs |
|---|---|---|
| Invented numbers or sources | facts model + "Source: to be added"; never invent an institute | spec, builder warnings |
| Numbers that disagree across slides | every figure from `facts`; `checks` assert the claims | builder (exit 2) |
| Derived figures added by hand | `sum`, `pct`, `cagr`, `wavg`, `first_at_least` in facts | builder |
| Invented targets that don't add up | goal × people × periods must fit the stated target; list in assumptions | writer + review |
| Recommendation contradicts its own scorecard | builder warns if `recommended` ≠ top score | builder |
| Labels instead of claims | headline test; `title_is_label` | `--outline`, lint |
| Same layout over and over | warning on 3 in a row; contact-sheet rhythm review | builder, render |
| Charting the same data twice | warning; summaries use words/KPIs | builder, lint |
| Two scales on one axis | warning; split the chart | builder |
| Text overflow, overlaps, off-slide | font-metric fitting with floors; lint; render | builder, lint, render |
| Low contrast | auto-flip on fills; lint contrast check | builder, lint |
| Repeated phrasing (machine tell) | `repeated_phrase`; vary sentence shape, not a new stock phrase | lint |
| Uniform case studies (machine tell) | vary depth and resolution; one may stay unresolved | review |
| Placeholders shipped | `[TBD]`, `[IMAGE NEEDED]`, lorem, xxx fail lint | lint (exit 1) |
| Self-grading | fresh-eye reviewer who has not seen the build | qa.md §5 |
| Time overrun | timing notes from `minutes`; read-aloud test | builder, rehearsal |
| A slide nobody needs | Gate 2: every title serves the spine; else appendix | review |
| Machine-sounding text | human-voice.md rules; `voice` lines; `ai_voice` / `ai_rhythm` | builders, lint, read-aloud |
| Expensive rework | final format built only after the draft is approved | Gate 5 |
| Draft promises what the final can't do | draft uses the final direction and fonts; final QA on the real file | routes.md §E, Stage 6 |

## 6. Review framework (rounds)

1. **Self-check pass** (on the draft, then again on the final file): render → look at every
   slide → lint (final) → ten-point check (qa.md). Fix.
2. **Fresh-eye pass** (high stakes): a separate agent with only the PNGs and the brief; triage each
   finding (adopt / reject with reason / ask the user); apply; rebuild.
3. **User round** (draft): show the draft, collect changes, apply them to the spec, rebuild.
   Repeat until the user approves. Content and structure come first, look second.
4. **Stop rule**: stop when a full pass finds nothing new. Report: number of findings, adopted
   changes, remaining concerns, in three lines. Ask before another round.
5. **Three fixes on the same defect without success**: stop patching; change the slide type or
   split the content.
6. **No soft language for defects**: "slightly tight", "nearly overlapping" means fix it.
