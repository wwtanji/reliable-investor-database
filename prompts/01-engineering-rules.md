# Engineering rules for the test task

These rules apply to every session and every agent working on the task. They are written to make the solution verifiable, honest and easy to defend at the interview.

## 1. Principles

- The reviewer judges judgement, not volume. A small, measured, honest result beats a large one that nobody can verify.
- The LLM proposes and code verifies. No fact enters the deliverable unless something deterministic has confirmed it.
- Every number is traceable. Anything in the README must lead back to a file, a script or a source URL.
- When something is unclear, decide yourself and write down why. Do not stall on ambiguity: record the decision in `docs/DECISIONS.md` and move on.
- Finish the essentials first. If time runs out, the missing parts are listed in the README, never hidden.

## 2. Process

1. **Read the brief twice.** Turn it into a requirement checklist at the bottom of the README before writing any code.
2. **Research before planning.** Open the real sources, count what exists, and only then commit to numbers in the plan.
3. **Plan before code.** `docs/PLAN.md` is committed before the first line of code. It holds the scope, testable rules, the data model, the verification design and the estimates, with their basis.
4. **Build a thin vertical slice first.** Take one record end to end (discover, extract, verify, export) before scaling to the sample.
5. **Scale in batches.** Work in small batches. After each batch, check the failures, fix the cause rather than the symptom, and commit.
6. **Verify independently.** The agent that checks output must not be the agent that produced it. It gets a different prompt and no access to the producer's reasoning.
7. **Measure honestly.** Automated metrics are labelled as agent-verified. Human-verified numbers come only from Roman's manual review.
8. **Write it up last, but keep notes all along.** The README is assembled from `PLAN.md`, `DECISIONS.md`, `ai-mistakes.md` and the measured outputs. It is never written from memory.

## 3. Working with agents

- Every subagent prompt is saved verbatim to `prompts/agents/<name>.md` before it runs.
- Each prompt states the role, the input, the exact output schema, what counts as evidence, and what to do when evidence is missing: return null with a reason, never guess.
- Agents run in parallel only on independent work, such as separate sources or separate batches. Merging and deduplication happen in code.
- Agent output is untrusted input. It is parsed against the schema, and anything that fails validation is rejected or retried once.
- Every caught agent mistake goes into `docs/ai-mistakes.md` as it happens: what went wrong, how it was caught, the fix, and whether a prompt or a code check was changed because of it. Record only mistakes that actually happened.
- Keep the conversation exportable: work in one main session and run `/export` to `ai-log/` at the end.

## 4. Data integrity

- Use public sources only. Respect robots.txt and site terms. No logins, no paywall bypassing, no LinkedIn scraping.
- Every fact carries `source_url`, `source_date`, `retrieved_at` and a verbatim quote of at most 30 words. Code checks that the quote is present on the fetched page.
- Unknown values stay `null` with a reason. Nothing is invented: not entities, URLs, numbers, dates or verification results.
- Excluded entities are kept, together with their reason codes. They prove the rules are applied.
- Individuals are recorded only through professional information they published themselves (GDPR).
- Currency conversions use ECB reference rates and record the date. The original value and currency are always kept.

## 5. Code

- Python 3.12 with `uv`, `ruff` and `pytest`. For a web task, TypeScript with strict mode.
- Do not write comments or prose docstrings. Names carry the meaning.
- Use full type hints. Use one schema (Pydantic) for records and use it everywhere.
- Repeated strings live in `constants.py`. Closed sets are `StrEnum`s.
- Keep code small and direct. Do not build abstractions for a single use case, plugin systems or wrapper classes.
- Shared logic lives in one place. Do not duplicate it across modules.
- Deterministic parts have tests: verification, deduplication, metrics and sampling.
- Runs are reproducible: fixed seeds, cached fetches, and a single command per stage that is documented in the README.

## 6. Git

- Commit small and often, so the history tells the story: plan, skeleton, slice, batches, verification, measurement, write-up.
- Messages follow Conventional Commits, in English, subject line only. Do not add a `Co-Authored-By` trailer.
- Never squash when merging. The incremental history is a deliverable.
- `ruff` and `pytest` pass before every commit that touches code.
- No secrets, caches or personal data in the repository.

## 7. Repository layout

```
README.md            results first, then how to run, decisions, AI workflow, limits, checklist
TASK.md              the brief
docs/PLAN.md         scope, rules, data model, verification design, estimates with basis
docs/DECISIONS.md    every judgement call and its reason
docs/COST.md         global scale-up estimate with formulas and scenarios
docs/ai-mistakes.md  real agent errors, how caught, how fixed
prompts/             kickoff prompt and every subagent prompt, verbatim
src/                 code
tests/               tests for deterministic logic
data/                final dataset, evidence table, excluded list, funnel
review/              manual review sheet, guide and precision script
ai-log/              /export of the Claude Code conversations
```

## 8. README standard

- Put results first: sample size, the funnel, precision with a 95% CI, who verified it, and the cost range.
- Back every claim with a link to the file that supports it.
- The section on how AI was used covers the agents and their prompts, the verification layers, and the real mistakes.
- Include a limitations section and a list of what is missing.
- End with the requirement checklist, ticked against the brief.

## 9. Definition of done

- Every requirement in the brief is ticked in the README checklist, or listed as missing with a reason.
- Every row in `data/` traces to evidence that code has verified.
- `PLAN.md`, `DECISIONS.md`, `COST.md`, `ai-mistakes.md` and the README agree with each other.
- `ruff` is clean and `pytest` passes.
- The history shows incremental commits, and `ai-log/` contains the export.
- One final pass is done as a reviewer: would this be convincing if read cold, in ten minutes?
