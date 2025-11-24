/**
 * Download Button Component
 * 
 * Downloads the generated deployment kit as a zip file
 */

"use client";

import { useState } from 'react';
import { Download, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { useProjectStore } from '@/lib/store';
import { downloadDeploymentKit } from '@/lib/api';

export function DownloadButton() {
  const [isDownloading, setIsDownloading] = useState(false);
  
  const terraformCode = useProjectStore((state) => state.terraformCode);
  const ansiblePlaybook = useProjectStore((state) => state.ansiblePlaybook);
  const costEstimate = useProjectStore((state) => state.costEstimate);
  const messages = useProjectStore((state) => state.messages);

  // Get the last user message as the prompt
  const userPrompt = messages
    .filter((m) => m.role === 'user')
    .pop()?.content || 'infrastructure';

  const handleDownload = async () => {
    if (!terraformCode || !ansiblePlaybook) return;

    setIsDownloading(true);

    try {
      // Call download API
      const blob = await downloadDeploymentKit({
        project_id: `project-${Date.now()}`,
        terraform_code: terraformCode,
        ansible_playbook: ansiblePlaybook,
        cost_estimate: costEstimate || 'N/A',
        user_prompt: userPrompt,
      });

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `infragenie-deployment-${Date.now()}.zip`;
      document.body.appendChild(link);
      link.click();
      
      // Cleanup
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download deployment kit. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  const isDisabled = !terraformCode || !ansiblePlaybook || isDownloading;

  return (
    <div className="p-4 border-t border-zinc-800 bg-zinc-900/50">
      <Button
        onClick={handleDownload}
        disabled={isDisabled}
        className="w-full bg-gradient-to-r from-violet-600 to-indigo-600 hover:from-violet-700 hover:to-indigo-700 text-white font-semibold shadow-lg disabled:opacity-50 disabled:cursor-not-allowed"
        size="lg"
      >
        {isDownloading ? (
          <>
            <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            Preparing Download...
          </>
        ) : (
          <>
            <Download className="w-4 h-4 mr-2" />
            Download Deployment Kit
          </>
        )}
      </Button>
      
      {isDisabled && !isDownloading && (
        <p className="text-xs text-zinc-500 text-center mt-2">
          Generate infrastructure first to download
        </p>
      )}
    </div>
  );
}
