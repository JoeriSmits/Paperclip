# TOOLS.md -- Sage Available Tools

## Paperclip API (via `paperclip` skill)

Your primary tool. Use it to:

- Check inbox and assignments
- Create tasks and subtasks (always set parentId + goalId)
- Assign tasks to team members
- Update task status and add comments
- Review company goals and projects
- Check agent workload and status

## Memory (via `para-memory-files` skill)

Store and recall knowledge:

- Daily notes for session logs
- PARA knowledge graph for persistent facts
- MEMORY.md for tacit knowledge and patterns

## Task Coordination Patterns

- **Creating work**: POST /api/companies/{companyId}/issues with title, description, assigneeAgentId, goalId
- **Checking goals**: GET /api/companies/{companyId}/dashboard for overview
- **Monitoring team**: GET /api/companies/{companyId}/agents for agent status
