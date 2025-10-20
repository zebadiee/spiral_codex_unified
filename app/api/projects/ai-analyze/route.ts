
import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { projectName, projectDescription, requirements, analysisType } = body;

    if (!projectName || !projectDescription || !analysisType) {
      return NextResponse.json(
        { error: 'Project name, description, and analysis type are required' },
        { status: 400 }
      );
    }

    let systemPrompt = '';
    let userMessage = '';

    switch (analysisType) {
      case 'requirements':
        systemPrompt = `You are a project planning expert. Analyze the project and generate comprehensive requirements.
        
        Respond with a JSON object with this structure:
        {
          "analysis": "Detailed requirements analysis as formatted text"
        }
        
        Format the analysis with clear sections using markdown-style formatting:
        - Use **bold** for section headers
        - Use numbered or bulleted lists for items
        - Be specific and actionable
        - Include functional and non-functional requirements
        
        Respond with raw JSON only. Do not include code blocks, markdown, or any other formatting.`;
        
        userMessage = `Project: ${projectName}\n\nDescription: ${projectDescription}\n\nGenerate detailed requirements for this project.`;
        break;
      
      case 'architecture':
        systemPrompt = `You are a software architecture expert. Analyze the project and suggest technical architecture.
        
        Respond with a JSON object with this structure:
        {
          "analysis": "Detailed architecture analysis as formatted text"
        }
        
        Include: technology stack, system components, data flow, scalability considerations, and best practices.
        
        Respond with raw JSON only. Do not include code blocks, markdown, or any other formatting.`;
        
        userMessage = `Project: ${projectName}\n\nDescription: ${projectDescription}\n\nRequirements: ${requirements || 'Not specified'}\n\nSuggest technical architecture for this project.`;
        break;
      
      case 'timeline':
        systemPrompt = `You are a project management expert. Analyze the project and create a realistic timeline.
        
        Respond with a JSON object with this structure:
        {
          "analysis": "Detailed timeline analysis as formatted text"
        }
        
        Include phases, milestones, estimated durations, and dependencies.
        
        Respond with raw JSON only. Do not include code blocks, markdown, or any other formatting.`;
        
        userMessage = `Project: ${projectName}\n\nDescription: ${projectDescription}\n\nRequirements: ${requirements || 'Not specified'}\n\nCreate a project timeline.`;
        break;
      
      case 'risks':
        systemPrompt = `You are a risk management expert. Analyze the project and identify potential risks.
        
        Respond with a JSON object with this structure:
        {
          "analysis": "Detailed risk analysis as formatted text"
        }
        
        Include: risk identification, impact assessment, probability, and mitigation strategies.
        
        Respond with raw JSON only. Do not include code blocks, markdown, or any other formatting.`;
        
        userMessage = `Project: ${projectName}\n\nDescription: ${projectDescription}\n\nRequirements: ${requirements || 'Not specified'}\n\nIdentify project risks and mitigation strategies.`;
        break;
      
      default:
        return NextResponse.json(
          { error: 'Invalid analysis type' },
          { status: 400 }
        );
    }

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
                    message: 'Analyzing project'
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
    console.error('Error analyzing project:', error);
    return NextResponse.json(
      { error: 'Failed to analyze project' },
      { status: 500 }
    );
  }
}
