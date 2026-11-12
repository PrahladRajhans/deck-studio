# Writing: headlines, body, numbers, notes, sources

## 1. Headlines by slide role, at the strength the evidence allows

| Slide role | Headline does this | Example |
|---|---|---|
| Recommendation | states the action and the reason | "Reduce changeover delays before adding production capacity" |
| Evidence | states what the evidence supports, no more | "Service costs explain most of the margin decline" |
| Teaching | states the concept or asks a purposeful question | "Why does a waterfall start at zero?" |
| Investigation | separates observation, interpretation and hypothesis | "Churn doubled in March; onboarding is the leading suspect" |
| Workshop | gives the room a task | "Rank these five risks by likelihood" |
| Transition | orients | "Where can we win?" |
| Closing | states the decision, action or takeaway | "Approve ₹1.8 crore by 20 May" |

Claim strength follows the evidence. Weak: "Operational excellence opportunities". Overstated: "The
campaign caused higher sales". Calibrated: "Sales rose during the campaign; the data does not
establish that the campaign caused it". Use the verbs the evidence earns: observed (rose, fell),
estimated (about, an estimated), forecast (is forecast to), hypothesis (may, the leading
explanation), recommendation (should, we propose). Assertion titles (Alley's assertion-evidence
pattern) suit substantive evidence slides; questions and labels are right when they serve a
teaching, transition or facilitation purpose on purpose.

## 1a. Document headlines (assertions)

- Test 1: can a reader answer "I disagree"? If the only response is "I see what this is about",
  it is a label. Rewrite.
- Test 2: hide the body. Does the headline still carry the point?
- A chart headline states what the chart means, not what it plots: "Online overtook stores in Q3",
  not "Revenue by channel".
- Specific nouns, real names, numbers, and verbs that say what happened (grew, fell, overtook,
  stopped), not "there is", "shows", "provides", "leverages".
- Put a count in a headline only when the number is the point; "three reasons" is not a claim.
  Any number in a headline must match the body (`spec_io.py` checks counts against the list).
- No topic label before a colon ("Market: ..."); the topic lives in the kicker.
- A headline stands alone: no "this", "as above", "here".
- Peer slides in one chapter share a grammatical form; different chapters may differ.
- Don't claim more than the body proves, especially about the reader's organisation.
- Exempt: cover, section dividers, agenda, sources, team and contact slides.
- If no assertion can be written, the slide is not ready (form the claim) or not needed (merge it).

## 2. Talk headlines (beats) and talk rules

- Mix forms by role (office-kit, from a speaker's own decks): a short label when a figure or
  screenshot is the star; a plain statement for a finding; an exclamation for a surprise; the
  audience's inner voice; a question for dividers; a cut-off line as a bridge. All-same forms read
  as machine-made; look for the same pattern three slides running.
- Choose the reveal by purpose: progressive (one step at a time, the answer last) when the room must
  be brought along; answer first when it is senior, time-poor or deciding, even live. An agenda
  belongs where it reduces uncertainty (workshops, teaching, long sessions); in a short persuasive
  talk, question dividers usually orient better. When a slide asks, the next slide answers.
- Dividers voice the audience's next question; one every 3-6 body slides; never the same question
  twice; the answer is complete before the next divider.
- Introduce a concept in three steps: what it is → what it improves (before/after) → a one-line
  analogy that the next slide builds on.
- One headline and 3-4 lines; one figure, large; one emphasis per slide.
- Don't add small text for what the screen already shows (captions under logos, notes under tables).
- Include at least one honest limitation slide; never only sell.
- Close with an action for the audience, not a summary or "thank you".
- Quote only real words, verbatim. No invented "what I typed".

## 3. Body text

- One slide, one message. Bullets only for truly parallel items; cause and sequence as sentences.
- Bullets in one list end the same way. Each bullet adds a new angle (cost, time, people, risk);
  delete any whose removal loses nothing.
- One concept, one term, throughout. Expand abbreviations at first use. No internal jargon in an
  external deck. For business audiences, gloss every domain term on first use (register = business);
  for specialists, keep the technical register.
- Name the human decision next to any automation: "AI drafts, the analyst approves".
- Evaluative words (enough, limited, significant) need evidence on the same slide.
- Later slides add points; they don't restate earlier ones.
- Sound like a person (human-voice.md): the specific fact instead of the stock word (leverage,
  unlock, seamless, robust), no "not just X but Y", no ", ensuring…" tails, no em dashes on slides,
  lists as long as the content (not always three).
- Phrasing diversity: don't end every slide with the same clause; don't fix a repeated phrase by
  swapping in a new stock phrase (that becomes the next tic). Vary sentence shape: sometimes state
  the number and stop.
- British English by default for this user (organise, colour, programme), unless told otherwise.
  Indian number formats (lakh, crore) are fine when the audience expects them; define once.

## 4. Numbers

- Every number from `facts`; derived numbers computed (sum, pct, cagr, wavg, cumsum, payback);
  `checks` for every claim the argument rests on.
- Decide once whether a figure is an increment or an absolute; never let another slide imply the
  other reading. When two slides show "the same" figure from different angles, make them equal or
  footnote why they differ.
- Success has a number: "≥ 95% on-time", "by 30 June", never "improved" or "no drop".
- Invented targets must add up: goal × people × periods fits the stated target; list the basis in
  `assumptions`.
- Units always: in the exhibit label, the axis or the header. Same decimals within a column.
- Proposed activity starts after today; retrospective and in-progress timelines are labelled as such.
  Monthly milestones cover every month or say why not.

## 5. Notes (write them first)

```
[~45 sec]                                   ← from deck `minutes`
<2-5 sentences the presenter says, point first, each figure with its source in the sentence>

--- For the presenter, not to be read out ---
Assumed (confirm before presenting): <anything not in the brief>
Sources: <real sources; or 'the brief'>
Likely questions: <Q> → <short answer> | ...
```

The slide carries the punch; the notes carry the depth. A presenter can give a 90-second version
from the slides and a 10-minute version from the notes. Objection answers: claim, proof, action.

## 6. Sources and footnotes

- Never invent a source, institute, quote, logo or person. Missing: "Source: to be added".
- For external data cite real bodies (a national statistics office, IMF, a named research firm);
  for a fictional or illustrative case, label figures illustrative on the slide.
- Cite consistently and sufficiently for the audience: publisher or body, title, date, and the
  locator (page, table) where a reader would check. Completeness beats variety; never thin out a
  citation to look less machine-made.
- Footnotes (method, assumptions) are numbered and tied to ¹ ² ³ markers; the source line is
  separate.
- Talk decks: sources in the notes, except claims about someone else's product when the deck will
  be published.

## 7. Turning a talk deck into a document (and back)

Talk → document: keep facts, numbers and history; rebuild answer-first; drop agenda and "what's
next" slides; move what only the notes said into the body (limitations included); put speaker and
company introductions in an appendix; recheck numbers flagged "verify before the talk".
Document → talk: keep the storyline; split dense slides into beats; move detail and sources to the
notes; replace the agenda with question dividers; end with an action.
