import { create } from 'zustand';
import type { Message, ModelInfo, SystemPromptInfo, AgentStatus } from './types';
import { api } from './api';

interface AppState {
  messages: Message[];
  models: ModelInfo[];
  systemPrompts: SystemPromptInfo[];
  currentModel: string;
  currentSystemPrompt: string;
  status: AgentStatus | null;
  knowledgeDocCount: number;
  isLoading: boolean;
  streamerPanelOpen: boolean;
  error: string | null;

  addMessage: (msg: Message) => void;
  clearMessages: () => void;
  fetchStatus: () => Promise<void>;
  fetchModels: () => Promise<void>;
  fetchSystemPrompts: () => Promise<void>;
  switchModel: (name: string) => Promise<void>;
  switchSystemPrompt: (name: string) => Promise<void>;
  setStreamerPanel: (open: boolean) => void;
  setError: (err: string | null) => void;
}

export const useStore = create<AppState>((set, get) => ({
  messages: [],
  models: [],
  systemPrompts: [],
  currentModel: 'deepseek',
  currentSystemPrompt: 'streamer_recommender',
  status: null,
  knowledgeDocCount: 0,
  isLoading: false,
  streamerPanelOpen: false,
  error: null,

  addMessage: (msg) => set((s) => ({ messages: [...s.messages, msg] })),

  clearMessages: () => set({ messages: [] }),

  fetchStatus: async () => {
    try {
      const status = await api.getStatus();
      set({
        status,
        currentModel: status.current_model,
        currentSystemPrompt: status.current_system_prompt,
        knowledgeDocCount: status.knowledge_base_count,
      });
    } catch {
      // silent on init
    }
  },

  fetchModels: async () => {
    try {
      const res = await api.getModels();
      set({ models: res.models, currentModel: res.current });
    } catch {
      // silent
    }
  },

  fetchSystemPrompts: async () => {
    try {
      const res = await api.getSystemPrompts();
      set({ systemPrompts: res.prompts, currentSystemPrompt: res.current });
    } catch {
      // silent
    }
  },

  switchModel: async (name) => {
    try {
      await api.switchModel(name);
      set({ currentModel: name });
    } catch (e: unknown) {
      set({ error: `切换模型失败: ${e instanceof Error ? e.message : String(e)}` });
    }
  },

  switchSystemPrompt: async (name) => {
    try {
      await api.switchSystemPrompt(name);
      set({ currentSystemPrompt: name });
    } catch (e: unknown) {
      set({ error: `切换系统提示词失败: ${e instanceof Error ? e.message : String(e)}` });
    }
  },

  setStreamerPanel: (open) => set({ streamerPanelOpen: open }),
  setError: (err) => set({ error: err }),
}));