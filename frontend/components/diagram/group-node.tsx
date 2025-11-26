import React, { memo } from "react";
import { Handle, Position } from "@xyflow/react";

interface GroupNodeData {
  label: string;
  resourceType?: string;
}

interface GroupNodeProps {
  data: GroupNodeData;
  selected?: boolean;
}

const GroupNode = ({ data, selected }: GroupNodeProps) => {
  return (
    <div
      className={`
        relative h-full w-full rounded-xl border-2 border-dashed transition-colors duration-200
        ${selected 
          ? "border-violet-500 bg-violet-500/5" 
          : "border-zinc-700 bg-zinc-900/10"
        }
      `}
    >
      {/* Label Badge */}
      <div className="absolute -top-3 left-4 rounded bg-zinc-950 px-2 py-0.5 border border-zinc-800 shadow-sm">
        <span className="text-[10px] font-mono font-bold text-zinc-500 uppercase tracking-wider">
          {data.label}
        </span>
      </div>

      {/* Hidden Handles (Required for ReactFlow to avoid warnings, even if not connecting directly to the group) */}
      <Handle type="target" position={Position.Top} className="opacity-0" />
      <Handle type="source" position={Position.Bottom} className="opacity-0" />
    </div>
  );
};

export default memo(GroupNode);