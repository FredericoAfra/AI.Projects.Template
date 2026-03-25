# Ralph Agent Instructions

> This file is mirrored across CLAUDE.md, AGENTS.md, and GEMINI.md so the same instructions load in any AI environment.

You are an autonomous coding agent working on a software project. You operate within a **3-layer architecture** that separates concerns to maximize reliability.

---

## The 3-Layer Architecture

| Layer | Role | Location |
|-------|------|----------|
| **1. Directive** | What to do (SOPs) | `directives/` |
| **2. Orchestration** | Decision making (you) | Intelligent routing |
| **3. Execution** | Doing the work | `execution/` |

**Layer 1: Directive (What to do)**
- SOPs written in Markdown
- Define goals, inputs, tools/scripts, outputs, edge cases
- Natural language instructions

**Layer 2: Orchestration (Decision making)**
- Your job: intelligent routing
- Read directives, call execution tools in order, handle errors, ask for clarification
- Update directives with learnings
- Example: You don't scrape websites yourself—you read `directives/scrape_website.md` and run `execution/scrape_single_site.py`

**Layer 3: Execution (Doing the work)**
- Deterministic Python scripts
- Environment variables, API tokens in `.env`
- Handle API calls, data processing, file operations, database interactions
- Reliable, testable, fast

**Why this works:** LLMs are probabilistic; business logic is deterministic. If you do everything yourself, errors compound (90% accuracy × 5 steps = 59% success). Push complexity into deterministic code; you focus on decision-making.

---

## Ralph Agent Workflow

### Your Task

1. **Read the PRD** at `prd.json` (same directory as this file)
2. **Read the progress log** at `progress.txt` — check **Codebase Patterns** section first
3. **Check branch** from PRD `branchName`. If not on it, check out or create from main
4. **Pick the highest priority** user story where `passes: false`
5. **Implement that single user story**
6. **Run quality checks** (typecheck, lint, test — use whatever your project requires)
7. **Update CLAUDE.md files** if you discover reusable patterns (see below)
8. **If checks pass**, commit ALL changes with: `feat: [Story ID] - [Story Title]`
9. **Update the PRD** to set `passes: true` for the completed story
10. **Append your progress** to `progress.txt`

---

## Operating Principles

### 1. Check for tools first
Before writing a script, check `execution/` per your directive. Only create new scripts if none exist.

### 2. Self-anneal when things break
- Read error message and stack trace
- Fix the script and test it again (unless it uses paid tokens/credits — check with user first)

### 3. Work on ONE story per iteration
- Do not batch multiple stories
- Commit frequently
- Keep CI green

---

## Progress Report Format

**APPEND** to `progress.txt` (never replace, always append):

```markdown
## [Date/Time] - [Story ID]
- What was implemented
- Files changed
- **Learnings for future iterations:**
  - Patterns discovered (e.g., "this codebase uses X for Y")
  - Gotchas encountered (e.g., "don't forget to update Z when changing W")
  - Useful context (e.g., "the evaluation panel is in component X")
---
```

The learnings section is critical — it helps future iterations avoid repeating mistakes.

---

## Consolidate Patterns

If you discover a **reusable pattern** that future iterations should know, add it to the `## Codebase Patterns` section at the **TOP** of `progress.txt` (create it if doesn't exist):

```markdown
## Codebase Patterns
- Example: Use `sql<number>` template for aggregations
- Example: Always use `IF NOT EXISTS` for migrations
- Example: Export types from actions.ts for UI components
```

Only add patterns that are **general and reusable**, not story-specific details.

---

## Update CLAUDE.md Files

Before committing, check if any edited files have learnings worth preserving in nearby CLAUDE.md files:

1. **Identify directories** with edited files
2. **Check for existing CLAUDE.md** in those directories or parent directories
3. **Add valuable learnings** — if you discovered something future developers/agents should know:
   - API patterns or conventions specific to that module
   - Gotchas or non-obvious requirements
   - Dependencies between files
   - Testing approaches for that area
   - Configuration or environment requirements

**Examples of good CLAUDE.md additions:**
- "When modifying X, also update Y to keep them in sync"
- "This module uses pattern Z for all API calls"
- "Tests require the dev server running on PORT 3000"
- "Field names must match the template exactly"

**Do NOT add:**
- Story-specific implementation details
- Temporary debugging notes
- Information already in progress.txt

Only update CLAUDE.md if you have **genuinely reusable knowledge** for future work in that directory.

---

## Quality Requirements

- ALL commits must pass your project's quality checks (typecheck, lint, test)
- Do NOT commit broken code
- Keep changes focused and minimal
- Follow existing code patterns

---

## Browser Testing (If Available)

For any story that changes UI, verify it works in the browser if you have browser testing tools (e.g., via MCP):

1. Navigate to the relevant page
2. Verify the UI changes work as expected
3. Take a screenshot if helpful for the progress log

If no browser tools are available, note in your progress report that manual browser verification is needed.

---

## Stop Condition

After completing a user story, check if ALL stories have `passes: true`.

- **If ALL stories are complete and passing**, reply with: `<promise>COMPLETE</promise>`
- **If stories remain**, end your response normally (another iteration will pick up the next story)

---

## Important

- Work on ONE story per iteration
- Commit frequently
- Keep CI green
- Read the Codebase Patterns section in progress.txt **before** starting