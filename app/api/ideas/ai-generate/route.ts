
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { prompt, context } = body;

    if (!prompt) {
      return NextResponse.json(
        { error: 'Prompt is required' },
        { status: 400 }
      );
    }

    const systemPrompt = `You are a creative brainstorming assistant. Generate innovative and practical ideas based on the user's request. 
    
    Respond with a JSON object with the following structure:
    {
      "ideas": [
        {
          "title": "Idea Title",
          "description": "Detailed description of the idea",
          "category": "Category name",
          "tags": ["tag1", "tag2", "tag3"]
        }
      ]
    }
    
    Generate exactly 3 unique and creative ideas. Make sure each idea has a catchy title, comprehensive description, appropriate category, and relevant tags.
    Respond with raw JSON only. Do not include code blocks, markdown, or any other formatting.`;

    const userMessage = context 
      ? `Generate ideas for: ${prompt}\n\nAdditional context: ${context}`
      : `Generate ideas for: ${prompt}`;

    const response = await fetch('https://apps.abacus.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.ABACUSAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4.1-mini',
        messages: [
          { role: 'system', content: systemPrompt },
          { role: 'user', content: userMessage }
        ],
        stream: true,
        max_tokens: 2000,
        response_format: { type: "json_object" }
      }),
    });

    if (!response?.ok) {
      throw new Error('LLM API request failed');
    }

    const stream = new ReadableStream({
      async start(controller) {
        const reader = response?.body?.getReader();
        const decoder = new TextDecoder();
        const encoder = new TextEncoder();
        
        if (!reader) {
          controller.error(new Error('Response body is not readable'));
          return;
        }

        let buffer = '';
        let partialRead = '';

        try {
          while (true) {
            const { done, value } = await reader.read();
            if (done) break;

            partialRead += decoder.decode(value, { stream: true });
            let lines = partialRead.split('\n');
            partialRead = lines.pop() ?? '';

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6);
                if (data === '[DONE]') {
                  try {
                    const finalResult = JSON.parse(buffer);
                    const finalData = JSON.stringify({
                      status: 'completed',
                      result: finalResult
                    });
                    controller.enqueue(encoder.encode(`data: ${finalData}\n\n`));
                  } catch (e) {
                    console.error('Failed to parse final JSON:', e);
                  }
                  controller.close();
                  return;
                }
                try {
                  const parsed = JSON.parse(data);
                  buffer += parsed?.choices?.[0]?.delta?.content || '';
                  const progressData = JSON.stringify({
                    status: 'processing',
                    message: 'Generating ideas'
                  });
                  controller.enqueue(encoder.encode(`data: ${progressData}\n\n`));
                } catch (e) {
                  // Skip invalid JSON
                }
              }
            }
          }
        } catch (error) {
          console.error('Stream error:', error);
          controller.error(error);
        }
      },
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });
  } catch (error) {
    console.error('Error generating ideas:', error);
    return NextResponse.json(
      { error: 'Failed to generate ideas' },
      { status: 500 }
    );
  }
}
