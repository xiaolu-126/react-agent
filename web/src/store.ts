import { create } from 'zustand';
import type { Message, Conversation, ModelInfo, SystemPromptInfo, AgentStatus } from './types';
import { api } from './api';

function generateId() {
  return `conv-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function now() {
  return Date.now();
}

const STORAGE_KEY = 'ai-agent-conversations';

function loadConversations(): Conversation[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return [];
}

function saveConversations(convs: Conversation[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(convs));
  } catch {}
}

function buildDefaultConversation(): Conversation {
  return {
    id: generateId(),
    name: '新对话',
    messages: [],
    createdAt: now(),
    updatedAt: now(),
  };
}

interface AppState {
  conversations: Conversation[];
  activeConversationId: string;
  models: ModelInfo[];
  systemPrompts: SystemPromptInfo[];
  currentModel: string;
  currentSystemPrompt: string;
  status: AgentStatus | null;
  knowledgeDocCount: number;
  isLoading: boolean;
  streamerPanelOpen: boolean;
  settingsPanelOpen: boolean;
  error: string | null;

  // derived
  activeConversation: () => Conversation | undefined;
  messages: () => Message[];

  // conversation actions
  createConversation: () => string;
  deleteConversation: (id: string) => void;
  renameConversation: (id: string, name: string) => void;
  switchConversation: (id: string) => void;
  addMessage: (msg: Message) => void;
  clearActiveConversation: () => void;

  // existing actions
  fetchStatus: () => Promise<void>;
  fetchModels: () => Promise<void>;
  fetchSystemPrompts: () => Promise<void>;
  switchModel: (name: string) => Promise<void>;
  switchSystemPrompt: (name: string) => Promise<void>;
  setStreamerPanel: (open: boolean) => void;
  setSettingsPanel: (open: boolean) => void;
  setError: (err: string | null) => void;
}

export const useStore = create<AppState>((set, get) => {
  const saved = loadConversations();
  let conversations: Conversation[];
  let activeConversationId: string;

  if (saved.length === 0) {
    const def = buildDefaultConversation();
    conversations = [def];
    activeConversationId = def.id;
    saveConversations(conversations);
  } else {
    conversations = saved;
    activeConversationId = saved[0].id;
  }

  return {
    conversations,
    activeConversationId,
    models: [],
    systemPrompts: [],
    currentModel: 'deepseek',
    currentSystemPrompt: 'streamer_recommender',
    status: null,
    knowledgeDocCount: 0,
    isLoading: false,
    streamerPanelOpen: false,
    settingsPanelOpen: false,
    error: null,

    activeConversation: () => {
      const s = get();
      return s.conversations.find((c) => c.id === s.activeConversationId);
    },

    messages: () => {
      const conv = get().activeConversation();
      return conv?.messages ?? [];
    },

    createConversation: () => {
      const conv = buildDefaultConversation();
      set((s) => {
        const updated = [conv, ...s.conversations];
        saveConversations(updated);
        return { conversations: updated, activeConversationId: conv.id };
      });
      return conv.id;
    },

    deleteConversation: (id) => {
      set((s) => {
        const updated = s.conversations.filter((c) => c.id !== id);
        if (updated.length === 0) {
          const def = buildDefaultConversation();
          updated.push(def);
          saveConversations(updated);
          return { conversations: updated, activeConversationId: def.id };
        }
        let newActive = s.activeConversationId;
        if (newActive === id) {
          newActive = updated[0].id;
        }
        saveConversations(updated);
        return { conversations: updated, activeConversationId: newActive };
      });
    },

    renameConversation: (id, name) => {
      set((s) => {
        const updated = s.conversations.map((c) =>
          c.id === id ? { ...c, name, updatedAt: now() } : c
        );
        saveConversations(updated);
        return { conversations: updated };
      });
    },

    switchConversation: (id) => {
      set({ activeConversationId: id });
    },

    addMessage: (msg) => {
      set((s) => {
        const updated = s.conversations.map((c) => {
          if (c.id !== s.activeConversationId) return c;
          const newMessages = [...c.messages, msg];
          let newName = c.name;
          if (newName === '新对话' && msg.role === 'user') {
            newName = msg.content.length > 20
              ? msg.content.slice(0, 20) + '...'
              : msg.content;
          }
          return { ...c, messages: newMessages, name: newName, updatedAt: now() };
        });
        saveConversations(updated);
        return { conversations: updated };
      });
    },

    clearActiveConversation: () => {
      set((s) => {
        const updated = s.conversations.map((c) =>
          c.id === s.activeConversationId
            ? { ...c, messages: [], name: '新对话', updatedAt: now() }
            : c
        );
        saveConversations(updated);
        return { conversations: updated };
      });
    },

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
    setSettingsPanel: (open) => set({ settingsPanelOpen: open }),
    setError: (err) => set({ error: err }),
  };
});