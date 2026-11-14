# Creative direction: make this deck worth looking at

Read for every new deck, substantial redesign, or request to make slides less generic. Use the
small creative brief and concept test first; consult the techniques only when they help. This is
a set of prompts for judgement, not another checklist of objects to add.

## Contents

1. Working stance
2. Find a concept in the material
3. Explore different ideas, not different skins
4. Make the relationship visible
5. Shape the sequence
6. Write with a person in mind
7. Escape the catalogue when useful
8. Review for usefulness and distinctiveness
9. Worked example and evaluation

## 1. Working stance

Make a presentation someone could recognise as belonging to this subject and presenter. Start
with what is interesting, difficult, surprising or consequential in the material. Then make it
clear. A template is a construction aid; it is not the idea.

Be ambitious about expression and conservative about evidence. You may invent a composition,
a way to reveal a process, a visual analogy or a headline. You may not invent results, customer
stories, quotations or source material. Label conceptual illustrations and fictional examples.
A fresh design must leave units, denominators, uncertainty and causality intact.

Prefer a fitting, memorable idea to a procession of competent cards. An unusually clear table
can be the right creative answer. A sober technical deck can be inventive through explanatory
sequencing and annotation. Creativity does not require loud colours, jokes, metaphors or motion.

## 2. Find a concept in the material

Keep a short `creative_brief` inside the existing `brief` object. Infer it from the material;
do not make the user complete another questionnaire.

| Prompt | What to record |
|---|---|
| Audience change | What should the audience understand, notice, feel or decide afterwards? |
| Central tension | What is in conflict, hidden, misunderstood or unexpectedly connected? |
| Distinctive raw material | A real detail, source figure, process, product, document, place or phrase |
| Creative latitude | What may change? What must the brand, setting or final format preserve? |
| Takeaway | The idea the audience should be able to explain afterwards |

Write a concept in a sentence linking meaning to form. Weak: "a bold modern deck". More useful:
"Make the handoff gap visible, so the reader sees why working faster upstream may grow the queue."
That suggests a spatial gap, tracked work items, evidence about the queue and a testable action.

Ask what would be lost if you used a normal title-and-cards slide. If nothing would be lost, use
it confidently. If the relationship would disappear, give that relationship the composition.

## 3. Explore different ideas, not different skins

When direction is open, consider a small number of genuinely different concepts, normally two or
three. Spend the effort on the most consequential slides; do not prototype an entire deck in every
style. For a routine update, reusing the established identity may be the best decision.

Candidates must differ in how the audience understands the material: organising idea, composition,
visual vocabulary or narrative approach. Changing a navy grid to a coral grid is a palette test.
`preview_directions.py` compares themes; it does not generate creative concepts.

For the same queue-review brief, credible alternatives could be:

| Concept | Opener | Evidence slide | Action slide |
|---|---|---|---|
| The gap between teams | A sentence separated by a physical gap | Work items accumulate at the actual handoff | Place the proposed handoff owner at that boundary |
| Follow one order | A real supplied order record, enlarged | Trace that record through time alongside the full dataset | Mark the intervention and what would be measured |
| Busy versus finished | Parallel views of activity and completed work | Common units and period expose the difference | Compare capacity expansion with a handoff trial |

The second approach requires a real supplied record. Without one, ask, choose another approach,
or use an explicitly authorised fictional demonstration. Do not manufacture documentary detail.

Test candidates with the same real content: a representative evidence slide, an explanation or
comparison, and an opener when relevant. Pick the strongest fit for understanding, distinctiveness,
readability and destination fidelity. A beautiful cover that cannot support evidence loses.
Show alternatives when requested or when the visual choice is consequential. Otherwise recommend
one and show the actual draft; keep exploration brief and avoid repeated approval interruptions.

## 4. Make the relationship visible

Use these as starting moves, not layout quotas. Borrow a way of organising information, not the
surface styling of an unrelated brand.

| What the material needs | Possible creative move | Preserve |
|---|---|---|
| A bottleneck or missing connection | Show the gap in the actual process; accumulate work at that location | Counts and sequence; no invented causal certainty |
| A mechanism or dependency | Build a causal or dependency diagram in explanatory steps | Direction, boundaries, exceptions; no analogy replacing the real mechanism |
| A hidden detail | Enlarge and annotate part of a real document, image or interface | Context and source; disclose crops; retain the whole where needed |
| Scale that is hard to grasp | Use comparable units, small multiples or an accurately counted unit array | A common scale and denominator; use a table when exact lookup matters |
| Two alternatives | Use the same frame and criteria so differences become apparent | Equal time horizon, units and scrutiny |
| A surprising finding | Give the finding a quiet, dominant moment, then show its proof | Claim strength, uncertainty and supporting exhibit |
| A campaign or product pitch | Let actual creative executions, product views or demonstrations lead | Real assets or clearly labelled mockups |
| A plan with dependencies | Place owners and decisions at the dependencies, rather than a decorative arrow | Actual prerequisites, dates and uncertainty |
| A complex comparison | Establish a repeated visual frame, then change only the variable of interest | Comparability; useful repetition is a strength |
| A strong sentence | Let typography and whitespace carry it | Legibility and meaning; do not stretch type to fill space |

Some useful provocations:
- What is the one thing I can show instead of describing?
- What could the audience infer from the picture before reading the caption?
- Is the evidence itself visually interesting enough to lead?
- Could a spatial relationship explain this faster than a container around each paragraph?
- What would this slide look like without any cards?
- Would a quieter composition make the surprising fact more noticeable?
- What can be removed while preserving the argument?

Use analogies only when they improve understanding; state where they stop applying. Never imply
measurement through the size, position or area of decorative objects. Technical diagrams must stay
technically correct, even when a more dramatic picture would be easier to draw.

## 5. Shape the sequence

Give each slide a job: orient, reveal, prove, explain, compare, invite participation or secure an
action. Link adjacent slides through the audience's next question. A recurring device can help:
follow the same work item, progressively reveal a system, reuse an annotated source, or hold a
comparison frame steady. Do not force a motif across unrelated evidence.

Plan rhythm by meaning. A short finding can create space before a dense exhibit; the next slide
can unpack it. Comparable exhibits may repeat the same layout. Do not alternate dark/light,
large/small or image/chart merely to create variation. A reading deck still needs self-contained
reasoning; a live talk can reveal and pause.

The opening should establish a useful question, consequence, demonstration or specific situation.
Avoid adding a generic industry preamble because the skeleton contains one. The close should make
the implication or next action clear; do not manufacture an ask in a purely explanatory session.

## 6. Write with a person in mind

Use human-voice.md to originate the writing, not only clean it up. Start with what this presenter
would actually say about this evidence to this audience. Write pivotal titles in a couple of
registers when helpful, then choose the one that is direct, credible and recognisably theirs.

A restrained line can be more distinctive than a slogan. A question can open an investigation.
A short fragment can work beside unmistakable visual evidence. Formal technical language is
welcome when the audience uses it. Keep necessary qualifiers and stable terminology.

Do not invent intimacy, autobiographical detail, customer quotes, slang or irregular rhythm.
Do not add numbers to make an otherwise generic sentence seem specific. Voice is a point of view
and a relationship with the audience, not a list of banned words.

## 7. Escape the catalogue when useful

The 44 types are a toolbox, not a ceiling or a mandatory menu. Choose a standard type when it
serves the idea. Use `custom` when a different composition would improve explanation, emphasis,
identity or the experience of reading the deck; you need not prove every standard type failed.
Keep it reproducible in the spec, with the deck tokens and an intentional reading order.

`custom` normally uses standard chrome. Set `full_bleed: true` for a full-stage composition when
the concept needs it, such as a documentary opener or a spatial explanation. The HTML renderer
retains notes and supplied source lines, and adds provenance labels for illustrative content.
Keep meaningful text editable and readable; include sources rather than hiding them behind art.

Before seeking approval for a custom design targeting editable PowerPoint, test its hardest native
relationship with real content. Choose reproducible text/shape/image primitives and retain the
reconstruction script. If the chosen treatment cannot survive, adapt it before approval or explain
the material compromise. An example of the full path is assets/forward-tests/rebuild_brand.py:
it reconstructs that specific four-slide brand concept as native editable text and shapes. This
is an example recipe, not a general HTML converter.

A custom HTML composition needs deliberate reconstruction in native PowerPoint after approval.
Record a feasible `pptx_note` and preserve the reconstruction script next to the spec. Choose
compositions the target can reproduce with editable text, shapes, images and supported charts.
Disclose any controlled adaptation. Do not let a placeholder become the delivered PowerPoint.

## 8. Review for usefulness and distinctiveness

Before approval, look at the real draft and ask:

- Could these slides belong to a different company or topic after replacing the nouns? If yes,
  find the missing subject-specific evidence, composition or point of view. A reusable status
  template is a valid exception when continuity is the purpose.
- What explains the concept on a substantive slide, beyond its palette and cover?
- Does the focal point match the important idea? Does the audience know where to look next?
- Is the relationship visible, or has prose merely been redistributed into shapes?
- Does the sequence earn its memorable moment, and does the moment improve understanding?
- Does the language sound like a plausible presenter, with evidence and caveats intact?
- Can the approved design survive its destination and remain usable?

If a substantive slide fails, try a different organising idea or composition before polishing its
colours. Keep the clearer option even if it is more familiar. Fix evidenced weaknesses; never
manufacture defects to satisfy a review quota. Do not use a novelty score that can outweigh truth.

## 9. Worked example and evaluation

`assets/creative-examples/queue-review.json` is an authorised fictional HTML demonstration. It
uses the handoff gap as its organising idea, a counted evidence display and a restrained next-step
comparison. Its brief records alternative concepts and the selection rationale. It is an example
of the method, not a visual style to copy into every deck. `custom` slides require a hand-built
PPTX route; the smoke workflow validates and renders this example as HTML only.

```bash
python3 scripts/build_html.py assets/creative-examples/queue-review.json --strict -o out/queue.html
python3 scripts/render_html.py out/queue.html out/queue-render
```

Evaluate transfer with tests/benchmark-briefs.md. Compare concept, explanatory value, composition,
voice, evidence fidelity and revision behavior separately. Retain the actual outputs and findings.
A worked example and passing renderer tests establish feasibility, not proof that every future
Claude deck will be creative. Judge the outputs on contrasting briefs and revise from failures.
