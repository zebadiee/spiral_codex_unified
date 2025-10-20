
'use client';

import { motion } from 'framer-motion';
import { Sparkles, Bell, Code, Cloud, CreditCard } from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';

interface ComingSoonModuleProps {
  title: string;
  iconName: 'code' | 'cloud' | 'credit-card';
  description: string;
  features: string[];
  gradient: string;
}

const iconMap = {
  'code': Code,
  'cloud': Cloud,
  'credit-card': CreditCard,
};

export function ComingSoonModule({ title, iconName, description, features, gradient }: ComingSoonModuleProps) {
  const Icon = iconMap[iconName];
  return (
    <div className="space-y-8">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-4"
      >
        <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
          Coming Soon
        </Badge>
        
        <div className="flex justify-center">
          <motion.div
            animate={{ 
              y: [0, -10, 0],
              rotate: [0, 5, -5, 0]
            }}
            transition={{ 
              duration: 4, 
              repeat: Infinity,
              ease: "easeInOut"
            }}
            className={`
              w-24 h-24 rounded-2xl flex items-center justify-center
              bg-gradient-to-br ${gradient} neon-glow-blue relative
            `}
          >
            <Icon className="h-12 w-12 text-white" />
            <motion.div
              className="absolute inset-0 blur-2xl opacity-50"
              animate={{ scale: [1, 1.3, 1] }}
              transition={{ duration: 3, repeat: Infinity }}
            />
          </motion.div>
        </div>
        
        <h1 className="text-4xl font-bold font-[family-name:var(--font-orbitron)] neon-text-blue">
          {title}
        </h1>
        
        <p className="text-xl text-slate-400 max-w-2xl mx-auto">
          {description}
        </p>
      </motion.div>

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="max-w-4xl mx-auto"
      >
        <Card className="glass border-blue-500/30">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-blue-400" />
              Planned Features
            </CardTitle>
            <CardDescription>
              This module is currently under development. Here's what you can expect:
            </CardDescription>
          </CardHeader>
          
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {features.map((feature, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.3 + index * 0.1 }}
                  className="flex items-start gap-3 p-4 rounded-lg glass hover:bg-blue-500/5 transition-colors"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    <div className="w-2 h-2 rounded-full bg-blue-400 neon-glow-blue" />
                  </div>
                  <p className="text-sm text-slate-300">{feature}</p>
                </motion.div>
              ))}
            </div>
          </CardContent>
        </Card>
      </motion.div>

      {/* Call to Action */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.5 }}
        className="text-center space-y-4"
      >
        <div className="p-6 rounded-2xl glass border border-blue-500/20 inline-block">
          <Bell className="h-8 w-8 text-blue-400 mx-auto mb-3" />
          <h3 className="text-lg font-semibold mb-2">Stay Updated</h3>
          <p className="text-sm text-slate-400 mb-4 max-w-md">
            We're working hard to bring you this module. Check back soon for updates!
          </p>
          <div className="flex gap-2 justify-center">
            <Button variant="outline" size="sm">
              Learn More
            </Button>
            <Button size="sm" className="gap-2">
              <Bell className="h-4 w-4" />
              Notify Me
            </Button>
          </div>
        </div>
      </motion.div>

      {/* Timeline Hint */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.7 }}
        className="text-center"
      >
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-slate-700">
          <Sparkles className="h-4 w-4 text-blue-400" />
          <span className="text-sm text-slate-400">
            Expected in future updates
          </span>
        </div>
      </motion.div>
    </div>
  );
}
