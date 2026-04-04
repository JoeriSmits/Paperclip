# Handleiding: Transcript toevoegen aan Obsidian vault

**Tijdsinvestering:** ~5 minuten na een vergadering

---

## Stap 1: Maak een nieuw bestand aan

Ga naar de map: **`Content/Transcripts/`**

Maak een nieuw bestand aan met de naamconventie:

```
YYYY-MM-DD-korte-beschrijving.md
```

Voorbeeld: `2026-04-10-klantgesprek-api-strategie.md`

---

## Stap 2: Voeg frontmatter toe

Plak dit bovenaan het bestand en vul de velden in:

```yaml
---
type: transcript
date: 2026-04-10
source: meeting
participants: [Joeri, Naam2, Naam3]
topics: [onderwerp1, onderwerp2]
tags: [transcript]
---
```

**Velduitleg:**

| Veld | Wat zet je er in | Voorbeeld |
|---|---|---|
| `type` | Altijd `transcript` | `transcript` |
| `date` | Datum van de vergadering (YYYY-MM-DD) | `2026-04-10` |
| `source` | Soort opname | `meeting`, `podcast`, `interview`, `video` |
| `participants` | Deelnemers (lijst) | `[Joeri, Klant, MT-lid]` |
| `topics` | Hoofdonderwerpen (lijst) | `[AI tooling, deployment, planning]` |
| `tags` | Altijd `[transcript]` toevoegen | `[transcript, klant]` |

---

## Stap 3: Schrijf de inhoud

Gebruik deze structuur:

```markdown
# YYYY-MM-DD Korte titel van de vergadering

## Context

Schrijf in 2-3 zinnen: wat was dit, wie was erbij, wat was het doel?

## Transcript

Schrijf de kernmomenten op. Geen woordelijk verslag nodig — dialoogfragmenten, beslissingen, en scherpe uitspraken. Wat iemand letterlijk zei is waardevoller dan een samenvatting.

**Joeri:** "..."
**Naam:** "..."

## Key Takeaways

- Bulletpoint met de belangrijkste conclusie
- Iets wat verrassend was of anders dan verwacht
- Een quote of one-liner die blijft hangen
```

**Vuistregel:** Context + 3-5 dialoogfragmenten + 3-5 takeaways is genoeg. Volledigheid is niet het doel — bruikbaarheid wel.

---

## Voorbeeld

Zie: `Content/Transcripts/2026-04-01-webbio-ai-tooling-sessie.md`

Dat bestand heeft de juiste structuur en is door Rex gebruikt voor LinkedIn content-analyse.

---

## Hoe gebruikt Rex dit?

Na het toevoegen van een transcript kan Rex:
- LinkedIn-hooks voorstellen op basis van echte ervaringen
- Patronen zien over meerdere vergaderingen heen
- Posts schrijven vanuit jouw stem, niet vanuit abstracte claims

Rex scant de vault bij elke wekelijkse content-cyclus. Je hoeft Rex niet te pingen — het transcript wordt vanzelf meegenomen.
