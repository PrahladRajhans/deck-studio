# Visual grammar and components

A design language is a small set of meaningful relationships. Choose it for this subject and keep
it coherent across typography, charts, photography, diagrams, icons and motion. Theme tokens control
colour and fonts; the creative brief explains why the composition belongs to this story.

## Choose an expressive system

Examples to develop, rather than copy as templates: an annotated field notebook for an investigation;
a product teardown with real artefacts; a route map for a transformation; a typographic editorial for
a strong point of view; a restrained evidence atlas for research; a photographic story for an event.
Test the system on a dense evidence slide, not only the cover. A metaphor must explain relationships
accurately. Do not force every exhibit into the metaphor or imply unsupported causation.

Record the grid, type hierarchy, spacing cadence, shape treatment, image treatment, data colour roles
and recurring motif in the brief. Reuse them intentionally. Alternate density and emphasis when the
story benefits; repeated comparison slides may use exactly the same composition.

## Visual choices

| Element | Useful role | Default to reconsider |
|---|---|---|
| Chart | Compare, show distribution, change or relationships | A bullet list of comparable numbers; a decorative chart with no question |
| Table | Exact lookup, assumptions, option tradeoffs | Dense paragraphs boxed into cells |
| Diagram | Make sequence, dependency or structure visible | Equal cards for unequal relationships; arrows that imply invented causality |
| Photography | Show real context, people, place or artefact | Generic stock handshake or invented documentary evidence |
| Art | Express an idea, atmosphere or metaphor | Treating an illustration as a sourced observation |
| Icon | Help scan familiar concepts | A different icon style on every slide; tiny decoration beside every sentence |
| Shape | Group, contain, connect or establish hierarchy | Arbitrary pills, bubbles or rounded cards around all content |
| Motion | Reveal dependencies, compare states, direct attention | A flourish with no explanatory purpose; evidence hidden in the static export |

Use image generation for conceptual art when available, with an honest description. Use deterministic
code/native objects for exact charts, mechanisms and diagrams. Preserve image credits, alt text,
permissions and sensitive-context constraints. Never invent a customer, quotation or project photo.

## Icons

Twelve MIT-licensed Feather SVGs are bundled in assets/icons/feather, with upstream commit and license.
For `columns`, use `"icon":"feather:clock"`, `feather:target`, `feather:users`, `feather:layers`,
`feather:activity`, `feather:inbox`, `feather:truck`, `feather:arrow-right`, `feather:check-circle`,
`feather:alert-triangle`, `feather:bar-chart-2` or `feather:help-circle`.
HTML embeds the SVG; PPTX embeds a high-resolution transparent PNG, independent of installed glyph
fonts. Legacy glyph identifiers still work. Keep one icon family per deck; choose only useful icons.

## Tables with richer semantics

Existing `table` slides accept ordinary strings and structured cells:

```json
{"kind":"status","status":"amber","label":"Supplier approval pending"}
{"kind":"harvey","score":3,"label":"Evidence strength"}
```

Status values are green, amber, red and unknown. A visible label accompanies the colour. Harvey scores
range from 0 to 4 and display a numeric fraction as well as a symbol. Define the assessment rubric and
source; these are ordinal judgements, not fabricated measured precision. RAG is categorical, not an
interpolated numerical scale. `base_cell:[row,column]` marks the base in a sensitivity table, zero-based; its row and column form
a subtle crosshair and the base cell is explicitly labelled.
Use native tables for editable outputs. Scenario matrices should label both varied inputs, units,
base case and assumptions. For unit economics, use rows for revenue, variable costs and contribution;
calculate totals in facts and distinguish fixed costs from per-unit costs. Do not add a slide type
when the existing table, waterfall or chart already expresses the relationship.

## Quantified processes and sensitivity

Process steps optionally accept `volume`, `duration`, `cost`, `conversion`, `defect_rate` and `drop_off`. Use facts tokens for
substantive numbers and label units and denominators. Show only metrics that exist; omit the rest.
Stage volumes and conversion denominators must reconcile. A bottleneck is not proven by a large box.

chart_images.py supports tornado (base; items with label, low and high outcome), and sensitivity
(rows, cols, values, base_cell, unit, fmt). A tornado varies one input at a time around the base;
it does not estimate causal contribution. Sensitivity matrices are conditional scenarios. Preserve
source data beside these raster charts; use native tables when editability matters more.

## Alignment, overlap and craft

Align meaningful groups on an explicit grid; use consistent gutters and baseline relationships.
Optical adjustments may improve large typography and irregular icons. Avoid claiming that every
object on the page should share an edge. Check actual rendered output at presentation size.

Intentional layering can add depth or connect an annotation to evidence. Check reading order,
contrast, clipping and the exported result. Never cover a label, source or data mark accidentally.
The PPTX linter accepts narrowly scoped `layout_review` annotations via `--spec`:

```json
{"alignment_groups":[{"shapes":["Metric A","Metric B"],"edge":"top","tolerance_pt":2}],
 "intentional_overlaps":[{"shapes":["Label","Annotation"],"reason":"Deliberate annotation crossing; inspected at full size"}]}
```

Names must match unique actual PowerPoint shape names. Supported edges: left, right, top, bottom,
center_x, center_y. Invalid names or reasons produce warnings and never grant an overlap exception.
Only that pair is exempted from text-overlap warnings; other checks remain. Geometric checks cannot
prove visual quality or detect every occlusion. HTML clipping and overflow still need rendered review.

## Evidence-aware visual details

Show uncertainty when it could change the interpretation; identify whether a range is a confidence
interval, prediction interval, observed spread or scenario range. They are not interchangeable.
Do not invent intervals or silently infer a distribution from endpoints. Keep material uncertainty
visible beside the finding. Offer exact lookup data or an explanatory alternative when the chart
would imply more precision than exists. The cited ONS guidance informs these choices, not a blanket
requirement to put error bars on every chart.

For accessibility, inspect reading order as well as appearance. A small icon with an adjacent label
may be decorative; an informative image needs a useful text alternative. Check keyboard navigation
for HTML and PowerPoint's Accessibility Checker/Reading Order pane in the target application when
available. A PNG inspection and contrast calculation do not certify screen-reader accessibility.
Use direct labels, text status and appropriate symbols so colour carries reinforcement, not the
only distinction. Primary-source links and the adoption boundary are in credits.md.

## Worked sample routes

- assets/examples/decision-tradeoffs.json: projected decision, genuine alternatives, RAG and Harvey
  assessments with a declared rubric, plus a quantified process.
- assets/examples/unit-economics.json: explicit contribution layers, native waterfall, missing LTV.
- assets/examples/cash-flow-teaching.json: question, reconciliation, worked example and retrieval task.
- assets/forward-tests/brand.json plus rebuild_brand.py: expressive conceptual typography and its
  native editable reconstruction. These are samples of judgement, not mandatory deck structures.
