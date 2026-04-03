---
entity: content-learnings
type: resource
agent: Rex
description: Accumulated learnings from published posts and Joeri's feedback
tags: [resource, content]
---

# Content Learnings

## Tone Corrections (from Joeri)
1. **OpenClaw language**: Joeri works WITH OpenClaw, not ON it. Use "ik gebruik", "ik werk met" -- never "ik bouw aan" or "ik werk aan".
2. **Experience, not discovery**: Joeri does this already. Tone must be confident from practice. Avoid "ik denk dat", "ik zie", "zou kunnen", "misschien", "ik ontdek".
3. **No "kijk mij nou"**: Self-congratulatory openings are rejected.
4. **No "wijsneuzerig"**: Know-it-all tone in replies is rejected. Respond as colleague.
5. **Inviting > dismissive**: "De chatbox was stap een. Agents zijn de volgende." NOT "Prompting is 2023."
6. **CTAs invite, not judge**: "Waar sta jij in deze verschuiving?" NOT "Ben jij al verder dan de chatbox?"
7. **3 iterations -> 1**: Persona document in SOUL.md was created to reduce post iterations from 3 to 1.

## Format Learnings
- "Nieuws + take" works best when Joeri has direct experience with the topic.
- Personal story + photo works well for engagement (coffee maker post beat news post on reactions).
- Hooks must have substance -- shallow hooks are rejected ("niet heel veel toegevoegde waarde").
- Complete picture needed before drafting -- no rapid-fire posts on each separate hook.
- Trend research is non-negotiable for relevance.

## Post Performance Insights
- Post 1 (AI agents, 25-03): 868 impressions, 10 reactions. Security discussion in comments was valuable.
- Post 2 (coffee maker, 01-04): 652 impressions, 14 reactions. Personal/light + photo = higher engagement rate.
- Joeri's security take resonated: nightly pentests, no external plugins (remakes them), data exposure principle.

## Buffer API Learnings
- GraphQL API requires `mode` (ShareMode enum) + `schedulingType` as required fields.
- `saveToDraft: true` is an additional boolean, not a replacement for `mode`.
- Correct draft payload: `{ channelId, text, schedulingType: "automatic", mode: "addToQueue", saveToDraft: true }`
- No update mutation available -- delete + create for changes.
- Analytics NOT available via API.
- Image upload via Imgur, then pass URL in `assets.images`.
