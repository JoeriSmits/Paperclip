---
type: tacit-knowledge
agent: Oscar
tags: [memory, patterns]
---

# Tacit Knowledge

## Joeri's Financial Situation
- ING betaalrekening: primaire rekening
- AMEX creditcard: secundair, billing cycle sluit op de 20e
- Bufferdoel: €10.000
- Huidige fase: Fase 1 (buffer opbouwen)
- Salaris: ~€4.343 netto/maand, elke 24e (Webbio)

## Vaste Lasten (~€2.524/maand)
- Huur: €1.262,97/maand (Stienstra Wonen)
- ING Lening 1: €263,40/maand (restschuld ~€2.000, afgelost ~okt 2026)
- ING Lening 2: €219,50/maand (restschuld ~€2.000, afgelost ~sep 2026)
- Totaal leningen: €482,90/maand -- beide bijna klaar
- Zorgverzekering: €151,25/maand (Menzis)
- Energie: €195,00/maand (Vattenfall)
- KPN (internet): €56,29/maand
- SIMYO (telefoon): €28,50/maand
- Belastingdienst: €61,00/maand
- BSR (gemeentebelasting): €111,84/maand
- Centraal Beheer (woon+reis+rechtsbijstand): €47,19/maand
- Motorverzekering: €55,00/maand
- Volleybal AETOS: €27,00/maand
- Videoland: €5,99/maand
- YouTube Premium: €4,34/maand (gedeeld)
- PayPal (abonnement): €13,59/maand
- ING bankkosten: €4,00/maand
- Vitens (water): €17,00/maand
- AMEX incasso: elke 25e (~€580/cyclus)

## Spaardoelen & Budget
- Vrij na vaste lasten: ~€1.819/maand
- Buffer inleg: €245/week = ~€1.062/maand (doel eind 2026)
- Creditcard pot inleg: ~€400/maand (buffer voor AMEX)
- Auto (tanken + onderhoud): €150/week = ~€650/maand (aparte pot)
- SkyDemon: €154/jaar (navigatie-app vliegen)
- Vlieguren: ~1 uur/maand = ~€150-€180/maand via AMEX

## Patronen
- Joeri spaart actief naar potten
- Plex verhuur inkomen: ~€10/maand
- AMEX cyclus kan voor roodstand zorgen als timing slecht is
- Leningen worden beide afgelost medio 2026 -- daarna +€483/maand vrij

## Transaction Categories
INKOMEN_FREELANCE, INKOMEN_OVERIG, VAST_HUUR, VAST_VERZEKERING, VAST_ABONNEMENT, VAST_UTILITIES, VAST_OVERIG, VAR_BOODSCHAPPEN, VAR_HORECA, VAR_TRANSPORT, VAR_SHOPPING, VAR_GEZONDHEID, VAR_VRIJE_TIJD, VAR_OVERIG, SPAAR_BUFFER, SPAAR_INVESTERING

## Data Source
- GoCardless Bank Account Data API (ING) -- read-only
- Output: JSON snapshots with netPosition, bufferGoal, bufferProgress, phase tracking, streak, prognosis, accounts, cashflow, transactions

## My Role
- I'm Oscar, Personal CFO. I report to Nox (CEO/orchestrator).
- I track income, expenses, cash flow, buffer progress.
- I speak Dutch and think in euros.
- Financial data is private -- never share with other agents. Only with Joeri.
- Ask Joeri when unsure about categorization.
