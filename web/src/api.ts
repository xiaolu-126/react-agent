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
  KnowledgeDocumentListResponse,
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

  addModel: (data: { model_type: string; model_name: string; api_key: string; api_base?: string; temperature?: number; max_tokens?: number }) =>
    request<{ name: string; display_name: string; is_current: boolean }>('/models/add', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  deleteModel: (modelType: string) =>
    request<{ message: string }>(`/models/${modelType}`, {
      method: 'DELETE',
    }),

  getSystemPrompts: () => request<SystemPromptListResponse>('/system-prompts'),

  getSystemPromptContent: (name: string) =>
    request<SystemPromptContent>(`/system-prompts/${name}`),

  getPromptTemplate: (name: string) =>
    request<{
      name: string;
      description: string;
      category: string;
      input_variables: string[];
      template_content: string;
    }>(`/prompts/${name}`),

  generateFromTemplateStream: (data: { template_name: string; variables: Record<string, string> }) => {
    const url = `${BASE_URL}/prompts/generate/stream`;
    return fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
  },

  getCustomPrompts: () =>
    request<{ prompts: CustomPromptInfo[] }>('/custom-prompts'),

  getCustomPromptDetail: (name: string) =>
    request<CustomPromptInfo>(`/custom-prompts/${name}`),

  createCustomPrompt: (data: { name: string; template: string; description?: string; category?: string; input_variables?: string[] }) =>
    request<{ message: string; name: string }>('/custom-prompts', {
      method: 'POST',
      body: JSON.stringify(data),
    }),

  editCustomPrompt: (name: string, data: { template?: string; input_variables?: string[]; description?: string; category?: string }) =>
    request<CustomPromptInfo>(`/custom-prompts/${name}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    }),

  deleteCustomPrompt: (name: string) =>
    request<{ message: string }>(`/custom-prompts/${name}`, {
      method: 'DELETE',
    }),

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

  editSystemPrompt: (name: string, data: { content?: string; description?: string; category?: string }) =>
    request<{ name: string }>(`/system-prompts/${name}`, {
      method: 'PUT',
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

  uploadDocument: async (file: File, metadata?: Record<string, string>) => {
    const formData = new FormData();
    formData.append('file', file);
    if (metadata && Object.keys(metadata).length > 0) {
      formData.append('metadata', JSON.stringify(metadata));
    }
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

  getKnowledgeDocuments: (limit = 50, offset = 0) =>
    request<KnowledgeDocumentListResponse>(`/knowledge/documents?limit=${limit}&offset=${offset}`),

  getKnowledgeFiles: () =>
    request<{ files: { source: string; chunk_count: number }[]; total: number }>('/knowledge/files'),

  getKnowledgeFileDetail: (source: string) =>
    request<{ source: string; chunk_count: number; documents: KnowledgeDocumentListResponse['documents'] }>(
      `/knowledge/file-detail?source=${encodeURIComponent(source)}`
    ),

  deleteKnowledgeFile: (source: string) =>
    request<{ source: string; deleted_chunks: number; message: string }>(
      `/knowledge/file-detail?source=${encodeURIComponent(source)}`,
      { method: 'DELETE' }
    ),

  deleteKnowledgeDocument: (docId: string) =>
    request<{ message: string }>(`/knowledge/documents/${docId}`, {
      method: 'DELETE',
    }),

  clearKnowledgeBase: () =>
    request<{ message: string }>('/knowledge/clear', { method: 'POST' }),
};