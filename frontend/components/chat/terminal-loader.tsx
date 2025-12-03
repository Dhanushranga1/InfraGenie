/**
 * Terminal Loader Component
 * 
 * Animated terminal-style loading indicator synced with workflow stages
 */

"use client";

import { Bot } from 'lucide-react';
import { useProjectStore } from '@/lib/store';

const STAGE_MESSAGES: Record<string, string> = {
  clarifier: '> Analyzing requirements...',
  planner: '> Planning infrastructure components...',
  architect: '> Generating Terraform code...',
  validator: '> Validating Terraform syntax...',
  completeness: '> Checking completeness...',
  deep_validation: '> Running terraform plan...',
  security: '> Scanning security policies...',
  parser: '> Building dependency graph...',
  finops: '> Estimating cloud costs...',
  ansible: '> Generating Ansible playbook...',
};

export function TerminalLoader() {
  const { workflowStage } = useProjectStore();
  const currentMessage = workflowStage?.current 
    ? STAGE_MESSAGES[workflowStage.current] || '> Processing...'
    : '> Initializing workflow...';
  
  return (
    <div className="flex gap-3 mb-4">
      {/* AI Icon */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center">
        <Bot className="w-4 h-4 text-violet-400 animate-pulse" />
      </div>
      
      {/* Terminal Message */}
      <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-zinc-900 border border-zinc-800 max-w-[85%]">
        <div className="flex items-center gap-2">
          <div className="flex gap-1">
            <div className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce [animation-delay:0ms]" />
            <div className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce [animation-delay:150ms]" />
            <div className="w-1.5 h-1.5 bg-violet-400 rounded-full animate-bounce [animation-delay:300ms]" />
          </div>
          <p className="font-mono text-sm text-violet-400">
            {currentMessage}
          </p>
        </div>
      </div>
    </div>
  );
}
