
'use client';

import { useState, useEffect } from 'react';
import { Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import type { Idea } from '@/lib/types';

interface EditIdeaDialogProps {
  idea: Idea | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onIdeaUpdated: () => void;
}

export function EditIdeaDialog({ idea, open, onOpenChange, onIdeaUpdated }: EditIdeaDialogProps) {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [category, setCategory] = useState('');
  const [tags, setTags] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    if (idea) {
      setTitle(idea?.title ?? '');
      setDescription(idea?.description ?? '');
      setCategory(idea?.category ?? '');
      setTags(idea?.tags?.map?.(t => t?.name)?.join?.(', ') ?? '');
    }
  }, [idea]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!title?.trim() || !description?.trim() || !idea?.id) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch(`/api/ideas/${idea.id}`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: title.trim(),
          description: description.trim(),
          category: category.trim() || undefined,
          tags: tags
            ?.split(',')
            ?.map?.(t => t?.trim?.())
            ?.filter?.(Boolean) ?? [],
        }),
      });
      
      if (response?.ok) {
        onOpenChange(false);
        onIdeaUpdated();
      }
    } catch (error) {
      console.error('Failed to update idea:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Edit Idea</DialogTitle>
          <DialogDescription>
            Update your idea details and organization.
          </DialogDescription>
        </DialogHeader>
        
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">Title *</label>
            <Input
              placeholder="Enter idea title..."
              value={title}
              onChange={(e) => setTitle(e?.target?.value ?? '')}
              required
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Description *</label>
            <Textarea
              placeholder="Describe your idea in detail..."
              value={description}
              onChange={(e) => setDescription(e?.target?.value ?? '')}
              rows={4}
              required
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Category</label>
            <Input
              placeholder="e.g., Web App, Mobile, AI, etc."
              value={category}
              onChange={(e) => setCategory(e?.target?.value ?? '')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">Tags</label>
            <Input
              placeholder="Separate with commas"
              value={tags}
              onChange={(e) => setTags(e?.target?.value ?? '')}
            />
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Save Changes
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
}
