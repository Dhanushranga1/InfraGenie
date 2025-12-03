/**
 * Deployment Checklist Component
 * 
 * Interactive checklist to track deployment progress
 * Persists state in localStorage
 */

"use client";

import { useState, useEffect } from 'react';
import { 
  CheckCircle2,
  Circle,
  Download,
  Wrench,
  Key,
  Terminal,
  Server,
  RotateCcw,
  ExternalLink
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';

interface ChecklistProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onOpenQuickStart?: () => void;
}

interface ChecklistItem {
  id: string;
  title: string;
  description: string;
  icon: any;
  link?: string;
  linkText?: string;
}

const CHECKLIST_ITEMS: ChecklistItem[] = [
  {
    id: 'extract',
    title: 'Extract deployment kit',
    description: 'Unzip the downloaded file to a working directory',
    icon: Download,
  },
  {
    id: 'prerequisites',
    title: 'Install prerequisites',
    description: 'Ensure Terraform, Ansible, AWS CLI, and jq are installed',
    icon: Wrench,
    link: '#',
    linkText: 'View requirements',
  },
  {
    id: 'credentials',
    title: 'Prepare AWS credentials',
    description: 'Have your AWS Access Key ID and Secret Access Key ready',
    icon: Key,
    link: 'https://console.aws.amazon.com/iam/home#/security_credentials',
    linkText: 'Get credentials',
  },
  {
    id: 'deploy',
    title: 'Run deployment script',
    description: 'Execute ./deploy.sh and follow the interactive prompts',
    icon: Terminal,
  },
  {
    id: 'connect',
    title: 'Connect to your server',
    description: 'Use the SSH command provided after successful deployment',
    icon: Server,
  },
];

const STORAGE_KEY = 'infragenie-checklist-state';

export function DeploymentChecklist({ 
  open, 
  onOpenChange,
  onOpenQuickStart 
}: ChecklistProps) {
  const [checkedItems, setCheckedItems] = useState<Set<string>>(new Set());

  // Load state from localStorage on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        try {
          const parsed = JSON.parse(saved);
          setCheckedItems(new Set(parsed));
        } catch (e) {
          console.error('Failed to load checklist state:', e);
        }
      }
    }
  }, []);

  // Save state to localStorage whenever it changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(Array.from(checkedItems)));
    }
  }, [checkedItems]);

  const handleToggle = (itemId: string) => {
    setCheckedItems((prev) => {
      const newSet = new Set(prev);
      if (newSet.has(itemId)) {
        newSet.delete(itemId);
      } else {
        newSet.add(itemId);
      }
      return newSet;
    });
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset the checklist?')) {
      setCheckedItems(new Set());
      localStorage.removeItem(STORAGE_KEY);
    }
  };

  const progress = (checkedItems.size / CHECKLIST_ITEMS.length) * 100;
  const isComplete = checkedItems.size === CHECKLIST_ITEMS.length;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[550px] bg-zinc-900 border-zinc-800 text-zinc-100">
        <DialogHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="p-2 rounded-lg bg-gradient-to-br from-emerald-600 to-green-600">
                <CheckCircle2 className="w-6 h-6 text-white" />
              </div>
              <div>
                <DialogTitle className="text-xl font-bold">
                  Deployment Checklist
                </DialogTitle>
                <DialogDescription className="text-zinc-400">
                  Track your deployment progress
                </DialogDescription>
              </div>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleReset}
              className="text-zinc-400 hover:text-zinc-200"
            >
              <RotateCcw className="w-4 h-4" />
            </Button>
          </div>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {/* Progress Bar */}
          <div className="space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-zinc-400">Progress</span>
              <span className="text-violet-400 font-semibold">
                {checkedItems.size} / {CHECKLIST_ITEMS.length} completed
              </span>
            </div>
            <Progress value={progress} className="h-2" />
          </div>

          {isComplete && (
            <div className="p-4 rounded-lg bg-green-900/20 border border-green-700/50 text-center">
              <div className="flex items-center justify-center gap-2 text-green-400 font-semibold mb-1">
                <CheckCircle2 className="w-5 h-5" />
                <span>All steps completed! 🎉</span>
              </div>
              <p className="text-xs text-green-400/80">
                Your infrastructure should be deployed and ready
              </p>
            </div>
          )}

          <Separator className="bg-zinc-800" />

          {/* Checklist Items */}
          <div className="space-y-3">
            {CHECKLIST_ITEMS.map((item, index) => {
              const isChecked = checkedItems.has(item.id);
              const Icon = item.icon;

              return (
                <div
                  key={item.id}
                  className={`
                    group p-3 rounded-lg border transition-all
                    ${isChecked 
                      ? 'bg-zinc-800/30 border-green-700/50' 
                      : 'bg-zinc-800/50 border-zinc-700/50 hover:border-zinc-600/50'
                    }
                  `}
                >
                  <div className="flex items-start gap-3">
                    {/* Checkbox */}
                    <Checkbox
                      id={item.id}
                      checked={isChecked}
                      onCheckedChange={() => handleToggle(item.id)}
                      className="mt-1"
                    />

                    {/* Icon */}
                    <div className={`
                      p-2 rounded transition-colors
                      ${isChecked 
                        ? 'bg-green-700/30 text-green-400' 
                        : 'bg-zinc-700/50 text-violet-400'
                      }
                    `}>
                      {isChecked ? (
                        <CheckCircle2 className="w-4 h-4" />
                      ) : (
                        <Icon className="w-4 h-4" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0">
                      <label
                        htmlFor={item.id}
                        className={`
                          text-sm font-medium cursor-pointer block mb-1
                          ${isChecked ? 'text-zinc-400 line-through' : 'text-zinc-200'}
                        `}
                      >
                        {index + 1}. {item.title}
                      </label>
                      <p className="text-xs text-zinc-400 mb-2">
                        {item.description}
                      </p>
                      {item.link && (
                        <a
                          href={item.link}
                          target={item.link.startsWith('http') ? '_blank' : '_self'}
                          rel={item.link.startsWith('http') ? 'noopener noreferrer' : ''}
                          onClick={(e) => {
                            if (item.link === '#' && onOpenQuickStart) {
                              e.preventDefault();
                              onOpenQuickStart();
                            }
                          }}
                          className="inline-flex items-center gap-1 text-xs text-violet-400 hover:text-violet-300 transition-colors"
                        >
                          {item.linkText}
                          {item.link.startsWith('http') && (
                            <ExternalLink className="w-3 h-3" />
                          )}
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Tips */}
          <div className="p-3 rounded-lg bg-blue-900/20 border border-blue-700/50">
            <p className="text-xs text-blue-400 mb-2 font-medium">
              💡 Pro Tips:
            </p>
            <ul className="text-xs text-blue-400/80 space-y-1">
              <li>• Check off items as you complete them</li>
              <li>• Your progress is automatically saved</li>
              <li>• Click on links for helpful resources</li>
              <li>• Reset checklist for a new deployment</li>
            </ul>
          </div>
        </div>

        <DialogFooter className="flex-col sm:flex-row gap-2">
          <Button
            variant="outline"
            onClick={onOpenQuickStart}
            className="border-zinc-700 hover:bg-zinc-800"
          >
            View Quick Start Guide
          </Button>
          <Button
            onClick={() => onOpenChange(false)}
            className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
          >
            Done
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}
