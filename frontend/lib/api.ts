/**
 * API Client Configuration
 * 
 * Centralized Axios instance for all backend API calls
 */

import axios from 'axios';

// Get API base URL from environment variable, fallback to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1';

// Create Axios instance with base configuration
export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 600000, // 10 minutes for LLM operations with retries (terraform init can be slow)
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for logging
api.interceptors.request.use(
  (config) => {
    console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('[API Request Error]', error);
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => {
    console.log(`[API Response] ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('[API Response Error]', {
      url: error.config?.url,
      status: error.response?.status,
      message: error.response?.data?.detail || error.message,
    });
    return Promise.reject(error);
  }
);

// API Types
export interface GenerateRequest {
  prompt: string;
}

export interface GenerateResponse {
  success: boolean;
  terraform_code: string;
  ansible_playbook: string;
  cost_estimate: string;
  validation_error: string | null;
  security_errors: string[];
  retry_count: number;
  is_clean: boolean;
  user_prompt: string;
  graph_data: {
    nodes: Array<{
      id: string;
      type: string;
      label: string;
      parent: string | null;
    }>;
    edges: Array<{
      source: string;
      target: string;
    }>;
  };
}

export interface DownloadRequest {
  project_id: string;
  terraform_code: string;
  ansible_playbook: string;
  cost_estimate: string;
  user_prompt: string;
}

// API Functions
export const generateInfrastructure = async (prompt: string): Promise<GenerateResponse> => {
  const response = await api.post<GenerateResponse>('/generate', { prompt });
  return response.data;
};

export const downloadDeploymentKit = async (request: DownloadRequest): Promise<Blob> => {
  const response = await api.post('/download', request, {
    responseType: 'blob',
  });
  return response.data;
};
