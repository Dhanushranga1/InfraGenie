"use client";

import { Navbar } from '@/components/navbar';
import { ChatInterface } from '@/components/chat/chat-interface';
import { ArchitectureDiagram } from '@/components/diagram/architecture-diagram';
import { StatusBadges } from '@/components/dashboard/status-badges';
import { DownloadButton } from '@/components/dashboard/download-button';

export default function HomePage() {
  return (
    <div className="h-screen w-full overflow-hidden flex flex-col">
      {/* Navigation Bar */}
      <Navbar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-row overflow-hidden">
        {/* Left Panel - Chat Interface */}
        <div className="w-[350px] min-w-[350px] border-r border-zinc-800 bg-zinc-900/50 backdrop-blur-xl flex flex-col">
          <div className="p-6 border-b border-zinc-800">
            <h2 className="text-lg font-bold text-violet-400 font-mono tracking-tight">
              Chat Interface
            </h2>
            <p className="text-xs text-zinc-500 mt-1">
              Describe your infrastructure needs
            </p>
          </div>
          
          {/* Chat Component */}
          <div className="flex-1 overflow-hidden">
            <ChatInterface />
          </div>

          {/* Download Button */}
          <DownloadButton />
        </div>

        {/* Right Panel - Architecture Diagram */}
        <div className="flex-1 bg-zinc-950 relative overflow-hidden">
          {/* Cyberpunk glow effects */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-violet-500/10 rounded-full blur-3xl pointer-events-none z-0" />
          <div className="absolute bottom-0 left-0 w-96 h-96 bg-cyan-500/10 rounded-full blur-3xl pointer-events-none z-0" />
          
          {/* Status Badges (floating over diagram) */}
          <StatusBadges />

          {/* Architecture Diagram Canvas */}
          <div className="relative z-10 h-[calc(100%-2.5rem)]">
            <ArchitectureDiagram />
          </div>

          {/* Status bar at bottom */}
          <div className="absolute bottom-0 left-0 right-0 h-10 border-t border-zinc-800 bg-zinc-900/80 backdrop-blur-xl flex items-center justify-between px-6">
            <div className="flex items-center gap-4">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                <span className="text-xs text-zinc-400">Backend Connected</span>
              </div>
              <div className="text-xs text-zinc-500">
                Model: llama-3.3-70b-versatile (Groq Cloud)
              </div>
            </div>
            <div className="text-xs text-zinc-500 font-mono">
              v Phase 2 Complete
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
