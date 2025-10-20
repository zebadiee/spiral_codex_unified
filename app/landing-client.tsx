
'use client';

import { motion } from 'framer-motion';
import { useRouter } from 'next/navigation';
import { 
  Lightbulb, 
  Rocket, 
  Code, 
  Cloud, 
  CreditCard,
  ArrowRight,
  Sparkles
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';

const workflowStages = [
  {
    id: 'brainstorming',
    name: 'Brainstorming',
    icon: Lightbulb,
    description: 'Generate and organize innovative ideas with AI-powered suggestions',
    path: '/brainstorming',
    status: 'available',
    color: 'from-yellow-500 to-orange-500'
  },
  {
    id: 'inception',
    name: 'Inception',
    icon: Rocket,
    description: 'Initialize projects with comprehensive planning and requirements gathering',
    path: '/inception',
    status: 'available',
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'creation',
    name: 'Creation',
    icon: Code,
    description: 'Build and develop your project with intelligent coding assistance',
    path: '/creation',
    status: 'coming-soon',
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'deployment',
    name: 'Deployment',
    icon: Cloud,
    description: 'Deploy your applications seamlessly to cloud platforms',
    path: '/deployment',
    status: 'coming-soon',
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'subscription',
    name: 'Subscription',
    icon: CreditCard,
    description: 'Manage subscriptions and monetize your deployed solutions',
    path: '/subscription',
    status: 'coming-soon',
    color: 'from-indigo-500 to-violet-500'
  },
];

export function LandingClient() {
  const router = useRouter();

  return (
    <div className="space-y-12">
      {/* Hero Section */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center space-y-6 py-12"
      >
        <div className="flex justify-center">
          <motion.div
            animate={{ 
              rotate: [0, 360],
              scale: [1, 1.1, 1]
            }}
            transition={{ 
              duration: 20, 
              repeat: Infinity,
              ease: "linear"
            }}
            className="relative"
          >
            <Sparkles className="h-20 w-20 text-blue-400 neon-glow-blue" />
            <motion.div
              className="absolute inset-0 blur-2xl bg-blue-400 opacity-50"
              animate={{ scale: [1, 1.5, 1] }}
              transition={{ duration: 3, repeat: Infinity }}
            />
          </motion.div>
        </div>
        
        <h1 className="text-5xl md:text-6xl font-bold font-[family-name:var(--font-orbitron)]">
          <span className="neon-text-blue">SPIRAL CODEX</span>
          <br />
          <span className="text-3xl md:text-4xl text-slate-400">Studio Platform</span>
        </h1>
        
        <p className="text-xl text-slate-400 max-w-3xl mx-auto">
          A comprehensive AI-powered platform that takes your project from initial concept to live deployment,
          guiding you through every stage of the development lifecycle.
        </p>
        
        <div className="flex gap-4 justify-center">
          <Button 
            size="lg"
            onClick={() => router.push('/brainstorming')}
            className="gap-2"
          >
            Get Started
            <ArrowRight className="h-5 w-5" />
          </Button>
          <Button 
            size="lg"
            variant="outline"
            onClick={() => {
              document.getElementById('workflow')?.scrollIntoView({ behavior: 'smooth' });
            }}
          >
            Explore Workflow
          </Button>
        </div>
      </motion.div>

      {/* Workflow Stages */}
      <div id="workflow" className="space-y-8">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-center"
        >
          <h2 className="text-3xl font-bold font-[family-name:var(--font-orbitron)] mb-4">
            Complete Development Workflow
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Follow our structured approach from ideation to monetization, with AI assistance at every step
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {workflowStages.map((stage, index) => {
            const Icon = stage.icon;
            const isAvailable = stage.status === 'available';
            
            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                whileHover={isAvailable ? { y: -8 } : {}}
              >
                <Card 
                  className={`
                    h-full hover-lift transition-all duration-300 relative overflow-hidden
                    ${isAvailable 
                      ? 'hover:border-blue-500/50 cursor-pointer' 
                      : 'opacity-60'
                    }
                  `}
                  onClick={() => isAvailable && router.push(stage.path)}
                >
                  {/* Gradient overlay */}
                  <div className={`absolute inset-0 bg-gradient-to-br ${stage.color} opacity-5`} />
                  
                  {!isAvailable && (
                    <div className="absolute top-4 right-4 z-10">
                      <Badge className="bg-yellow-500/20 text-yellow-400 border-yellow-500/30">
                        Coming Soon
                      </Badge>
                    </div>
                  )}
                  
                  <CardHeader className="relative">
                    <div className={`
                      w-14 h-14 rounded-xl flex items-center justify-center mb-4
                      bg-gradient-to-br ${stage.color} neon-glow-blue
                    `}>
                      <Icon className="h-7 w-7 text-white" />
                    </div>
                    <CardTitle className="text-xl">{stage.name}</CardTitle>
                    <CardDescription>{stage.description}</CardDescription>
                  </CardHeader>
                  
                  <CardContent className="relative">
                    {isAvailable ? (
                      <Button 
                        variant="outline" 
                        className="w-full gap-2"
                        onClick={(e) => {
                          e.stopPropagation();
                          router.push(stage.path);
                        }}
                      >
                        Launch Module
                        <ArrowRight className="h-4 w-4" />
                      </Button>
                    ) : (
                      <div className="text-center py-2 text-sm text-slate-500">
                        Available in future updates
                      </div>
                    )}
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </div>

      {/* Features */}
      <motion.div
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        viewport={{ once: true }}
        className="space-y-8 py-12"
      >
        <div className="text-center">
          <h2 className="text-3xl font-bold font-[family-name:var(--font-orbitron)] mb-4">
            Powered by AI
          </h2>
          <p className="text-slate-400 max-w-2xl mx-auto">
            Every module leverages advanced AI to enhance your productivity and creativity
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            {
              title: 'Intelligent Suggestions',
              description: 'Get AI-powered recommendations tailored to your project needs',
              icon: Sparkles
            },
            {
              title: 'Automated Planning',
              description: 'Generate comprehensive project plans and requirements automatically',
              icon: Rocket
            },
            {
              title: 'Seamless Integration',
              description: 'All modules work together in a unified, intuitive workflow',
              icon: ArrowRight
            }
          ].map((feature, index) => {
            const FeatureIcon = feature.icon;
            return (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="text-center h-full">
                  <CardHeader>
                    <div className="flex justify-center mb-4">
                      <div className="p-3 rounded-lg bg-blue-500/10">
                        <FeatureIcon className="h-6 w-6 text-blue-400" />
                      </div>
                    </div>
                    <CardTitle className="text-lg">{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              </motion.div>
            );
          })}
        </div>
      </motion.div>
    </div>
  );
}
