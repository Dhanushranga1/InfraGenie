/**
 * Quick Start Guide Component
 * 
 * Interactive step-by-step guide for deploying infrastructure
 */

"use client";

import { useState } from 'react';
import { 
  Book, 
  Terminal, 
  CheckCircle, 
  AlertCircle,
  Copy,
  Check,
  ExternalLink,
  Zap,
  Shield,
  Download as DownloadIcon
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from '@/components/ui/accordion';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';

interface QuickStartGuideProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

const CopyButton = ({ text, label }: { text: string; label?: string }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      onClick={handleCopy}
      className="h-8 px-2 hover:bg-zinc-700"
    >
      {copied ? (
        <Check className="w-3 h-3 text-green-500" />
      ) : (
        <Copy className="w-3 h-3" />
      )}
      {label && <span className="ml-1 text-xs">{label}</span>}
    </Button>
  );
};

const CodeBlock = ({ children, copyText }: { children: React.ReactNode; copyText: string }) => (
  <div className="mt-2 p-3 rounded-lg bg-zinc-900 border border-zinc-700 font-mono text-sm">
    <div className="flex items-start justify-between gap-2">
      <code className="text-green-400 flex-1">{children}</code>
      <CopyButton text={copyText} />
    </div>
  </div>
);

export function QuickStartGuide({ open, onOpenChange }: QuickStartGuideProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[700px] max-h-[85vh] overflow-hidden bg-zinc-900 border-zinc-800 text-zinc-100">
        <DialogHeader>
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-gradient-to-br from-blue-600 to-cyan-600">
              <Book className="w-6 h-6 text-white" />
            </div>
            <div>
              <DialogTitle className="text-xl font-bold">
                Quick Start Guide
              </DialogTitle>
              <DialogDescription className="text-zinc-400">
                Everything you need to deploy successfully
              </DialogDescription>
            </div>
          </div>
        </DialogHeader>

        <Tabs defaultValue="prerequisites" className="mt-4">
          <TabsList className="grid w-full grid-cols-4 bg-zinc-800">
            <TabsTrigger value="prerequisites" className="text-xs">
              Prerequisites
            </TabsTrigger>
            <TabsTrigger value="deployment" className="text-xs">
              Deployment
            </TabsTrigger>
            <TabsTrigger value="walkthrough" className="text-xs">
              Walkthrough
            </TabsTrigger>
            <TabsTrigger value="troubleshooting" className="text-xs">
              Help
            </TabsTrigger>
          </TabsList>

          <div className="max-h-[50vh] overflow-y-auto mt-4 px-1">
            {/* Prerequisites Tab */}
            <TabsContent value="prerequisites" className="space-y-4">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-zinc-300 flex items-center gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500" />
                  Required Tools
                </h3>
                
                <div className="space-y-3">
                  {/* Terraform */}
                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-zinc-200">Terraform</span>
                      <Badge variant="outline" className="text-xs">Required</Badge>
                    </div>
                    <p className="text-xs text-zinc-400 mb-2">
                      Infrastructure provisioning tool
                    </p>
                    <CodeBlock copyText="brew install terraform  # macOS">
                      brew install terraform  # macOS
                    </CodeBlock>
                    <CodeBlock copyText="sudo apt install terraform  # Linux">
                      sudo apt install terraform  # Linux
                    </CodeBlock>
                  </div>

                  {/* Ansible */}
                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-zinc-200">Ansible</span>
                      <Badge variant="outline" className="text-xs">Required</Badge>
                    </div>
                    <p className="text-xs text-zinc-400 mb-2">
                      Configuration management tool
                    </p>
                    <CodeBlock copyText="brew install ansible  # macOS">
                      brew install ansible  # macOS
                    </CodeBlock>
                    <CodeBlock copyText="sudo apt install ansible  # Linux">
                      sudo apt install ansible  # Linux
                    </CodeBlock>
                  </div>

                  {/* AWS CLI */}
                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-zinc-200">AWS CLI</span>
                      <Badge variant="outline" className="text-xs">Required</Badge>
                    </div>
                    <p className="text-xs text-zinc-400 mb-2">
                      AWS command line interface
                    </p>
                    <CodeBlock copyText="brew install awscli  # macOS">
                      brew install awscli  # macOS
                    </CodeBlock>
                    <CodeBlock copyText="sudo apt install awscli  # Linux">
                      sudo apt install awscli  # Linux
                    </CodeBlock>
                  </div>

                  {/* Dialog/Whiptail */}
                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-medium text-zinc-200">Dialog</span>
                      <Badge variant="outline" className="text-xs border-blue-500/50 text-blue-400">
                        Optional
                      </Badge>
                    </div>
                    <p className="text-xs text-zinc-400 mb-2">
                      For beautiful TUI prompts (auto-fallback available)
                    </p>
                    <CodeBlock copyText="brew install dialog  # macOS">
                      brew install dialog  # macOS
                    </CodeBlock>
                    <CodeBlock copyText="sudo apt install dialog  # Linux">
                      sudo apt install dialog  # Linux
                    </CodeBlock>
                  </div>
                </div>

                <div className="flex items-start gap-2 p-3 rounded-lg bg-blue-900/20 border border-blue-700/50 text-xs text-blue-400">
                  <AlertCircle className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>
                    The deployment script checks all prerequisites automatically and provides helpful error messages if anything is missing.
                  </span>
                </div>
              </div>
            </TabsContent>

            {/* Deployment Tab */}
            <TabsContent value="deployment" className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                    <Terminal className="w-4 h-4 text-violet-400" />
                    Deployment Steps
                  </h3>
                  
                  <div className="space-y-3">
                    {/* Step 1 */}
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold">
                        1
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-zinc-200 mb-1">
                          Extract the ZIP file
                        </p>
                        <CodeBlock copyText="unzip infragenie-deployment-*.zip">
                          unzip infragenie-deployment-*.zip
                        </CodeBlock>
                        <CodeBlock copyText="cd infragenie-deployment-*">
                          cd infragenie-deployment-*
                        </CodeBlock>
                      </div>
                    </div>

                    {/* Step 2 */}
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold">
                        2
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-zinc-200 mb-1">
                          Make the script executable
                        </p>
                        <CodeBlock copyText="chmod +x deploy.sh">
                          chmod +x deploy.sh
                        </CodeBlock>
                      </div>
                    </div>

                    {/* Step 3 */}
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-violet-600 flex items-center justify-center text-xs font-bold">
                        3
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-zinc-200 mb-1">
                          Run the deployment script
                        </p>
                        <CodeBlock copyText="./deploy.sh">
                          ./deploy.sh
                        </CodeBlock>
                        <p className="text-xs text-zinc-400 mt-2">
                          The interactive wizard will guide you through:
                        </p>
                        <ul className="text-xs text-zinc-400 mt-2 space-y-1 ml-4">
                          <li>• Prerequisites check</li>
                          <li>• AWS credential setup</li>
                          <li>• Infrastructure provisioning</li>
                          <li>• Server configuration</li>
                        </ul>
                      </div>
                    </div>

                    {/* Step 4 */}
                    <div className="flex gap-3">
                      <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-600 flex items-center justify-center text-xs font-bold">
                        ✓
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium text-zinc-200 mb-1">
                          Connect to your server
                        </p>
                        <p className="text-xs text-zinc-400 mb-2">
                          After deployment, use the SSH command shown in the success message
                        </p>
                        <CodeBlock copyText="ssh -i infragenie-key.pem ubuntu@<YOUR_IP>">
                          ssh -i infragenie-key.pem ubuntu@{'<YOUR_IP>'}
                        </CodeBlock>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="flex items-start gap-2 p-3 rounded-lg bg-yellow-900/20 border border-yellow-700/50 text-xs text-yellow-400">
                  <Zap className="w-4 h-4 mt-0.5 flex-shrink-0" />
                  <span>
                    <strong>Typical deployment time:</strong> 3-7 minutes depending on your AWS region and instance type
                  </span>
                </div>
              </div>
            </TabsContent>

            {/* Walkthrough Tab */}
            <TabsContent value="walkthrough" className="space-y-4">
              <div className="space-y-3">
                <h3 className="text-sm font-semibold text-zinc-300 mb-3 flex items-center gap-2">
                  <DownloadIcon className="w-4 h-4 text-cyan-400" />
                  What to Expect
                </h3>

                <div className="space-y-3">
                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      🎉 Welcome Screen
                    </h4>
                    <p className="text-xs text-zinc-400">
                      Beautiful dialog box welcomes you to the InfraGenie Deployment Wizard
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      📋 Prerequisites Check
                    </h4>
                    <p className="text-xs text-zinc-400 mb-2">
                      Animated progress gauge checks for:
                    </p>
                    <ul className="text-xs text-zinc-400 space-y-1 ml-4">
                      <li>✅ Terraform installation & version</li>
                      <li>✅ Ansible installation & version</li>
                      <li>✅ AWS CLI installation & version</li>
                      <li>✅ jq JSON processor</li>
                    </ul>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      🔐 AWS Credentials
                    </h4>
                    <p className="text-xs text-zinc-400 mb-2">
                      Secure input boxes collect:
                    </p>
                    <ul className="text-xs text-zinc-400 space-y-1 ml-4">
                      <li>• AWS Access Key ID (visible)</li>
                      <li>• AWS Secret Access Key (hidden password field)</li>
                      <li>• AWS Region (default: us-east-1)</li>
                    </ul>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      📊 Deployment Confirmation
                    </h4>
                    <p className="text-xs text-zinc-400">
                      Summary dialog shows what will be deployed with Yes/No buttons to proceed or cancel
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      🏗️ Infrastructure Provisioning
                    </h4>
                    <p className="text-xs text-zinc-400">
                      Progress gauge shows: Init → Validate → Plan → Apply (2-5 minutes)
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      🔌 SSH Connection Waiting
                    </h4>
                    <p className="text-xs text-zinc-400">
                      Animated gauge waits for server to be ready (typically 1-3 minutes)
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50">
                    <h4 className="text-sm font-medium text-zinc-200 mb-2">
                      ⚙️ Server Configuration
                    </h4>
                    <p className="text-xs text-zinc-400">
                      Ansible installs packages and configures security (with auto-retry)
                    </p>
                  </div>

                  <div className="p-3 rounded-lg bg-green-800/30 border border-green-700/50">
                    <h4 className="text-sm font-medium text-green-200 mb-2">
                      🎉 Success!
                    </h4>
                    <p className="text-xs text-green-400">
                      Final dialog shows SSH connection details, important reminders, and next steps
                    </p>
                  </div>
                </div>
              </div>
            </TabsContent>

            {/* Troubleshooting Tab */}
            <TabsContent value="troubleshooting" className="space-y-4">
              <Accordion type="single" collapsible className="w-full">
                <AccordionItem value="item-1" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    Prerequisites check fails
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>Install the missing tool(s) shown in the error message:</p>
                    <CodeBlock copyText="brew install terraform ansible awscli">
                      brew install terraform ansible awscli
                    </CodeBlock>
                    <p>Then run deploy.sh again.</p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="item-2" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    AWS credentials invalid
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>Verify your credentials:</p>
                    <ul className="space-y-1 ml-4">
                      <li>• Go to AWS Console → IAM → Users</li>
                      <li>• Create new access key if needed</li>
                      <li>• Ensure user has EC2, VPC permissions</li>
                      <li>• Check for typos in Access Key ID/Secret</li>
                    </ul>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="item-3" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    Terraform apply fails
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>Common issues:</p>
                    <ul className="space-y-1 ml-4">
                      <li>• <strong>Quota limits:</strong> Check AWS service limits</li>
                      <li>• <strong>Region:</strong> Try a different AWS region</li>
                      <li>• <strong>Permissions:</strong> Ensure IAM permissions are correct</li>
                      <li>• <strong>VPC limits:</strong> Check if you've hit VPC limits</li>
                    </ul>
                    <p className="mt-2">Review error message and fix the specific issue, then re-run.</p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="item-4" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    SSH connection timeout
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>Check these items:</p>
                    <ul className="space-y-1 ml-4">
                      <li>• AWS Console → EC2 → Instance status (should show 2/2 checks)</li>
                      <li>• Security Group allows SSH (port 22) from your IP</li>
                      <li>• Instance has a public IP address</li>
                      <li>• Instance is in a public subnet</li>
                    </ul>
                    <p className="mt-2">The script waits up to 6 minutes. If it still fails, check AWS Console for instance issues.</p>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="item-5" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    Ansible configuration fails
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>The script automatically retries 3 times. If it still fails:</p>
                    <ul className="space-y-1 ml-4">
                      <li>• Check the error logs shown</li>
                      <li>• SSH to the server manually to verify connectivity</li>
                      <li>• Run Ansible manually:</li>
                    </ul>
                    <CodeBlock copyText="ansible-playbook -i inventory.ini playbook.yml">
                      ansible-playbook -i inventory.ini playbook.yml
                    </CodeBlock>
                  </AccordionContent>
                </AccordionItem>

                <AccordionItem value="item-6" className="border-zinc-800">
                  <AccordionTrigger className="text-sm text-zinc-300 hover:text-zinc-100">
                    Need to destroy infrastructure
                  </AccordionTrigger>
                  <AccordionContent className="text-xs text-zinc-400 space-y-2">
                    <p>To safely destroy all resources:</p>
                    <CodeBlock copyText="./destroy.sh">
                      ./destroy.sh
                    </CodeBlock>
                    <p className="mt-2">
                      This removes all AWS resources created by Terraform. Make sure you're in the same directory with terraform.tfstate file.
                    </p>
                    <div className="flex items-start gap-2 p-2 rounded bg-red-900/20 border border-red-700/50 text-red-400 mt-2">
                      <Shield className="w-3 h-3 mt-0.5 flex-shrink-0" />
                      <span className="text-xs">
                        Always run destroy.sh when done to avoid ongoing AWS charges!
                      </span>
                    </div>
                  </AccordionContent>
                </AccordionItem>
              </Accordion>

              <div className="p-3 rounded-lg bg-zinc-800/50 border border-zinc-700/50 text-xs text-zinc-400">
                <p className="font-medium text-zinc-300 mb-2">Still having issues?</p>
                <ul className="space-y-1 ml-4">
                  <li>• Check the complete logs in terminal</li>
                  <li>• Review AWS CloudFormation/CloudWatch logs</li>
                  <li>• Verify all prerequisites are correctly installed</li>
                  <li>• Try deploying in a different AWS region</li>
                </ul>
              </div>
            </TabsContent>
          </div>
        </Tabs>
      </DialogContent>
    </Dialog>
  );
}
