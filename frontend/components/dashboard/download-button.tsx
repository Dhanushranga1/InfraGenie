/**
 * Download Button Component
 * 
 * Downloads the generated deployment kit as a zip file
 */

"use client";

import { useState, useEffect } from 'react';
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

  const isDisabled = !terraformCode || !ansiblePlaybook || isDownloading;

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

  const handleDownload = async () => {
    console.log('[Download] Button clicked');
    console.log('[Download] Terraform code length:', terraformCode?.length);
    console.log('[Download] Ansible playbook length:', ansiblePlaybook?.length);
    
    if (!terraformCode || !ansiblePlaybook) {
      console.error('[Download] Missing required data');
      alert('Missing infrastructure code. Please generate infrastructure first.');
      return;
    }

    setIsDownloading(true);
    console.log('[Download] Starting download...');

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
    } catch (error: any) {
      console.error('[Download] Failed:', error);
      console.error('[Download] Error details:', {
        message: error.message,
        response: error.response?.data,
        status: error.response?.status,
      });
      alert(`Failed to download deployment kit: ${error.message || 'Unknown error'}. Check console for details.`);
    } finally {
      setIsDownloading(false);
    }
  };

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
