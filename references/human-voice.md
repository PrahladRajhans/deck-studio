# Human voice: slides that sound like a person wrote them

Generic phrasing can weaken clarity and credibility. Review wording for specificity, audience
fit and the presenter's voice. This file is
the single home for voice rules. It adapts the BeHuman and Unslop skills (both built on Wikipedia's
"Signs of AI writing" field guide) to slides, where text is short, fragmentary and spoken over.

These are density signals, not a ban on words, and a check that fires is not evidence of AI
authorship. One "robust" in a statistics appendix is fine. Five stock words, three "-ing" tails and
repeated stock structures are reasons to review the writing, not a diagnosis of authorship. Rewrite only when the new wording is clearer, more
specific, better evidenced or a better fit for the room.

Avoiding stock phrases is half the job. The other half is sounding like this presenter.

## 1. The voice brief (fill it in Stage 1; infer it when the material makes it clear)

| Field | Example |
|---|---|
| Presenter stance | analyst, teacher, founder, practitioner, candidate |
| Formality | conversational, professional, formal |
| Relationship to the audience | peer, adviser, examiner, customer, student |
| Claim strength | observed, estimated, proposed, uncertain (writing.md §1) |
| Vocabulary | the room's terms and the technical words that must stay |
| Samples | a few headlines or notes the presenter actually wrote, when available |

Match the presenter's register and relationship with the audience. Prefer concrete nouns,
accountable actors ("the analyst approves", not "approval is obtained") and claims bounded by the
evidence. Never manufacture anecdotes, quotations, emotional detail, slang or irregular rhythm to
simulate a person.

## 1a. How to work

1. **Write with the rules on.** Draft headlines and notes without the patterns below; don't plan
   to clean up later.
2. **Say it out loud as the presenter, to this room.** If you would not say the sentence to that
   partner, judge or interviewer across a table, rewrite it until you would.
3. **Swap every abstract claim for the fact it was hiding**, when the evidence has it. "Robust
   growth" becomes "revenue up 38% in two quarters" only if 38% is in the facts. Specificity must
   come from evidence: without it, narrow or qualify the claim ("revenue grew in both quarters"),
   never invent precision. If the line has no job at all, cut it.
4. **Run the checks.** `build_html.py` and `build_deck.py` print `style` prompts; `lint_deck.py`
   reports `style_review` (warn) and `style_rhythm` (info) on any .pptx. Technical uses are
   already skipped (robust standard errors, financial leverage, landscape orientation). For each
   remaining prompt, either rewrite or keep it on purpose by adding the word or phrase to
   `voice_ok` (deck or slide level) when a short shared rationale helps. Do not create a separate compliance record for each legitimate word.
5. **Read the headline track for clarity** (`--outline`): vary form when it helps; preserve
   repetition when it supports comparison, learning or the presenter's authentic register.

Protect useful consistency: one concept keeps one term (writing.md §3), and parallel comparison
labels stay parallel. Vary sentence shape, not terminology.

Slides are allowed to be fragments. Labels, kickers, chart headers and talk punchlines ("Then the
rain came.") can be two words. The rule against tiny sentences is for prose, not slide furniture.

## 1b. Originate a voice; do not only remove phrases

1. Start with the evidence and the presenter's actual judgement: what matters, what is difficult,
   what they recommend and what they are unsure about. If samples exist, preserve their useful
   vocabulary, cadence, understatement, humour and degree of formality. Do not homogenise them.
2. Draft a plain spoken sentence for each pivotal idea. Then edit it for its job: a self-contained
   document headline, a short talk beat, an analytical caption or a line in the speaker's notes.
   The same sentence need not do all four jobs.
3. For an opening, turning point or close that sounds generic, try a couple of genuinely different
   phrasings: direct, understated, observational, questioning or vivid. Choose the one the evidence
   and presenter can carry. Do not generate variants for every label or force a slogan.
4. Keep the detail that makes the sentence belong here: the real constraint, trade-off, object,
   disagreement or observation. Specificity can be qualitative. Missing numerical evidence is a
   reason to qualify the sentence, not to add a plausible-looking percentage.
5. Read a short run of slides and their notes together. It should sound like one person explaining
   a thought, not a sequence of polished captions. Connect ideas through meaning; use deliberate
   repetition when it helps. Keep necessary caveats, quoted wording and technical terms intact.

Examples below assume the stated material was actually supplied. They demonstrate choices of
voice, not claims to reuse:

| Material | Generic line | A fitting alternative |
|---|---|---|
| Orders wait between picking and packing; no capacity study | Unlock operational excellence | Clear the handoff before buying more capacity |
| A technical audience must locate a queue in a visible diagram | Optimising workflow efficiency | The queue forms here |
| A board pre-read needs that finding without narration | Optimising workflow efficiency | Orders wait at the picking-to-packing handoff |
| A proposed experiment has no measured outcome yet | Our solution will transform delivery | Test a named handoff owner; measure the queue before expanding |
| A presenter describes a real supplied reversal | A journey of resilience and innovation | We changed the plan when the interviews contradicted it |

Humanised does not mean casual, chatty or emotional. It means credible authorship: a point of view,
a clear relationship with the audience, natural syntax and details grounded in the work. Never
claim to defeat AI detectors, add fake imperfections, or substitute a performance of humanity for
honest content.

## 2. Words to review in decorative use

Use the plain word or the fact instead. Quotes, proper names and literal technical uses are exempt.

| Avoid (decorative use) | Write instead |
|---|---|
| leverage, harness, unlock, unleash, empower | use; or the action itself ("cuts the queue from 9 days to 2") |
| robust, seamless, best-in-class, world-class, cutting-edge, state-of-the-art | what it survives, how fast, compared with what |
| crucial, pivotal, vital, key (as filler) | what breaks without it |
| transformative, game-changing, revolutionise, next-level, supercharge | what changed and by how much |
| holistic, comprehensive, multifaceted, end-to-end | list what it covers |
| foster, drive (as filler), streamline, elevate, enhance | the real verb: hire, fund, remove, merge, train |
| landscape, realm, journey, ecosystem (metaphorical) | the market, the process, the partners, by name |
| synergies | the specific saving or revenue, with its number |
| delve, deep dive, dive into | look at; or just show it |
| stands as, serves as, plays a key role | is, has, does |
| moreover, furthermore, additionally, ultimately | nothing; start the next point |
| in today's fast-paced world, in the digital age | delete |
| key takeaways, actionable insights | the takeaway itself, as the title |

Customer journey, user journey and buyer journey are real terms and are not flagged.

## 3. Sentence patterns to review in context

- **"Not just X, it's Y" / "It's not about X. It's about Y."** Fake reveal. State Y with its proof.
- **"No X. No Y. Just Z."** Slogan rhythm. Say what is actually true.
- **The "-ing" tail**: ", ensuring...", ", highlighting...", ", driving...", ", unlocking...". It
  welds an unproven conclusion onto a fact. Cut it, or give the conclusion its own line and evidence.
- **Vague sources**: "experts say", "studies show", "industry reports suggest". Name the source and
  year, or drop the claim (truth rule 1 already requires this).
- **False ranges**: "from startups to Fortune 500s". Name who you mean.
- **Puffery**: "a testament to", "a watershed moment", "sets the stage for". Show the evidence.
- **Hype close**: "The future is bright", "Exciting times ahead", "Let's build the future together".
  Close with the ask: what, who, by when, the number it moves.

## 4. Slide-level tells (the ones decks add on top of prose)

- **Rhetorical devices used by default.** "No pressure. No flow." can be a deliberate line in an
  engineering talk; the same shape on every slide is a tic. Keep intentional ones (record them in
  `voice_ok`), cut reflexive ones.
- **Every list has three items.** Three cards, three pillars, three bullets, three steps on every
  slide. Let the content set the count; two and five are normal. (Checked deck-wide.)
- **Every title has the same shape without a reason**: review the pattern rather than varying
  it automatically. Parallel comparisons and technical teaching may benefit from repeated forms.
- **Repeated Noun: Clause titles.** A sequence such as "Margin: …", "Risk: …", "Growth: …"
  often adds a generic label before the actual thought. Put the subject into the sentence and use
  the kicker for navigation. Keep a colon when it helps, and retain intentional parallel labels.
- **Strawman options.** A scorecard with rejected options all red and the preferred option all green
  can manufacture an easy answer. Give each genuinely viable contender its real strengths and
  disadvantages; do not invent a token advantage. Explain a truly dominated option rather than
  forcing symmetry. See domain-packs.md for fair criteria and uncertainty.
- **Gerund bullets**: "Driving growth / Enhancing efficiency / Ensuring quality". Write what
  happens: "Two new campuses by June".
- **Bold-label bullets that restate themselves**: "**Speed:** we are fast". Use the fact, or make it
  a two-column table if the labels really are categories.
- **Symmetric everything**: every card the same length, before/after mirror images, risks all
  "Medium". Real material is uneven; let it be.
- **Same closing clause on every slide** (writing.md §3: phrasing diversity).
- **Generic sections**: "Challenges and opportunities", "Looking ahead", "Key takeaways",
  "Conclusion" slides that merely repeat earlier wording. A useful synthesis or teaching takeaway
  is welcome. Close on the consequence appropriate to the audience.
- **Emoji icons and decorative symbols** standing in for meaning. Use consistent bundled icons for useful navigation or concepts, and labelled
  glyphs for status (✓ done, ▲ up); see visual-components.md. Avoid decoration without a purpose.
- **Em dashes.** None on slides; use a comma, a colon or a full stop. (User preference too.)
- **Too-precise invented numbers** ("83.7% of users love it") with no source. Truth rule 1.
- **Chatbot residue**: "Certainly", "Here's", "I hope this helps", "[Insert name]".

## 5. What a human puts in

Removing tells is half the job; sterile text is just as obvious.

- **Specifics nobody else could write**: the store in Pune, the 14th interview, the week the app
  went down, the actual quote from the actual customer (verbatim, sourced).
- **A point of view.** "We recommend B, and it costs us a quarter of margin" beats a neutral table.
  Commit where the evidence lets you; hedge once, honestly, where it doesn't.
- **First person where it fits**: personal stories, interviews and talks use "I" and "we".
- **One honest limitation** (writing.md §2). It reads as confidence, not weakness.
- **The room's words**: their units (₹ crore, lakh), their product names, their metrics.
- **Intentional rhythm**: let the subject determine where to pause, explain or compare. A dense
  exhibit can need a quiet follow-up; a run of comparable exhibits can need stable repetition.
- **Notes in spoken English**: contractions, short sentences, the way the presenter actually talks
  ("Here's the surprise: the rain helped us."). The notes are a script, not a report.

## 6. Do not overcorrect

- No fake slang, forced typos or manufactured casualness. A board deck stays formal; formal is not
  the same as machine-like.
- Never change a fact, drop a caveat or soften a number to "sound natural".
- Keep the room's real jargon (EBITDA, CAC, MECE in a consulting room). The ban is on decorative
  words, not on precise ones.
- Quotes stay verbatim even if they contain flagged words.

## 7. Rewrite drills (slides)

These are illustrative editorial alternatives. Never reuse their numbers, names or outcomes
unless supplied evidence supports them. Section 1b shows how to be specific without adding figures.

| Before | After |
|---|---|
| Leveraging AI to unlock operational efficiencies | AI drafts the claim report; the analyst approves it in 10 minutes, not 2 hours |
| Our robust, scalable platform empowers seamless collaboration | 40 teams share one plan; nobody re-types a number |
| It's not just an app, it's a movement | 9,400 students open it every week; 60% came from a friend's link |
| Key Takeaways | Price, not volume, rescued the year (the takeaway is the title) |
| Driving growth / Enhancing efficiency / Ensuring quality | Two new campuses by June · Ticket backlog under 24 hours · First-reply quality audited weekly |
| The future looks bright: let's build it together! | Approve ₹1.8 crore and three creators by 20 May |
| Experts agree the market is booming | The market grew 22% in 2025 (named source, year); we grew 38% (both figures from the evidence; if they aren't, say "the market is growing; our share rose", not a made-up number) |

## 8. Where this runs in the flow

Stage 1 establishes the voice; creative-direction.md links it to the concept; Stage 4 originates
the writing and edits it in context; Gate 4 includes "every style prompt fixed or kept on
purpose"; the semantic review (qa.md §3) is separate and checks what the words claim; the
fresh-eye review (qa.md §6) asks the reviewer to flag phrasing that feels AI-written. For long
prose that travels with a deck (handouts, notes pages, an email to the client), the behuman or
unslop skill, when installed, can sweep the text with the same rules.

## Typography in context

Prefer sentence case for authored titles and headers, except proper nouns, acronyms and supplied brand
forms. Use en dashes for ranges such as FY24–FY26 and 10–15 minutes. Preserve exact quotations and code.
These are editorial defaults, not mechanical rewrites of technical language.
