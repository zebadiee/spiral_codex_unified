
'use client';

import { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { 
  ArrowLeft, 
  Edit, 
  Save, 
  Sparkles,
  FileText,
  Calendar,
  Target,
  CheckCircle2
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { formatDate, getStatusColor } from '@/lib/utils';
import type { Project } from '@/lib/types';

interface ProjectDetailClientProps {
  projectId: string;
}

export function ProjectDetailClient({ projectId }: ProjectDetailClientProps) {
  const router = useRouter();
  const [project, setProject] = useState<Project | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  
  // Edit form state
  const [editData, setEditData] = useState<Partial<Project>>({});

  const fetchProject = useCallback(async () => {
    if (!projectId) {
      setIsLoading(false);
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`/api/projects/${projectId}`);
      if (response?.ok) {
        const data = await response.json();
        setProject(data?.project);
        setEditData(data?.project ?? {});
      }
    } catch (error) {
      console.error('Failed to fetch project:', error);
    } finally {
      setIsLoading(false);
    }
  }, [projectId]);

  useEffect(() => {
    fetchProject();
  }, [fetchProject]);

  const handleSave = async () => {
    setIsSaving(true);
    try {
      const response = await fetch(`/api/projects/${projectId}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(editData),
      });
      
      if (response?.ok) {
        await fetchProject();
        setIsEditing(false);
      }
    } catch (error) {
      console.error('Failed to update project:', error);
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-blue-500"></div>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen">
        <h2 className="text-2xl font-bold mb-4">Project not found</h2>
        <Button onClick={() => router.push('/inception')}>
          Back to Projects
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex items-center justify-between"
      >
        <div className="flex items-center gap-4">
          <Button
            variant="outline"
            size="icon"
            onClick={() => router.push('/inception')}
          >
            <ArrowLeft className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold font-[family-name:var(--font-orbitron)] neon-text-blue">
              {project?.name}
            </h1>
            <div className="flex items-center gap-2 mt-1">
              {project?.type && <Badge variant="outline">{project.type}</Badge>}
              <div className={`px-2 py-0.5 rounded text-xs ${getStatusColor(project?.status)}`}>
                {project?.status?.replace?.('-', ' ')}
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex gap-2">
          {isEditing ? (
            <>
              <Button
                variant="outline"
                onClick={() => {
                  setIsEditing(false);
                  setEditData(project);
                }}
                disabled={isSaving}
              >
                Cancel
              </Button>
              <Button onClick={handleSave} disabled={isSaving}>
                <Save className="h-4 w-4 mr-2" />
                {isSaving ? 'Saving...' : 'Save Changes'}
              </Button>
            </>
          ) : (
            <Button onClick={() => setIsEditing(true)}>
              <Edit className="h-4 w-4 mr-2" />
              Edit
            </Button>
          )}
        </div>
      </motion.div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Description */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-400" />
                Description
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editData?.description ?? ''}
                  onChange={(e) => setEditData({ ...editData, description: e?.target?.value })}
                  rows={4}
                />
              ) : (
                <p className="text-slate-400">{project?.description}</p>
              )}
            </CardContent>
          </Card>

          {/* Requirements */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-blue-400" />
                Requirements
              </CardTitle>
            </CardHeader>
            <CardContent>
              {isEditing ? (
                <Textarea
                  value={editData?.requirements ?? ''}
                  onChange={(e) => setEditData({ ...editData, requirements: e?.target?.value })}
                  rows={8}
                  placeholder="Project requirements..."
                />
              ) : project?.requirements ? (
                <div className="text-slate-400 whitespace-pre-wrap">{project.requirements}</div>
              ) : (
                <p className="text-slate-500 italic">No requirements specified yet</p>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column - Meta Info */}
        <div className="space-y-6">
          {/* Progress */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Target className="h-5 w-5 text-blue-400" />
                Progress
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex items-center justify-between text-sm mb-2">
                  <span className="text-slate-400">Completion</span>
                  <span className="text-blue-400 font-semibold">
                    {project?.completionPercentage ?? 0}%
                  </span>
                </div>
                <div className="h-3 bg-slate-800 rounded-full overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${project?.completionPercentage ?? 0}%` }}
                    transition={{ duration: 1 }}
                    className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
                  />
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Timeline */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="h-5 w-5 text-blue-400" />
                Timeline
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <label className="text-xs text-slate-400">Duration</label>
                {isEditing ? (
                  <Input
                    value={editData?.estimatedDuration ?? ''}
                    onChange={(e) => setEditData({ ...editData, estimatedDuration: e?.target?.value })}
                    placeholder="e.g., 3 months"
                    className="mt-1"
                  />
                ) : (
                  <p className="text-sm mt-1">{project?.estimatedDuration || 'Not specified'}</p>
                )}
              </div>
              
              <div>
                <label className="text-xs text-slate-400">Target Date</label>
                {isEditing ? (
                  <Input
                    type="date"
                    value={editData?.targetDate ? new Date(editData.targetDate).toISOString().split('T')[0] : ''}
                    onChange={(e) => setEditData({ ...editData, targetDate: e?.target?.value ? new Date(e.target.value) : undefined })}
                    className="mt-1"
                  />
                ) : (
                  <p className="text-sm mt-1">{formatDate(project?.targetDate)}</p>
                )}
              </div>
              
              <div>
                <label className="text-xs text-slate-400">Created</label>
                <p className="text-sm mt-1">{formatDate(project?.createdAt)}</p>
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          {!isEditing && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Sparkles className="h-5 w-5 text-blue-400" />
                  Quick Actions
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <Sparkles className="h-4 w-4 mr-2" />
                  Generate Architecture
                </Button>
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <Calendar className="h-4 w-4 mr-2" />
                  Create Timeline
                </Button>
                <Button variant="outline" className="w-full justify-start" size="sm">
                  <Target className="h-4 w-4 mr-2" />
                  Analyze Risks
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
