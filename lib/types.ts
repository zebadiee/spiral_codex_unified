
// ============================================
// Database Entity Types
// ============================================

export interface Idea {
  id: string;
  title: string;
  description: string;
  category?: string | null;
  tags?: Tag[];
  status: string;
  aiSuggestions?: string | null;
  exportedToProjectId?: string | null;
  createdAt: Date;
  updatedAt: Date;
}

export interface Tag {
  id: string;
  name: string;
  color: string;
  createdAt: Date;
}

export interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  type?: string | null;
  requirements?: string | null;
  technicalSpecs?: string | null;
  architecture?: string | null;
  estimatedDuration?: string | null;
  startDate?: Date | null;
  targetDate?: Date | null;
  currentPhase: string;
  completionPercentage: number;
  milestones?: Milestone[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Milestone {
  id: string;
  title: string;
  description?: string | null;
  status: string;
  dueDate?: Date | null;
  completedAt?: Date | null;
  projectId: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface ActivityLog {
  id: string;
  module: string;
  action: string;
  entityType: string;
  entityId: string;
  details?: string | null;
  createdAt: Date;
}

// ============================================
// API Request/Response Types
// ============================================

export interface CreateIdeaRequest {
  title: string;
  description: string;
  category?: string;
  tags?: string[];
}

export interface UpdateIdeaRequest {
  title?: string;
  description?: string;
  category?: string;
  tags?: string[];
  status?: string;
  aiSuggestions?: string;
}

export interface AIIdeaSuggestionRequest {
  ideaTitle: string;
  ideaDescription: string;
  context?: string;
}

export interface CreateProjectRequest {
  name: string;
  description: string;
  type?: string;
  requirements?: string;
  fromIdeaId?: string;
}

export interface UpdateProjectRequest {
  name?: string;
  description?: string;
  status?: string;
  type?: string;
  requirements?: string;
  technicalSpecs?: string;
  architecture?: string;
  estimatedDuration?: string;
  startDate?: string;
  targetDate?: string;
  currentPhase?: string;
  completionPercentage?: number;
}

export interface AIProjectAnalysisRequest {
  projectName: string;
  projectDescription: string;
  requirements?: string;
  analysisType: 'requirements' | 'architecture' | 'timeline' | 'risks';
}

// ============================================
// UI Component Types
// ============================================

export interface WorkflowStage {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'active' | 'completed' | 'locked' | 'available';
  path: string;
}

export interface HUDStats {
  activeIdeas: number;
  activeProjects: number;
  completedProjects: number;
  totalTags: number;
}

export interface NotificationMessage {
  id: string;
  type: 'success' | 'error' | 'info' | 'warning';
  title: string;
  message: string;
  timestamp: Date;
}

// ============================================
// Utility Types
// ============================================

export type ModuleType = 'brainstorming' | 'inception' | 'creation' | 'deployment' | 'subscription';

export type IdeaStatus = 'active' | 'archived' | 'exported';

export type ProjectStatus = 'planning' | 'in-progress' | 'completed' | 'on-hold';

export type ProjectPhase = 'inception' | 'creation' | 'deployment' | 'subscription';

export type MilestoneStatus = 'pending' | 'in-progress' | 'completed';
