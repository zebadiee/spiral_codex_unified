
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

// GET all ideas
export async function GET() {
  try {
    const ideas = await prisma.idea.findMany({
      include: {
        tags: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    return NextResponse.json({ ideas: ideas ?? [] });
  } catch (error) {
    console.error('Error fetching ideas:', error);
    return NextResponse.json(
      { error: 'Failed to fetch ideas' },
      { status: 500 }
    );
  }
}

// POST create new idea
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, description, category, tags } = body;

    if (!title || !description) {
      return NextResponse.json(
        { error: 'Title and description are required' },
        { status: 400 }
      );
    }

    // Handle tags
    const tagObjects = await Promise.all(
      (tags ?? []).map(async (tagName: string) => {
        const existingTag = await prisma.tag.findUnique({
          where: { name: tagName },
        });

        if (existingTag) {
          return { id: existingTag.id };
        }

        const newTag = await prisma.tag.create({
          data: { name: tagName },
        });

        return { id: newTag.id };
      })
    );

    const idea = await prisma.idea.create({
      data: {
        title,
        description,
        category: category || null,
        tags: {
          connect: tagObjects,
        },
      },
      include: {
        tags: true,
      },
    });

    return NextResponse.json({ idea }, { status: 201 });
  } catch (error) {
    console.error('Error creating idea:', error);
    return NextResponse.json(
      { error: 'Failed to create idea' },
      { status: 500 }
    );
  }
}
