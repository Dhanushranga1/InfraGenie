/**
 * Architecture Diagram Component
 * 
 * ReactFlow canvas for visualizing infrastructure as a graph
 */

"use client";

import { useEffect, useCallback } from 'react';
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  ConnectionMode,
  Node,
  Edge,
} from '@xyflow/react';
import '@xyflow/react/dist/style.css';

import { useProjectStore } from '@/lib/store';
import { parseTerraformToElements, getLayoutedElements } from '@/lib/graph-utils';
import { ResourceNode } from './resource-node';

// Register custom node types
const nodeTypes = {
  resourceNode: ResourceNode,
};

export function ArchitectureDiagram() {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  
  // Get Terraform code from global store
  const terraformCode = useProjectStore((state) => state.terraformCode);
  const isLoading = useProjectStore((state) => state.isLoading);

  // Parse and layout Terraform code when it changes
  useEffect(() => {
    if (!terraformCode) {
      setNodes([]);
      setEdges([]);
      return;
    }

    // Parse Terraform to nodes and edges
    const { nodes: parsedNodes, edges: parsedEdges } = parseTerraformToElements(terraformCode);
    
    // Apply auto-layout
    const { nodes: layoutedNodes, edges: layoutedEdges } = getLayoutedElements(
      parsedNodes,
      parsedEdges,
      'TB' // Top to Bottom
    );

    setNodes(layoutedNodes);
    setEdges(layoutedEdges);
  }, [terraformCode, setNodes, setEdges]);

  const onInit = useCallback(() => {
    console.log('[ReactFlow] Initialized');
  }, []);

  return (
    <div className="w-full h-full relative">
      {/* Empty State */}
      {!terraformCode && !isLoading && (
        <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-zinc-900/50 border border-zinc-800 backdrop-blur-xl glow-violet">
              <svg className="w-12 h-12 text-violet-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            
            <h2 className="text-3xl font-bold text-zinc-100 font-mono">
              Infrastructure Visualization Canvas
            </h2>
            <p className="text-zinc-400 max-w-md">
              Generate infrastructure code and visualize your architecture in real-time
            </p>
          </div>
        </div>
      )}

      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center z-10 pointer-events-none">
          <div className="text-center space-y-4">
            <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-zinc-900/50 border border-zinc-800 backdrop-blur-xl">
              <div className="w-12 h-12 border-4 border-violet-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
            <p className="text-violet-400 font-mono">
              Generating architecture diagram...
            </p>
          </div>
        </div>
      )}

      {/* ReactFlow Canvas */}
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onInit={onInit}
        nodeTypes={nodeTypes}
        connectionMode={ConnectionMode.Loose}
        fitView
        fitViewOptions={{
          padding: 0.2,
          minZoom: 0.5,
          maxZoom: 1.5,
        }}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
        }}
        className="bg-zinc-950"
      >
        {/* Background with dot pattern */}
        <Background
          color="#27272a"
          gap={24}
          size={1}
          className="bg-zinc-950"
        />
        
        {/* Controls (Zoom, Fit View) */}
        <Controls
          className="!bg-zinc-900 !border-zinc-800"
          showInteractive={false}
        />
        
        {/* MiniMap */}
        <MiniMap
          className="!bg-zinc-900 !border-zinc-800"
          nodeColor="#8b5cf6"
          maskColor="rgba(24, 24, 27, 0.8)"
          position="bottom-left"
        />
      </ReactFlow>
    </div>
  );
}
