---
type: dashboard
tags: [dashboard, entities]
---

# People & Companies

## People

```dataview
TABLE agent AS "Known by", file.folder AS "Location"
WHERE type = "entity" AND contains(tags, "people")
SORT file.name ASC
```

## Companies

```dataview
TABLE agent AS "Known by", file.folder AS "Location"
WHERE type = "entity" AND contains(tags, "company")
SORT file.name ASC
```
