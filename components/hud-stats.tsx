
'use client';

import { useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { Lightbulb, FolderKanban, CheckCircle2, Tag } from 'lucide-react';

interface Stats {
  activeIdeas: number;
  activeProjects: number;
  completedProjects: number;
  totalTags: number;
}

export function HUDStats() {
  const [stats, setStats] = useState<Stats>({
    activeIdeas: 0,
    activeProjects: 0,
    completedProjects: 0,
    totalTags: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  const fetchStats = useCallback(async () => {
    setIsLoading(true);

    try {
      const response = await fetch('/api/stats');
      if (response?.ok) {
        const data = await response.json();
        setStats((prev) => data?.stats ?? prev);
      }
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  const statItems = [
    { label: 'Active Ideas', value: stats?.activeIdeas ?? 0, icon: Lightbulb, color: 'text-yellow-400' },
    { label: 'Active Projects', value: stats?.activeProjects ?? 0, icon: FolderKanban, color: 'text-blue-400' },
    { label: 'Completed', value: stats?.completedProjects ?? 0, icon: CheckCircle2, color: 'text-green-400' },
    { label: 'Tags', value: stats?.totalTags ?? 0, icon: Tag, color: 'text-purple-400' },
  ];

  if (isLoading) {
    return (
      <div className="border-b border-slate-800/50 bg-slate-900/30">
        <div className="container mx-auto px-4 py-3 max-w-7xl">
          <div className="flex gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-12 w-32 bg-slate-800/30 rounded animate-pulse" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ delay: 0.3 }}
      className="border-b border-slate-800/50 bg-slate-900/30 backdrop-blur-sm"
    >
      <div className="container mx-auto px-4 py-3 max-w-7xl">
        <div className="flex items-center gap-6 overflow-x-auto no-scrollbar">
          {statItems.map((item, index) => {
            const Icon = item.icon;
            return (
              <motion.div
                key={item.label}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.1 * index }}
                className="flex items-center gap-3 min-w-fit"
              >
                <div className={`p-2 rounded-lg bg-slate-800/50 ${item.color}`}>
                  <Icon className="h-5 w-5" />
                </div>
                <div>
                  <p className="text-xs text-slate-400">{item.label}</p>
                  <motion.p
                    key={item.value}
                    initial={{ scale: 1.2, color: 'hsl(217 91% 60%)' }}
                    animate={{ scale: 1, color: 'hsl(210 40% 98%)' }}
                    className="text-lg font-bold font-[family-name:var(--font-orbitron)]"
                  >
                    {item.value}
                  </motion.p>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </motion.div>
  );
}
