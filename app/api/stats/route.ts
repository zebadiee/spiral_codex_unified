
import { NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

export async function GET() {
  try {
    const [activeIdeas, activeProjects, completedProjects, totalTags] = await Promise.all([
      prisma.idea.count({ where: { status: 'active' } }),
      prisma.project.count({ where: { status: { in: ['planning', 'in-progress'] } } }),
      prisma.project.count({ where: { status: 'completed' } }),
      prisma.tag.count(),
    ]);

    return NextResponse.json({
      stats: {
        activeIdeas: activeIdeas ?? 0,
        activeProjects: activeProjects ?? 0,
        completedProjects: completedProjects ?? 0,
        totalTags: totalTags ?? 0,
      },
    });
  } catch (error) {
    console.error('Error fetching stats:', error);
    return NextResponse.json(
      { error: 'Failed to fetch stats' },
      { status: 500 }
    );
  }
}
