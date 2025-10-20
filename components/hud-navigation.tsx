
'use client';

import { usePathname, useRouter } from 'next/navigation';
import { motion } from 'framer-motion';
import { 
  Lightbulb, 
  Rocket, 
  Code, 
  Cloud, 
  CreditCard,
  Sparkles
} from 'lucide-react';

const workflowStages = [
  { id: 'brainstorming', name: 'Brainstorming', icon: Lightbulb, path: '/brainstorming' },
  { id: 'inception', name: 'Inception', icon: Rocket, path: '/inception' },
  { id: 'creation', name: 'Creation', icon: Code, path: '/creation' },
  { id: 'deployment', name: 'Deployment', icon: Cloud, path: '/deployment' },
  { id: 'subscription', name: 'Subscription', icon: CreditCard, path: '/subscription' },
];

export function HUDNavigation() {
  const pathname = usePathname();
  const router = useRouter();

  return (
    <motion.nav
      initial={{ y: -100 }}
      animate={{ y: 0 }}
      transition={{ duration: 0.5, type: 'spring' }}
      className="sticky top-0 z-50 glass border-b border-blue-500/20"
    >
      <div className="container mx-auto px-4 max-w-7xl">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.button
            onClick={() => router.push('/')}
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            className="flex items-center gap-2 group"
          >
            <div className="relative">
              <Sparkles className="h-8 w-8 text-blue-400 group-hover:text-blue-300 transition-colors" />
              <motion.div
                className="absolute inset-0 blur-xl bg-blue-400 opacity-0 group-hover:opacity-50"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>
            <div>
              <h1 className="text-xl font-bold font-[family-name:var(--font-orbitron)] neon-text-blue">
                SPIRAL CODEX
              </h1>
              <p className="text-xs text-slate-400">Studio Platform</p>
            </div>
          </motion.button>

          {/* Workflow Stages */}
          <div className="hidden md:flex items-center gap-1">
            {workflowStages.map((stage, index) => {
              const Icon = stage.icon;
              const isActive = pathname?.startsWith(stage.path);
              
              return (
                <div key={stage.id} className="flex items-center">
                  <motion.button
                    onClick={() => router.push(stage.path)}
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    className={`
                      relative px-4 py-2 rounded-lg transition-all duration-300
                      ${isActive 
                        ? 'bg-blue-500/20 text-blue-400 neon-glow-blue' 
                        : 'text-slate-400 hover:text-blue-400 hover:bg-blue-500/10'
                      }
                    `}
                  >
                    <div className="flex items-center gap-2">
                      <Icon className="h-4 w-4" />
                      <span className="text-sm font-medium">{stage.name}</span>
                    </div>
                    
                    {isActive && (
                      <motion.div
                        layoutId="activeStage"
                        className="absolute inset-0 border-2 border-blue-400 rounded-lg"
                        transition={{ type: 'spring', duration: 0.5 }}
                      />
                    )}
                  </motion.button>
                  
                  {index < workflowStages.length - 1 && (
                    <div className="w-8 h-0.5 bg-gradient-to-r from-blue-500/50 to-transparent mx-1" />
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </motion.nav>
  );
}
