---
type: dashboard
tags: [dashboard, projects]
---

# Projects & Resources

## Active Projects

```dataview
TABLE agent AS "Owner", tags AS "Tags"
WHERE type = "project"
SORT file.name ASC
```

## Resources

```dataview
TABLE agent AS "Agent", tags AS "Tags"
WHERE type = "resource"
SORT agent ASC, file.name ASC
```
