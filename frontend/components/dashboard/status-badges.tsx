/**
 * Status Badges Component
 * 
 * Floating badges showing cost estimate and security status
 */

"use client";

import { DollarSign, ShieldCheck, ShieldAlert } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useProjectStore } from '@/lib/store';
import { cn } from '@/lib/utils';

export function StatusBadges() {
  const costEstimate = useProjectStore((state) => state.costEstimate);
  const securityRisks = useProjectStore((state) => state.securityRisks);

  // Don't show badges if no data
  if (!costEstimate && securityRisks.length === 0) {
    return null;
  }

  // Parse cost to determine color
  const getCostColor = (cost: string | null) => {
    if (!cost) return 'emerald';
    
    // Extract number from string like "$24.50" or "$24.50/month"
    const match = cost.match(/\$?([\d.]+)/);
    if (!match) return 'emerald';
    
    const value = parseFloat(match[1]);
    return value > 50 ? 'amber' : 'emerald';
  };

  const costColor = getCostColor(costEstimate);
  const isSecure = securityRisks.length === 0;

  return (
    <div className="absolute top-4 right-4 z-10 flex gap-2">
      {/* Cost Badge */}
      {costEstimate && (
        <div
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg backdrop-blur-xl border shadow-lg',
            costColor === 'amber'
              ? 'bg-amber-500/10 border-amber-500/20 text-amber-500'
              : 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
          )}
        >
          <DollarSign className="w-4 h-4" />
          <div className="flex flex-col">
            <span className="text-xs font-medium opacity-70">Est. Cost</span>
            <span className="text-sm font-bold font-mono">{costEstimate}</span>
          </div>
        </div>
      )}

      {/* Security Badge */}
      {(costEstimate || securityRisks.length > 0) && (
        <div
          className={cn(
            'flex items-center gap-2 px-3 py-2 rounded-lg backdrop-blur-xl border shadow-lg',
            isSecure
              ? 'bg-emerald-500/10 border-emerald-500/20 text-emerald-500'
              : 'bg-rose-500/10 border-rose-500/20 text-rose-500'
          )}
        >
          {isSecure ? (
            <ShieldCheck className="w-4 h-4" />
          ) : (
            <ShieldAlert className="w-4 h-4" />
          )}
          <div className="flex flex-col">
            <span className="text-xs font-medium opacity-70">Security</span>
            <span className="text-sm font-bold">
              {isSecure ? 'Secure' : `${securityRisks.length} Risk${securityRisks.length > 1 ? 's' : ''}`}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
