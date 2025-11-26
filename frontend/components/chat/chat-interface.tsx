/**
 * Chat Interface Component
 * 
 * Main chat panel with message history and input
 */

"use client";

import { useState, useRef, useEffect } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Send } from 'lucide-react';
import { ScrollArea } from '@/components/ui/scroll-area';
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
  const { messages, isLoading, setLoading, setProjectData, addMessage } = useProjectStore();
  
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
    },
    onSuccess: (data) => {
      // Update global store with infrastructure data
      setProjectData({
        terraformCode: data.terraform_code,
        ansiblePlaybook: data.ansible_playbook,
        costEstimate: data.cost_estimate,
        securityRisks: data.security_errors,
        graphData: data.graph_data,
      });
      
      // Add AI response to chat
      const responseText = data.is_clean
        ? `✅ Infrastructure generated successfully!\n\n**Cost Estimate:** ${data.cost_estimate}\n**Security:** No critical issues found\n\nYour Terraform and Ansible code are ready for deployment.`
        : `⚠️ Infrastructure generated with warnings.\n\n**Cost Estimate:** ${data.cost_estimate}\n**Security Issues:** ${data.security_errors.length} found\n\nPlease review the security risks before deployment.`;
      
      addMessage('ai', responseText);
      setLoading(false);
    },
    onError: (error: any) => {
      const errorMessage = error.response?.data?.detail || error.message || 'Failed to generate infrastructure';
      addMessage('ai', `❌ Error: ${errorMessage}\n\nPlease try again or refine your prompt.`);
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
      <ScrollArea className="flex-1 p-6" ref={scrollRef}>
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
      </ScrollArea>
      
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
