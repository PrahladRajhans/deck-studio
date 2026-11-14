# Brief and reasoning tools

Use the relevant section at intake or storyline work. SKILL.md owns the stage order and gates;
creative-direction.md owns concept exploration; visual-language.md owns theme and grid defaults.

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
| Purpose | Inform, teach, persuade, diagnose, secure a decision, report progress | Secure a decision |
| Consumption | Live, read alone, workshop, hybrid | Live, then circulated as PDF |
| Domain | Which domain pack applies (domain-packs.md) | Consumer goods / marketing |
| Voice | Presenter stance, formality, relationship, claim strength (human-voice.md §1) | Peer adviser, professional, claims measured |

**Evidence inventory** (beside the canvas): each fact you will use, where it sits (file, page,
cell, URL), its kind (observed, estimate, forecast, assumption, target, illustrative) and whether
it is verified. This becomes `facts`, `fact_meta` and `evidence` in the spec (spec.md).

If you cannot write the governing thought yet, choose one: frame the deck around an explicit open
question plus the evidence plan that would answer it (an exploratory or research deck is
legitimate), or say the material is not ready and offer a one-page issue summary instead.

## 2. Decision framework: from material to argument

1. **Governing thought** in one sentence, at the confidence the evidence supports.
2. **Structure** the support (pick per decision-trees.md T4):
   - *Pyramid (Minto)*: governing thought → the distinct key lines, usually 2-5 (all reasons OR all steps, never mixed) →
     evidence under each. Key lines are MECE: no overlaps, no gaps a judge would spot.
   - *SCQA*: Situation (agreed facts) → Complication (what changed) → Question (what should we do?) →
     Answer. Give only the situation the reader needs.
   - *Sparkline (Duarte)*: alternate "what is" and "what could be", end with a call to action and
     the "new bliss"; the audience is the hero, the presenter the mentor.
   - *Problem-agitate-solve* for rooms that already feel the pain.
3. **Rhetorical emphasis** (qualitative; no percentages, since nothing measures them):

| Emphasis | What leads | Typical rooms |
|---|---|---|
| Evidence-led | data, analysis, method; stories only as illustration | executive readouts, working decks, research |
| Demonstration-led | the product, prototype or worked example shown | pitches, product reviews, technical teaching |
| Story-supported | a real case or person carries the argument; data proves it | interviews, change programmes, marketing |
| Participation-led | questions, exercises, the room's own input | workshops, teaching, facilitation |

   Every emphasis still needs credibility (method, limits, a devil's advocate slide).
4. **Devil's advocate**: write the strongest objection to the governing thought. Either it gets a
   slide (limits, risks, "what would change our mind") or the notes carry the answer.
5. **Ghost deck**: one line per slide, in order. Lines may be premises, facts or questions as well
   as answers; read in sequence they form one speech.


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
| Generic presentation despite clean layout | concept and subject-specific evidence appear on substantive slides | creative-direction.md §8 |
| Uniform case studies | preserve their real differences; never invent unevenness | review |
| Placeholders shipped | `[TBD]`, `[IMAGE NEEDED]`, lorem, xxx fail lint | lint (exit 1) |
| Self-grading | fresh-eye reviewer who has not seen the build; zero findings allowed | qa.md §6 |
| Time overrun | timing notes from `minutes`; read-aloud test | builder, rehearsal |
| A slide nobody needs | Gate 2: every title serves the spine; else appendix | review |
| Headline overstates its exhibit; counts or promises not kept | semantic review (qa.md §3); count check in `spec_io.py` | review, validator |
| Unverified or unclassified evidence reaching the final file | `fact_meta`, `evidence`, `data_status`; `--strict` release gate | validator, Stage 6 |
| Arithmetic that silently drops data | vector and weighted helpers reject unequal lengths; "not reached" cannot index a year | facts model |
| Machine-sounding text | human-voice.md rules; `style` prompts; `style_review` / `style_rhythm` | builders, lint, read-aloud |
| Expensive rework | final format built only after the draft is approved | Gate 5 |
| Draft promises what the final can't do | draft uses the final direction and fonts; final QA on the real file | routes.md §E, Stage 6 |

