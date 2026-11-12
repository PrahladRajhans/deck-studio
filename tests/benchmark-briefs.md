# Benchmark briefs: test the skill on contrasting tasks

A skill can read as comprehensive and still produce the same deck every time. Run these briefs
before and after any substantial change to the skill, keep the drafts, and compare them. The smoke
test checks that the tools work; these check that the judgement works.

Score each dimension separately, 0-2, and never let one compensate for another: an attractive deck
with an unsupported claim fails on factual fidelity whatever its design score.

| Dimension | 2 = good | 0 = fails |
|---|---|---|
| Factual fidelity | every figure from evidence or labelled; claims at the right strength | an invented or contradicted figure, source or causal claim |
| Audience fit | structure, density and register suit the room | a document deck for a live room, or the reverse |
| Reasoning | titles tell the story; the recommendation follows | jumps, repeats, conclusions without premises |
| Visual appropriateness | each exhibit shows the relationship that answers the slide's question | decoration, wrong chart form, every slide the same |
| Readability | nothing below the floors, nothing clipped, clear focal point | flagged slides left in |
| Voice | sounds like the presenter; no stock phrasing | generic or manufactured voice |
| Revision reliability | a requested change is made, nothing else moves | unrelated slides changed |

## The briefs

1. **Executive recommendation**: a CFO must approve or reject a ₹50 crore warehouse automation
   project in a 10-minute board slot. Supplied: costs, labour savings, one vendor quote. Tests
   prioritisation, answer-first, economics, the ask.
2. **Marketing campaign review**: a brand team reviews a festive campaign with reach, clicks and a
   sales uplift that coincided with a price cut. Tests attribution vs causation and calibrated
   headlines.
3. **Oil and gas investment case**: an investment committee reviews a field development with a
   production profile, capex estimate and a single oil price. Tests units, sensitivities (and asking
   for them), technical schematic vs decoration.
4. **Technical teaching session**: 45 minutes teaching first-year MBA students how to read a cash
   flow statement. Tests explanatory sequencing, questions, agenda use, build-up slides.
5. **Dense reading deck**: a 20-slide pre-read for a steering committee that will not be presented.
   Tests self-contained reasoning, document density, exec summary references.
6. **Expressive brand pitch**: a student club pitches a festival to sponsors with photos from last
   year. Tests creative range, real imagery, a crisp sponsorship ask.
7. **Supplied corporate template**: the user attaches a branded .pptx template and asks for a
   quarterly update in it. Tests template profiling and layout reuse instead of a direction.
8. **Single-slide revision**: "change the chart on slide 6 to show 2024 too". Tests that only slide 6
   changes and the facts stay consistent.
9. **Incomplete evidence**: a market-entry deck where market size and competitor share are missing.
   Tests visible gaps, questions to the user, no invented numbers, `--strict` blocking the final.
10. **Long or multilingual text**: the same five slides with Hindi labels and long English titles.
    Tests glyph coverage, fitting, the overflow rule.

Record for each run: the brief, the spec, the draft contact sheet, the validator and lint output,
the scores, and what changed in the skill since the last run.
