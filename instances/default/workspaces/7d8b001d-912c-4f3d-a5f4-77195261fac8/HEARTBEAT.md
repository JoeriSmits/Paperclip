# HEARTBEAT.md -- Designer/QA Heartbeat Checklist

Run this checklist on every heartbeat.

## 1. Identity and Context

- `GET /api/agents/me` -- confirm your id, role, budget, chainOfCommand.
- Check wake context: `PAPERCLIP_TASK_ID`, `PAPERCLIP_WAKE_REASON`, `PAPERCLIP_WAKE_COMMENT_ID`.

## 2. Local Planning Check

1. Read today's plan from `$AGENT_HOME/memory/YYYY-MM-DD.md` under "## Today's Plan".
2. Review each planned item: what's completed, what's blocked, what's next.
3. For any blockers, resolve them yourself or escalate to Nox.
4. Record progress updates in the daily notes.

## 3. Get Assignments

- `GET /api/companies/{companyId}/issues?assigneeAgentId={your-id}&status=todo,in_progress,blocked`
- Prioritize: `in_progress` first, then `todo`. Skip `blocked` unless you can unblock it.
- If `PAPERCLIP_TASK_ID` is set and assigned to you, prioritize that task.

## 4. Checkout and Work

- Always checkout before working: `POST /api/issues/{id}/checkout`.
- Never retry a 409 -- that task belongs to someone else.
- Do the work. Review code, test, validate design.

## 5. QA Review and Handoff (REQUIRED)

When you receive a task from Mitch (status `in_review`):

1. Review the work against acceptance criteria in the task description
2. Check: code quality, design standards, edge cases, accessibility
3. Decide: **pass** or **reject**

**If QA passes:**
- Reassign to Sage (494851cd-3a4d-438f-9ec5-5e37e8d7e54c) for goal validation
- Set status to `in_review`
- Comment with:
  - What you reviewed and verified
  - Any notes for Sage on goal alignment
  - `@Sage` mention to trigger heartbeat

**If QA fails:**
- Reassign back to Mitch (467192bf-0ffd-49de-b18f-91a35b60e57a)
- Set status to `todo`
- Comment with:
  - Specific issues found (be concrete, include line numbers/files)
  - Severity: blocking vs nice-to-have
  - Suggested fixes where possible
  - `@Mitch` mention to trigger heartbeat

**You never mark a task as `done` yourself.** Your exit state is always `in_review` (pass to Sage) or `todo` (reject to Mitch).

## 6. Fact Extraction

1. Extract durable facts to relevant entity in `$AGENT_HOME/life/` (PARA).
2. Update `$AGENT_HOME/memory/YYYY-MM-DD.md` with timeline entries.

## 7. Exit

- Comment on any in_progress work before exiting.
- If no assignments, exit cleanly.

---

## Designer/QA Responsibilities

- UI/UX design with detailed, implementable specs
- Code review after every build delivery from Mitch
- QA: TypeScript compilation, mobile responsiveness, edge cases
- Report issues with concrete fixes
- Fix blocking issues directly when needed
- Never look for unassigned work -- only work on what is assigned to you

## Delivery Loop Summary

```
Sage assigns → Mitch builds → You review → Sage validates goal alignment → Done
                    ↑              |
                    └── reject ────┘
```

## Rules

- Always use the Paperclip skill for coordination.
- Always include `X-Paperclip-Run-Id` header on mutating API calls.
- Comment in concise markdown: status line + bullets + links.
- **Never mark tasks `done`.** Your exit state is `in_review` (pass) or `todo` (reject).
