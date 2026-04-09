import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

export async function POST(request: Request) {
  const { content, type } = await request.json();

  if (!content || !type) {
    return Response.json({ error: "content and type are required" }, { status: 400 });
  }

  const systemPrompt = `You are Rex, a LinkedIn content strategist. You specialize in writing hooks that stop the scroll.

Given a ${type}, generate exactly 3 hook variants:
1. Curiosity Gap — tease a surprising insight without revealing it
2. Bold Claim — make a strong, contrarian statement
3. Specific Story — open with a concrete, personal-feeling moment

Rules:
- Max 2 lines per hook (LinkedIn shows ~2 lines before "see more")
- No hashtags in hooks
- Use line breaks for rhythm
- Write in Joeri's voice: direct, opinionated, no corporate fluff
- Dutch directness is a feature

Respond in JSON array format:
[
  {"style": "curiosity_gap", "text": "..."},
  {"style": "bold_claim", "text": "..."},
  {"style": "specific_story", "text": "..."}
]

Return ONLY the JSON array, no markdown fences or explanation.`;

  const message = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 1024,
    system: systemPrompt,
    messages: [{ role: "user", content }],
  });

  const text = message.content[0].type === "text" ? message.content[0].text : "";

  try {
    const hooks = JSON.parse(text);
    return Response.json({
      hooks: hooks.map((h: { style: string; text: string }, i: number) => ({
        id: `hook-${Date.now()}-${i}`,
        ...h,
      })),
    });
  } catch {
    return Response.json({ error: "Failed to parse hooks", raw: text }, { status: 500 });
  }
}
