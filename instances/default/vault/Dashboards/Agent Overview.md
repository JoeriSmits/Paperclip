---
type: dashboard
tags: [dashboard, agents]
---

# Agent Overview

## Recent Daily Notes

```dataview
TABLE agent AS "Agent", date AS "Date"
WHERE type = "daily-note"
SORT date DESC
LIMIT 20
```

## Knowledge per Agent

```dataview
TABLE agent AS "Agent", type AS "Type", tags AS "Tags"
WHERE agent != null AND type != "daily-note" AND type != "dashboard"
SORT agent ASC, type ASC
```
