
import { NextRequest, NextResponse } from 'next/server';
import { PrismaClient } from '@prisma/client';

export const dynamic = 'force-dynamic';

const prisma = new PrismaClient();

// GET all projects
export async function GET() {
  try {
    const projects = await prisma.project.findMany({
      include: {
        milestones: true,
      },
      orderBy: {
        createdAt: 'desc',
      },
    });

    return NextResponse.json({ projects: projects ?? [] });
  } catch (error) {
    console.error('Error fetching projects:', error);
    return NextResponse.json(
      { error: 'Failed to fetch projects' },
      { status: 500 }
    );
  }
}

// POST create new project
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { 
      name, 
      description, 
      type, 
      requirements, 
      estimatedDuration, 
      targetDate 
    } = body;

    if (!name || !description) {
      return NextResponse.json(
        { error: 'Name and description are required' },
        { status: 400 }
      );
    }

    const project = await prisma.project.create({
      data: {
        name,
        description,
        type: type || null,
        requirements: requirements || null,
        estimatedDuration: estimatedDuration || null,
        targetDate: targetDate ? new Date(targetDate) : null,
      },
    });

    return NextResponse.json({ project }, { status: 201 });
  } catch (error) {
    console.error('Error creating project:', error);
    return NextResponse.json(
      { error: 'Failed to create project' },
      { status: 500 }
    );
  }
}
