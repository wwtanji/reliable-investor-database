# Reliable investor database

Work in progress. Results, how to run, decisions, AI workflow and limitations are filled in as the phases in [prompts/00-kickoff.md](prompts/00-kickoff.md) complete. Nothing below the checklist is claimed until a file in this repository backs it.

## Requirement checklist

Derived from [TASK.md](TASK.md) and the [original email](docs/brief-original-email.md) before any code was written. Ticked only when the linked file exists and supports the claim.

### Plan

- [ ] Inclusion and exclusion rules that decide who is in the database (`docs/PLAN.md`)
- [ ] How records are checked for authenticity and correct classification (`docs/PLAN.md`)
- [ ] Estimated range of investor types obtainable from public sources (`docs/PLAN.md`)
- [ ] Estimated number of investors, with its basis (`docs/PLAN.md`)
- [ ] Expected reliability of the data, with its basis (`docs/PLAN.md`)

### Record content, for every investor

- [ ] Real investor, not an arbitrary company (inclusion rule plus dated investment evidence)
- [ ] Sector of focus
- [ ] Typical investments: stage and ticket size
- [ ] Total investment capital
- [ ] Source for every data point

### Sample validation

- [ ] Smaller sample, for example VC funds in one country (`data/`)
- [ ] Source and date proving each entity actively invests (`data/evidence.csv`)
- [ ] Precision measured on a manually verified sample (`review/`)

### Scale-up

- [ ] Cost estimate for extending the database worldwide (`docs/COST.md`)

### Process and deliverables

- [ ] Public data only
- [ ] Essentials prioritised; anything missing is listed in this README
- [ ] README describes the AI workflow: agent instructions, how output was checked, where agents erred
- [ ] Unclear points decided and justified (`docs/DECISIONS.md`)
- [ ] Source code with full incremental commit history
- [ ] `ai-log/` with the Claude Code `/export`
- [ ] Public GitHub repository link sent by reply email by 30 October 2026 (Roman)

### Explicitly out of scope

- Landing page, user journey, conversion rate, A/B hypotheses and Vercel deployment: these belong to Option B, see [D1](docs/DECISIONS.md#d1-option-a-only-the-landing-page-paragraph-is-out-of-scope).
