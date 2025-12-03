/**
 * Global State Store
 * 
 * Zustand store for sharing infrastructure data between Chat and Visualizer panels
 */

import { create } from 'zustand';

interface ProjectState {
  selectedNodeId: string | null;
  setSelectedNode: (id: string | null) => void;
  // Loading state
  isLoading: boolean;
  
  // Infrastructure data
  terraformCode: string | null;
  ansiblePlaybook: string | null;
  costEstimate: string | null;
  securityRisks: string[];
  graphData: any;
  
  // Workflow tracking
  workflowStage: {
    current: string | null;
    [key: string]: string | null;
  } | null;
  workflowError: string | null;
  
  // Chat history
  messages: Array<{
    id: string;
    role: 'user' | 'ai';
    content: string;
    timestamp: Date;
  }>;
  
  // Actions
  setLoading: (loading: boolean) => void;
  setProjectData: (data: {
  terraformCode?: string;
  ansiblePlaybook?: string;
  costEstimate?: string;
  securityRisks?: string[];
  graphData?: any;
  }) => void;
  setWorkflowStage: (stage: string, status?: 'active' | 'complete' | 'error') => void;
  setWorkflowError: (error: string | null) => void;
  addMessage: (role: 'user' | 'ai', content: string) => void;
  clearProject: () => void;
}

export const useProjectStore = create<ProjectState>((set) => ({
  // Initial state
  isLoading: false,
  terraformCode: null,
  ansiblePlaybook: null,
  costEstimate: null,
  securityRisks: [],
  graphData: null,
  selectedNodeId: null,
  messages: [],
  workflowStage: null,
  workflowError: null,
  
  // Actions
  setLoading: (loading) => set({ isLoading: loading }),
  setSelectedNode: (id) => set({ selectedNodeId: id }),
  
  setProjectData: (data) => set((state) => ({
  terraformCode: data.terraformCode ?? state.terraformCode,
  ansiblePlaybook: data.ansiblePlaybook ?? state.ansiblePlaybook,
  costEstimate: data.costEstimate ?? state.costEstimate,
  securityRisks: data.securityRisks ?? state.securityRisks,
  graphData: data.graphData ?? state.graphData,
  })),
  
  setWorkflowStage: (stage, status = 'active') => set((state) => ({
    workflowStage: {
      ...state.workflowStage,
      current: status === 'active' ? stage : state.workflowStage?.current || null,
      [stage]: status,
    },
  })),
  
  setWorkflowError: (error) => set({ workflowError: error }),
  
  addMessage: (role, content) => set((state) => ({
    messages: [
      ...state.messages,
      {
        id: `${Date.now()}-${Math.random()}`,
        role,
        content,
        timestamp: new Date(),
      },
    ],
  })),
  
  clearProject: () => set({
    isLoading: false,
    terraformCode: null,
    ansiblePlaybook: null,
    costEstimate: null,
    securityRisks: [],
    messages: [],
    workflowStage: null,
    workflowError: null,
  }),
}));
