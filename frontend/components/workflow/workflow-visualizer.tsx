/**
 * Workflow Visualizer Component
 * 
 * Real-time visualization of the multi-agent workflow pipeline
 * Shows progress through: Clarifier → Planner → Architect → Validator → etc.
 */

"use client";

import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, Loader2, XCircle, ArrowRight } from 'lucide-react';
import { useProjectStore } from '@/lib/store';

const WORKFLOW_STAGES = [
  { id: 'clarifier', name: 'Clarifier', description: 'Analyzing requirements' },
  { id: 'planner', name: 'Planner', description: 'Planning components' },
  { id: 'architect', name: 'Architect', description: 'Generating Terraform' },
  { id: 'validator', name: 'Validator', description: 'Validating syntax' },
  { id: 'completeness', name: 'Completeness', description: 'Checking completeness' },
  { id: 'deep_validation', name: 'Deep Check', description: 'Running terraform plan' },
  { id: 'security', name: 'Security', description: 'Security scanning' },
  { id: 'parser', name: 'Parser', description: 'Building graph' },
  { id: 'finops', name: 'FinOps', description: 'Cost estimation' },
  { id: 'ansible', name: 'Ansible', description: 'Configuration' },
];

type StageStatus = 'pending' | 'active' | 'complete' | 'error';

export function WorkflowVisualizer() {
  const { isLoading, workflowStage, workflowError } = useProjectStore();

  const getStageStatus = (stageId: string): StageStatus => {
    if (!isLoading) {
      // If not loading and we have terraform code, assume complete
      const stages = useProjectStore.getState().workflowStage;
      if (stages && stages[stageId] === 'complete') return 'complete';
      if (stages && stages[stageId] === 'error') return 'error';
      return 'pending';
    }

    const currentIndex = WORKFLOW_STAGES.findIndex(s => s.id === workflowStage?.current);
    const stageIndex = WORKFLOW_STAGES.findIndex(s => s.id === stageId);

    if (workflowError && workflowStage?.current === stageId) return 'error';
    if (stageIndex < currentIndex) return 'complete';
    if (stageIndex === currentIndex) return 'active';
    return 'pending';
  };

  if (!isLoading && !workflowStage?.current) {
    return null; // Don't show when idle
  }

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-zinc-900/95 backdrop-blur-xl border-t border-zinc-800 z-50">
      <div className="max-w-7xl mx-auto p-4">
        {/* Header */}
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-2 h-2 rounded-full bg-violet-500 animate-pulse" />
            <h3 className="text-sm font-semibold text-zinc-300">
              Workflow Pipeline
            </h3>
          </div>
          <div className="text-xs text-zinc-500 font-mono">
            {workflowStage?.current ? `Stage: ${workflowStage.current}` : 'Idle'}
          </div>
        </div>

        {/* Workflow Stages */}
        <div className="relative">
          {/* Progress Bar Background */}
          <div className="absolute top-5 left-0 right-0 h-0.5 bg-zinc-800" />
          
          {/* Animated Progress Bar */}
          <motion.div
            className="absolute top-5 left-0 h-0.5 bg-gradient-to-r from-violet-600 to-indigo-600"
            initial={{ width: '0%' }}
            animate={{
              width: `${((WORKFLOW_STAGES.findIndex(s => s.id === workflowStage?.current) + 1) / WORKFLOW_STAGES.length) * 100}%`
            }}
            transition={{ duration: 0.5, ease: 'easeOut' }}
          />

          {/* Stages */}
          <div className="relative flex justify-between">
            {WORKFLOW_STAGES.map((stage, index) => {
              const status = getStageStatus(stage.id);
              const isLast = index === WORKFLOW_STAGES.length - 1;

              return (
                <div key={stage.id} className="flex items-center">
                  {/* Stage Circle */}
                  <motion.div
                    className="relative flex flex-col items-center"
                    initial={{ scale: 0.8, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    transition={{ delay: index * 0.05 }}
                  >
                    {/* Icon */}
                    <div className={`
                      relative z-10 w-10 h-10 rounded-full flex items-center justify-center
                      ${status === 'pending' ? 'bg-zinc-800 border-2 border-zinc-700' : ''}
                      ${status === 'active' ? 'bg-violet-600 border-2 border-violet-500 shadow-lg shadow-violet-500/50' : ''}
                      ${status === 'complete' ? 'bg-green-600 border-2 border-green-500' : ''}
                      ${status === 'error' ? 'bg-red-600 border-2 border-red-500' : ''}
                    `}>
                      <AnimatePresence mode="wait">
                        {status === 'pending' && (
                          <motion.div
                            key="pending"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                          >
                            <Circle className="w-5 h-5 text-zinc-600" />
                          </motion.div>
                        )}
                        {status === 'active' && (
                          <motion.div
                            key="active"
                            initial={{ scale: 0, rotate: 0 }}
                            animate={{ scale: 1, rotate: 360 }}
                            exit={{ scale: 0 }}
                            transition={{ rotate: { duration: 2, repeat: Infinity, ease: 'linear' } }}
                          >
                            <Loader2 className="w-5 h-5 text-white" />
                          </motion.div>
                        )}
                        {status === 'complete' && (
                          <motion.div
                            key="complete"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                          >
                            <CheckCircle2 className="w-5 h-5 text-white" />
                          </motion.div>
                        )}
                        {status === 'error' && (
                          <motion.div
                            key="error"
                            initial={{ scale: 0 }}
                            animate={{ scale: 1 }}
                            exit={{ scale: 0 }}
                          >
                            <XCircle className="w-5 h-5 text-white" />
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>

                    {/* Label */}
                    <div className="mt-2 text-center min-w-[80px]">
                      <div className={`
                        text-xs font-medium
                        ${status === 'pending' ? 'text-zinc-600' : ''}
                        ${status === 'active' ? 'text-violet-400' : ''}
                        ${status === 'complete' ? 'text-green-400' : ''}
                        ${status === 'error' ? 'text-red-400' : ''}
                      `}>
                        {stage.name}
                      </div>
                      {status === 'active' && (
                        <motion.div
                          className="text-[10px] text-zinc-500 mt-0.5"
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                        >
                          {stage.description}
                        </motion.div>
                      )}
                    </div>
                  </motion.div>

                  {/* Arrow Connector */}
                  {!isLast && (
                    <div className="flex items-center mx-1 -mt-6">
                      <ArrowRight className={`
                        w-4 h-4
                        ${status === 'complete' ? 'text-green-600' : 'text-zinc-700'}
                      `} />
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Error Message */}
        {workflowError && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3 rounded-lg bg-red-950/50 border border-red-900/50"
          >
            <div className="flex items-start gap-2">
              <XCircle className="w-4 h-4 text-red-400 mt-0.5 flex-shrink-0" />
              <div>
                <div className="text-sm font-medium text-red-400">Workflow Error</div>
                <div className="text-xs text-red-300/80 mt-1">{workflowError}</div>
              </div>
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
