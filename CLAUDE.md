# Working rules

## Code

- Python 3.12, managed with `uv`. Lint with `ruff check` and format with `ruff format`. Tests use `pytest`.
- Do not write comments or prose docstrings in code. Names carry the meaning; if code needs a comment, rename or restructure it.
- Every function signature has full type hints. Avoid `Any` when the shape is known.
- Repeated string values live in `constants.py`. Closed sets (investor type, stage, sector, source kind, exclusion reason) are `StrEnum`s.
- Define one Pydantic schema for records and use it everywhere. Do not keep parallel dict shapes.
- Do not overengineer: no plugin systems, no base classes with a single implementation, no wrappers that add nothing.
- Keep duplication to a minimum. Shared logic lives in one module.

## Data integrity

- Deterministic work belongs in code: fetching, caching, quote verification, deduplication, FX conversion, metrics, sampling. Discovery, reading and judgement belong to LLM agents.
- No fact enters `data/` unless it has `source_url`, `source_date` (publication date when known), `retrieved_at` (ISO date) and a verbatim evidence quote of at most 30 words. Code must have found that quote in the fetched page.
- Never invent investors, URLs, numbers, dates or verification results. When a value is unknown, it stays `null` with a reason.
- Only Roman fills the human verification columns. Agents never write `human_verdict`.
- Use public sources only. Respect robots.txt and site terms. No LinkedIn scraping, no logins, no paywall bypassing.
- For individual angels and private investors, use only professional information they published about themselves (GDPR).

## Workflow

- Make small commits after each meaningful step and push them, so the history shows how the work progressed.
- Commit messages follow Conventional Commits, in English, subject line only. Do not add a `Co-Authored-By` trailer.
- Save every prompt you give to a subagent, verbatim, to `prompts/agents/<name>.md` before you run it.
- Whenever you catch an agent mistake, append it to `docs/ai-mistakes.md` right away: what went wrong, how it was caught, and how it was fixed. Record only mistakes that actually happened.
- When the brief is ambiguous, decide yourself, record the decision and its reason in `docs/DECISIONS.md`, and continue.
