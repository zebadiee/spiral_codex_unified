
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

// GET single idea
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const idea = await prisma.idea.findUnique({
      where: { id: params?.id },
      include: { tags: true },
    });

    if (!idea) {
      return NextResponse.json(
        { error: 'Idea not found' },
        { status: 404 }
      );
    }

    return NextResponse.json({ idea });
  } catch (error) {
    console.error('Error fetching idea:', error);
    return NextResponse.json(
      { error: 'Failed to fetch idea' },
      { status: 500 }
    );
  }
}

// PATCH update idea
export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const body = await request.json();
    const { title, description, category, tags, status, aiSuggestions } = body;

    // Handle tags if provided
    let tagUpdate = {};
    if (tags !== undefined) {
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

      tagUpdate = {
        tags: {
          set: [],
          connect: tagObjects,
        },
      };
    }

    const idea = await prisma.idea.update({
      where: { id: params?.id },
      data: {
        ...(title !== undefined && { title }),
        ...(description !== undefined && { description }),
        ...(category !== undefined && { category }),
        ...(status !== undefined && { status }),
        ...(aiSuggestions !== undefined && { aiSuggestions }),
        ...tagUpdate,
      },
      include: {
        tags: true,
      },
    });

    return NextResponse.json({ idea });
  } catch (error) {
    console.error('Error updating idea:', error);
    return NextResponse.json(
      { error: 'Failed to update idea' },
      { status: 500 }
    );
  }
}

// DELETE idea
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    await prisma.idea.delete({
      where: { id: params?.id },
    });

    return NextResponse.json({ success: true });
  } catch (error) {
    console.error('Error deleting idea:', error);
    return NextResponse.json(
      { error: 'Failed to delete idea' },
      { status: 500 }
    );
  }
}
