
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { 
  MoreVertical, 
  Edit, 
  Trash2, 
  Archive, 
  Share2, 
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { Card, CardContent, CardFooter, CardHeader } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { EditIdeaDialog } from './edit-idea-dialog';
import { formatRelativeTime, truncate, getStatusColor } from '@/lib/utils';
import type { Idea } from '@/lib/types';

interface IdeaCardProps {
  idea: Idea;
  index: number;
  onUpdate: () => void;
  onDelete: () => void;
}

export function IdeaCard({ idea, index, onUpdate, onDelete }: IdeaCardProps) {
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const handleDelete = async () => {
    if (!confirm('Are you sure you want to delete this idea?')) return;
    
    setIsDeleting(true);
    try {
      const response = await fetch(`/api/ideas/${idea?.id}`, {
        method: 'DELETE',
      });
      
      if (response?.ok) {
        onDelete();
      }
    } catch (error) {
      console.error('Failed to delete idea:', error);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleArchive = async () => {
    try {
      const response = await fetch(`/api/ideas/${idea?.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ status: 'archived' }),
      });
      
      if (response?.ok) {
        onUpdate();
      }
    } catch (error) {
      console.error('Failed to archive idea:', error);
    }
  };

  return (
    <>
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
                <h3 className="font-semibold text-lg line-clamp-2 group-hover:text-blue-400 transition-colors">
                  {idea?.title ?? 'Untitled'}
                </h3>
                {idea?.category && (
                  <Badge variant="outline" className="mt-2">
                    {idea.category}
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
                        setIsEditDialogOpen(true);
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-blue-500/10 flex items-center gap-2 rounded-t-lg"
                    >
                      <Edit className="h-4 w-4" />
                      Edit
                    </button>
                    <button
                      onClick={() => {
                        handleArchive();
                        setShowMenu(false);
                      }}
                      className="w-full px-4 py-2 text-sm text-left hover:bg-blue-500/10 flex items-center gap-2"
                    >
                      <Archive className="h-4 w-4" />
                      Archive
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
          
          <CardContent className="relative">
            <p className="text-sm text-slate-400 line-clamp-3">
              {truncate(idea?.description, 150)}
            </p>
            
            {idea?.tags && idea.tags.length > 0 && (
              <div className="flex flex-wrap gap-1 mt-3">
                {idea.tags.slice(0, 3).map((tag) => (
                  <Badge
                    key={tag?.id}
                    style={{ 
                      backgroundColor: `${tag?.color}20`,
                      borderColor: `${tag?.color}50`,
                      color: tag?.color 
                    }}
                  >
                    {tag?.name}
                  </Badge>
                ))}
                {(idea?.tags?.length ?? 0) > 3 && (
                  <Badge variant="outline">
                    +{idea.tags.length - 3} more
                  </Badge>
                )}
              </div>
            )}
          </CardContent>
          
          <CardFooter className="relative flex items-center justify-between">
            <span className="text-xs text-slate-500">
              {formatRelativeTime(idea?.createdAt)}
            </span>
            
            <div className={`px-2 py-1 rounded text-xs ${getStatusColor(idea?.status)}`}>
              {idea?.status}
            </div>
          </CardFooter>
        </Card>
      </motion.div>

      <EditIdeaDialog
        idea={idea}
        open={isEditDialogOpen}
        onOpenChange={setIsEditDialogOpen}
        onIdeaUpdated={onUpdate}
      />
    </>
  );
}
