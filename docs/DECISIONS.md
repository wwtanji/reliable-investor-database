# Decisions

Each entry: the decision, the reason, and the date. Newest at the bottom.

## D1. Option A only; the landing-page paragraph is ignored

- **Decision.** Build Option A (reliable investor database). The English email puts one paragraph (track the user journey to form submission, conversion rate, three A/B hypotheses, deploy on Vercel) under Option A, but that paragraph belongs to Option B (an advertisement / landing page): it mentions "both versions of the advertisement" and "for Task B, also include the URL of the live page".
- **Reason.** The deliverables list for Task A names only the plan, the sample data with sources and the accuracy assessment. The Slovak-derived `TASK.md` has no such paragraph. A landing page would add volume without serving the data-reliability goal.
- **Date.** 2026-10-23.

## D2. Sample: VC funds headquartered in the Czech Republic

- **Decision.** Keep the kickoff default, the Czech Republic.
- **Reason.** Reconnaissance (web search, see `docs/PLAN.md` §6) found a regulator with a public list of fund managers (87 managers at end-2025 per the CNB), an association whose full members are PE/VC managers (CVCA, 19 full members per its profile), a public fund-of-funds programme (EIF-managed RRF Czech Republic FoF; EIF reports ~€300M committed to 15 Czech equity funds) and several Czech VC guides listing 15–20 names. That is enough for a pool of ~30 candidates, which the precision measurement needs. Slovakia was not researched further: the same sources suggest a pool too small for a meaningful confidence interval.
- **Date.** 2026-10-23.

## D3. Network policy blocks page fetching; no fabricated substitute

- **Decision.** The cloud environment blocks every source host (403 on CONNECT for cnb.cz, cvca.cz, ecb.europa.eu, eif.org, czechcrunch.cz, wikipedia.org, web.archive.org and others; WebFetch fails with ENOTFOUND). Only web search works. Planning uses web-search summaries, labelled as such. No record enters `data/` until code has fetched the cited page and found the quote. Roman was asked to switch the environment to full network access.
- **Reason.** The core guarantee of the solution is "code verifies the quote on the fetched page". Search snippets are paraphrased by a model and cannot serve as verbatim evidence.
- **Date.** 2026-10-23.

## D4. No `Co-Authored-By` trailer on commits

- **Decision.** Commit messages are subject-line only, without the trailer the harness suggests.
- **Reason.** `CLAUDE.md` and the rules file forbid it explicitly, and the user's instructions take precedence.
- **Date.** 2026-10-23.

## D5. Total capital: one number, always labelled with its basis

- **Decision.** `total_capital` holds one amount with a `basis`: `aum` (manager-level assets under management as stated by the manager), `sum_of_fund_sizes` (computed in code from per-fund sizes that each carry evidence), or `latest_fund_size` (only one fund size known). Preference order: `aum` stated within 36 months, then `sum_of_fund_sizes`, then `latest_fund_size`.
- **Reason.** Managers publish these three different numbers and readers compare them as if they were the same. A label makes the difference visible, and computing sums in code keeps the arithmetic deterministic.
- **Date.** 2026-10-23.

## D6. FX: ECB reference rate on the source date

- **Decision.** Convert to EUR with the ECB euro foreign exchange reference rate of the evidence `source_date`, or the closest earlier publication day; fall back to `retrieved_at` when the source date is unknown. Keep the original amount and currency and store the rate and its date.
- **Reason.** Fund sizes are announced in CZK, EUR and USD at different times; converting at the announcement date reflects what was announced.
- **Date.** 2026-10-23.

## D7. Fund-of-funds and LP-only investors are excluded from the sample

- **Decision.** Entities that invest only into other funds (e.g. the EIF-managed RRF CZ FoF) get reason `fund_of_funds_only` and are used as discovery sources, not as records.
- **Reason.** The brief asks for investors in companies. A fund-of-funds never holds a stake in an operating company.
- **Date.** 2026-10-23.
