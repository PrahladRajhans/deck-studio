# Evidence policy: universal honesty, proportionate documentation

The validator checks records and calculations. It does not retrieve sources, establish causality,
or prove that a claim inventory is complete. Never populate `verified` merely to satisfy a gate.
Use the user-supplied brief as a source when appropriate; do not invent external citations for it.

## Assurance profiles

Choose once at intake from the consequences of the claims, independent of creative style or live
versus reading mode. `standard` is the default for backward compatibility.

| Profile | Appropriate work | Required records |
|---|---|---|
| `brief` | Straightforward low-risk supplied information, such as an event invitation | Observed facts retain their sources; factual slides link `evidence_ids` or explicitly state a non-factual role. No separate exact-text inventory is required when a slide has supplied evidence links |
| `standard` | Analytical, business, research and ordinary substantive decks | Reviewed claims inventory or legitimate non-factual reason; fact tokens inherit evidence links |
| `high` | Consequential clinical guidance, financial decisions or sensitive public assertions | Reviewed inventory on each substantive slide, including illustrative teaching material; stronger source-support and final-output review |

A medical talk may require high assurance. A routine board update may not. Do not select `brief`
to silence a substantive uncertainty or bypass analytical review. A high-stakes user request
requires high assurance even if the preferred visual treatment is playful or minimal.

Every profile keeps: no fabricated facts or sources, accurate quantities and derived figures,
source/claim agreement, explicit assumptions, visible illustrative labels, material limitations,
placeholder checks and final-output reconciliation. Profiles change documentation, not honesty.

## Link provenance once, review the interpretation separately

- Raw observations name an evidence record in `fact_meta`. Evidence records name a real source,
  precise locator and truthful verification status.
- `{=fact}` and nested chart expressions inherit source IDs through derived fact dependencies.
  A claim referring to those tokens need not repeat identical `evidence_ids`.
- Reviewed status and claim classification do not inherit automatically. "Sales rose {=growth}%"
  and "The campaign caused sales to rise {=growth}%" can use the same quantity while requiring
  different evidence. Source linkage alone does not establish the second claim.
- Quotations still require evidence for their exact wording and attribution. Arithmetic cannot
  establish a quotation. Assumptions and recommendations explain their basis rather than pretending
  to be observations.
- Explicit citation links remain available for qualitative claims, screenshots, sources in notes
  and statements not expressed through the facts model.

## Unused research and missing information

The release gate traces the facts and citations used in slides, claims and notes. It blocks
unverified or incomplete records on those paths. An unused missing source or unclassified unused
fact remains an advisory research-history entry; it need not be deleted to produce unrelated work.

This does not permit omission of evidence that the recommendation actually needs. Semantic review
must identify unsupported premises even when the model forgot to link them. Dropping a material
limitation from a slide is not a legitimate way to make its evidence record "unused".

Keep missing evidence visibly marked during drafting. For final production, verify it, narrow or
remove the claim, or deliver a useful evidence-limited version whose remaining claims are supported.
Unresolved essential decision evidence should stop the recommendation, not force invented data.

Record agreement to illustrative examples once at deck level when the user requested or authorised
them. Keep the label visible. Never relabel real metrics illustrative to avoid source verification.
Administrative number exceptions are narrow, explained and unrelated to substantive quantities.
