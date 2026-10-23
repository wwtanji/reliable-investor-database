# Task: Reliable investor database

Position: Junior AI Developer. Deadline: 30 October 2026. Translated and condensed from the original Slovak brief. Nothing was added.

## Goal

Build a database of investors in companies: VC funds, private equity, family offices, angel investors and large private investors.

Data reliability is the main point. Every record must be a real investor, not a random company. Each investor record must state:

- the sector it operates in
- what it typically invests in, and in what amounts
- its total investment capital
- where each piece of information comes from

## Required steps

1. **Plan first.** The plan must make clear who is in the database and who is not: the rules for including or excluding an entity. It must also describe how records are checked for authenticity and correct classification. Estimate what range of investors can be obtained from public sources, roughly how many there will be, and how reliable the data will be. State what the estimate is based on.
2. **Validate the plan on a smaller sample,** for example VC funds in one country. Every record needs a source and a date that prove the entity actually invests.
3. **Measure precision** on a manually verified sample.
4. **Estimate the cost** of extending the database to the whole world.

Use publicly available data only.

## Process requirements

- Work in Claude Code or a similar tool.
- If not everything can be finished, prioritise the essential parts and state what is missing.
- The README must describe how AI was used: what instructions the agents got, how their output was checked, and where they made mistakes.
- Where the brief is unclear, decide yourself and justify the decision in the README.

## Deliverables

- A public GitHub repository containing:
  - the plan
  - the sample data, with a source for every data point
  - the result of the precision measurement
  - the code, with an incremental commit history
  - an `ai-log/` folder with the Claude Code conversation export (`/export`)
- The solution is sent as a reply to the email, with a link to the repository.
