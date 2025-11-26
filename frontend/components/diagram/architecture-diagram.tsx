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
import { convertGraphDataToReactFlow } from '@/lib/graph-utils';
import GroupNode from './group-node';
import NodeInspector from './node-inspector';

// Register custom node types - Professional AWS Architecture Style (Dark Theme)
const nodeTypes = {
  resourceNode: ({ data }: any) => (
    <div 
      className="group relative rounded-2xl border-2 shadow-2xl transition-all duration-300 hover:scale-105 hover:shadow-3xl backdrop-blur-sm"
      style={{ 
        backgroundColor: data.bgColor || '#18181B',
        borderColor: data.borderColor || '#8b5cf6',
        minWidth: '180px',
        minHeight: '95px',
      }}
    >
      {/* Top accent line (glowing) */}
      <div 
        className="absolute top-0 left-0 right-0 h-1 rounded-t-2xl shadow-glow"
        style={{ 
          backgroundColor: data.color || '#8b5cf6',
          boxShadow: `0 0 10px ${data.color || '#8b5cf6'}80`
        }}
      />
      
      {/* Main content */}
      <div className="px-4 py-3 pt-4">
        <div className="flex items-center gap-3">
          {/* Icon with glow */}
          <div 
            className="flex items-center justify-center w-12 h-12 rounded-xl shadow-inner"
            style={{ 
              backgroundColor: data.color ? `${data.color}30` : '#8b5cf630',
              border: `1.5px solid ${data.color || '#8b5cf6'}60`,
              boxShadow: `0 0 15px ${data.color || '#8b5cf6'}40`
            }}
          >
            <span className="text-2xl">{data.icon || '📦'}</span>
          </div>
          
          {/* Text content */}
          <div className="flex-1 min-w-0">
            <div className="text-[10px] font-mono font-semibold uppercase tracking-wide truncate"
                 style={{ color: data.color || '#8b5cf6' }}>
              {data.resourceType.replace('aws_', '')}
            </div>
            <div className="text-sm font-bold text-zinc-100 truncate mt-0.5">
              {data.resourceName}
            </div>
          </div>
        </div>
        
        {/* Category badge with glow */}
        <div className="mt-2 inline-flex items-center px-2 py-0.5 rounded-full text-[9px] font-semibold uppercase tracking-wider"
             style={{ 
               backgroundColor: `${data.color || '#8b5cf6'}25`,
               color: data.color || '#8b5cf6',
               boxShadow: `0 0 10px ${data.color || '#8b5cf6'}30`
             }}>
          {data.category}
        </div>
      </div>
      
      {/* Hover glow effect (stronger) */}
      <div 
        className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none blur-2xl"
        style={{ 
          backgroundColor: data.color || '#8b5cf6',
          filter: 'blur(25px)',
          zIndex: -1
        }}
      />
    </div>
  ),
  groupNode: GroupNode,
};

export function ArchitectureDiagram() {
  const setSelectedNode = useProjectStore((state) => state.setSelectedNode);
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  
  // Get graphData from global store
  const graphData = useProjectStore((state) => state.graphData);
  const isLoading = useProjectStore((state) => state.isLoading);

  // Parse and layout graphData when it changes
  useEffect(() => {
    if (!graphData) {
      setNodes([]);
      setEdges([]);
      return;
    }

    console.log('[Architecture Diagram] Received graphData:', graphData);

    // Convert graphData to ReactFlow nodes/edges
    const { nodes: rfNodes, edges: rfEdges } = convertGraphDataToReactFlow(graphData);
    
    console.log('[Architecture Diagram] Converted to ReactFlow:', {
      nodes: rfNodes.length,
      edges: rfEdges.length,
      nodesSample: rfNodes.slice(0, 2)
    });
    
    setNodes(rfNodes);
    setEdges(rfEdges);
  }, [graphData, setNodes, setEdges]);

  const onInit = useCallback(() => {
    console.log('[ReactFlow] Initialized');
  }, []);

  return (
    <div className="w-full h-full relative">
  {/* Empty State */}
  {!graphData && !isLoading && (
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

      {/* ReactFlow Canvas - Professional Architecture Style */}
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
          minZoom: 0.3,
          maxZoom: 1.5,
          duration: 800,
        }}
        minZoom={0.1}
        maxZoom={2.5}
        defaultEdgeOptions={{
          type: 'smoothstep',
          animated: true,
          style: {
            strokeWidth: 3,
            stroke: '#64748B',
          },
          markerEnd: {
            type: 'arrowclosed',
            width: 20,
            height: 20,
          },
        }}
        className="bg-gradient-to-br from-zinc-900 via-zinc-900/95 to-violet-950/30"
        onNodeClick={(_, node) => {
          console.log('[Architecture Diagram] Node clicked:', node);
          setSelectedNode(node.id);
        }}
        proOptions={{ hideAttribution: true }}
      >
        {/* Professional Grid Background (matches dark theme) */}
        <Background
          color="#52525B"
          gap={32}
          size={1.5}
          className="opacity-20"
        />
        
        {/* Controls with dark theme styling */}
        <Controls
          className="!bg-zinc-800/90 !border-zinc-700 !shadow-2xl !backdrop-blur-sm rounded-xl [&_button]:!bg-zinc-800 [&_button]:!border-zinc-700 [&_button]:!text-violet-400 [&_button:hover]:!bg-violet-600/20"
          showInteractive={false}
        />
        
        {/* MiniMap with dark theme */}
        <MiniMap
          className="!bg-zinc-800/90 !border-zinc-700 !shadow-2xl !backdrop-blur-sm rounded-xl"
          nodeColor={(node: any) => node.data?.color || '#8b5cf6'}
          maskColor="rgba(24, 24, 27, 0.8)"
          position="bottom-left"
          pannable
          zoomable
        />
      </ReactFlow>
      <NodeInspector />
    </div>
  );
}
