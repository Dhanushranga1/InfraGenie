/**
 * Download Modal Component
 * 
 * Beautiful modal that shows deployment kit contents,
 * download progress, and success state
 */

"use client";

import { useState } from 'react';
import { 
  Download, 
  FileCode, 
  FileText, 
  Terminal, 
  Shield, 
  CheckCircle2,
  Sparkles,
  Copy,
  Check,
  Package
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Separator } from '@/components/ui/separator';

interface DownloadModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onDownload: () => Promise<void>;
  isDownloading: boolean;
  downloadComplete: boolean;
  estimatedSize?: string;
  onOpenQuickStart?: () => void;
  onOpenChecklist?: () => void;
}

interface FileItem {
  name: string;
  description: string;
  icon: any;
  badge?: string;
}

const FILE_CONTENTS: FileItem[] = [
  {
    name: 'main.tf',
    description: 'AI-generated Terraform infrastructure code',
    icon: FileCode,
    badge: 'Validated'
  },
  {
    name: 'playbook.yml',
    description: 'Ansible configuration playbook',
    icon: FileText,
    badge: 'Tested'
  },
  {
    name: 'deploy.sh',
    description: 'Automated deployment script with TUI',
    icon: Terminal,
    badge: 'Interactive'
  },
  {
    name: 'destroy.sh',
    description: 'Safe infrastructure cleanup script',
    icon: Shield,
  },
  {
    name: 'README.md',
    description: 'Comprehensive deployment guide',
    icon: FileText,
  },
];

export function DownloadModal({
  open,
  onOpenChange,
  onDownload,
  isDownloading,
  downloadComplete,
  estimatedSize = '~25 KB',
  onOpenQuickStart,
  onOpenChecklist,
}: DownloadModalProps) {
  const [copiedFile, setCopiedFile] = useState<string | null>(null);
  const [downloadProgress, setDownloadProgress] = useState(0);

  // Simulate download progress
  const handleDownloadClick = async () => {
    setDownloadProgress(0);
    
    // Simulate progress updates
    const progressInterval = setInterval(() => {
      setDownloadProgress((prev) => {
        if (prev >= 95) {
          clearInterval(progressInterval);
          return prev;
        }
        return prev + 5;
      });
    }, 100);

    try {
      await onDownload();
      setDownloadProgress(100);
    } catch (error) {
      clearInterval(progressInterval);
      setDownloadProgress(0);
    }
  };

  const copyToClipboard = (text: string, fileName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedFile(fileName);
    setTimeout(() => setCopiedFile(null), 2000);
  };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[600px] bg-zinc-900 border-zinc-800 text-zinc-100">
        {!downloadComplete ? (
          <>
            <DialogHeader>
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-gradient-to-br from-violet-600 to-indigo-600">
                  <Package className="w-6 h-6 text-white" />
                </div>
                <div>
                  <DialogTitle className="text-xl font-bold">
                    Download Deployment Kit
                  </DialogTitle>
                  <DialogDescription className="text-zinc-400">
                    Everything you need to deploy your infrastructure
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            <div className="space-y-4 py-4">
              {/* File Contents */}
              <div>
                <h3 className="text-sm font-semibold text-zinc-300 mb-3">
                  📦 What's included:
                </h3>
                <div className="space-y-2">
                  {FILE_CONTENTS.map((file) => (
                    <div
                      key={file.name}
                      className="flex items-start gap-3 p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 hover:border-zinc-600/50 transition-colors"
                    >
                      <div className="p-2 rounded bg-zinc-700/50">
                        <file.icon className="w-4 h-4 text-violet-400" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-medium text-zinc-200">
                            {file.name}
                          </span>
                          {file.badge && (
                            <Badge variant="outline" className="text-xs border-violet-500/50 text-violet-400">
                              {file.badge}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-zinc-400 mt-0.5">
                          {file.description}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <Separator className="bg-zinc-800" />

              {/* Features */}
              <div>
                <h3 className="text-sm font-semibold text-zinc-300 mb-3">
                  ✨ Features:
                </h3>
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Zero-config deployment</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Interactive TUI dialogs</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Auto-validation</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Smart retry logic</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Cost control built-in</span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-zinc-400">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span>Complete docs</span>
                  </div>
                </div>
              </div>

              {/* Download Progress */}
              {isDownloading && (
                <div className="space-y-2">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-400">Preparing download...</span>
                    <span className="text-violet-400 font-medium">{downloadProgress}%</span>
                  </div>
                  <Progress value={downloadProgress} className="h-2" />
                </div>
              )}

              {/* Size Info */}
              <div className="flex items-center justify-between text-xs text-zinc-500 px-1">
                <span>Total size: {estimatedSize}</span>
                <span>Self-contained deployment kit</span>
              </div>
            </div>

            <DialogFooter className="flex-col sm:flex-row gap-2">
              <Button
                variant="outline"
                onClick={() => onOpenChange(false)}
                className="border-zinc-700 hover:bg-zinc-800"
              >
                Cancel
              </Button>
              <Button
                onClick={handleDownloadClick}
                disabled={isDownloading}
                className="bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-semibold"
              >
                {isDownloading ? (
                  <>
                    <Download className="w-4 h-4 mr-2 animate-bounce" />
                    Downloading...
                  </>
                ) : (
                  <>
                    <Download className="w-4 h-4 mr-2" />
                    Download Kit
                  </>
                )}
              </Button>
            </DialogFooter>
          </>
        ) : (
          <>
            {/* Success State */}
            <DialogHeader>
              <div className="flex flex-col items-center gap-4 py-6">
                <div className="relative">
                  <div className="p-4 rounded-full bg-gradient-to-br from-green-600 to-emerald-600 animate-pulse">
                    <CheckCircle2 className="w-12 h-12 text-white" />
                  </div>
                  <Sparkles className="w-6 h-6 text-yellow-400 absolute -top-1 -right-1 animate-spin" />
                </div>
                <div className="text-center">
                  <DialogTitle className="text-2xl font-bold mb-2">
                    Download Complete! 🎉
                  </DialogTitle>
                  <DialogDescription className="text-zinc-400">
                    Your deployment kit is ready to use
                  </DialogDescription>
                </div>
              </div>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div className="p-4 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                <h3 className="text-sm font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                  <Terminal className="w-4 h-4 text-violet-400" />
                  Next Steps:
                </h3>
                <ol className="space-y-2 text-sm text-zinc-400">
                  <li className="flex items-start gap-2">
                    <span className="text-violet-400 font-bold">1.</span>
                    <span>Extract the downloaded ZIP file</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-violet-400 font-bold">2.</span>
                    <div className="flex-1">
                      <span>Open terminal and run:</span>
                      <div className="mt-2 p-2 rounded bg-zinc-900 border border-zinc-700 font-mono text-xs flex items-center justify-between">
                        <code className="text-green-400">./deploy.sh</code>
                        <Button
                          variant="ghost"
                          size="sm"
                          className="h-6 px-2"
                          onClick={() => copyToClipboard('./deploy.sh', 'deploy')}
                        >
                          {copiedFile === 'deploy' ? (
                            <Check className="w-3 h-3 text-green-500" />
                          ) : (
                            <Copy className="w-3 h-3" />
                          )}
                        </Button>
                      </div>
                    </div>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-violet-400 font-bold">3.</span>
                    <span>Follow the interactive prompts</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-violet-400 font-bold">4.</span>
                    <span>Connect to your deployed infrastructure! 🚀</span>
                  </li>
                </ol>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Button
                  variant="outline"
                  onClick={onOpenQuickStart}
                  className="border-zinc-700 hover:bg-zinc-800"
                >
                  <FileText className="w-4 h-4 mr-2" />
                  Quick Start Guide
                </Button>
                <Button
                  variant="outline"
                  onClick={onOpenChecklist}
                  className="border-zinc-700 hover:bg-zinc-800"
                >
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  View Checklist
                </Button>
              </div>
            </div>

            <DialogFooter>
              <Button
                onClick={() => onOpenChange(false)}
                className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700"
              >
                Done
              </Button>
            </DialogFooter>
          </>
        )}
      </DialogContent>
    </Dialog>
  );
}
