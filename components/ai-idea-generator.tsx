
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Sparkles, Wand2, Loader2 } from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from './ui/dialog';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';

interface AIIdeaGeneratorProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onIdeaCreated: () => void;
}

export function AIIdeaGenerator({ open, onOpenChange, onIdeaCreated }: AIIdeaGeneratorProps) {
  const [prompt, setPrompt] = useState('');
  const [context, setContext] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedIdeas, setGeneratedIdeas] = useState<any[]>([]);
  const [isSaving, setIsSaving] = useState<string | null>(null);

  const handleGenerate = async () => {
    if (!prompt?.trim()) return;
    
    setIsGenerating(true);
    setGeneratedIdeas([]);
    
    try {
      const response = await fetch('/api/ideas/ai-generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: prompt.trim(),
          context: context.trim() || undefined,
        }),
      });

      if (!response?.ok) {
        throw new Error('Failed to generate ideas');
      }

      const reader = response?.body?.getReader();
      const decoder = new TextDecoder();
      let buffer = '';
      let partialRead = '';

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        partialRead += decoder.decode(value, { stream: true });
        let lines = partialRead.split('\n');
        partialRead = lines.pop() ?? '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            const data = line.slice(6);
            if (data === '[DONE]') {
              return;
            }
            try {
              const parsed = JSON.parse(data);
              if (parsed?.status === 'completed') {
                setGeneratedIdeas(parsed?.result?.ideas ?? []);
                return;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to generate ideas:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleSaveIdea = async (idea: any) => {
    setIsSaving(idea?.title);
    try {
      const response = await fetch('/api/ideas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          title: idea?.title,
          description: idea?.description,
          category: idea?.category || 'AI Generated',
          tags: idea?.tags ?? [],
        }),
      });
      
      if (response?.ok) {
        onIdeaCreated();
        setGeneratedIdeas(prev => prev?.filter?.(i => i?.title !== idea?.title) ?? []);
      }
    } catch (error) {
      console.error('Failed to save idea:', error);
    } finally {
      setIsSaving(null);
    }
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto custom-scrollbar">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-blue-400" />
            AI Idea Generator
          </DialogTitle>
          <DialogDescription>
            Let AI help you brainstorm innovative ideas based on your interests
          </DialogDescription>
        </DialogHeader>
        
        <div className="space-y-4">
          <div>
            <label className="text-sm font-medium mb-2 block">
              What kind of ideas are you looking for? *
            </label>
            <Input
              placeholder="E.g., mobile app ideas for fitness, SaaS products for developers..."
              value={prompt}
              onChange={(e) => setPrompt(e?.target?.value ?? '')}
            />
          </div>
          
          <div>
            <label className="text-sm font-medium mb-2 block">
              Additional Context (optional)
            </label>
            <Textarea
              placeholder="Provide any specific requirements, target audience, or constraints..."
              value={context}
              onChange={(e) => setContext(e?.target?.value ?? '')}
              rows={3}
            />
          </div>
          
          <Button
            onClick={handleGenerate}
            disabled={isGenerating || !prompt?.trim()}
            className="w-full"
          >
            {isGenerating ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Generating Ideas...
              </>
            ) : (
              <>
                <Wand2 className="mr-2 h-4 w-4" />
                Generate Ideas
              </>
            )}
          </Button>
          
          {/* Generated Ideas */}
          {generatedIdeas?.length > 0 && (
            <div className="space-y-3 mt-6">
              <h3 className="font-semibold text-lg flex items-center gap-2">
                <Sparkles className="h-5 w-5 text-blue-400" />
                Generated Ideas
              </h3>
              
              {generatedIdeas.map((idea, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="p-4 rounded-lg glass border border-blue-500/20"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <h4 className="font-semibold text-blue-400 mb-2">
                        {idea?.title}
                      </h4>
                      <p className="text-sm text-slate-400 mb-2">
                        {idea?.description}
                      </p>
                      {idea?.tags && idea.tags.length > 0 && (
                        <div className="flex flex-wrap gap-1">
                          {idea.tags.map((tag: string, i: number) => (
                            <span
                              key={i}
                              className="text-xs px-2 py-0.5 rounded-full bg-blue-500/10 text-blue-400 border border-blue-500/30"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                    
                    <Button
                      size="sm"
                      onClick={() => handleSaveIdea(idea)}
                      disabled={isSaving === idea?.title}
                    >
                      {isSaving === idea?.title ? (
                        <Loader2 className="h-4 w-4 animate-spin" />
                      ) : (
                        'Save'
                      )}
                    </Button>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
