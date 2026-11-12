# Human voice: slides that sound like a person wrote them

A deck that reads as machine-written loses the room before the argument starts: judges, partners
and interviewers now spot the pattern in seconds and discount everything after it. This file is
the single home for voice rules. It adapts the BeHuman and Unslop skills (both built on Wikipedia's
"Signs of AI writing" field guide) to slides, where text is short, fragmentary and spoken over.

These are density signals, not a ban on words. One "robust" in a statistics appendix is fine. Five
stock words, three "-ing" tails and every list in threes on one slide is a signature.

## 1. How to work

1. **Write with the rules on.** Draft headlines and notes without the patterns below; don't plan
   to clean up later.
2. **Say it out loud as the presenter, to this room.** If you would not say the sentence to that
   partner, judge or interviewer across a table, rewrite it until you would.
3. **Swap every abstract claim for the fact it was hiding.** "Robust growth" becomes "revenue up
   38% in two quarters". If there is no fact, the line had no job: cut it.
4. **Run the checks.** `build_html.py` and `build_deck.py` print `voice` lines; `lint_deck.py`
   reports `ai_voice` (warn) and `ai_rhythm` (info) on any .pptx. Fix each hit or keep it on
   purpose (a literal "landscape" in an architecture deck); never leave one unseen.
5. **Read the headline track for rhythm** (`--outline`): mixed lengths, mixed shapes, no formula.

Slides are allowed to be fragments. Labels, kickers, chart headers and talk punchlines ("Then the
rain came.") can be two words. The rule against tiny sentences is for prose, not slide furniture.

## 2. Words that give it away

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

## 3. Sentence shapes that give it away

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

- **Every list has three items.** Three cards, three pillars, three bullets, three steps on every
  slide. Let the content set the count; two and five are normal. (Checked deck-wide.)
- **Every title has the same shape**: all "Topic: phrase", all ten words, all starting with "Our"
  or "Driving". Mix forms (writing.md §1-2). (Checked deck-wide.)
- **Gerund bullets**: "Driving growth / Enhancing efficiency / Ensuring quality". Write what
  happens: "Two new campuses by June".
- **Bold-label bullets that restate themselves**: "**Speed:** we are fast". Use the fact, or make it
  a two-column table if the labels really are categories.
- **Symmetric everything**: every card the same length, before/after mirror images, risks all
  "Medium". Real material is uneven; let it be.
- **Same closing clause on every slide** (writing.md §3: phrasing diversity).
- **Generic sections**: "Challenges and opportunities", "Looking ahead", "Key takeaways",
  "Conclusion" slides that restate the deck. A document ends on the decision; a talk on the action.
- **Emoji icons and decorative symbols** standing in for meaning. Use glyph badges only where they
  carry a status (✓ done, ▲ up).
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
- **Uneven rhythm**: a long headline, then a four-word one. A dense exhibit, then a single number.
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

| Before | After |
|---|---|
| Leveraging AI to unlock operational efficiencies | AI drafts the claim report; the analyst approves it in 10 minutes, not 2 hours |
| Our robust, scalable platform empowers seamless collaboration | 40 teams share one plan; nobody re-types a number |
| It's not just an app, it's a movement | 9,400 students open it every week; 60% came from a friend's link |
| Key Takeaways | Price, not volume, rescued the year (the takeaway is the title) |
| Driving growth / Enhancing efficiency / Ensuring quality | Two new campuses by June · Ticket backlog under 24 hours · First-reply quality audited weekly |
| The future looks bright: let's build it together! | Approve ₹1.8 crore and three creators by 20 May |
| Experts agree the market is booming | The market grew 22% in 2025 (named source, year); we grew 38% |

## 8. Where this runs in the flow

Stage 4 (Draft) writes with these rules; Gate 4 includes "no voice hits left unexamined"; the
fresh-eye review (qa.md §5) asks the reviewer to flag phrasing that feels AI-written. For long
prose that travels with a deck (handouts, notes pages, an email to the client), the behuman or
unslop skill, when installed, can sweep the text with the same rules.
