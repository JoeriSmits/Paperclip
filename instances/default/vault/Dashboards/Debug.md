---
type: dashboard
---

# Debug - Dataview Test

## 1. Show ALL files in vault (no filter)

```dataview
LIST
LIMIT 10
```

## 2. Show all files with ANY frontmatter type

```dataview
TABLE type, agent
WHERE type != null
```

## 3. Simple test - files with tags

```dataview
TABLE tags
WHERE tags != null
```
