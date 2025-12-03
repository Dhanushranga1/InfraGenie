/**
 * Download Button Component
 * 
 * Enhanced download experience with modal, guide, and checklist
 */

"use client";

import { useState, useEffect } from 'react';
import { Download, Loader2, Sparkles } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useProjectStore } from '@/lib/store';
import { downloadDeploymentKit } from '@/lib/api';
import { DownloadModal } from './download-modal';
import { QuickStartGuide } from './quick-start-guide';
import { DeploymentChecklist } from './deployment-checklist';
import { toast } from 'sonner';

export function DownloadButton() {
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadComplete, setDownloadComplete] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showQuickStart, setShowQuickStart] = useState(false);
  const [showChecklist, setShowChecklist] = useState(false);
  
  const terraformCode = useProjectStore((state) => state.terraformCode);
  const ansiblePlaybook = useProjectStore((state) => state.ansiblePlaybook);
  const costEstimate = useProjectStore((state) => state.costEstimate);
  const messages = useProjectStore((state) => state.messages);

  // Get the last user message as the prompt
  const userPrompt = messages
    .filter((m) => m.role === 'user')
    .pop()?.content || 'infrastructure';

  const isDisabled = !terraformCode || !ansiblePlaybook;

  // Debug logging - only when values change
  useEffect(() => {
    console.log('[DownloadButton] State updated:', {
      hasTerraformCode: !!terraformCode,
      hasAnsiblePlaybook: !!ansiblePlaybook,
      isDisabled,
      terraformCodeLength: terraformCode?.length || 0,
      ansiblePlaybookLength: ansiblePlaybook?.length || 0,
    });
  }, [terraformCode, ansiblePlaybook, isDisabled]);

  // Reset download complete state when modal closes
  useEffect(() => {
    if (!showModal) {
      setDownloadComplete(false);
    }
  }, [showModal]);

  const handleDownloadClick = () => {
    console.log('[Download] Opening modal');
    setShowModal(true);
  };

  const handleDownload = async () => {
    console.log('[Download] Starting download...');
    console.log('[Download] Terraform code length:', terraformCode?.length);
    console.log('[Download] Ansible playbook length:', ansiblePlaybook?.length);
    
    if (!terraformCode || !ansiblePlaybook) {
      console.error('[Download] Missing required data');
      toast.error('Missing infrastructure code. Please generate infrastructure first.');
      return;
    }

    setIsDownloading(true);
    setDownloadComplete(false);

    try {
      // Call download API
      console.log('[Download] Calling API...');
      const blob = await downloadDeploymentKit({
        project_id: `project-${Date.now()}`,
        terraform_code: terraformCode,
        ansible_playbook: ansiblePlaybook,
        cost_estimate: costEstimate || 'N/A',
        user_prompt: userPrompt,
      });

      console.log('[Download] Received blob:', blob.size, 'bytes');

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `infragenie-deployment-${Date.now()}.zip`;
      document.body.appendChild(link);
      console.log('[Download] Triggering download...');
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      
      console.log('[Download] Download completed successfully!');
      setDownloadComplete(true);
      
      // Show success toast
      toast.success('Deployment kit downloaded!', {
        description: 'Extract the ZIP file and run ./deploy.sh to get started.',
        duration: 5000,
      });
      
    } catch (error: any) {
      console.error('[Download] Failed:', error);
      console.error('[Download] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      
      toast.error('Download failed', {
        description: error.message || 'Unknown error. Check console for details.',
        duration: 5000,
      });
      
      setShowModal(false);
    } finally {
      setIsDownloading(false);
    }
  };

  const handleOpenQuickStart = () => {
    setShowModal(false);
    setShowChecklist(false);
    setShowQuickStart(true);
  };

  const handleOpenChecklist = () => {
    setShowModal(false);
    setShowQuickStart(false);
    setShowChecklist(true);
  };

  return (
    <>
      {/* Download Modal */}
      <DownloadModal
        open={showModal}
        onOpenChange={setShowModal}
        onDownload={handleDownload}
        isDownloading={isDownloading}
        downloadComplete={downloadComplete}
        estimatedSize="~25 KB"
        onOpenQuickStart={handleOpenQuickStart}
        onOpenChecklist={handleOpenChecklist}
      />

      {/* Quick Start Guide */}
      <QuickStartGuide
        open={showQuickStart}
        onOpenChange={setShowQuickStart}
      />

      {/* Deployment Checklist */}
      <DeploymentChecklist
        open={showChecklist}
        onOpenChange={setShowChecklist}
        onOpenQuickStart={handleOpenQuickStart}
      />

      {/* Enhanced Download Button */}
      <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
        <div className="space-y-3">
          {/* Main Download Button */}
          <Button
            onClick={handleDownloadClick}
            disabled={isDisabled || isDownloading}
            className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-semibold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed relative overflow-hidden group"
            size="lg"
          >
            {/* Shimmer effect */}
            <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000" />
            
            {isDownloading ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Preparing Download...
              </>
            ) : (
              <>
                <Download className="w-4 h-4 mr-2" />
                Download Deployment Kit
                <Sparkles className="w-4 h-4 ml-2 opacity-70" />
              </>
            )}
          </Button>
          
          {/* Helper Links */}
          {!isDisabled && (
            <div className="flex items-center justify-center gap-3 text-xs">
              <button
                onClick={() => setShowQuickStart(true)}
                className="text-violet-400 hover:text-violet-300 transition-colors underline underline-offset-2"
              >
                Quick Start Guide
              </button>
              <span className="text-zinc-700">•</span>
              <button
                onClick={() => setShowChecklist(true)}
                className="text-violet-400 hover:text-violet-300 transition-colors underline underline-offset-2"
              >
                Deployment Checklist
              </button>
            </div>
          )}
          
          {/* Disabled State Message */}
          {isDisabled && !isDownloading && (
            <p className="text-xs text-zinc-500 text-center">
              Generate infrastructure first to download
            </p>
          )}
          
          {/* Kit Info */}
          {!isDisabled && (
            <div className="flex items-center justify-center gap-2 text-xs text-zinc-600">
              <span>Complete deployment kit</span>
              <span>•</span>
              <span>~25 KB</span>
              <span>•</span>
              <span>Self-contained</span>
            </div>
          )}
        </div>
      </div>
    </>
  );
}
