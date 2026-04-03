---
type: resource
agent: Nox
tags: [integrations]
---

# Integration Configs (from OpenClaw)

## Picnic / ChefClaw
- Auth: `picnic-api` npm package with 2FA (SMS to Joeri)
- Auth key stored: `~/.openclaw/workspace/integrations/picnic-auth.json`
- Script: `~/.openclaw/workspace/projects/chef-claw/fill-cart.mjs`
- Search: `client.catalog.search(query)` returns flat array of products
- Add: `client.cart.addProductToCart(productId, count)`
- Lessons: direct library 50x faster than MCP one-shot calls. Auth key reusable while session valid.
- Quality issues: search can return wrong product type (e.g. dried vs fresh parsley). Needs specific queries.

## Tempo (Hour Logging)
- Config: `~/.openclaw/workspace/integrations/tempo-config.json`
- Jira: webbiohq.atlassian.net, Joeri account ID: 5acf2c62bb811e2b3af8ff53
- GitHub: JoeriSmits, org webbio
- Minimum 7u/dag
- FAC-145 = general internal communication task
- Draft: `~/.openclaw/workspace/integrations/tempo-draft-DATUM.json`
- Reconstruction: GitHub commits > Jira activity > Calendar > FAC-145 filler

## Buffer (LinkedIn Posts)
- Endpoint: https://api.buffer.com (GraphQL)
- Token: $BUFFER_ACCESS_TOKEN
- LinkedIn Channel ID: 69bc68a37be9f8b17173d2e9
- Organization ID: 69bc687f642fef9605e9a89d
- Images: upload via Imgur (Client-ID: 546c25a59c58ad7), then reference URL in Buffer
- No update mutation -- delete + create for changes
- Analytics NOT available via API

## Films & Series
- OMDB API key: "trilogy" (free demo) for movie posters
- TVmaze API for series posters
- Discord buttons: `{"reusable": true, "blocks": [{"type": "actions", "buttons": [...]}]}`
- Only 2025-2026 releases, IMDb 7.0+
- Watchlist: `~/.openclaw/workspace/integrations/watchlist.json`

## News/RSS
- nu.nl blocks scraping -> use RSS feeds
- Reuters blocks direct -> Google News RSS
- Brave Search API not configured -> web_fetch as alternative

## GoCardless (Oscar)
- ING bank read-only access
- Financial data private -- Oscar agent only

## Google
- Calendar + Tasks API: project 611989129571
- gog CLI: joeri@webbio.nl
- Tasks list ID: MDY2NTE0NTE2MDI3MTg4NDM5NDk6MDow

## Smart Home
- HomeWizard Energy Socket: 192.168.2.16 (coffee machine - Profitect Drive)
- Coffee webhook: port 18790, auth X-Token: koffie2026
- Sonos: sonoscli via ~/go/bin/sonos (Woonkamer + Balkon)
