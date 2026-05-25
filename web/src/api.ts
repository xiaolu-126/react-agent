import type {
  ChatRequest,
  ChatResponse,
  GenerateRequest,
  GenerateResponse,
  ModelListResponse,
  SystemPromptListResponse,
  SystemPromptContent,
  AgentStatus,
  HistoryResponse,
  KnowledgeStatus,
  KnowledgeSearchResponse,
} from './types';

const BASE_URL = 'http://localhost:8000/api/v1';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || err.error || 'Request failed');
  }
  return res.json();
}

export const api = {
  chat: (data: ChatRequest) =>
    request<ChatResponse>('/chat', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  chatStream: (data: ChatRequest) => {
    const url = `${BASE_URL}/chat/stream`;
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  generate: (data: GenerateRequest) =>
    request<GenerateResponse>('/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  generateStream: (data: GenerateRequest) => {
    const url = `${BASE_URL}/generate/stream`;
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  getModels: () => request<ModelListResponse>('/models'),

  switchModel: (modelType: string) =>
    request<{ name: string }>('/models/switch', {
      method: 'POST',
      body: JSON.stringify({ model_type: modelType }),
    }),

  getSystemPrompts: () => request<SystemPromptListResponse>('/system-prompts'),

  getSystemPromptContent: (name: string) =>
    request<SystemPromptContent>(`/system-prompts/${name}`),

  switchSystemPrompt: (promptName: string) =>
    request<{ name: string }>('/system-prompts/switch', {
      method: 'POST',
      body: JSON.stringify({ prompt_name: promptName }),
    }),

  createSystemPrompt: (data: { name: string; content: string; description?: string; category?: string }) =>
    request<{ name: string }>('/system-prompts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteSystemPrompt: (name: string) =>
    request<{ message: string }>(`/system-prompts/${name}`, {
      method: 'DELETE',
    }),

  getStatus: () => request<AgentStatus>('/status'),

  getHistory: () => request<HistoryResponse>('/history'),

  clearMemory: () =>
    request<{ message: string }>('/memory/clear', { method: 'POST' }),

  getKnowledgeStatus: () => request<KnowledgeStatus>('/knowledge/status'),

  searchKnowledge: (query: string, k = 4) =>
    request<KnowledgeSearchResponse>('/knowledge/search', {
      method: 'POST',
      body: JSON.stringify({ query, k }),
    }),

  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    const res = await fetch(`${BASE_URL}/knowledge/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: res.statusText }));
      throw new Error(err.detail || 'Upload failed');
    }
    return res.json();
  },
};