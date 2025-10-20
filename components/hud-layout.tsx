
'use client';

import { ReactNode, useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { HUDNavigation } from './hud-navigation';
import { HUDStats } from './hud-stats';
import { AIAssistant } from './ai-assistant';

interface HUDLayoutProps {
  children: ReactNode;
}

export function HUDLayout({ children }: HUDLayoutProps) {
  const [isClient, setIsClient] = useState(false);

  useEffect(() => {
    setIsClient(true);
  }, []);

  if (!isClient) {
    return (
      <div className="min-h-screen bg-slate-950">
        <div className="fixed inset-0 grid-background opacity-20" />
        {children}
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      {/* Animated grid background */}
      <div className="fixed inset-0 grid-background opacity-20" />
      
      {/* Gradient overlay */}
      <div className="fixed inset-0 bg-gradient-to-br from-blue-950/20 via-transparent to-purple-950/20 pointer-events-none" />
      
      {/* HUD Container */}
      <div className="relative z-10">
        {/* Top Navigation Bar */}
        <HUDNavigation />
        
        {/* Stats Bar */}
        <HUDStats />
        
        {/* Main Content Area */}
        <AnimatePresence mode="wait">
          <motion.main
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="container mx-auto px-4 py-6 max-w-7xl"
          >
            {children}
          </motion.main>
        </AnimatePresence>
        
        {/* AI Assistant Overlay */}
        <AIAssistant />
      </div>
    </div>
  );
}
