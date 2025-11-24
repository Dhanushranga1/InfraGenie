/**
 * Terminal Loader Component
 * 
 * Animated terminal-style loading indicator with cycling messages
 */

"use client";

import { useEffect, useState } from 'react';
import { Bot } from 'lucide-react';

const LOADING_MESSAGES = [
  '> Architecting solution...',
  '> Validating Terraform syntax...',
  '> Scanning security policies...',
  '> Estimating cloud costs...',
];

export function TerminalLoader() {
  const [messageIndex, setMessageIndex] = useState(0);
  
  useEffect(() => {
    const interval = setInterval(() => {
      setMessageIndex((prev) => (prev + 1) % LOADING_MESSAGES.length);
    }, 2000);
    
    return () => clearInterval(interval);
  }, []);
  
  return (
    <div className="flex gap-3 mb-4">
      {/* AI Icon */}
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center">
        <Bot className="w-4 h-4 text-violet-400 animate-pulse" />
      </div>
      
      {/* Terminal Message */}
      <div className="px-4 py-3 rounded-2xl rounded-tl-none bg-zinc-900 border border-zinc-800 max-w-[85%]">
        <p className="font-mono text-sm text-violet-400 animate-pulse">
          {LOADING_MESSAGES[messageIndex]}
        </p>
      </div>
    </div>
  );
}
