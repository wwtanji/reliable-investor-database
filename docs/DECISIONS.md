# Decisions

Every judgement call made where the brief was unclear, with its reason. Newest last.

## D1. Option A only; the landing-page paragraph is out of scope

The original email ([brief-original-email.md](brief-original-email.md)) places a paragraph about tracking a user journey to form submission, conversion rate, three A/B hypotheses and Vercel deployment inside Option A. Those requirements describe a landing page, and the deliverables line names a "live page" only for Task B. The condensed [TASK.md](../TASK.md) already leaves them out. Decision: treat that paragraph as belonging to Option B and do not build a page. Reason: nothing in an investor database has a form to submit, and building one would add volume without serving the brief's stated core, data reliability. The README lists this under scope.

## D2. Rule sources and their precedence

The binding rules are `TASK.md`, `CLAUDE.md`, [prompts/00-kickoff.md](../prompts/00-kickoff.md) and [prompts/01-engineering-rules.md](../prompts/01-engineering-rules.md) (the engineering rules Roman supplied in the main session, stored verbatim). Where tooling defaults differ from them, they win. Concretely: commit messages are subject-line-only Conventional Commits with no `Co-Authored-By` trailer, as both rule files require.

## D3. Python 3.12 is provisioned by `uv`

The container ships Python 3.13; the rules require 3.12. `uv python install 3.12` provides a managed 3.12.13 interpreter and the project pins `requires-python = ">=3.12,<3.13"`. Reason: follow the rule exactly without depending on the host interpreter.
