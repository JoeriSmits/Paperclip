const BUFFER_API_URL = "https://graph.bufferapp.com/graphql";

async function bufferQuery(query: string, variables?: Record<string, unknown>) {
  const apiKey = process.env.BUFFER_API_KEY;
  if (!apiKey) {
    throw new Error("BUFFER_API_KEY is not configured");
  }

  const res = await fetch(BUFFER_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${apiKey}`,
    },
    body: JSON.stringify({ query, variables }),
  });

  if (!res.ok) {
    throw new Error(`Buffer API error: ${res.status}`);
  }

  return res.json();
}

// GET: discover channels
export async function GET() {
  try {
    const data = await bufferQuery(`
      query {
        channels {
          id
          name
          service
          avatar
        }
      }
    `);
    return Response.json(data);
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Buffer API error" },
      { status: 500 }
    );
  }
}

// POST: schedule a post
export async function POST(request: Request) {
  const { channelId, text } = await request.json();

  if (!text) {
    return Response.json({ error: "text is required" }, { status: 400 });
  }

  try {
    // If no channelId, discover the first LinkedIn channel
    let targetChannel = channelId;
    if (!targetChannel) {
      const channelsData = await bufferQuery(`
        query {
          channels {
            id
            service
          }
        }
      `);
      const linkedIn = channelsData?.data?.channels?.find(
        (c: { service: string }) => c.service === "linkedin"
      );
      if (!linkedIn) {
        return Response.json({ error: "No LinkedIn channel found in Buffer" }, { status: 404 });
      }
      targetChannel = linkedIn.id;
    }

    const data = await bufferQuery(
      `
      mutation CreatePost($input: CreatePostInput!) {
        createPost(input: $input) {
          post {
            id
            text
            scheduledAt
            status
          }
        }
      }
    `,
      {
        input: {
          channelIds: [targetChannel],
          text,
          schedulingType: "automatic",
        },
      }
    );

    return Response.json(data);
  } catch (error) {
    return Response.json(
      { error: error instanceof Error ? error.message : "Buffer API error" },
      { status: 500 }
    );
  }
}
