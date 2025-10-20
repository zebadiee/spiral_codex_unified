
'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Loader2, ChevronRight, ChevronLeft, Sparkles } from 'lucide-react';
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

interface CreateProjectWizardProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onProjectCreated: () => void;
}

const steps = [
  { id: 1, title: 'Basic Info', description: 'Tell us about your project' },
  { id: 2, title: 'Requirements', description: 'Define what you need' },
  { id: 3, title: 'Planning', description: 'Timeline and resources' },
];

export function CreateProjectWizard({ open, onOpenChange, onProjectCreated }: CreateProjectWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGeneratingRequirements, setIsGeneratingRequirements] = useState(false);
  
  // Form data
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [type, setType] = useState('');
  const [requirements, setRequirements] = useState('');
  const [estimatedDuration, setEstimatedDuration] = useState('');
  const [targetDate, setTargetDate] = useState('');

  const handleNext = () => {
    if (currentStep < steps.length) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleGenerateRequirements = async () => {
    if (!name?.trim() || !description?.trim()) {
      alert('Please fill in project name and description first');
      return;
    }
    
    setIsGeneratingRequirements(true);
    try {
      const response = await fetch('/api/projects/ai-analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          projectName: name.trim(),
          projectDescription: description.trim(),
          analysisType: 'requirements',
        }),
      });

      if (!response?.ok) {
        throw new Error('Failed to generate requirements');
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
                setRequirements(parsed?.result?.analysis ?? '');
                return;
              }
            } catch (e) {
              // Skip invalid JSON
            }
          }
        }
      }
    } catch (error) {
      console.error('Failed to generate requirements:', error);
    } finally {
      setIsGeneratingRequirements(false);
    }
  };

  const handleSubmit = async () => {
    if (!name?.trim() || !description?.trim()) return;
    
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/projects', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: name.trim(),
          description: description.trim(),
          type: type.trim() || undefined,
          requirements: requirements.trim() || undefined,
          estimatedDuration: estimatedDuration.trim() || undefined,
          targetDate: targetDate || undefined,
        }),
      });
      
      if (response?.ok) {
        // Reset form
        setName('');
        setDescription('');
        setType('');
        setRequirements('');
        setEstimatedDuration('');
        setTargetDate('');
        setCurrentStep(1);
        onOpenChange(false);
        onProjectCreated();
      }
    } catch (error) {
      console.error('Failed to create project:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const canProceed = () => {
    if (currentStep === 1) return name?.trim() && description?.trim();
    if (currentStep === 2) return true;
    if (currentStep === 3) return true;
    return false;
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto custom-scrollbar">
        <DialogHeader>
          <DialogTitle>Create New Project</DialogTitle>
          <DialogDescription>
            Step {currentStep} of {steps.length}: {steps[currentStep - 1]?.description}
          </DialogDescription>
        </DialogHeader>
        
        {/* Progress Steps */}
        <div className="flex items-center justify-between mb-6">
          {steps.map((step, index) => (
            <div key={step.id} className="flex items-center flex-1">
              <div className="flex flex-col items-center flex-1">
                <div
                  className={`
                    w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all
                    ${currentStep >= step.id 
                      ? 'bg-blue-500 text-white neon-glow-blue' 
                      : 'bg-slate-800 text-slate-400'
                    }
                  `}
                >
                  {step.id}
                </div>
                <span className="text-xs mt-1 text-slate-400">{step.title}</span>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={`
                    h-0.5 flex-1 transition-all
                    ${currentStep > step.id ? 'bg-blue-500' : 'bg-slate-800'}
                  `}
                />
              )}
            </div>
          ))}
        </div>

        {/* Step Content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
            className="space-y-4 min-h-[300px]"
          >
            {currentStep === 1 && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Project Name *</label>
                  <Input
                    placeholder="Enter project name..."
                    value={name}
                    onChange={(e) => setName(e?.target?.value ?? '')}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Description *</label>
                  <Textarea
                    placeholder="Describe your project goals and vision..."
                    value={description}
                    onChange={(e) => setDescription(e?.target?.value ?? '')}
                    rows={5}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Project Type</label>
                  <Input
                    placeholder="e.g., Web App, Mobile App, API, etc."
                    value={type}
                    onChange={(e) => setType(e?.target?.value ?? '')}
                  />
                </div>
              </>
            )}

            {currentStep === 2 && (
              <>
                <div className="flex items-center justify-between mb-2">
                  <label className="text-sm font-medium">Requirements</label>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={handleGenerateRequirements}
                    disabled={isGeneratingRequirements}
                  >
                    {isGeneratingRequirements ? (
                      <>
                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        Generating...
                      </>
                    ) : (
                      <>
                        <Sparkles className="mr-2 h-4 w-4" />
                        AI Generate
                      </>
                    )}
                  </Button>
                </div>
                <Textarea
                  placeholder="List your project requirements and features..."
                  value={requirements}
                  onChange={(e) => setRequirements(e?.target?.value ?? '')}
                  rows={12}
                />
                <p className="text-xs text-slate-500">
                  Use AI to automatically generate comprehensive requirements based on your project description
                </p>
              </>
            )}

            {currentStep === 3 && (
              <>
                <div>
                  <label className="text-sm font-medium mb-2 block">Estimated Duration</label>
                  <Input
                    placeholder="e.g., 3 months, 6 weeks, etc."
                    value={estimatedDuration}
                    onChange={(e) => setEstimatedDuration(e?.target?.value ?? '')}
                  />
                </div>
                
                <div>
                  <label className="text-sm font-medium mb-2 block">Target Completion Date</label>
                  <Input
                    type="date"
                    value={targetDate}
                    onChange={(e) => setTargetDate(e?.target?.value ?? '')}
                  />
                </div>
                
                <div className="p-4 rounded-lg glass border border-blue-500/20">
                  <h4 className="font-semibold mb-2 text-blue-400">Project Summary</h4>
                  <div className="space-y-2 text-sm">
                    <div>
                      <span className="text-slate-400">Name:</span>{' '}
                      <span className="text-slate-200">{name || 'Not set'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Type:</span>{' '}
                      <span className="text-slate-200">{type || 'Not specified'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Duration:</span>{' '}
                      <span className="text-slate-200">{estimatedDuration || 'Not specified'}</span>
                    </div>
                    <div>
                      <span className="text-slate-400">Target Date:</span>{' '}
                      <span className="text-slate-200">{targetDate || 'Not set'}</span>
                    </div>
                  </div>
                </div>
              </>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation Buttons */}
        <div className="flex items-center justify-between pt-4 border-t border-slate-800">
          <Button
            variant="outline"
            onClick={handleBack}
            disabled={currentStep === 1 || isSubmitting}
          >
            <ChevronLeft className="h-4 w-4 mr-2" />
            Back
          </Button>
          
          {currentStep < steps.length ? (
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
            >
              Next
              <ChevronRight className="h-4 w-4 ml-2" />
            </Button>
          ) : (
            <Button
              onClick={handleSubmit}
              disabled={!canProceed() || isSubmitting}
            >
              {isSubmitting && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Create Project
            </Button>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
