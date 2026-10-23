# Plan: reliable investor database

Status: written before any code, on 2026-10-23. All counts in §6 come from web-search summaries of the cited pages; the pages themselves could not be opened from the build environment (see `DECISIONS.md` D3). They are planning inputs, not dataset facts, and are re-checked when fetching is available.

## 1. Scope

- **Database scope:** investors in companies: VC, PE, family offices, angels and large private investors, worldwide.
- **Sample scope (validation run):** VC investors headquartered in the Czech Republic, active within 36 months of the retrieval date. Other types found during discovery are recorded in `data/excluded.csv` with reason `out_of_scope_type`, which shows that the type rules are applied.
- **Core principle:** an LLM proposes, deterministic code verifies. A fact enters `data/` only if code has fetched its `source_url` and found its verbatim quote (≤ 30 words) in the page text.

## 2. Definitions per investor type

| Type | Counts as an investor when | Typical evidence |
|---|---|---|
| `vc` | A management company, fund or corporate venture unit that deploys managed or dedicated capital as minority equity or quasi-equity (convertible loan, SAFE) into private, early- to growth-stage companies. Corporate VC counts if it is a named unit with its own budget or vehicle. An accelerator counts if it invests its own capital for equity. | Fund website, portfolio page, deal press release, regulator register |
| `pe` | A manager that buys majority or significant minority stakes in mature private companies (buyout, growth, expansion, mezzanine). | Same as VC, plus deal announcements of acquisitions |
| `family_office` | A single- or multi-family office managing a family's private wealth that makes direct investments in private companies. Pure LP commitments to funds do not count (see D7). | Own website, investee press release naming the office |
| `angel` | A natural person investing personal money into unlisted startups, evidenced only by professional information they published themselves or by an investee announcement naming them as an investor (GDPR). | Personal professional page, angel-network member page, investee press release |
| `private_investor` | A natural person or their personal holding company (not structured as a family office) investing own capital into private companies with at least one evidenced ticket ≥ €1M. | Holding company website, deal press release |

## 3. Inclusion rules (all must pass)

| Code | Rule | How it is tested |
|---|---|---|
| I1 | The entity is identifiable: a legal or trading name and a website domain or registry ID. | Field `website` or `registry_id` is non-null and resolves. |
| I2 | It deploys its own or managed capital into equity or quasi-equity of private companies. | `investor_type` fact has an L1-verified quote stating it invests. |
| I3 | At least one investment is evidenced within 36 months before `retrieved_at` by a dated source naming the portfolio company. | At least one `investments` item with `deal_date` or `source_date` ≥ `retrieved_at` − 36 months, L1-verified. |
| I4 | Sample only: type is `vc`, and the management company's registered office or the majority of its listed partners is in the Czech Republic. | `country == "CZ"` with an L1-verified quote. |
| I5 | All evidence is public: no login, no paywall, robots.txt respected, no LinkedIn. | The fetcher refuses disallowed URLs and logs them. |

## 4. Exclusion rules

Each excluded entity is kept in `data/excluded.csv` with one reason code and the evidence that triggered it.

| Reason code | Excludes | Real-world example |
|---|---|---|
| `accelerator_no_capital` | Accelerators, incubators and programmes that do not invest their own capital for equity | CzechInvest's CzechAccelerator programme (government support, no equity) |
| `advisor` | Corporate-finance advisors, M&A boutiques, placement agents, law firms | CVCA associate members (law and consulting firms) |
| `crowdfunding_platform` | Platforms that let others invest; the platform itself is not the investor | Fundlift (Czech equity crowdfunding) |
| `lender` | Banks and pure lenders (debt only) | Národní rozvojová banka's loan and guarantee programmes |
| `public_markets_only` | Asset managers investing only in listed securities | Retail mutual-fund managers on the CNB list (e.g. Conseq Investment Management) |
| `real_estate_only` | Funds investing only in property | Investika realitní fond |
| `fund_of_funds_only` | Invests only into other funds (D7) | EIF-managed RRF Czech Republic Fund of Funds |
| `inactive` | No investment evidenced within 36 months (fails I3) | Determined in the run; examples land in `data/excluded.csv` |
| `corporate_no_cvc` | Corporates that acquire companies but have no venture unit | ČEZ as a group (its CVC, Inven Capital, is the investor) |
| `duplicate` | A second record for the same investor: manager vs. its fund vehicles, renamed firms | KAYA, formerly Enern (one record, alias kept); Credo Ventures vs. its fund vehicles |
| `out_of_scope_type` | Real investors outside the sample's type | A Czech PE buyout manager found during discovery |
| `out_of_scope_geo` | Real VC investors headquartered outside the sample country | A foreign VC with a Czech portfolio company |
| `insufficient_evidence` | Claimed investors whose evidence could not be verified by code | Determined in the run |

The examples are planning illustrations; the actual excluded rows carry their own verified evidence.

### Edge cases

| Case | Decision | Reason |
|---|---|---|
| Corporate VC (e.g. Inven Capital, ČEZ group) | Include the CVC unit as `vc` with `is_cvc = true`; exclude the parent as `corporate_no_cvc` | The unit has a dedicated vehicle and makes minority equity investments. |
| Accelerator that invests (e.g. StartupYard) | Include as `vc` | It deploys its own capital for equity; the brief cares about who invests. |
| Venture studio or evergreen holding of founders | Include as `vc` if it takes minority stakes in third-party startups; otherwise `out_of_scope_type` | Building only own companies is operating a business, not investing. |
| Public co-investment fund (state-backed, invests directly) | Include as `vc` | It deploys managed capital into companies. |
| State fund-of-funds | `fund_of_funds_only` | D7. |
| Angel network or club | Exclude as `crowdfunding_platform` if it only matches; include as `angel` group only if it invests through its own vehicle | The network is not the capital owner. |
| Manager with several funds | One record per manager; funds are listed inside `funds` | The brief counts investors, not vehicles. |
| Renamed firm | One record; the old name goes to `aliases` | Avoids double counting. |
| Foreign manager with a Prague office | `out_of_scope_geo` unless the registered office or most partners are Czech | I4 must be testable from the website. |
| CVCA full member that is PE | `out_of_scope_type` | Sample is VC only. |
| Fund in wind-down that still makes follow-ons | Include only if a new or follow-on investment is evidenced in 36 months | Follow-ons are investments. |

## 5. Data model

One Pydantic schema (`src/investor_db/schema.py`) used by every stage. Every field is a `Fact`: a value, a list of evidence, a null reason and a confidence.

- **Evidence:** `source_url`, `source_kind` (`regulator`, `association`, `co_investor`, `press`, `own_website`), `source_date` (publication date, nullable), `retrieved_at` (ISO date), `quote` (≤ 30 words), `verified` (set only by code), `content_sha256`.
- **Investor:** `investor_id` (slug), `name`, `aliases`, `investor_type`, `is_cvc`, `country`, `website`, `sectors`, `stages`, `ticket_min`, `ticket_max`, `total_capital`, `investments`, `status` (`included` / `excluded`), `exclusion_reason`.
- **Sectors:** fixed taxonomy (`StrEnum`): `software`, `fintech`, `health_bio`, `deeptech_hardware`, `ai_data`, `energy_climate`, `mobility`, `consumer_ecommerce`, `industrial`, `agrifood`, `edtech`, `cybersecurity`, `media_gaming`, `proptech`, `generalist`.
- **Stages:** `pre_seed`, `seed`, `series_a`, `series_b_plus`, `growth`, `buyout`.
- **Money:** `amount`, `currency` (ISO 4217, original), `amount_eur`, `fx_rate`, `fx_date` (ECB reference rate, D6).
- **Total capital:** `Money` plus `basis` (`aum`, `sum_of_fund_sizes`, `latest_fund_size`) and `as_of` (D5).
- **Investment evidence:** `portfolio_company`, `deal_date` (nullable), plus the `Evidence` list.

Outputs: `data/investors.jsonl` (canonical), `data/investors.csv` (flat), `data/evidence.csv` (one row per fact), `data/excluded.csv`, `data/funnel.json`.

## 6. Verification design

| Layer | Who | What it checks |
|---|---|---|
| L1 | Code | The URL is public and allowed by robots.txt; the fetch returns 200; the quote appears in the normalised page text (NFKC, case-fold, unified quotes and dashes, collapsed whitespace); numbers in the value appear in the quote; dates parse and fall in range. A failed claim gets one extractor retry, then the field becomes `null` with a reason. |
| L2 | Code | Cross-source agreement: the same value is supported by evidence on two different registrable domains (money within 10%). |
| L3 | Verifier agent | A separate agent, with a different prompt and no access to the extractor's reasoning, receives only the record and its sources and tries to refute each claim: wrong type, not actually investing, wrong number, stale. Verdict per claim: `supported`, `refuted`, `uncertain`. |
| L4 | Roman | Manual review of a stratified random sample (~30 included records, ~10 excluded entities), one row per claim. Only Roman fills `human_verdict`. |

**Confidence per field:** `high` = L1 + L2 + L3 supported; `medium` = L1 + L3 supported; `low` = L1 only, or L3 uncertain. L1 fail → field `null`. L3 refuted → field `null` and logged for adjudication. A human verdict overrides all of these.

**Precision:** per claim type and per record (a record is correct when existence, type and investment evidence are all correct), with a Wilson 95% interval. Automated numbers are labelled *agent-verified*; only L4 results are labelled *human-verified*.

## 7. Coverage and reliability estimate

"Discoverable" means an active investor (≥ 1 evidenced deal in 36 months) whose existence and activity can be proven from public pages.

### Czech Republic, VC (sample)

| Input | Value | Source |
|---|---|---|
| Fund managers on the CNB list, end-2025 | 87 (851 funds); most are real-estate or retail funds | CNB board member J. Procházka, article "Český investiční trh roste", cnb.cz |
| CVCA full members (PE + VC managers) | 19 of 68 members | CVCA profile (undated) |
| EIF commitments to Czech equity funds | ~€300M into 15 funds | eif.org, RRF Czech Republic pages |
| Prague VC guides | 15–20 names each, overlapping | papermark.com, failory.com, vestbee.com (2025–2026) |

**Estimate:** 25–40 active Czech-headquartered VC investors. Arithmetic: ~10 VC among the 19 CVCA full members; plus ~10–15 non-member funds named in guides; plus CVC units, investing accelerators and new RRF/EIF-backed funds (~5–15). The discovery funnel will test this number.

### World, all types

| Type | Base count | Source | Active share | Publicly evidenced share | Discoverable |
|---|---|---|---|---|---|
| VC | US 2,984 firms (2025); Europe ~800–1,000 VC of >1,750 PE/VC firms surveyed; rest of world assumed 1.0–1.5× US | NVCA Yearbook 2026; Invest Europe activity survey | 70–85% | 85–95% | **4,000–7,000** |
| PE | ~7,000 firms worldwide (6,000 US) | American Investment Council via Vault | 75–85% | 80–90% | **4,000–6,000** |
| Family office | 8,030 single-family offices (2024), 9,030 projected for 2025 | Deloitte Private, Family Office Insights | — | 15–30% (most do not publish deals) | **1,200–2,700** |
| Angel | US 445,535 active angels (2024); Europe ~39,400 in networks (2021) | UNH Center for Venture Research; EBAN Statistics Compendium | — | 1–3% self-publish professional profiles with evidenced deals | **5,000–15,000** |
| Private investor | 3,428 billionaires (Forbes 2026) | Forbes World's Billionaires 2026 | — | 25–45% have a public direct-investment vehicle | **900–1,500** |
| **Total** | | | | | **~15,000–32,000** |

Arithmetic for VC: (2,984 + 800–1,000 + 3,000–4,500) × 0.70–0.85 × 0.85–0.95 ≈ 4,000–7,000. For PE: 7,000 × 0.75–0.85 × 0.80–0.90 ≈ 4,200–5,400, widened to 4,000–6,000 for the uncertain base. The shares are assumptions, set from the brief's reliability criteria and to be replaced with measured rates from the Czech run (share of candidates that pass I3; share whose evidence passes L1).

### Expected reliability per field

| Field | Expected fill | Expected precision | Why |
|---|---|---|---|
| Existence / active | 100% of included | ≥ 95% | Rule I3 requires a dated, code-verified deal. |
| Investor type | 100% | ~90% | VC/PE and CVC/accelerator boundaries are fuzzy. |
| Investment evidence | 100% | ≥ 95% | Code-verified quote naming the company. |
| Sectors | ~90% | ~85% | Self-described focus maps imperfectly onto a fixed taxonomy. |
| Stage | ~85% | ~85% | Usually stated on the website. |
| Ticket min/max | 40–60% | ~80% | Often unpublished or given as a single "typical" figure. |
| Total capital | 60–80% | ~80% | Self-reported, mixed bases (AUM vs. fund size), CZK/EUR/USD. |
| Angels (all fields) | low coverage | — | GDPR limits sources to self-published information. |

## 8. Sample run design

1. **Discovery**: parallel agents, one per source family (regulator, association, co-investors, deal press, fund portfolio pages). Each returns candidates with the URL where they were found. Merge and dedup in code (normalised name + registrable domain).
2. **Enrichment**: batches of ~10, parallel extractor agents, every field with evidence. L1 in code, one retry, then `null` with reason.
3. **Verification**: an independent verifier agent (L3); code computes L2, L1 pass rate, verifier agreement and fill rates.
4. **Human review**: `review/manual_review.csv`, stratified with a fixed seed; precision script with Wilson CIs.
5. **Cost**: `docs/COST.md`, scaled from the measured run (pages, agent runs, tokens, wall time, L1 failure rate, Roman's review minutes).

## 9. Risks and limits

- **Legal / GDPR:** angels and private investors are recorded only through information they published about themselves. No LinkedIn scraping, no logins, no paywalls.
- **Staleness:** activity decays; the 36-month window and `retrieved_at` make age visible. Refresh cadence goes into the cost model.
- **Survivorship bias:** public sources over-represent successful, marketing-active funds; quiet but active investors are under-counted.
- **Self-reported numbers:** AUM and fund sizes come from the managers themselves and mix bases; labelling (D5) mitigates but does not fix this.
- **Small sample:** ~30 records give a wide confidence interval (e.g. 28/30 correct → 79–98%). The interval is reported, not hidden.
- **Environment:** the build environment currently cannot fetch pages (D3). Until that is fixed, no data rows can be produced.
