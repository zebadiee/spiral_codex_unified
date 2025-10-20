
'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Rocket, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { ProjectCard } from '@/components/project-card';
import { CreateProjectWizard } from '@/components/create-project-wizard';
import type { Project } from '@/lib/types';

export function InceptionClient() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isWizardOpen, setIsWizardOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>('all');

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await fetch('/api/projects');
      if (response?.ok) {
        const data = await response.json();
        setProjects(data?.projects ?? []);
      }
    } catch (error) {
      console.error('Failed to fetch projects:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleProjectCreated = () => {
    fetchProjects();
  };

  const handleProjectUpdated = () => {
    fetchProjects();
  };

  const handleProjectDeleted = () => {
    fetchProjects();
  };

  const filteredProjects = projects?.filter?.((project) => {
    const matchesSearch = 
      project?.name?.toLowerCase?.()?.includes?.(searchQuery?.toLowerCase?.() ?? '') ||
      project?.description?.toLowerCase?.()?.includes?.(searchQuery?.toLowerCase?.() ?? '');
    
    const matchesStatus = 
      selectedStatus === 'all' || 
      project?.status?.toLowerCase?.() === selectedStatus?.toLowerCase?.();
    
    return matchesSearch && matchesStatus;
  }) ?? [];

  const statuses = ['all', 'planning', 'in-progress', 'completed', 'on-hold'];

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
            Inception
          </h1>
          <p className="text-slate-400 mt-1">
            Initialize and plan your projects with AI-powered guidance
          </p>
        </div>
        
        <Button onClick={() => setIsWizardOpen(true)} className="gap-2">
          <Plus className="h-4 w-4" />
          New Project
        </Button>
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
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e?.target?.value ?? '')}
            className="pl-10"
          />
        </div>
        
        <div className="flex gap-2 overflow-x-auto no-scrollbar">
          {statuses?.map?.((status) => (
            <Button
              key={status}
              onClick={() => setSelectedStatus(status)}
              variant={selectedStatus === status ? 'default' : 'outline'}
              size="sm"
              className="whitespace-nowrap capitalize"
            >
              {status === 'all' ? 'All Status' : status.replace('-', ' ')}
            </Button>
          ))}
        </div>
      </motion.div>

      {/* Projects Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="h-72 bg-slate-800/30 rounded-xl animate-pulse"
            />
          ))}
        </div>
      ) : filteredProjects?.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="flex flex-col items-center justify-center py-20 text-center"
        >
          <div className="p-6 rounded-full bg-blue-500/10 mb-4">
            <Rocket className="h-12 w-12 text-blue-400" />
          </div>
          <h3 className="text-xl font-semibold mb-2">No projects yet</h3>
          <p className="text-slate-400 mb-6 max-w-md">
            Start your journey by creating your first project with our guided wizard
          </p>
          <Button onClick={() => setIsWizardOpen(true)}>
            <Plus className="h-4 w-4 mr-2" />
            Create Project
          </Button>
        </motion.div>
      ) : (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4"
        >
          {filteredProjects?.map?.((project, index) => (
            <ProjectCard
              key={project?.id}
              project={project}
              index={index}
              onUpdate={handleProjectUpdated}
              onDelete={handleProjectDeleted}
            />
          ))}
        </motion.div>
      )}

      {/* Wizard */}
      <CreateProjectWizard
        open={isWizardOpen}
        onOpenChange={setIsWizardOpen}
        onProjectCreated={handleProjectCreated}
      />
    </div>
  );
}
