# Domain packs: what each field asks a deck to prove

Industry shapes the evidence vocabulary and the conventions; purpose and audience shape the story.
An oil and gas deck can be an investor pitch, an engineering review or a safety briefing, and each
needs a different structure. Pick the archetype first (decision-trees.md T3), then apply the pack.

Each pack lists: the questions the room will ask, the evidence it expects, exhibits that suit it,
terms to get right, and traps. These are starting conventions, not a substitute for the user's own
domain knowledge or house rules; when the user's organisation does it differently, follow theirs.
Packs are added from real use: when a deck in a new field teaches something, add it here.

## Consulting and strategy

- **Questions**: What is the governing question? What did you rule out and why? What does it cost,
  what does it return, and when? Who does what next? What would change the recommendation?
- **Evidence**: market sizing with a stated method, a diagnostic tree that is mutually exclusive and
  collectively exhaustive, options scored on agreed criteria, economics (investment, payback, NPV
  or IRR when the audience expects them), an implementation plan with owners, risks with
  mitigations.
- **Exhibits**: issue tree, waterfall, sorted bar, options scorecard, 2×2 matrix, Gantt with owners.
- **Terms**: governing thought, MECE, SCQA, so-what, base case vs scenarios.
- **Traps**: sizing presented as a forecast; options scored with invented weights; a recommendation
  the scorecard doesn't support; implementation that starts before the decision date.

## Finance, investment and banking

- **Questions**: What is it worth, on what assumptions? How sensitive is the answer? What are the
  returns, and the downside? Is the period, currency and basis consistent?
- **Evidence**: historical financials with source and period; projections with explicit drivers;
  valuation by more than one method; sensitivities; comparable companies or transactions with the
  selection rule stated.
- **Exhibits**: football field (range), sensitivity table, waterfall bridge (EBITDA, cash),
  indexed line, table with right-aligned figures and negatives in parentheses.
- **Terms**: keep period labels exact (FY vs CY, LTM, quarter end); state currency and units once
  per exhibit (₹ crore, USD M); nominal vs real.
- **Traps**: mixing fiscal and calendar years; growth rates on different bases; a valuation that
  doesn't reconcile across slides; "payback" without cash flows; precision the model doesn't have.

## Marketing, brand and consumer

- **Questions**: Who is the customer and what do we know about them (and how)? What is the insight?
  Why will this work, and how will we know? What does it cost per outcome?
- **Evidence**: consumer research (sample, method, date), funnel definitions with the source of each
  stage, channel roles, creative work itself, a measurement plan with the metric and baseline, unit
  economics (cost per acquisition, contribution per order) when claiming payback.
- **Exhibits**: funnel, journey map, real creative executions and mock-ups (labelled as mock-ups),
  before/after, slope or share charts, KPI tiles against plan.
- **Terms**: reach, frequency, CTR, conversion rate (state the denominator), CAC, LTV, share of
  voice; attribution vs incrementality.
- **Traps**: attribution claims stated as causation; funnel stages with mismatched denominators;
  "the campaign drove sales" without a control or test; payback claims without margin data; stock
  lifestyle imagery standing in for real creative.

## Energy, oil and gas, and heavy industry

- **Questions**: What is the asset and its context? What are the production or capacity
  assumptions? What does it cost to build and run? How sensitive is the case to price, volume and
  schedule? What are the safety and environmental implications?
- **Evidence**: units stated precisely and consistently (bbl/d, boe, MMscf/d, MW vs MWh,
  tonnes CO2e), production or load profiles over time, capital and operating cost estimates with
  their class or basis, price assumptions with source and date, sensitivities, schedule.
- **Exhibits**: production profile (line or area), cost breakdown (stacked bar), sensitivity
  (tornado as a sorted range or bar), annotated schematic or site map (labelled as technical
  evidence), Gantt for project phases.
- **Terms**: get unit conversions and capacity vs generation right; distinguish reserves and
  resources categories as the source defines them; CAPEX vs OPEX.
- **Traps**: confusing capacity (MW) with energy (MWh); mixing units across slides; decorative
  industrial photography in a technical decision deck; safety claims without data; a single price
  assumption with no sensitivity.

## Science, health and medicine

- **Questions**: What was the study design? Who was in it (population, n)? What is the effect size,
  with its uncertainty? What are the limitations? Does the conclusion stay within the data?
- **Evidence**: design (randomised, cohort, case-control, survey), sample size and denominators,
  effect sizes with confidence intervals, pre-registered vs exploratory analyses, the source figure
  when reproduced (with credit).
- **Exhibits**: forest plot or dot-and-interval charts (image or custom), flow diagram of
  participants, distribution plots rather than averages alone, tables of results.
- **Terms**: relative vs absolute risk, statistical vs clinical significance, association vs
  causation.
- **Traps**: relative risk without the absolute numbers; causal language from observational data;
  dropping the denominator; cropping a source figure in a way that changes its meaning; any patient
  detail that could identify someone.

## Technology, product and operations

- **Questions**: What problem, for whom, with what evidence of need? How does it work (system
  boundary, interfaces, dependencies)? What breaks, and how do we know? What does it cost to run?
- **Evidence**: usage or performance data with the measurement method, architecture and
  dependency diagrams, failure modes and incident history, service levels, roadmap with
  dependencies.
- **Exhibits**: architecture or dependency diagram (custom), process flow, before/after metrics,
  real screenshots (labelled), roadmap (now/next/later), code when the audience reads code.
- **Terms**: latency vs throughput, uptime as a percentage with its period, p50/p95/p99.
- **Traps**: concept mock-ups shown as shipped product; averages hiding tail latency; roadmaps that
  ignore dependencies; uptime without the measurement window.

## Public policy, government and development

- **Questions**: What is the problem's scale and who is affected? What has been tried? What does the
  option cost and who pays? What are the distributional effects and the risks?
- **Evidence**: official statistics with the issuing body and year, programme evaluations, budget
  figures with the fiscal year, stakeholder positions stated fairly.
- **Exhibits**: maps when geography matters, indexed trends, options tables, logic models (inputs →
  outputs → outcomes), timelines.
- **Terms**: outputs vs outcomes vs impact; per capita and real terms where comparisons need them.
- **Traps**: comparing totals across regions of different size; nominal comparisons over long
  periods; presenting one stakeholder's view as consensus.

## Education and teaching

- **Questions**: What should learners be able to do afterwards? What do they already know? How will
  you check understanding?
- **Evidence**: worked examples, real cases, data the learners can inspect, practice tasks.
- **Exhibits**: question slides, build-up diagrams, before/after, worked steps, short quizzes.
- **Terms**: learning objective, prior knowledge, misconception.
- **Traps**: dense document slides used for live teaching; answers given before the question has
  landed; no check for understanding.
