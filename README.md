# Reliable investor database

Work in progress. The results section is filled from measured outputs at the end.

- Plan: [`docs/PLAN.md`](docs/PLAN.md)
- Decisions: [`docs/DECISIONS.md`](docs/DECISIONS.md)

## Requirement checklist

Taken from [`TASK.md`](TASK.md) before any code was written. Ticked only when the linked file exists and supports the claim.

- [ ] Plan: who is in the database and who is not (inclusion and exclusion rules)
- [ ] Plan: how authenticity and classification are checked
- [ ] Plan: range of investors obtainable from public sources, approximate count, expected reliability, and the basis of the estimate
- [ ] Every record states its sector
- [ ] Every record states what it typically invests in and in what amounts
- [ ] Every record states its total investment capital
- [ ] Every data point states its source
- [ ] Sample run on a smaller scope (VC funds in one country)
- [ ] Every sample record has a source and a date proving the entity actually invests
- [ ] Precision measured on a manually verified sample
- [ ] Cost estimate for extending the database worldwide
- [ ] Public data only
- [ ] Missing parts stated
- [ ] README describes how AI was used: agent instructions, how output was checked, where agents made mistakes
- [ ] Unclear points decided and justified
- [ ] Code with incremental commit history
- [ ] `ai-log/` with the `/export` of the Claude Code conversation
