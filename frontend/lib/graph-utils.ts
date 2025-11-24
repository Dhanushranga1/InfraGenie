/**
 * Graph Utilities
 * 
 * Parse Terraform HCL code and convert to ReactFlow nodes/edges
 * Auto-layout using dagre
 */

import dagre from 'dagre';
import { Node, Edge, Position } from '@xyflow/react';

export interface ResourceNode extends Node {
  data: {
    resourceType: string;
    resourceName: string;
    label: string;
  };
}

/**
 * Parse Terraform HCL code to extract resources and relationships
 */
export function parseTerraformToElements(hcl: string | null): {
  nodes: ResourceNode[];
  edges: Edge[];
} {
  if (!hcl || !hcl.trim()) {
    return { nodes: [], edges: [] };
  }

  const nodes: ResourceNode[] = [];
  const edges: Edge[] = [];
  const resourceMap = new Map<string, string>(); // full_name -> id

  try {
    // Regex to match resource blocks: resource "type" "name" { ... }
    const resourceRegex = /resource\s+"([^"]+)"\s+"([^"]+)"\s*\{/g;
    let match;

    let nodeId = 0;
    while ((match = resourceRegex.exec(hcl)) !== null) {
      const resourceType = match[1]; // e.g., "aws_instance"
      const resourceName = match[2]; // e.g., "web_server"
      const fullName = `${resourceType}.${resourceName}`;
      const id = `node-${nodeId++}`;

      resourceMap.set(fullName, id);

      nodes.push({
        id,
        type: 'resourceNode',
        position: { x: 0, y: 0 }, // Will be set by dagre
        data: {
          resourceType,
          resourceName,
          label: resourceName,
        },
      });
    }

    // If no resources found, return empty
    if (nodes.length === 0) {
      console.warn('[Graph] No resources found in Terraform code');
      return { nodes: [], edges: [] };
    }

    // Find references between resources
    // Look for patterns like: vpc_id = aws_vpc.main.id
    // Parse each resource block to find dependencies
    const resourceBlocks: Array<{ type: string; name: string; content: string }> = [];
    
    // Extract resource blocks with their content
    const lines = hcl.split('\n');
    let currentBlock: { type: string; name: string; content: string } | null = null;
    let braceCount = 0;
    let blockContent: string[] = [];
    
    for (const line of lines) {
      const resourceMatch = /resource\s+"([^"]+)"\s+"([^"]+)"\s*\{/.exec(line);
      
      if (resourceMatch && braceCount === 0) {
        currentBlock = {
          type: resourceMatch[1],
          name: resourceMatch[2],
          content: '',
        };
        braceCount = 1;
        blockContent = [];
        continue;
      }
      
      if (currentBlock) {
        braceCount += (line.match(/\{/g) || []).length;
        braceCount -= (line.match(/\}/g) || []).length;
        
        if (braceCount > 0) {
          blockContent.push(line);
        } else if (braceCount === 0) {
          currentBlock.content = blockContent.join('\n');
          resourceBlocks.push(currentBlock);
          currentBlock = null;
          blockContent = [];
        }
      }
    }
    
    // Find references in each block
    for (const block of resourceBlocks) {
      const sourceFullName = `${block.type}.${block.name}`;
      const sourceId = resourceMap.get(sourceFullName);
      
      if (!sourceId) continue;
      
      // Find all AWS resource references in this block
      const referenceRegex = /(aws_[a-z_]+)\.([\w-]+)/g;
      let refMatch;
      
      while ((refMatch = referenceRegex.exec(block.content)) !== null) {
        const targetType = refMatch[1];
        const targetName = refMatch[2];
        const targetFullName = `${targetType}.${targetName}`;
        const targetId = resourceMap.get(targetFullName);
        
        if (targetId && targetId !== sourceId) {
          // Create edge from target to source (dependency direction)
          const edgeId = `edge-${targetId}-${sourceId}`;
          
          // Avoid duplicate edges
          if (!edges.find(e => e.id === edgeId)) {
            edges.push({
              id: edgeId,
              source: targetId,
              target: sourceId,
              type: 'smoothstep',
              animated: true,
              style: {
                stroke: '#8b5cf6', // violet-500
                strokeWidth: 2,
              },
            });
          }
        }
      }
    }

    console.log(`[Graph] Parsed ${nodes.length} nodes and ${edges.length} edges`);
    return { nodes, edges };
    
  } catch (error) {
    console.error('[Graph] Error parsing Terraform code:', error);
    return { nodes: [], edges: [] };
  }
}

/**
 * Auto-layout nodes using dagre
 */
export function getLayoutedElements(
  nodes: ResourceNode[],
  edges: Edge[],
  direction: 'TB' | 'LR' = 'TB'
): { nodes: ResourceNode[]; edges: Edge[] } {
  if (!nodes || nodes.length === 0) {
    return { nodes: [], edges: [] };
  }

  try {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));

    const nodeWidth = 200;
    const nodeHeight = 100;

    // Configure graph layout with better spacing
    dagreGraph.setGraph({
      rankdir: direction,
      ranksep: 120, // Vertical spacing between ranks (increased)
      nodesep: 100,  // Horizontal spacing between nodes (increased)
      edgesep: 60,  // Edge spacing (increased)
      marginx: 50,  // Horizontal margin
      marginy: 50,  // Vertical margin
    });

    // Add nodes to dagre
    nodes.forEach((node) => {
      dagreGraph.setNode(node.id, { width: nodeWidth, height: nodeHeight });
    });

    // Add edges to dagre
    edges.forEach((edge) => {
      dagreGraph.setEdge(edge.source, edge.target);
    });

    // Calculate layout
    dagre.layout(dagreGraph);

    // Apply calculated positions to nodes
    const layoutedNodes: ResourceNode[] = nodes.map((node) => {
      const nodeWithPosition = dagreGraph.node(node.id);
      
      return {
        ...node,
        position: {
          x: nodeWithPosition.x - nodeWidth / 2,
          y: nodeWithPosition.y - nodeHeight / 2,
        },
        sourcePosition: direction === 'TB' ? Position.Bottom : Position.Right,
        targetPosition: direction === 'TB' ? Position.Top : Position.Left,
      };
    });

    console.log('[Graph] Layout calculated successfully');
    return { nodes: layoutedNodes, edges };
    
  } catch (error) {
    console.error('[Graph] Error layouting elements:', error);
    // Return nodes with fallback positions
    return {
      nodes: nodes.map((node, index) => ({
        ...node,
        position: { x: 100 + (index % 3) * 250, y: 100 + Math.floor(index / 3) * 150 },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      })),
      edges,
    };
  }
}

/**
 * Helper to get icon name for resource type
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
    aws_ecs_cluster: 'Container',
    aws_ecs_service: 'Container',
    aws_lambda_function: 'Zap',
  };

  return iconMap[resourceType] || 'Box';
}
