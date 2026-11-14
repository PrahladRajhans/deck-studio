# ChatGPT host adapter

Read after the user selects Deck Studio. Keep the shared creative, human-voice, evidence and
approval workflow in SKILL.md; this adapter changes execution and delivery only.

- Use the installed skill location supplied by the host. Resolve bundled paths from that location;
  do not assume a Claude mount path, a permanent checkout or a particular model release.
- Discover the actual execution, preview, image, file and connector tools exposed in this session.
  Skill installation does not install Python packages, Chromium, LibreOffice, fonts or connectors.
  Run the route-specific checks in workflow.md when code execution is available. Use the Python
  executable and dependency paths provided by the environment, if any. Attempt setup only where
  permitted; retain the existing bounded recovery and explicit stop outcomes.
- Keep HTML-first design and approval. Show a self-contained HTML preview using the available
  host preview mechanism. If inline HTML is unavailable, deliver the HTML download and rendered
  slide images/contact sheet for review. Do not claim a download is an interactive inline preview.
  Do not silently replace HTML approval with an unreviewed PowerPoint export.
- For editable PowerPoint, use route B when its prerequisites are ready. Route A is specific to
  Claude and must not be invoked merely because this is a presentation request. Use connected
  destinations only after discovering their live operations and obtaining any required approval.
- Follow the host's actual saving and file-link conventions, including persistent file storage
  when required. Verify that the delivered link refers to the current generated file. Never copy
  Claude-specific artifact syntax or claim an attachment exists when only a local path was made.
- If execution or a renderer is absent, explain the affected feature once and preserve useful
  planning or a labelled draft through workflow.md's fallback. Never claim strict, visual or
  target-application validation that could not be performed. Do not switch route without agreement
  when it materially changes editability, design or destination.

The OpenAI metadata permits implicit discovery so the consent question can be offered. It does
not grant consent or enforce a platform popup. Explicit skill selection already supplies consent.
Availability and invocation controls vary by ChatGPT surface; use the controls actually exposed.
