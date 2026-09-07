# Python Challenges Agent

A personal practice repo with two goals:

1. **Learn to build agents with LangChain** — an orchestration layer, tool-calling, structured output, and a persistence layer, built from scratch rather than copied from a tutorial.
2. **Practice Python broadly** — pandas/numpy data wrangling, but also general-purpose topics like class design, SQL, and API calls — using the agent itself as a source of endless, graded practice problems.

The agent generates a random (or topic-specific) Python/pandas challenge, waits for an attempt, grades it with an LLM, and logs the result to a local database so progress can be tracked over time.

## How it works

```
                 ┌─────────────────────┐
   user  ──────► │       agent.py       │  orchestrator (LangChain agent + tools)
                 └──────────┬───────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
 generate_question   retrieve_attempt     grade_and_log
 (chain_generate     (reads a file path   (chain_logScore.py →
  Question.py)        from disk)           LLM grades + writes
                                            a row via sql_db.py)
                                                   │
                                                   ▼
                                            scorecard.db (SQLite)
                                                   │
                                                   ▼
                                             progress.md
```

1. **`agent.py`** is the orchestration layer. It builds a LangChain `create_agent` graph with four tools and runs a simple REPL loop, feeding the conversation back into the graph each turn.
2. **`chain_generateQuestion.py`** asks Claude for a random or topic-specific challenge, always including a concrete runnable sample dataset.
3. You solve the challenge in a `.py` file (see `attempt/`).
4. **`chain_logScore.py`** reads your attempt, has Claude grade it against the challenge, and returns a structured `ScorecardRow` (via `pydantic_schema.py`) which gets written to SQLite.
5. **`sql_db.py`** is a small, schema-driven SQLite layer: it derives `CREATE TABLE`/`INSERT`/`SELECT` statements directly from the `ScorecardRow` Pydantic model, so adding/removing a graded field only requires editing the schema, not hand-writing SQL.
6. Every grading pass also regenerates **`progress.md`**, a running summary of scores by topic.

## Repo layout

| Path | Purpose |
|---|---|
| `agent.py` | Entry point. Defines the LangChain tools and the orchestrator's system prompt, runs the CLI loop. |
| `chain_generateQuestion.py` | LLM chain that generates a practice question. |
| `chain_logScore.py` | LLM chain that grades an attempt and logs it; also rebuilds `progress.md`. |
| `pydantic_schema.py` | `ScorecardRow` — the single source of truth for what a graded row looks like. |
| `sql_db.py` | Generic SQLite helper functions, driven by the Pydantic schema above. |
| `attempt/` | Where solved challenges live — one file per challenge. |
| `scorecard.db` | SQLite database of every graded attempt. |
| `progress.md` | Auto-generated score breakdown by topic. |

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt
```

Create a `.env` file in the repo root with your Anthropic API key:

```
ANTHROPIC_API_KEY=your-key-here
```

## Usage

```bash
python agent.py
```

You'll be prompted for what you want to practice (or press Enter for a random question). Solve the challenge in a new file under `attempt/`, then tell the agent the file path when it asks — it'll grade the attempt, log the score, and update `progress.md`. Type `quit` or `exit` to end the session.

## Notes

- The database is **SQLite**, not MySQL/Postgres — chosen for zero setup, since this is a single-user local tool.
- `Id` in `ScorecardRow` is an optional, auto-generated primary key (`INTEGER PRIMARY KEY AUTOINCREMENT`) — omit it when constructing a row and SQLite assigns the next value.
