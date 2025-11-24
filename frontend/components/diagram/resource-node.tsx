/**
 * Resource Node Component
 * 
 * Custom ReactFlow node styled as a "Tech Card"
 */

"use client";

import { memo } from 'react';
import { Handle, Position, NodeProps } from '@xyflow/react';
import { 
  Server, 
  Database, 
  Shield, 
  Cloud, 
  Network,
  Globe,
  Route,
  Workflow,
  Scale,
  Container,
  Zap,
  Box,
  type LucideIcon
} from 'lucide-react';

interface ResourceNodeData {
  resourceType: string;
  resourceName: string;
  label: string;
}

const iconMap: Record<string, LucideIcon> = {
  Server,
  Database,
  Shield,
  Cloud,
  Network,
  Globe,
  Route,
  Workflow,
  Scale,
  Container,
  Zap,
  Box,
};

function getIconForResourceType(resourceType: string): LucideIcon {
  const mapping: Record<string, string> = {
    aws_instance: 'Server',
    aws_ec2_instance: 'Server',
    aws_s3_bucket: 'Database',
    aws_db_instance: 'Database',
    aws_rds_instance: 'Database',
    aws_security_group: 'Shield',
    aws_vpc: 'Cloud',
    aws_subnet: 'Network',
    aws_internet_gateway: 'Globe',
    aws_route_table: 'Route',
    aws_nat_gateway: 'Workflow',
    aws_lb: 'Scale',
    aws_ecs_cluster: 'Container',
    aws_ecs_service: 'Container',
    aws_lambda_function: 'Zap',
  };

  const iconName = mapping[resourceType] || 'Box';
  return iconMap[iconName];
}

function ResourceNodeComponent({ data }: NodeProps) {
  const nodeData = data as unknown as ResourceNodeData;
  const Icon = getIconForResourceType(nodeData.resourceType);

  return (
    <div className="relative">
      {/* Input Handle (top) */}
      <Handle
        type="target"
        position={Position.Top}
        className="!bg-violet-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />

      {/* Tech Card Container */}
      <div className="bg-zinc-900 border border-zinc-700 rounded-md min-w-[180px] shadow-xl">
        {/* Header */}
        <div className="flex items-center gap-2 px-3 py-2 border-b border-zinc-800 bg-zinc-900/50">
          <Icon className="w-4 h-4 text-violet-400" />
          <span className="text-xs font-mono text-zinc-400 truncate">
            {nodeData.resourceType}
          </span>
        </div>

        {/* Body */}
        <div className="px-3 py-3">
          <p className="text-sm font-semibold text-zinc-100 truncate">
            {nodeData.resourceName}
          </p>
        </div>
      </div>

      {/* Output Handle (bottom) */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="!bg-violet-500 !w-3 !h-3 !border-2 !border-zinc-900"
      />
    </div>
  );
}

export const ResourceNode = memo(ResourceNodeComponent);
