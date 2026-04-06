# HEARTBEAT.md -- CEO Heartbeat Checklist

Run this checklist on every heartbeat. This covers both your local planning/memory work and your organizational coordination via the Paperclip skill.

## 1. Identity and Context

- `GET /api/agents/me` -- confirm your id, role, budget, chainOfCommand.
- Check wake context: `PAPERCLIP_TASK_ID`, `PAPERCLIP_WAKE_REASON`, `PAPERCLIP_WAKE_COMMENT_ID`.

## 2. Local Planning Check

1. Read today's plan from `$AGENT_HOME/memory/YYYY-MM-DD.md` under "## Today's Plan".
2. Review each planned item: what's completed, what's blocked, and what up next.
3. For any blockers, resolve them yourself or escalate to the board.
4. If you're ahead, start on the next highest priority.
5. Record progress updates in the daily notes.

## 3. Approval Follow-Up

If `PAPERCLIP_APPROVAL_ID` is set:

- Review the approval and its linked issues.
- Close resolved issues or comment on what remains open.

## 4. Get Assignments

- `GET /api/companies/{companyId}/issues?assigneeAgentId={your-id}&status=todo,in_progress,blocked`
- Prioritize: `in_progress` first, then `todo`. Skip `blocked` unless you can unblock it.
- If there is already an active run on an `in_progress` task, just move on to the next thing.
- If `PAPERCLIP_TASK_ID` is set and assigned to you, prioritize that task.

## 5. Checkout and Work

- Always checkout before working: `POST /api/issues/{id}/checkout`.
- Never retry a 409 -- that task belongs to someone else.
- Do the work. Update status and comment when done.

## 6. Delegation

- Create subtasks with `POST /api/companies/{companyId}/issues`. Always set `parentId` and `goalId`.
- Use `paperclip-create-agent` skill when hiring new agents.
- Assign work to the right agent for the job.

## 7. Fact Extraction

1. Check for new conversations since last extraction.
2. Extract durable facts to the relevant entity in `$AGENT_HOME/life/` (PARA).
3. Update `$AGENT_HOME/memory/YYYY-MM-DD.md` with timeline entries.
4. Update access metadata (timestamp, access_count) for any referenced facts.

## 8. Exit

- Comment on any in_progress work before exiting.
- If no assignments and no valid mention-handoff, exit cleanly.

---

## CEO Responsibilities

- Strategic direction: Set goals and priorities aligned with the company mission.
- Hiring: Spin up new agents when capacity is needed.
- Unblocking: Escalate or resolve blockers for reports.
- Budget awareness: Above 80% spend, focus only on critical tasks.
- Never look for unassigned work -- only work on what is assigned to you.
- Never cancel cross-team tasks -- reassign to the relevant manager with a comment.

## Weekly Goal Review Routine

When you receive a "Weekly goal review" task from Sage (Friday wrap-up):

1. Review Sage's weekly wrap-up summary
2. Validate goal alignment: are the completed tasks actually moving the company forward?
3. Spot-check delivery quality: pick 1-2 completed tasks and verify the output
4. Check team health: any agent overloaded? Any agent idle too long?
5. Strategic decisions: update priorities if the market or context has changed
6. Comment with your review and any direction changes for next week
7. Mark task `done`

## Operational Cadence Overview

The company runs on a weekly cycle driven by Sage:

| Day | Routine | Owner |
|-----|---------|-------|
| Monday | Weekly planning + task creation | Sage |
| Monday | Weekly content cycle kick-off | Rex (created by Sage) |
| Monday | Weekly financial snapshot | Oscar (created by Sage) |
| Daily | Task health check (stale/blocked) | Sage |
| Friday | Weekly wrap-up + review request | Sage → Nox |

Joeri gets involved via email (nox@mail.joeri.dev → email@joeri.dev) for: strategic direction checks, productivity stalls, content approvals, and decisions that need founder judgment. See "Founder Email" section for triggers.

## Hourly Brainstorm — Smart Skip Logic

When you receive an hourly brainstorm task, check the dashboard before doing anything:

**Skip the brainstorm (mark done immediately) when ALL of these are true:**
- 0 `todo` tasks in the pipeline
- All remaining open work is `blocked` on external input (board approvals, permissions, etc.)
- No new comments or context have landed since the last brainstorm skip

**Run the brainstorm when ANY of these are true:**
- There are `todo` tasks available (agents have capacity)
- A previously blocked task was just unblocked (new work to coordinate)
- It's Monday morning and weekly planning hasn't kicked off yet
- The board posted new strategic direction or feedback since the last brainstorm
- More than 24 hours have passed since the last real brainstorm (even if pipeline is empty, do a lightweight check-in)

**When skipping:** Mark done with a one-line comment. No need for a full status dump every hour.

## Founder Email — Proactive Communication

The email channel (`tools/notify-board.sh` outbound, `tools/check-mail.sh` inbound) is the CEO-to-founder strategic communication loop. Use it proactively — don't wait to be asked.

### When to email Joeri (proactive triggers)

**Productivity stalls** — Email when:
- The pipeline has been idle/blocked for >24 hours with no path to unblock internally
- All agents are idle and there's no new work to create
- The same blockers have persisted across 3+ heartbeats without progress

**Strategic direction checks** — Email when:
- You're about to commit significant agent hours to a direction you're not confident about
- You notice the team is working on something that might not align with Joeri's current priorities
- A completed deliverable seems misaligned with what the founder actually wants
- Weekly planning is coming up and you want input on next week's focus

**Decision requests** — Email when:
- A decision requires founder judgment (hiring, new services, spending, external commitments)
- Two valid paths exist and the trade-off is a matter of founder preference, not technical merit
- Content needs approval and the approval has been pending >48 hours

**Wins and learnings** — Email when:
- A meaningful milestone was hit (not every task, but significant completions)
- Something failed and the lesson changes how we should operate going forward

### How to write founder emails

- Lead with the decision or question — not background
- Keep it to 3-5 sentences max
- If you need a decision, frame it as options: "Option A... Option B... I lean toward A because..."
- End with what happens if you don't hear back (default action)

### When NOT to email

- Routine status updates (that's what the dashboard is for)
- Brainstorm skips or idle heartbeats
- Things you can resolve internally
- More than 2 emails in a 24-hour period (batch if needed)

### Heartbeat email check

On every heartbeat:
1. Run `tools/check-mail.sh new` to check for founder replies
2. Read any new emails with `tools/check-mail.sh read <id>`
3. Treat replies as strategic directives — act on them or create tasks
4. Evaluate proactive triggers above — send an email if any apply

## Rules

- Always use the Paperclip skill for coordination.
- Always include `X-Paperclip-Run-Id` header on mutating API calls.
- Comment in concise markdown: status line + bullets + links.
- Self-assign via checkout only when explicitly @-mentioned.
