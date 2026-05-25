import { useState, useEffect } from 'react';
import {
  Cpu,
  FileText,
  FileCode,
  CheckCircle2,
  Plus,
  Trash2,
  Eye,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { useStore } from '../store';
import { api } from '../api';
import type { SystemPromptContent, CustomPromptInfo } from '../types';

type Tab = 'models' | 'system-prompts' | 'custom-prompts';

export default function SettingsView() {
  const [activeTab, setActiveTab] = useState<Tab>('models');

  return (
    <div className="flex flex-col h-full">
      <div className="border-b border-[var(--border-color)] px-5 py-3">
        <h2 className="text-base font-semibold text-[var(--text-primary)]">管理后台</h2>
      </div>

      {/* Tabs */}
      <div className="flex border-b border-[var(--border-color)] px-5">
        {[
          { key: 'models', label: '模型管理', icon: Cpu },
          { key: 'system-prompts', label: '系统提示词', icon: FileText },
          { key: 'custom-prompts', label: '自定义提示词', icon: FileCode },
        ].map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as Tab)}
              className={`flex items-center gap-2 px-4 py-3 text-sm border-b-2 transition-all ${
                activeTab === tab.key
                  ? 'border-[var(--accent)] text-[var(--accent-hover)]'
                  : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
              }`}
            >
              <Icon size={16} />
              {tab.label}
            </button>
          );
        })}
      </div>

      <div className="flex-1 overflow-y-auto p-5">
        {activeTab === 'models' && <ModelManager />}
        {activeTab === 'system-prompts' && <SystemPromptManager />}
        {activeTab === 'custom-prompts' && <CustomPromptManager />}
      </div>
    </div>
  );
}

function ModelManager() {
  const { models, currentModel, switchModel, fetchModels } = useStore();

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const modelNames: Record<string, string> = {
    openai: 'GPT-4 / GPT-3.5',
    anthropic: 'Claude 3',
    dashscope: '通义千问',
    qianfan: '文心一言',
    deepseek: 'DeepSeek',
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-[var(--text-primary)]">可用模型</h3>
        <button onClick={fetchModels} className="btn-ghost text-xs flex items-center gap-1.5">
          <RefreshCw size={14} />
          刷新
        </button>
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {models.map((model) => (
          <button
            key={model.name}
            onClick={() => switchModel(model.name)}
            className={`glass-card rounded-xl p-4 text-left transition-all ${
              model.is_current
                ? 'ring-1 ring-[var(--accent)] bg-[var(--accent)]/5'
                : 'hover:bg-white/5'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm font-medium text-[var(--text-primary)]">
                {model.display_name}
              </span>
              {model.is_current && (
                <CheckCircle2 size={16} className="text-[var(--accent-hover)]" />
              )}
            </div>
            <span className="tag tag-blue text-xs">{model.name}</span>
          </button>
        ))}
      </div>
    </div>
  );
}

function SystemPromptManager() {
  const { systemPrompts, currentSystemPrompt, switchSystemPrompt, fetchSystemPrompts } = useStore();
  const [selectedContent, setSelectedContent] = useState<SystemPromptContent | null>(null);
  const [loading, setLoading] = useState<string | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [newName, setNewName] = useState('');
  const [newContent, setNewContent] = useState('');
  const [newDesc, setNewDesc] = useState('');

  useEffect(() => {
    fetchSystemPrompts();
  }, [fetchSystemPrompts]);

  const viewContent = async (name: string) => {
    setLoading(name);
    try {
      const content = await api.getSystemPromptContent(name);
      setSelectedContent(content);
    } catch {
      // silent
    } finally {
      setLoading(null);
    }
  };

  const createPrompt = async () => {
    if (!newName.trim() || !newContent.trim()) return;
    try {
      await api.createSystemPrompt({ name: newName, content: newContent, description: newDesc });
      await fetchSystemPrompts();
      setShowCreate(false);
      setNewName('');
      setNewContent('');
      setNewDesc('');
    } catch {
      // silent
    }
  };

  const deletePrompt = async (name: string) => {
    try {
      await api.deleteSystemPrompt(name);
      await fetchSystemPrompts();
      setSelectedContent(null);
    } catch {
      // silent
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-sm font-medium text-[var(--text-primary)]">提示词列表</h3>
          <button onClick={() => setShowCreate(!showCreate)} className="btn-ghost text-xs flex items-center gap-1.5">
            <Plus size={14} />
            新建
          </button>
        </div>

        {showCreate && (
          <div className="glass-card rounded-xl p-4 mb-3 space-y-3 animate-fade-in">
            <input
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="模板名称"
              className="input-field text-sm"
            />
            <input
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
              placeholder="描述（可选）"
              className="input-field text-sm"
            />
            <textarea
              value={newContent}
              onChange={(e) => setNewContent(e.target.value)}
              placeholder="提示词内容"
              rows={4}
              className="input-field text-sm resize-none font-mono"
            />
            <button onClick={createPrompt} className="btn-primary w-full text-sm">
              创建
            </button>
          </div>
        )}

        <div className="space-y-2">
          {systemPrompts.map((p) => (
            <div
              key={p.name}
              className={`glass-card rounded-xl p-3 transition-all ${
                p.is_current ? 'ring-1 ring-[var(--cyan)]' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-[var(--text-primary)]">{p.name}</span>
                  <span className={`tag ${p.category === 'recommendation' ? 'tag-cyan' : p.category === 'general' ? 'tag-blue' : 'tag-amber'} text-xs`}>
                    {p.category}
                  </span>
                </div>
                {p.is_current && <span className="text-[10px] text-[var(--cyan)]">当前</span>}
              </div>
              <p className="text-xs text-[var(--text-muted)] mb-2">{p.description}</p>
              <div className="flex items-center gap-1.5">
                <button
                  onClick={() => switchSystemPrompt(p.name)}
                  disabled={p.is_current}
                  className="btn-ghost text-xs !py-1 !px-2"
                >
                  切换
                </button>
                <button onClick={() => viewContent(p.name)} className="btn-ghost text-xs !py-1 !px-2">
                  {loading === p.name ? <Loader2 size={12} className="animate-spin" /> : <Eye size={12} />}
                  查看
                </button>
                {!['streamer_recommender', 'general_assistant', 'code_expert'].includes(p.name) && (
                  <button onClick={() => deletePrompt(p.name)} className="btn-ghost text-xs !py-1 !px-2 text-red-400 hover:text-red-300">
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      <div>
        <h3 className="text-sm font-medium text-[var(--text-primary)] mb-4">内容预览</h3>
        {selectedContent ? (
          <div className="glass-card rounded-xl p-4 animate-fade-in">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm font-medium text-[var(--text-primary)]">{selectedContent.name}</span>
              <span className="text-[10px] text-[var(--text-muted)]">{selectedContent.file_path}</span>
            </div>
            <pre className="text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap font-mono bg-[var(--bg-primary)] rounded-lg p-3">
              {selectedContent.content}
            </pre>
          </div>
        ) : (
          <div className="flex items-center justify-center h-32 text-sm text-[var(--text-muted)]">
            点击"查看"按钮预览内容
          </div>
        )}
      </div>
    </div>
  );
}

function CustomPromptManager() {
  const [prompts, setPrompts] = useState<CustomPromptInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPrompts = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/api/v1/custom-prompts');
      if (!res.ok) throw new Error('Failed to fetch');
      const data = await res.json();
      setPrompts(data.prompts);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPrompts();
  }, []);

  if (error) {
    return (
      <div className="text-sm text-[var(--text-muted)]">
        加载失败: {error}
        <button onClick={fetchPrompts} className="btn-ghost text-xs ml-2">重试</button>
      </div>
    );
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-[var(--text-primary)]">自定义模板</h3>
        <button onClick={fetchPrompts} className="btn-ghost text-xs flex items-center gap-1.5">
          <RefreshCw size={14} className={loading ? 'animate-spin' : ''} />
          刷新
        </button>
      </div>
      {loading ? (
        <div className="flex items-center justify-center py-8">
          <Loader2 size={20} className="animate-spin text-[var(--text-muted)]" />
        </div>
      ) : (
        <div className="space-y-2">
          {prompts.map((p) => (
            <div key={p.name} className="glass-card rounded-xl p-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="text-sm font-medium text-[var(--text-primary)]">{p.name}</span>
                <span className="tag tag-blue text-xs">{p.category}</span>
              </div>
              {p.description && (
                <p className="text-xs text-[var(--text-muted)] mb-1">{p.description}</p>
              )}
              {p.input_variables.length > 0 && (
                <div className="flex flex-wrap gap-1 mt-1.5">
                  {p.input_variables.map((v) => (
                    <span key={v} className="text-[10px] text-[var(--cyan)] bg-[var(--cyan)]/10 px-1.5 py-0.5 rounded">
                      {'{'}{v}{'}'}
                    </span>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}