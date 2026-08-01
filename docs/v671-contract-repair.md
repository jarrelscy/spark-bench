# v6.7.1 Scenario Contract Repair

Date: 2026-08-01

## Why the methodology changed

The first DeepSeek V4 Flash, GLM-5.2, and Inkling Small v6.7 challenge cohort
successfully exposed model differences, but a transcript-level audit found six
cases where the prompt, offered tools, or grader did not measure the intended
behavior. The recorded outputs and scores remain immutable historical
artifacts. They are not qualified as final ranking evidence.

## Repairs

| Scenario | Observed defect | v6.7.1 contract |
|---|---|---|
| CODE-12 | Prompt prohibited `threading.Lock`, while the executable grader awarded full credit to lock-based answers when dynamic source inspection failed. Portable lock-free mutation is not a valid Python standard-library requirement. | Prompt requires exactly one per-instance `threading.Lock`. An AST gate verifies its construction and use in `increment`, `decrement`, and `value`; concurrent behavior is then executed. |
| CODE-14 | Prose declared one `streams` list, while the example and tests called the function variadically. | Prompt and tests both require `merge_sorted_streams(*streams)`, including zero streams. |
| RO-03 | `No secret passcode is present` was a valid abstention rejected by the wording regex. | The observed wording is accepted and regression-tested. |
| RR-02 | All models supplied the common quoted tautology fixture, but the regex required an extra trailing quote. | Optional quoting around both operands is accepted; UNION, comment, and parameterization checks remain required. |
| TUH-10 | `get_weather` and `get_weather_global` both claimed live current-city weather, but only the first received full credit. | `get_weather_global` is now a country-level climate summary with a `country_code` schema and explicitly excludes live city conditions. |
| MSC-02 | The grader required notification before the model had received the contact lookup result. | Contact results are included in the conversation state before event creation and notification are graded. |

PL-02 was also clarified without changing its intended score: the stock tool
returns one current company price and cannot supply historical, index, or ETF
performance; web search explicitly supplies broad-market performance data.

## Version and comparison boundary

- Full runs stamp methodology `v6.7.1-full`.
- Challenge runs stamp methodology `v6.7.1-challenge`.
- v6.6 full-suite and v6.7 challenge scores are not numerically comparable to
  v6.7.1 because prompts, tool schemas, and graders changed.
- Existing transcripts may demonstrate a defect, but replacement leaderboard
  numbers require fresh model responses to the repaired contracts.

## Verification

- Unit tests: 40/40 passed.
- Grader self-tests: 17/17 passed.
- Golden gate: 12/12 passed, including Chromium-rendered race and locomotion
  fixtures.

The seven new regression tests cover the exact abstention, SQL fixture, tool
ambiguity, missing conversation state, planning-tool descriptions, and both
code-contract repairs found in the audited cohort.
