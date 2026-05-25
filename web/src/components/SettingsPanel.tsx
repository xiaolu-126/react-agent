import { useState, useEffect, useRef, useCallback } from 'react';
import {
  X,
  Cpu,
  FileText,
  FileCode,
  Database,
  Upload,
  Search,
  CheckCircle2,
  Plus,
  Trash2,
  Eye,
  Loader2,
  RefreshCw,
} from 'lucide-react';
import { useStore } from '../store';
import { api } from '../api';
import type { SystemPromptContent, CustomPromptInfo, KnowledgeStatus, KnowledgeSearchResult } from '../types';

type Tab = 'models' | 'prompts' | 'custom' | 'knowledge';

const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: 'models', label: '模型', icon: Cpu },
  { key: 'prompts', label: '提示词', icon: FileText },
  { key: 'custom', label: '自定义', icon: FileCode },
  { key: 'knowledge', label: '知识库', icon: Database },
];

export default function SettingsPanel() {
  const { settingsPanelOpen, setSettingsPanel } = useStore();
  const [activeTab, setActiveTab] = useState<Tab>('models');

  useEffect(() => {
    if (!settingsPanelOpen) {
      setActiveTab('models');
    }
  }, [settingsPanelOpen]);

  if (!settingsPanelOpen) return null;

  return (
    <div className="fixed inset-0 z-40 flex" onClick={() => setSettingsPanel(false)}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      <div
        className="relative ml-auto w-[600px] max-w-[90vw] h-full bg-[var(--bg-primary)] border-l border-[var(--border-color)] shadow-2xl animate-slide-in flex flex-col"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)]">
          <h2 className="text-base font-semibold text-[var(--text-primary)]">设置</h2>
          <button
            onClick={() => setSettingsPanel(false)}
            className="p-1.5 rounded-lg hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex border-b border-[var(--border-color)] px-4 shrink-0">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`flex items-center gap-2 px-3 py-2.5 text-xs border-b-2 transition-all ${
                  activeTab === tab.key
                    ? 'border-[var(--accent)] text-[var(--accent-hover)]'
                    : 'border-transparent text-[var(--text-secondary)] hover:text-[var(--text-primary)]'
                }`}
              >
                <Icon size={15} />
                {tab.label}
              </button>
            );
          })}
        </div>

        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'models' && <ModelManager />}
          {activeTab === 'prompts' && <SystemPromptManager />}
          {activeTab === 'custom' && <CustomPromptManager />}
          {activeTab === 'knowledge' && <KnowledgePanel />}
        </div>
      </div>
    </div>
  );
}

/* ---------- Model Manager ---------- */

function ModelManager() {
  const { models, currentModel, switchModel, fetchModels } = useStore();

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

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
            className={`rounded-xl p-4 text-left transition-all border ${
              model.is_current
                ? 'border-[var(--accent)] bg-[var(--accent)]/5'
                : 'border-[var(--border-color)] bg-[var(--bg-secondary)]/30 hover:bg-white/5'
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

/* ---------- System Prompt Manager ---------- */

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
    <div className="grid grid-cols-1 gap-4">
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-[var(--text-primary)]">提示词列表</h3>
          <button onClick={() => setShowCreate(!showCreate)} className="btn-ghost text-xs flex items-center gap-1.5">
            <Plus size={14} />
            新建
          </button>
        </div>

        {showCreate && (
          <div className="border border-[var(--border-color)] rounded-xl p-4 mb-3 space-y-3 animate-fade-in bg-[var(--bg-secondary)]/30">
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
              className={`border rounded-xl p-3 transition-all ${
                p.is_current ? 'border-[var(--cyan)]' : 'border-[var(--border-color)] bg-[var(--bg-secondary)]/20'
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

      {selectedContent && (
        <div className="border border-[var(--border-color)] rounded-xl p-4 animate-fade-in bg-[var(--bg-secondary)]/20">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm font-medium text-[var(--text-primary)]">{selectedContent.name}</span>
            <span className="text-[10px] text-[var(--text-muted)]">{selectedContent.file_path}</span>
          </div>
          <pre className="text-xs text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap font-mono bg-[var(--bg-primary)] rounded-lg p-3">
            {selectedContent.content}
          </pre>
        </div>
      )}
    </div>
  );
}

/* ---------- Custom Prompt Manager ---------- */

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
            <div key={p.name} className="border border-[var(--border-color)] rounded-xl p-3 bg-[var(--bg-secondary)]/20">
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

/* ---------- Knowledge Panel ---------- */

function KnowledgePanel() {
  const [status, setStatus] = useState<KnowledgeStatus | null>(null);
  const [loading, setLoading] = useState(false);

  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<KnowledgeSearchResult[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchDone, setSearchDone] = useState(false);

  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<string | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchStatus = useCallback(async () => {
    setLoading(true);
    try {
      const s = await api.getKnowledgeStatus();
      setStatus(s);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStatus();
  }, [fetchStatus]);

  const doSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    setSearchDone(false);
    try {
      const res = await api.searchKnowledge(searchQuery);
      setSearchResults(res.results);
      setSearchDone(true);
    } catch {
      // silent
    } finally {
      setSearchLoading(false);
    }
  };

  const handleFileDrop = async (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) await doUpload(file);
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) await doUpload(file);
  };

  const doUpload = async (file: File) => {
    setUploading(true);
    setUploadResult(null);
    try {
      const res = await api.uploadDocument(file);
      setUploadResult(`上传成功: ${res.file_name} (${res.chunk_count} 个分块)`);
      fetchStatus();
    } catch (e) {
      setUploadResult(`上传失败: ${(e as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="space-y-5">
      {/* Status */}
      <div className="border border-[var(--border-color)] rounded-xl p-4 bg-[var(--bg-secondary)]/20">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-[var(--text-primary)] flex items-center gap-2">
            <Database size={16} className="text-[var(--cyan)]" />
            状态概览
          </h3>
          <button onClick={fetchStatus} className="btn-ghost text-xs flex items-center gap-1">
            <RefreshCw size={12} className={loading ? 'animate-spin' : ''} />
            刷新
          </button>
        </div>
        {status ? (
          <div className="grid grid-cols-2 gap-3">
            <div className="bg-[var(--bg-secondary)]/50 rounded-lg p-3">
              <div className="text-2xl font-bold text-[var(--accent-hover)]">{status.document_count}</div>
              <div className="text-xs text-[var(--text-muted)]">文档数量</div>
            </div>
            <div className="bg-[var(--bg-secondary)]/50 rounded-lg p-3">
              <div className="text-sm font-medium text-[var(--text-primary)] truncate">{status.collection_name}</div>
              <div className="text-xs text-[var(--text-muted)]">集合名称</div>
            </div>
            <div className="bg-[var(--bg-secondary)]/50 rounded-lg p-3">
              <div className="text-sm font-medium text-[var(--text-primary)] truncate">{status.embedding_model}</div>
              <div className="text-xs text-[var(--text-muted)]">嵌入模型</div>
            </div>
            <div className="bg-[var(--bg-secondary)]/50 rounded-lg p-3">
              <div className="text-sm font-medium text-[var(--text-primary)] truncate">{status.persist_directory || '内存'}</div>
              <div className="text-xs text-[var(--text-muted)]">持久化目录</div>
            </div>
          </div>
        ) : (
          <div className="text-sm text-[var(--text-muted)] py-4 text-center">加载中...</div>
        )}
      </div>

      {/* Upload */}
      <div className="border border-[var(--border-color)] rounded-xl p-4 bg-[var(--bg-secondary)]/20">
        <h3 className="text-sm font-medium text-[var(--text-primary)] flex items-center gap-2 mb-3">
          <Upload size={16} className="text-[var(--accent-hover)]" />
          上传文档
        </h3>
        <div
          className={`border-2 border-dashed rounded-xl p-6 text-center transition-all cursor-pointer ${
            dragOver
              ? 'border-[var(--accent)] bg-[var(--accent)]/5'
              : 'border-[var(--border-color)] hover:border-[var(--text-muted)]'
          }`}
          onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={handleFileDrop}
          onClick={() => fileInputRef.current?.click()}
        >
          <input ref={fileInputRef} type="file" accept=".pdf,.txt,.md,.yaml,.yml,.json,.csv" className="hidden" onChange={handleFileSelect} />
          {uploading ? (
            <Loader2 size={24} className="animate-spin mx-auto text-[var(--accent-hover)] mb-2" />
          ) : (
            <Upload size={24} className="mx-auto text-[var(--text-muted)] mb-2" />
          )}
          <p className="text-sm text-[var(--text-secondary)]">
            {uploading ? '上传处理中...' : '拖拽文件到此处，或点击选择'}
          </p>
          <p className="text-xs text-[var(--text-muted)] mt-1">支持 PDF、TXT、MD、YAML、JSON、CSV 格式</p>
        </div>
        {uploadResult && (
          <div className={`flex items-center gap-2 mt-3 text-xs ${uploadResult.includes('失败') ? 'text-red-400' : 'text-[var(--cyan)]'}`}>
            {uploadResult.includes('失败') ? <Trash2 size={12} /> : <CheckCircle2 size={12} />}
            {uploadResult}
          </div>
        )}
      </div>

      {/* Search */}
      <div className="border border-[var(--border-color)] rounded-xl p-4 bg-[var(--bg-secondary)]/20">
        <h3 className="text-sm font-medium text-[var(--text-primary)] flex items-center gap-2 mb-3">
          <Search size={16} className="text-[var(--accent-hover)]" />
          知识搜索
        </h3>
        <div className="flex gap-2">
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && doSearch()}
            placeholder="输入搜索关键词..."
            className="input-field text-sm flex-1"
          />
          <button onClick={doSearch} disabled={!searchQuery.trim() || searchLoading} className="btn-primary text-sm flex items-center gap-1.5">
            {searchLoading ? <Loader2 size={14} className="animate-spin" /> : <Search size={14} />}
            搜索
          </button>
        </div>
        {searchLoading && (
          <div className="flex items-center justify-center py-4">
            <Loader2 size={20} className="animate-spin text-[var(--text-muted)]" />
          </div>
        )}
        {searchDone && !searchLoading && (
          <div className="mt-3 space-y-2">
            {searchResults.length === 0 ? (
              <p className="text-sm text-[var(--text-muted)] py-4 text-center">未找到相关结果</p>
            ) : (
              searchResults.map((r, i) => (
                <div key={i} className="bg-[var(--bg-secondary)]/50 rounded-lg p-3 animate-fade-in">
                  <p className="text-xs text-[var(--text-secondary)] leading-relaxed line-clamp-3">
                    {r.content}
                  </p>
                  {r.score !== null && (
                    <span className="text-[10px] text-[var(--text-muted)] mt-1 block">
                      相似度: {(r.score * 100).toFixed(1)}%
                    </span>
                  )}
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}