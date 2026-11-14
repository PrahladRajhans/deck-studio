"""Shared authoring schema, with no rendering dependencies."""

from _common import DIRECTIONS

SCHEMA = """deck-level: assurance (brief|standard|high; default standard), title, direction (DIRS), theme {token overrides}, mode (document|talk),
  frame (classic|clean|editorial|rail; default from direction), footer, sources [..], minutes (adds
  [~N sec] timing to notes), facts {name: number|[numbers]|"=expr"}, checks ["expr", ..],
  fact_meta {name: {kind, evidence}}, evidence {id: {source, locator, status}},
  illustrative_authorized (true only with user agreement),
  title_rule (bool), number_kickers (bool; default on in document mode, off in talk mode)
every light slide: type, id (for exec-summary refs), kicker, title (an assertion; ^^word^^ = accent),
  letter ("A" -> governing-thought prefix), subtitle, so_what, source, exhibit (label + unit),
  tag ("Illustrative" | "Non-exhaustive"), footnotes [..] (mark claims with ¹ ² ³), frame,
  seconds (positive rehearsal timing override), layout_review (see visual-components.md),
  notes {say, assumptions[], sources[], qa[]}, data_status (sourced|illustrative), evidence_ids[],
  claims [{text, kind, evidence_ids[], status (reviewed), basis}], non_factual_reason,
  number_exceptions [{text, reason}] (administrative text only; see references/spec.md)
OPENERS AND STRUCTURE
  cover        eyebrow, title, subtitle, meta[], figure {value,label}, style (field|gradient|split|minimal), image
  agenda       title, items[], active (1-based chapter to light up)          [talk mode: only if it orients]
  divider      number, title (talk mode: the audience's next question), subtitle
  exec_summary rows [{claim, detail, ref (slide id), pages, highlight}]
  framework    kicker, title (the thesis), points [{heading, body}]          dark rail + numbered points
  statement    claim, points[]                     quote      quote, attribution
  question     title, options[], prompt, dark      (quiz / poll / think-about-it)
  closing      title, ask, figure {value,label}, lines[]
NUMBERS
  big_number   value, label, context, points[]     data_contrast items[2] {label,value,detail}, versus, highlight
  kpi          items [{value, label, delta, good, detail}], highlight
  chart        chart {kind: column|bar|line|stacked|stacked_bar|doughnut|pie|area|waterfall|range|scatter,
               categories[], series [{name, values}], highlight, number_format, min, max, show_values,
               smooth (line), target + target_label (line), alt}
               waterfall: values[] (start total, deltas), totals [indexes]
               range: low[], high[], label_format  (football field / valuation / scenario ranges)
               scatter: points [{label, x, y}], x_title, y_title, highlight
               side {heading, points[]}
  table        columns[], rows[[..]], widths[], highlight_row, total_row, base_cell [row,column], note, side{}
               cells may be {kind:status, status:green|amber|red|unknown, label} or {kind:harvey, score:0..4, label}
  options      criteria [{name, weight}], options [{name, scores[]}], recommended, scale
DIAGRAMS
  process      steps [{heading, label, body, volume, duration, cost, conversion}], highlight
  cycle        steps [{heading, body}], center, highlight, side{}
  funnel       stages [{label, value, note, conversion}], highlight
  pyramid      levels [{label, detail}] (top -> base), highlight
  hub          center, spokes [{heading, body}], highlight
  issue_tree   root, branches [{label, leaves[]}], highlight
  matrix       x_axis{label}, y_axis{label}, quadrants[4], items [{label, x, y, highlight}], highlight_quadrant
  swot         strengths[], weaknesses[], opportunities[], threats[], highlight
  venn         sets [{label, detail}] (2-3), overlap, side{}
  journey      stages [{name, feeling -1..1, doing, thinking, pain, opportunity}], rows[], row_labels{}
COMPARE AND PLAN
  compare      columns [{heading, points[]}], highlight
  columns      columns [{icon, heading, points[] | body}], highlight   icons: feather:name (bundled) or legacy GLYPHS
  cards        items [{heading, body}], numbered, highlight
  before_after before {label, heading, points[], image}, after {...}
  pricing      tiers [{name, price, period, features[]}], recommended, recommended_label
  timeline     periods[], rows [{label, owner, bars [{start, end, label, milestone, highlight}]}]
  milestones   milestones [{date, label, detail, state: done|now|next}]
  roadmap      lanes [{heading, items [{heading, body}]}], highlight
  actions      rows [{action, owner, date, status: done|on_track|at_risk|late|not_started}]
  risks        rows [{risk, likelihood H|M|L, impact H|M|L, mitigation, owner}]
  ask          ask, why[], cost[], figure {value,label}, owner
PEOPLE, PROOF, PICTURES
  team         people [{name, role, line, photo}]
  faq          items [{q, a, proof}]               (objections: claim, proof, action)
  image        path, alt, side, image_width, heading, points[]
  image_full   path, alt, kicker, title, subtitle, credit   (full-bleed story card)
  gallery      images [{path, caption, alt}]
  code         code, points[], side_heading
  bullets      items[] (max 6), side{}             (last resort)
  custom       html (draft body), full_bleed (optional full-stage HTML composition), pptx_note
               (tailored explanation or expression; rebuild with native objects in PPTX)
  references   items[]
tokens: any string may contain {=expr|fmt} (e.g. {=rev[2]|.1f}, {=pct(rev[0],rev[2])|+.0f}%);
        a value of "=expr" becomes a number or list (e.g. "values": "=rev").
functions: sum min max len abs round avg wavg approx pct cagr cumsum share vadd vsub first_at_least
           logistic(n, cap, mid, k) rng(n) all any list
markup in text: **bold**, ^^accent^^""".replace("DIRS", ", ".join(DIRECTIONS))

