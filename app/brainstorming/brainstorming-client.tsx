
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Sparkles, Search, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { IdeaCard } from '@/components/idea-card';
import { CreateIdeaDialog } from '@/components/create-idea-dialog';
import { AIIdeaGenerator } from '@/components/ai-idea-generator';
import type { Idea } from '@/lib/types';

export function BrainstormingClient() {
  const [ideas, setIdeas] = useState<Idea[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isAIGeneratorOpen, setIsAIGeneratorOpen] = useState(false);

  useEffect(() => {
    fetchIdeas();
  }, []);

  const fetchIdeas = async () => {
    try {
      const response = await fetch('/api/ideas');
      if (response?.ok) {
        const data = await response.json();
        setIdeas(data?.ideas ?? []);
      }
    } catch (error) {
      console.error('Failed to fetch ideas:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleIdeaCreated = () => {
    fetchIdeas();
  };

  const handleIdeaUpdated = () => {
    fetchIdeas();
  };

  const handleIdeaDeleted = () => {
    fetchIdeas();
  };

  const filteredIdeas = ideas?.filter?.((idea) => {
    const matchesSearch = 
      idea?.title?.toLowerCase?.()?.includes?.(searchQuery?.toLowerCase?.() ?? '') ||
      idea?.description?.toLowerCase?.()?.includes?.(searchQuery?.toLowerCase?.() ?? '');
    
    const matchesCategory = 
      selectedCategory === 'all' || 
      idea?.category?.toLowerCase?.() === selectedCategory?.toLowerCase?.();
    
    return matchesSearch && matchesCategory;
  }) ?? [];

  const categories = ['all', ...Array.from(new Set(ideas?.map?.(i => i?.category)?.filter?.(Boolean) ?? []))];

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold font-[family-name:var(--font-orbitron)] neon-text-blue">
            Brainstorming
          </h1>
          <p className="text-slate-400 mt-1">
            Generate and organize your innovative ideas with AI assistance
          </p>
        </div>
        
        <div className="flex gap-2">
          <Button
            onClick={() => setIsAIGeneratorOpen(true)}
            className="gap-2"
            variant="outline"
          >
            <Sparkles className="h-4 w-4" />
            AI Generate
          </Button>
          <Button onClick={() => setIsCreateDialogOpen(true)} className="gap-2">
            <Plus className="h-4 w-4" />
            New Idea
          </Button>
        </div>
      </motion.div>

      {/* Filters */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col gap-4 sm:flex-row"
      >
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400" />
          <Input
            placeholder="Search ideas..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e?.target?.value ?? '')}
            className="pl-10"
          />
        </div>
        
        <div className="flex gap-2 overflow-x-auto no-scrollbar">
          {categories?.map?.((category) => (
            <Button
              key={category}
              onClick={() => setSelectedCategory(category ?? 'all')}
              variant={selectedCategory === category ? 'default' : 'outline'}
              size="sm"
              className="whitespace-nowrap"
            >
              {category === 'all' ? 'All Categories' : category}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Ideas Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-64 bg-slate-800/30 rounded-xl animate-pulse"
            />
          ))}
        </div>
      ) : filteredIdeas?.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center py-20 text-center"
        >
          <div className="p-6 rounded-full bg-blue-500/10 mb-4">
            <Sparkles className="h-12 w-12 text-blue-400" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No ideas yet</h3>
          <p className="text-slate-400 mb-6 max-w-md">
            Start your creative journey by adding your first idea or use AI to generate inspiration
          </p>
          <div className="flex gap-2">
            <Button onClick={() => setIsAIGeneratorOpen(true)} variant="outline">
              <Sparkles className="h-4 w-4 mr-2" />
              AI Generate
            </Button>
            <Button onClick={() => setIsCreateDialogOpen(true)}>
              <Plus className="h-4 w-4 mr-2" />
              Create Idea
            </Button>
          </div>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filteredIdeas?.map?.((idea, index) => (
            <IdeaCard
              key={idea?.id}
              idea={idea}
              index={index}
              onUpdate={handleIdeaUpdated}
              onDelete={handleIdeaDeleted}
            />
          ))}
        </motion.div>
      )}

      {/* Dialogs */}
      <CreateIdeaDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onIdeaCreated={handleIdeaCreated}
      />
      
      <AIIdeaGenerator
        open={isAIGeneratorOpen}
        onOpenChange={setIsAIGeneratorOpen}
        onIdeaCreated={handleIdeaCreated}
      />
    </div>
  );
}
