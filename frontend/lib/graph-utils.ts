/**
 * Graph Utilities - Professional Architecture Diagram System
 * Converts Backend Graph JSON to ReactFlow with enterprise-grade visualization
 * Inspired by eraser.io, AWS Architecture Icons, and Lucidchart
 */

import { Node, Edge, Position } from '@xyflow/react';

// Professional Resource Type Configurations (AWS Architecture Style)
const RESOURCE_CONFIGS: Record<string, { 
  color: string; 
  bgColor: string;
  borderColor: string;
  icon: string; 
  category: 'compute' | 'network' | 'storage' | 'database' | 'security' | 'serverless' | 'container';
  width: number; 
  height: number;
}> = {
  // Compute Resources
  aws_instance: { 
    color: '#FF9900', 
    bgColor: '#FFF4E6',
    borderColor: '#FF9900',
    icon: '💻', 
    category: 'compute',
    width: 180, 
    height: 95 
  },
  aws_ec2_instance: { 
    color: '#FF9900', 
    bgColor: '#FFF4E6',
    borderColor: '#FF9900',
    icon: '🖥️', 
    category: 'compute',
    width: 180, 
    height: 95 
  },
  
  // Network Resources
  aws_vpc: { 
    color: '#7C3AED', 
    bgColor: '#F5F3FF',
    borderColor: '#7C3AED',
    icon: '🏢', 
    category: 'network',
    width: 220, 
    height: 110 
  },
  aws_subnet: { 
    color: '#3B82F6', 
    bgColor: '#EFF6FF',
    borderColor: '#3B82F6',
    icon: '🌐', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  aws_internet_gateway: { 
    color: '#06B6D4', 
    bgColor: '#ECFEFF',
    borderColor: '#06B6D4',
    icon: '🌍', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  aws_nat_gateway: { 
    color: '#0EA5E9', 
    bgColor: '#F0F9FF',
    borderColor: '#0EA5E9',
    icon: '🔄', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  aws_route_table: { 
    color: '#0284C7', 
    bgColor: '#E0F2FE',
    borderColor: '#0284C7',
    icon: '�️', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  
  // Load Balancing
  aws_lb: { 
    color: '#8B5CF6', 
    bgColor: '#F5F3FF',
    borderColor: '#8B5CF6',
    icon: '⚖️', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  aws_alb: { 
    color: '#7C3AED', 
    bgColor: '#F5F3FF',
    borderColor: '#7C3AED',
    icon: '�', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  aws_elb: { 
    color: '#6D28D9', 
    bgColor: '#FAF5FF',
    borderColor: '#6D28D9',
    icon: '⚖️', 
    category: 'network',
    width: 180, 
    height: 95 
  },
  
  // Security Resources
  aws_security_group: { 
    color: '#F59E0B', 
    bgColor: '#FFFBEB',
    borderColor: '#F59E0B',
    icon: '🛡️', 
    category: 'security',
    width: 180, 
    height: 95 
  },
  aws_iam_role: { 
    color: '#A855F7', 
    bgColor: '#FAF5FF',
    borderColor: '#A855F7',
    icon: '👤', 
    category: 'security',
    width: 180, 
    height: 95 
  },
  aws_iam_policy: { 
    color: '#9333EA', 
    bgColor: '#FAF5FF',
    borderColor: '#9333EA',
    icon: '📋', 
    category: 'security',
    width: 180, 
    height: 95 
  },
  aws_iam_instance_profile: { 
    color: '#7C3AED', 
    bgColor: '#F5F3FF',
    borderColor: '#7C3AED',
    icon: '🎫', 
    category: 'security',
    width: 180, 
    height: 95 
  },
  
  // Storage Resources
  aws_s3_bucket: { 
    color: '#10B981', 
    bgColor: '#ECFDF5',
    borderColor: '#10B981',
    icon: '🪣', 
    category: 'storage',
    width: 180, 
    height: 95 
  },
  aws_ebs_volume: { 
    color: '#059669', 
    bgColor: '#D1FAE5',
    borderColor: '#059669',
    icon: '💾', 
    category: 'storage',
    width: 180, 
    height: 95 
  },
  
  // Database Resources
  aws_db_instance: { 
    color: '#EC4899', 
    bgColor: '#FDF2F8',
    borderColor: '#EC4899',
    icon: '🗄️', 
    category: 'database',
    width: 180, 
    height: 95 
  },
  aws_rds_cluster: { 
    color: '#DB2777', 
    bgColor: '#FCE7F3',
    borderColor: '#DB2777',
    icon: '🗃️', 
    category: 'database',
    width: 180, 
    height: 95 
  },
  aws_dynamodb_table: { 
    color: '#BE185D', 
    bgColor: '#FDF2F8',
    borderColor: '#BE185D',
    icon: '📊', 
    category: 'database',
    width: 180, 
    height: 95 
  },
  
  // Serverless
  aws_lambda_function: { 
    color: '#EF4444', 
    bgColor: '#FEF2F2',
    borderColor: '#EF4444',
    icon: '⚡', 
    category: 'serverless',
    width: 180, 
    height: 95 
  },
  
  // Containers
  aws_ecs_cluster: { 
    color: '#F97316', 
    bgColor: '#FFF7ED',
    borderColor: '#F97316',
    icon: '📦', 
    category: 'container',
    width: 180, 
    height: 95 
  },
  aws_ecs_service: { 
    color: '#EA580C', 
    bgColor: '#FFEDD5',
    borderColor: '#EA580C',
    icon: '🐳', 
    category: 'container',
    width: 180, 
    height: 95 
  },
  
  // Default fallback
  default: { 
    color: '#6B7280', 
    bgColor: '#F9FAFB',
    borderColor: '#6B7280',
    icon: '📦', 
    category: 'compute',
    width: 180, 
    height: 95 
  },
};

function getResourceConfig(type: string) {
  return RESOURCE_CONFIGS[type] || RESOURCE_CONFIGS.default;
}

// Category-based swim lanes for professional layout
const CATEGORY_LANES: Record<string, { offset: number; label: string; color: string }> = {
  network: { offset: 0, label: 'Network Layer', color: '#7C3AED' },
  security: { offset: 300, label: 'Security Layer', color: '#F59E0B' },
  compute: { offset: 600, label: 'Compute Layer', color: '#FF9900' },
  storage: { offset: 900, label: 'Storage Layer', color: '#10B981' },
  database: { offset: 1200, label: 'Database Layer', color: '#EC4899' },
  serverless: { offset: 1500, label: 'Serverless Layer', color: '#EF4444' },
  container: { offset: 1800, label: 'Container Layer', color: '#F97316' },
};

export interface ResourceNode extends Node {
  data: {
    resourceType: string;
    resourceName: string;
    label: string;
    icon: string;
    color: string;
    bgColor: string;
    borderColor: string;
    category: string;
  };
}

/**
 * Convert backend graph_data JSON to ReactFlow nodes/edges with auto-layout
 */
export function convertGraphDataToReactFlow(graphData: any): { nodes: Node[]; edges: Edge[] } {
  if (!graphData || !Array.isArray(graphData.nodes)) {
    return { nodes: [], edges: [] };
  }

  // Filter out IAM resources, SSH keys, and helper resources - they clutter the diagram
  // Users care about INFRASTRUCTURE (EC2, VPC, RDS, S3), not internal implementation details
  const HIDDEN_RESOURCE_TYPES = [
    // IAM Resources (access control - not visible infrastructure)
    'aws_iam_role',
    'aws_iam_instance_profile', 
    'aws_iam_policy',
    'aws_iam_role_policy',
    'aws_iam_role_policy_attachment',
    'aws_iam_policy_attachment',
    
    // SSH Key Resources (automatically handled - not infrastructure)
    'tls_private_key',           // Generates SSH key pair
    'aws_key_pair',              // Registers public key with AWS
    'local_file',                // Saves private key to disk
    
    // Helper Resources (internal glue code)
    'random_password',           // Password generators
    'random_string',             // Random value generators
    'random_id',                 // ID generators
    'null_resource',             // Terraform provisioners
    
    // Monitoring/Logging (shown via attributes, not separate nodes)
    'aws_cloudwatch_log_group',  // Logs shown in EC2/Lambda cards
    'aws_cloudwatch_metric_alarm' // Alarms shown inline
  ];

  // Filter nodes - keep only visible infrastructure resources
  const visibleNodes = graphData.nodes.filter((node: any) => 
    !HIDDEN_RESOURCE_TYPES.includes(node.type)
  );

  // Get set of visible node IDs for edge filtering
  const visibleNodeIds = new Set(visibleNodes.map((n: any) => n.id));

  // Filter edges - only keep edges between visible nodes
  const visibleEdges = Array.isArray(graphData.edges) 
    ? graphData.edges.filter((edge: any) => 
        visibleNodeIds.has(edge.source) && visibleNodeIds.has(edge.target)
      )
    : [];

  const nodes: Node[] = [];
  const edges: Edge[] = [];

  // Build dependency map for hierarchical layout
  const dependencyMap = new Map<string, string[]>();
  const reverseDependencyMap = new Map<string, string[]>();
  
  visibleNodes.forEach((n: any) => {
    dependencyMap.set(n.id, []);
    reverseDependencyMap.set(n.id, []);
  });

  // Build dependency relationships from visible edges
  visibleEdges.forEach((e: any) => {
    const deps = dependencyMap.get(e.target) || [];
    deps.push(e.source);
    dependencyMap.set(e.target, deps);
    
    const revDeps = reverseDependencyMap.get(e.source) || [];
    revDeps.push(e.target);
    reverseDependencyMap.set(e.source, revDeps);
  });

  // Calculate levels for hierarchical layout (topological sort)
  const levels = new Map<string, number>();
  const visited = new Set<string>();
  
  function calculateLevel(nodeId: string): number {
    if (levels.has(nodeId)) return levels.get(nodeId)!;
    if (visited.has(nodeId)) return 0; // Cycle detection
    
    visited.add(nodeId);
    const dependencies = dependencyMap.get(nodeId) || [];
    
    if (dependencies.length === 0) {
      levels.set(nodeId, 0);
      return 0;
    }
    
    const maxParentLevel = Math.max(...dependencies.map(dep => calculateLevel(dep)));
    const level = maxParentLevel + 1;
    levels.set(nodeId, level);
    return level;
  }

  // Calculate levels for all nodes
  visibleNodes.forEach((n: any) => {
    calculateLevel(n.id);
  });

  // Group nodes by level
  const nodesByLevel = new Map<number, any[]>();
  visibleNodes.forEach((n: any) => {
    const level = levels.get(n.id) || 0;
    if (!nodesByLevel.has(level)) {
      nodesByLevel.set(level, []);
    }
    nodesByLevel.get(level)!.push(n);
  });

  // Layout nodes in a professional hierarchical grid with swim lanes
  const levelSpacing = 280; // Vertical spacing between levels (more generous)
  const nodeSpacing = 240; // Horizontal spacing between nodes (more generous)
  const startX = 100;
  const startY = 80;

  // Group nodes by category for swim lane layout
  const nodesByCategory = new Map<string, any[]>();
  visibleNodes.forEach((n: any) => {
    const config = getResourceConfig(n.type);
    if (!nodesByCategory.has(config.category)) {
      nodesByCategory.set(config.category, []);
    }
    nodesByCategory.get(config.category)!.push(n);
  });

  // Create VPC/Subnet parent nodes (visual containers)
  const parentContainers = new Map<string, any>();
  const vpcs = visibleNodes.filter((n: any) => n.type === 'aws_vpc');
  const subnets = visibleNodes.filter((n: any) => n.type === 'aws_subnet');
  
  // Create VPC container nodes
  vpcs.forEach((vpc: any) => {
    const children = visibleNodes.filter((n: any) => n.parent === vpc.id);
    if (children.length > 0) {
      parentContainers.set(vpc.id, {
        type: 'vpc',
        children: children,
        node: vpc
      });
    }
  });
  
  // Create Subnet container nodes
  subnets.forEach((subnet: any) => {
    const children = visibleNodes.filter((n: any) => n.parent === subnet.id);
    if (children.length > 0) {
      parentContainers.set(subnet.id, {
        type: 'subnet',
        children: children,
        node: subnet
      });
    }
  });

  visibleNodes.forEach((n: any) => {
    const level = levels.get(n.id) || 0;
    const nodesAtLevel = nodesByLevel.get(level) || [];
    const indexInLevel = nodesAtLevel.indexOf(n);
    const config = getResourceConfig(n.type);
    
    // Check if this node is a VPC or Subnet (render as group)
    const isContainer = n.type === 'aws_vpc' || n.type === 'aws_subnet';
    const hasChildren = parentContainers.has(n.id);
    
    // Use swim lane layout for better organization
    const categoryLane = CATEGORY_LANES[config.category] || { offset: 0 };
    const categoryNodes = nodesByCategory.get(config.category) || [];
    const categoryIndex = categoryNodes.indexOf(n);
    
    // Calculate position with swim lanes
    const offsetX = startX + (categoryIndex * nodeSpacing) + (indexInLevel * 50);
    const offsetY = startY + (level * levelSpacing) + categoryLane.offset;

    // Render containers (VPC/Subnet) differently
    if (isContainer && hasChildren) {
      const container = parentContainers.get(n.id)!;
      nodes.push({
        id: n.id,
        type: 'groupNode',
        data: {
          label: n.label,
          resourceType: n.type,
          resourceName: n.label,
          icon: config.icon,
          color: config.color,
          bgColor: config.bgColor,
          borderColor: config.borderColor,
          category: config.category,
          isContainer: true,
          containerType: container.type,
        },
        position: { x: offsetX, y: offsetY },
        style: {
          width: 500,
          height: 400,
          backgroundColor: n.type === 'aws_vpc' ? 'rgba(123, 58, 237, 0.05)' : 'rgba(59, 130, 246, 0.05)',
          border: `2px dashed ${config.color}`,
          borderRadius: '16px',
          padding: '20px',
        },
      });
    } else {
      // Regular resource nodes
      nodes.push({
        id: n.id,
        type: 'resourceNode',
        data: {
          label: n.label,
          resourceType: n.type,
          resourceName: n.label,
          icon: config.icon,
          color: config.color,
          bgColor: config.bgColor,
          borderColor: config.borderColor,
          category: config.category,
        },
        position: { x: offsetX, y: offsetY },
        ...(n.parent && { 
          parentId: n.parent,
          extent: 'parent' as const 
        }),
        style: {
          width: config.width,
          height: config.height,
        },
      });
    }
  });

  // Create edges with professional styling (AWS Architecture style)
  visibleEdges.forEach((e: any, idx: number) => {
    // Determine edge style based on relationship type
    const sourceNode = visibleNodes.find((n: any) => n.id === e.source);
    const targetNode = visibleNodes.find((n: any) => n.id === e.target);
    
    // Default professional edge style - more visible
    let edgeStyle = {
      stroke: '#64748B',  // Darker slate for better visibility
      strokeWidth: 3,     // Thicker line
    };
    
    // Color-code edges based on relationship
    if (sourceNode && targetNode) {
        const sourceConfig = getResourceConfig(sourceNode.type);
        const targetConfig = getResourceConfig(targetNode.type);
        
        // Network connections - blue
        if (sourceConfig.category === 'network' || targetConfig.category === 'network') {
          edgeStyle.stroke = '#3B82F6';
          edgeStyle.strokeWidth = 3.5;
        }
        // Security connections - orange
        else if (sourceConfig.category === 'security' || targetConfig.category === 'security') {
          edgeStyle.stroke = '#F59E0B';
          edgeStyle.strokeWidth = 3.5;
        }
        // Data flow - green
        else if (sourceConfig.category === 'database' || targetConfig.category === 'storage') {
          edgeStyle.stroke = '#10B981';
          edgeStyle.strokeWidth = 3.5;
        }
        // Compute - purple
        else if (sourceConfig.category === 'compute') {
          edgeStyle.stroke = '#8B5CF6';
          edgeStyle.strokeWidth = 3.5;
        }
      }

      edges.push({
        id: e.id || `edge_${idx}`,
        source: e.source,
        target: e.target,
        type: 'smoothstep',
        animated: true,
        label: e.label || '',
        style: edgeStyle,
        markerEnd: {
          type: 'arrowclosed',
          width: 24,
          height: 24,
          color: edgeStyle.stroke,
        },
        labelStyle: {
          fill: '#1E293B',
          fontSize: 12,
          fontWeight: 600,
        },
        labelBgStyle: {
          fill: '#FFFFFF',
          fillOpacity: 0.95,
          rx: 4,
          ry: 4,
        },
        labelBgPadding: [8, 4],
        labelBgBorderRadius: 4,
      });
  });

  console.log(`[Graph Utils] ✓ Converted ${nodes.length} nodes, ${edges.length} edges in ${nodesByCategory.size} categories`);
  return { nodes, edges };
}

/**
 * Helper to get icon name for resource type
 * Used by the ResourceNode component to render the correct Lucide icon
 */
export function getResourceIcon(resourceType: string): string {
  const iconMap: Record<string, string> = {
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
    aws_elb: 'Scale',
    aws_alb: 'Scale',
    aws_ecs_cluster: 'Container',
    aws_ecs_service: 'Container',
    aws_lambda_function: 'Zap',
    aws_iam_role: 'Shield',
    aws_iam_policy: 'Shield',
  };

  // Fallback for unknown resources
  return iconMap[resourceType] || 'Box';
}