/**
 * Navbar Component
 * 
 * Top navigation bar with logo and user button
 */

"use client";

import { UserButton } from '@clerk/nextjs';
import { Zap } from 'lucide-react';

export function Navbar() {
  return (
    <nav className="h-16 border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-xl flex items-center justify-between px-6">
      {/* Logo */}
      <div className="flex items-center gap-3">
        {/* <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-500 to-indigo-500 flex items-center justify-center">
          <Zap className="w-5 h-5 text-white" />
        </div> */}
        <span className="font-mono font-bold text-xl text-violet-500">
          InfraGenie
        </span>
      </div>

      {/* User Button */}
      <UserButton
        appearance={{
          elements: {
            avatarBox: "w-10 h-10",
            userButtonPopoverCard: "bg-zinc-900 border border-zinc-800",
            userButtonPopoverActionButton: "hover:bg-zinc-800",
          },
        }}
      />
    </nav>
  );
}
