
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { 
  MoreVertical, 
  Edit, 
  Trash2, 
  Eye, 
  Calendar,
  CheckCircle2
} from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { formatDate, truncate, getStatusColor } from '@/lib/utils';
import type { Project } from '@/lib/types';

interface ProjectCardProps {
  project: Project;
  index: number;
  onUpdate: () => void;
  onDelete: () => void;
}

export function ProjectCard({ project, index, onUpdate, onDelete }: ProjectCardProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this project?')) return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`/api/projects/${project?.id}`, {
        method: 'DELETE',
      });
      
      if (response?.ok) {
        onDelete();
      }
    } catch (error) {
      console.error('Failed to delete project:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleView = () => {
    router.push(`/inception/${project?.id}`);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05 }}
      whileHover={{ y: -4 }}
      className="group"
    >
      <Card className="h-full hover-lift hover:border-blue-500/50 transition-all duration-300 relative overflow-hidden">
        {/* Gradient overlay */}
        <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 via-transparent to-purple-500/5 opacity-0 group-hover:opacity-100 transition-opacity" />
        
        <CardHeader className="relative">
          <div className="flex items-start justify-between gap-2">
            <div className="flex-1">
              <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-blue-400 transition-colors cursor-pointer" onClick={handleView}>
                {project?.name ?? 'Untitled Project'}
              </h3>
              {project?.type && (
                <Badge variant="outline" className="mt-2">
                  {project.type}
                </Badge>
              )}
            </div>
            
            <div className="relative">
              <Button
                size="icon"
                variant="ghost"
                onClick={() => setShowMenu(!showMenu)}
                className="h-8 w-8"
              >
                <MoreVertical className="h-4 w-4" />
              </Button>
              
              {showMenu && (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="absolute right-0 top-full mt-1 w-48 glass rounded-lg border border-blue-500/20 shadow-xl z-10"
                >
                  <button
                    onClick={() => {
                      handleView();
                      setShowMenu(false);
                    }}
                    className="w-full px-4 py-2 text-sm text-left hover:bg-blue-500/10 flex items-center gap-2 rounded-t-lg"
                  >
                    <Eye className="h-4 w-4" />
                    View Details
                  </button>
                  <button
                    onClick={() => {
                      handleDelete();
                      setShowMenu(false);
                    }}
                    disabled={isDeleting}
                    className="w-full px-4 py-2 text-sm text-left hover:bg-red-500/10 text-red-400 flex items-center gap-2 rounded-b-lg"
                  >
                    <Trash2 className="h-4 w-4" />
                    {isDeleting ? 'Deleting...' : 'Delete'}
                  </button>
                </motion.div>
              )}
            </div>
          </div>
        </CardHeader>
        
        <CardContent className="relative space-y-3">
          <p className="text-sm text-slate-400 line-clamp-3">
            {truncate(project?.description, 150)}
          </p>
          
          {/* Progress Bar */}
          <div>
            <div className="flex items-center justify-between text-xs mb-1">
              <span className="text-slate-400">Progress</span>
              <span className="text-blue-400 font-semibold">
                {project?.completionPercentage ?? 0}%
              </span>
            </div>
            <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${project?.completionPercentage ?? 0}%` }}
                transition={{ duration: 1, delay: 0.2 }}
                className="h-full bg-gradient-to-r from-blue-500 to-purple-500"
              />
            </div>
          </div>
          
          {/* Meta Info */}
          <div className="flex items-center gap-4 text-xs text-slate-500">
            {project?.targetDate && (
              <div className="flex items-center gap-1">
                <Calendar className="h-3 w-3" />
                {formatDate(project.targetDate)}
              </div>
            )}
            {project?.milestones && (
              <div className="flex items-center gap-1">
                <CheckCircle2 className="h-3 w-3" />
                {project.milestones.filter(m => m?.status === 'completed')?.length ?? 0} / {project.milestones.length ?? 0}
              </div>
            )}
          </div>
        </CardContent>
        
        <CardFooter className="relative flex items-center justify-between">
          <div className={`px-2 py-1 rounded text-xs ${getStatusColor(project?.status)}`}>
            {project?.status?.replace?.('-', ' ')}
          </div>
          
          <Button
            size="sm"
            variant="ghost"
            onClick={handleView}
            className="gap-1"
          >
            View
            <Eye className="h-3 w-3" />
          </Button>
        </CardFooter>
      </Card>
    </motion.div>
  );
}
