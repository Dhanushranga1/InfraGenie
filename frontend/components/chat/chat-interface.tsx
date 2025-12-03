/**
 * Chat Interface Component
 * 
 * Main chat panel with message history and input
 */

"use client";

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { MessageBubble } from './message-bubble';
import { TerminalLoader } from './terminal-loader';
import { useProjectStore } from '@/lib/store';
import { generateInfrastructure } from '@/lib/api';

export function ChatInterface() {
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);
  
  // Zustand store
  const { messages, isLoading, setLoading, setProjectData, addMessage, setWorkflowStage, setWorkflowError } = useProjectStore();
  
  // Simulate workflow stages during loading
  useEffect(() => {
    if (!isLoading) {
      setWorkflowStage('', 'complete'); // Reset
      return;
    }

    const stages = [
      { name: 'clarifier', delay: 1000 },
      { name: 'planner', delay: 3000 },
      { name: 'architect', delay: 8000 },
      { name: 'validator', delay: 12000 },
      { name: 'completeness', delay: 14000 },
      { name: 'deep_validation', delay: 18000 },
      { name: 'security', delay: 22000 },
      { name: 'parser', delay: 24000 },
      { name: 'finops', delay: 27000 },
      { name: 'ansible', delay: 30000 },
    ];

    const timeouts: NodeJS.Timeout[] = [];

    stages.forEach(({ name, delay }) => {
      const timeout = setTimeout(() => {
        setWorkflowStage(name, 'active');
        // Mark previous as complete
        const prevIndex = stages.findIndex(s => s.name === name) - 1;
        if (prevIndex >= 0) {
          setWorkflowStage(stages[prevIndex].name, 'complete');
        }
      }, delay);
      timeouts.push(timeout);
    });

    return () => {
      timeouts.forEach(clearTimeout);
    };
  }, [isLoading, setWorkflowStage]);
  
  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isLoading]);
  
  // Mutation for generating infrastructure
  const mutation = useMutation({
    mutationFn: generateInfrastructure,
    onMutate: () => {
      setLoading(true);
      setWorkflowStage('clarifier', 'active');
      setWorkflowError(null);
    },
    onSuccess: (data) => {
      console.log('[ChatInterface] Received data from API:', {
        hasTerraformCode: !!data.terraform_code,
        terraformCodeLength: data.terraform_code?.length || 0,
        hasAnsiblePlaybook: !!data.ansible_playbook,
        ansiblePlaybookLength: data.ansible_playbook?.length || 0,
        hasCostEstimate: !!data.cost_estimate,
        hasGraphData: !!data.graph_data,
        graphNodes: data.graph_data?.nodes?.length || 0,
        graphEdges: data.graph_data?.edges?.length || 0,
      });
      
      // Mark all stages as complete
      const allStages = ['clarifier', 'planner', 'architect', 'validator', 'completeness', 'deep_validation', 'security', 'parser', 'finops', 'ansible'];
      allStages.forEach(stage => setWorkflowStage(stage, 'complete'));
      
      // Update global store with infrastructure data
      setProjectData({
        terraformCode: data.terraform_code,
        ansiblePlaybook: data.ansible_playbook,
        costEstimate: data.cost_estimate,
        securityRisks: data.security_errors,
        graphData: data.graph_data,
      });
      
      console.log('[ChatInterface] Updated store with data');
      
      // Verify store was actually updated
      setTimeout(() => {
        const currentState = useProjectStore.getState();
        console.log('[ChatInterface] Store verification after 100ms:', {
          hasTerraformInStore: !!currentState.terraformCode,
          terraformLength: currentState.terraformCode?.length || 0,
          hasGraphDataInStore: !!currentState.graphData,
          graphNodesInStore: currentState.graphData?.nodes?.length || 0,
          graphEdgesInStore: currentState.graphData?.edges?.length || 0,
        });
      }, 100);
      
      // Add AI response to chat with better error context
      let responseText: string;
      
      if (data.validation_error) {
        // Workflow failed - explain why download/diagram won't work
        responseText = `❌ **Infrastructure Generation Failed**\n\n${data.validation_error}\n\n⚠️ **Note:** The download button and architecture diagram will not be available because the workflow did not complete successfully.`;
      } else if (data.is_clean) {
        responseText = `✅ Infrastructure generated successfully!\n\n**Cost Estimate:** ${data.cost_estimate}\n**Security:** No critical issues found\n\nYour Terraform and Ansible code are ready for deployment.`;
      } else {
        responseText = `⚠️ Infrastructure generated with warnings.\n\n**Cost Estimate:** ${data.cost_estimate}\n**Security Issues:** ${data.security_errors.length} found\n\nPlease review the security risks before deployment.`;
      }
      
      addMessage('ai', responseText);
      setLoading(false);
    },
    onError: (error: any) => {
      const isTimeout = error.code === 'ECONNABORTED' || error.message?.includes('timeout');
      const isRateLimit = error.response?.data?.detail?.includes('Rate limit') || 
                          error.response?.data?.detail?.includes('rate_limit');
      const errorDetail = error.response?.data?.detail || error.message || 'Failed to generate infrastructure';
      
      if (isRateLimit) {
        setWorkflowError('API rate limit exceeded');
        addMessage('ai', `🚫 **API Rate Limit Exceeded**\n\nYour Groq API has hit its daily token limit. Please:\n\n1. Wait for the limit to reset (~46 minutes)\n2. Or use a different API key in the backend .env file\n3. Or upgrade your Groq tier at https://console.groq.com/settings/billing\n\n**Error:** ${errorDetail}`);
      } else if (isTimeout) {
        setWorkflowError('Request timeout - infrastructure generation took too long. This can happen with complex requests or slow network.');
        addMessage('ai', `⏱️ **Timeout Error**\n\nThe infrastructure generation took longer than expected (>10 minutes). This can happen when:\n- Terraform init downloads large providers\n- Deep validation runs multiple times\n- Network is slow\n\n**Try:**\n- Simplifying your request\n- Checking your internet connection\n- Retrying in a moment`);
      } else {
        setWorkflowError(errorDetail);
        addMessage('ai', `❌ Error: ${errorDetail}\n\nPlease try again or refine your prompt.`);
      }
      setLoading(false);
    },
  });
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;
    
    // Add user message to chat
    addMessage('user', input);
    
    // Call backend API
    mutation.mutate(input);
    
    // Clear input
    setInput('');
  };
  
  return (
    <div className="h-full flex flex-col relative">
      {/* Message List */}
      <div className="flex-1 overflow-y-auto p-6" ref={scrollRef}>
        <div className="space-y-4">
          {messages.length === 0 && (
            <div className="text-center py-12 space-y-4">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-violet-600/10 border border-violet-600/20">
                <svg className="w-8 h-8 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-zinc-300 mb-2">
                  Start a Conversation
                </h3>
                <p className="text-sm text-zinc-500 max-w-xs mx-auto">
                  Describe your infrastructure needs and I'll generate the code for you.
                </p>
              </div>
              <div className="flex flex-col gap-2 max-w-xs mx-auto text-left">
                <div className="text-xs text-zinc-600 font-mono">Examples:</div>
                <div className="text-xs text-zinc-500 bg-zinc-900/50 rounded px-3 py-2 border border-zinc-800">
                  "AWS EC2 instance with Nginx"
                </div>
                <div className="text-xs text-zinc-500 bg-zinc-900/50 rounded px-3 py-2 border border-zinc-800">
                  "ECS cluster with PostgreSQL RDS"
                </div>
              </div>
            </div>
          )}
          
          {messages.map((message) => (
            <MessageBubble
              key={message.id}
              role={message.role}
              content={message.content}
            />
          ))}
          
          {/* Terminal Loader */}
          {isLoading && <TerminalLoader />}
        </div>
      </div>
      
      {/* Input Area */}
      <div className="border-t border-zinc-800 bg-zinc-900/50 backdrop-blur-xl p-4">
        <form onSubmit={handleSubmit} className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Describe your infrastructure..."
            disabled={isLoading}
            className="flex-1 bg-zinc-950 border-zinc-800 text-zinc-100 placeholder:text-zinc-600 focus-visible:ring-violet-500"
          />
          <Button
            type="submit"
            disabled={isLoading || !input.trim()}
            className="bg-violet-600 hover:bg-violet-700 text-white"
          >
            <Send className="w-4 h-4" />
          </Button>
        </form>
        
        {/* Status Text */}
        {isLoading && (
          <p className="text-xs text-zinc-500 mt-2 font-mono">
            Processing your request...
          </p>
        )}
      </div>
    </div>
  );
}
