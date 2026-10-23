# Kickoff prompt

You are a senior AI engineer and the lead on this task. `TASK.md` is the brief and `CLAUDE.md` holds the working rules; both are binding. Roman reviews and defends this work at the interview, so every number in it must be traceable and every decision must be explained.

The reviewer is evaluating judgement, not volume. A small, honest, well-measured sample beats a large, unverifiable one. The core idea of the solution is that **an LLM proposes and deterministic code verifies**. No claim enters the dataset unless code has confirmed that its evidence quote exists on the cited page.

Work through the phases in order. Commit and push at the end of every phase, more often if useful. Do not stop to ask questions, except at the gate in Phase 5. Decide everything else yourself and record it in `docs/DECISIONS.md`.

## Phase 0: Reconnaissance and plan (`docs/PLAN.md`), no code yet

Research the public sources before writing the plan. Search the web and open the actual pages.

Pick the sample country. The default is the **Czech Republic**, because its pool is large enough for a meaningful precision measurement. It has regulator registers (the Czech National Bank list of investment fund managers and funds), an industry association member list (CVCA), public co-investors (NRI / Národní rozvojový fond, EIF fund-of-funds commitments) and active deal press. Slovakia, at roughly 20 entities, is likely too small. Verify these claims; if they turn out wrong, pick a better country and justify the choice.

Stick to the scope the brief suggests: VC funds in one country. Plan for all investor types, but collect only VC in the sample.

`PLAN.md` must contain:

1. **Definitions.** What counts as an investor, defined separately for each type: VC, PE, family office, angel, large private investor.
2. **Inclusion rules, which are testable.** At minimum: the entity deploys its own or managed capital into the equity or quasi-equity of private companies, and at least one investment is evidenced within the last 36 months by a dated source.
3. **Exclusion rules, each with a reason code and a real-world example:** accelerators or incubators without their own capital, advisors and M&A boutiques, crowdfunding platforms, banks and pure lenders, public-markets-only asset managers, real-estate-only funds, inactive funds, corporates without a CVC arm, and duplicates such as a management company versus its individual funds. Add an edge-case table with a decision and a reason for each row.
4. **Field definitions.**
   - Sectors use a fixed taxonomy.
   - Typical investment covers the stage and the ticket min/max, in the original currency and in EUR. Use ECB reference rates and record the FX date.
   - Total capital is the AUM or the total of fund sizes. Define exactly which number is used and how it is labelled.
   - Investment evidence is a portfolio company, a deal date, a source URL and a publication date.
5. **Verification design, in layers.**
   - L1, code: the URL resolves, the quote appears in the fetched text after normalisation, and the dates parse.
   - L2: cross-source agreement.
   - L3: an independent verifier agent tries to refute each record.
   - L4: a human spot check.
   - Define a per-field confidence score from these layers.
6. **Coverage and reliability estimate, for each investor type and for the world.**
   - Give counts with their sources: regulator counts, association member counts and published industry reports.
   - State expected reliability per field. For example: existence is high, AUM is medium, ticket size is patchy, and angels have low coverage.
   - Show the arithmetic and the assumptions.
7. **Risks and limits:** legal and GDPR for individuals, staleness, survivorship bias, and self-reported AUM.

Commit the plan before Phase 1.

## Phase 1: Skeleton

Set up the `uv` project with the following:

- the Pydantic schema, where each field holds its value together with its evidence list
- a page fetcher with an on-disk cache in `.cache/`, which is gitignored; commit only the content hashes
- a text normaliser and a quote verifier
- dedup by normalised name and registrable domain
- ECB FX conversion
- exports
- a metrics module: precision with a Wilson 95% CI, plus a funnel report
- a stratified sampler with a fixed seed

Write `pytest` tests for the verifier, dedup and metrics. Keep the code small.

The canonical data and the outputs are:

- `data/investors.jsonl`
- `data/investors.csv`, a flat file for readers
- `data/evidence.csv`, one row per fact: investor_id, field, value, source_url, source_date, retrieved_at, quote, verified
- `data/excluded.csv`, with reason codes
- `data/funnel.json`

## Phase 2: Discovery

Run parallel subagents, one per source family: regulator register, association, public co-investors, deal press, and fund portfolio pages. Each returns candidates with the URL where it found them. Save every prompt to `prompts/agents/` before running it.

Merge and dedup the candidates. Keep the excluded entities and their reasons, because they show that the rules work. Record the funnel: candidates, then after dedup, then included and excluded.

## Phase 3: Enrichment

Process candidates in batches of about 10, with parallel extractor subagents. Each one reads the fund's website, the register and the press, and returns a record whose every field carries evidence.

Code then runs L1 on every claim. If a claim fails, the extractor gets one retry; if it fails again, the field is set to null with a reason. Log real extractor errors in `docs/ai-mistakes.md` as they happen.

## Phase 4: Independent verification

Run a separate verifier agent with a different prompt and no access to the extractor's reasoning. It gets only the record and its sources. Its job is to refute: wrong type, not actually investing, wrong numbers, stale data.

Adjudicate the disagreements and log them. Compute the automated metrics: L1 pass rate, verifier agreement, and field fill rates.

## Phase 5: Human precision measurement (gate)

Generate `review/manual_review.csv`. It holds a stratified random sample: about 30 included records and about 10 excluded entities, the latter to catch wrongly applied rules. Use one row per checked claim, covering existence, type, investment evidence, sector, ticket and capital. Each row has a clickable source and empty `human_verdict` and `human_note` columns.

Write `review/HOW_TO_REVIEW.md`, a guide of at most 10 lines, and a script that computes precision per field and per record, each with a CI.

Then stop and tell Roman to fill in the CSV. Until he does, label every number in the README as **agent-verified, not human-verified**. Never fill those columns yourself.

## Phase 6: Global scale-up estimate (`docs/COST.md`)

Base the estimate on the measured run: records processed, subagent runs, pages fetched, wall time, and L1 failure rate. Use current API pricing from the official Anthropic pricing page, and search or fetch API pricing from the providers' own pages.

Add human QA hours, scaled from Roman's measured review time, and the refresh cadence. Give low, base and high scenarios per investor type and region, built on the coverage counts from `PLAN.md`. Show the formulas.

Compare the result against buying a commercial dataset, citing public price points only.

## Phase 7: README

The README sections, in order:

1. Results: sample size, the funnel, precision with its CI and the label saying who verified it, and the global cost range.
2. What is in the repo.
3. How to run it.
4. Key decisions, linking to `DECISIONS.md`.
5. How AI was used: the agents and their prompts, how output was checked, and the actual mistakes from `ai-mistakes.md`.
6. Limitations and what is missing.
7. Next steps.

Keep it scannable. Put numbers before prose.

## Definition of done

- `ruff` is clean and `pytest` passes.
- Every row in `data/` traces to evidence that code has verified.
- `PLAN.md`, `DECISIONS.md`, `COST.md`, `ai-mistakes.md` and the README are consistent with each other.
- The history shows incremental commits.
- Before finishing, re-read `TASK.md` and tick off every requirement in a checklist at the bottom of the README.
