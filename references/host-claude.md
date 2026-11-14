# Claude host adapter

Read after the user selects Deck Studio. Preserve the existing HTML-first creative workflow,
presenter register, evidence checks, draft approval and editable-production rules in SKILL.md.

- Resolve references and scripts from the uploaded skill's actual location. Do not hardcode mount
  paths, model names or a particular Claude release's tools.
- Discover available code execution, artifact types, image tools and connectors. Check required
  features with the production guidance in workflow.md. Do not assume Playwright, Chromium,
  fonts, native libraries or LibreOffice are installed merely because the host is Claude.
- Show the HTML draft in the supported preview/artifact mechanism. If inline preview is absent,
  deliver the HTML file with rendered slide images/contact sheet for review. Preserve the existing
  browser controls and draft approval; report unavailable rendering rather than claiming inspection.
- Keep route A only when the session actually exposes a Slides artifact type and the destination
  fits the user's request. For a requested editable PowerPoint, use route B or an agreed available
  destination. An HTML artifact is not proof that a Slides artifact or PPTX export exists.
- Follow the host's current artifact, attachment and file-delivery rules. Verify the output exists
  and link to the current file. Discover Gamma/Canva capabilities at runtime as routes.md requires.
- Additional OpenAI metadata is for compatible OpenAI hosts and is not a Claude runtime dependency.
  If a feature is unavailable, follow the same bounded fallback and honest delivery limits as
  workflow.md; never weaken evidence or creative requirements to report a successful build.
