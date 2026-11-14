# Bounded execution and linkage closure — 14 November 2026

Base: main 5edc16f1c5893c2878f16636e91018fd8cb8119c. Scope is the five remaining findings
from the internal wiring audit, while preserving creative exploration and existing samples.

## Findings and closure

| Finding | Change | Verification |
|---|---|---|
| Unbounded conversion/preview subprocesses | Shared execution helper, per-command limits and overall deadlines; clear timeout exit 124 | Actual sleeping-process and descendant tests; real preview smoke routes |
| Nested ownership could escape an outer timeout | Retain one POSIX group through nested commands; timeout marker and owned scratch cleanup | Both shorter-outer and shorter-inner regressions; independent reproduction |
| Repairs could restart indefinitely across new layouts | Three rounds/15 minutes across the deck and routes; explicit stop-with-draft outcome | Fresh scenario execution: layout switch does not authorise another round |
| Dependency preflight omitted icon/native prerequisites | Feature-specific import/raster probes, JSON report and --require; missing Pillow is safe | Missing-dependency isolation and required-feature failure tests; full CI preflight |
| Historical Gamma/Canva account/network assumptions | Discover actual operations, permissions, assets, costs and exports; bounded lookup/fallback | Fresh scenarios for missing export and a rejected historical ID; no live paid generation claimed |
| Tornado/sensitivity missing from route summary | Route G and chart helper documentation include all registered kinds | Registry-to-reference regression |
| Linkage checks were manual-only | Standard-library internal-reference/section and local-import-cycle checker, wired into CI | Current bundle passes; deliberate broken references and cyclic modules fail |

Independent source review found the initial nested-session flaw; it was repaired before publication.
Reused preview directories also discard old comparison inputs before a new run, so a failed or
shortened preview cannot present the previous comparison as current.
The environment checker initially tried to measure fonts with absent Pillow; it now reports that
feature unavailable without crashing or blocking standard-library HTML authoring.

## Recovery contract

Initial authoring and creative exploration are not QA failure-recovery rounds. For failed QA,
count a changed fix plus its check as a round. Three rounds or 15 minutes across the whole deck,
whichever first, is the default; a user budget overrides it. Layout/route switches do not reset it.
One refreshed lookup and one verified alternative bound a rejected external step. Unchanged retries
are not permitted. Missing evidence, approval and unavailable destination operations have explicit
pause/diagnostic outcomes. Do not label an unchecked final ready merely because a budget ran out.

## Validation record

Local suite: 88 tests, 80 passed and eight renderer-dependency skips. Link checker: 237 pointers,
18 modules, no unresolved references or circular local imports. Full CI installs rendering features
and the optional PyMuPDF fallback, checks readiness, runs every retained example and the two actual
preview routes, then verifies the upload package. Final CI/source-readback outcomes are recorded on
the pull request; main publication must pass and re-download its ZIP before a ready link is shared.

## Limits

This closes identified failure paths; it is not a mathematical guarantee about arbitrary LLM
trajectories, malicious inputs, kernel failures or every platform. POSIX child groups receive stage
cleanup; Windows cleanup is direct-child and requires host/job supervision. Actual Claude execution,
live paid Gamma/Canva generation and target-application accessibility remain untested. No claim is
made that internal path resolution proves semantic equivalence of all prose.
