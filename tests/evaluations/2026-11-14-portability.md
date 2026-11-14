# Shared-host revision, 14 November 2026

## Scope and preservation

One upload package, one method, two thin host adapters. Shared creativity, human voice, evidence,
charts, visual composition, examples and builder semantics remain intact. Existing commands and
specification fields are unchanged. New activation consent precedes the existing draft-approval
workflow; explicit selection permits immediate intake. OpenAI metadata allows discovery rather
than enforcing a consent popup. Neither importer nor an LLM can be guaranteed by packaging checks.

## Activation cases to evaluate after host/model changes

These are expected behaviors for later in-application evaluation, not recorded execution results.

| Request or context | Expected behavior |
|---|---|
| Prepare a PowerPoint about our Q3 results | Offer Deck Studio and wait; do not begin its planning |
| Prepare a deck / make slides / improve this presentation | Offer when no choice is already known |
| Use Deck Studio to make a teaching presentation | Proceed to intake without repeating consent |
| Explicit selection through the host's skill picker | Treat deliberate selection as consent |
| Make slides without Deck Studio | Do not impose this skill's planning, HTML or approval rules |
| Revise slide 3 of a deck already using Deck Studio | Retain the choice; preserve local-edit scope |
| New unrelated deck, no continuing preference | Offer a fresh choice |
| Skip the draft and give me a PowerPoint | Ask skill choice first; if selected, honour draft skip |
| What is a PowerPoint file? | Answer normally; a definition alone is not a deck-production task |
| Unattended request with no choice | Pause for selection; do not assume consent |
| Opt out halfway through a deck | Respect the changed choice; do not keep imposing this method |

## Runtime and future maintenance

Resolve the actual skill root, use only exposed tools, preflight required features and preserve
the same bounded failure outcomes. If HTML cannot preview inline, provide its download plus actual
renders where available. Missing renderers remain declared limits. Never report a draft screenshot
as a final PowerPoint render. Keep Claude Slides conditional and external connectors capability-based.
Recheck imports, package contents, links, builders and representative creative/evidence briefs after
material updates. Evaluate triggering, opt-out, previews and delivery in each host when appropriate;
do not create model-name branches or claim perpetual future compatibility.

## Verification boundary

The user reports successful Claude use of the previous release and explicitly waived testing this
revision inside ChatGPT and Claude. Local structural checks and existing full GitHub regression CI
are the publication checks. No prompt behavior or native installer result is certified here.

## Primary sources consulted

- [ChatGPT Skills](https://help.openai.com/en/articles/20001066-skills-in-chatgpt): native upload,
  eligible workspace access and product/admin limitations.
- [OpenAI skill authoring](https://learn.chatgpt.com/docs/build-skills): description-based discovery,
  explicit selection, optional OpenAI metadata and product-specific invocation controls.
- [Claude skill use](https://support.claude.com/en/articles/12512180-use-skills-in-claude): upload,
  enable/disable and automatic selection.
- [Claude custom skills](https://support.claude.com/en/articles/12512198-how-to-create-custom-skills):
  matching ZIP root, progressive loading and the documented 200-character description limit.
- [Agent Skills specification](https://agentskills.io/specification): shared folder format,
  metadata and relative references. The broader spec permits a longer description; this package
  uses the stricter host guidance without deleting the detailed workflow or use-case references.

These documents describe current behavior; recheck them when changing installation guidance.
