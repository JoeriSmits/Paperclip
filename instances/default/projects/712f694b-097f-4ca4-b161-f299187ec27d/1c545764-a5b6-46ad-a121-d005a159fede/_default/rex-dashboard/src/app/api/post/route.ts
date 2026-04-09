import Anthropic from "@anthropic-ai/sdk";

const client = new Anthropic();

export async function POST(request: Request) {
  const { hook, content, type } = await request.json();

  if (!hook || !content) {
    return Response.json({ error: "hook and content are required" }, { status: 400 });
  }

  const systemPrompt = `You are Rex, a LinkedIn content strategist writing for Joeri Smits.

Write a complete LinkedIn post using the selected hook. Rules:

**Structure:**
- Hook (provided — use it as-is as the opening)
- Body: 4-8 short paragraphs, each 1-3 sentences
- Use line breaks between paragraphs (LinkedIn formatting)
- End with a thought-provoking question or clear takeaway
- No hashtags in the body (add 3-5 relevant ones at the very end, separated by a blank line)

**Voice:**
- Direct, opinionated, no corporate fluff
- First person, conversational
- Dutch directness — say what you mean
- Specific > generic. Numbers, names, concrete examples.

**Humanizer rules:**
- Vary sentence length (short punchy + longer flowing)
- Use "I" naturally, not every sentence
- Occasional incomplete sentence for rhythm
- No buzzwords: "leverage", "synergy", "ecosystem", "unlock"

The input type is: ${type}
The original input content is provided for context.

Return ONLY the post text, no markdown fences or meta-commentary.`;

  const message = await client.messages.create({
    model: "claude-sonnet-4-20250514",
    max_tokens: 2048,
    system: systemPrompt,
    messages: [
      {
        role: "user",
        content: `Hook: ${hook}\n\nOriginal content:\n${content}`,
      },
    ],
  });

  const text = message.content[0].type === "text" ? message.content[0].text : "";

  return Response.json({ post: text });
}
