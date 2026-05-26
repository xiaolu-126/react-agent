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
  Settings2,
  Save,
  Pencil,
  ChevronRight,
} from 'lucide-react';
import { useStore } from '../store';
import { api } from '../api';
import type { SystemPromptContent, CustomPromptInfo, KnowledgeStatus, KnowledgeSearchResult, KnowledgeDocumentInfo } from '../types';

type Tab = 'models' | 'prompts' | 'custom' | 'knowledge';

const tabs: { key: Tab; label: string; icon: React.ElementType }[] = [
  { key: 'models', label: '模型', icon: Cpu },
  { key: 'prompts', label: '提示词', icon: FileText },
  { key: 'custom', label: '自定义', icon: FileCode },
  { key: 'knowledge', label: '知识库', icon: Database },
];

/* ---------- Prompt Edit Modal ---------- */

function PromptEditModal({
  prompt,
  onClose,
  onSaved,
}: {
  prompt: SystemPromptContent;
  onClose: () => void;
  onSaved: () => void;
}) {
  const [editMode, setEditMode] = useState(false);
  const [content, setContent] = useState(prompt.content);
  const [saving, setSaving] = useState(false);

  const handleSave = async () => {
    setSaving(true);
    try {
      await api.editSystemPrompt(prompt.name, { content });
      onSaved();
      setEditMode(false);
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={onClose}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
      <div
        className="relative w-[640px] max-w-[92vw] max-h-[85vh] bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-2xl shadow-2xl flex flex-col animate-fade-in"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)] shrink-0">
          <div className="flex items-center gap-3">
            <h3 className="text-sm font-semibold text-[var(--text-primary)]">
              提示词: {prompt.name}
            </h3>
            <span className="text-[10px] text-[var(--text-muted)] truncate max-w-[200px]">
              {prompt.file_path}
            </span>
          </div>
          <div className="flex items-center gap-2">
            {editMode ? (
              <button
                onClick={handleSave}
                disabled={saving}
                className="btn-primary text-xs flex items-center gap-1.5 !py-1.5 !px-3"
              >
                {saving ? <Loader2 size={12} className="animate-spin" /> : <Save size={12} />}
                保存
              </button>
            ) : (
              <button
                onClick={() => setEditMode(true)}
                className="btn-ghost text-xs flex items-center gap-1.5 !py-1.5 !px-3"
              >
                <Pencil size={12} />
                编辑
              </button>
            )}
            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        </div>
        <div className="flex-1 overflow-y-auto p-5">
          {editMode ? (
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="input-field text-sm font-mono w-full min-h-[300px] resize-y leading-relaxed"
              autoFocus
            />
          ) : (
            <pre className="text-sm text-[var(--text-secondary)] leading-relaxed whitespace-pre-wrap font-mono bg-[var(--bg-secondary)]/30 rounded-xl p-4 border border-[var(--border-color)]">
              {prompt.content}
            </pre>
          )}
        </div>
      </div>
    </div>
  );
}

/* ---------- Main Settings Panel ---------- */

export default function SettingsPanel() {
  const { settingsPanelOpen, setSettingsPanel, fetchStatus } = useStore();

  const [activeTab, setActiveTab] = useState<Tab>('models');

  useEffect(() => {
    if (!settingsPanelOpen) {
      setActiveTab('models');
    }
  }, [settingsPanelOpen]);

  if (!settingsPanelOpen) return null;

  return (
    <div className="fixed inset-0 z-40 flex" onClick={() => setSettingsPanel(false)}>
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />

      <div
        className="relative w-full max-w-[900px] mx-auto my-6 h-[calc(100vh-48px)] bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-2xl shadow-2xl flex flex-col animate-scale-in overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border-color)] shrink-0">
          <h2 className="text-base font-semibold text-[var(--text-primary)]">设置</h2>
          <button
            onClick={() => setSettingsPanel(false)}
            className="p-1.5 rounded-lg hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
          >
            <X size={18} />
          </button>
        </div>

        <div className="flex border-b border-[var(--border-color)] px-5 shrink-0">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
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

        <div className="flex-1 overflow-y-auto p-6">
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

const BUILTIN_MODELS = ['openai', 'anthropic', 'dashscope', 'qianfan', 'deepseek'];

function ModelManager() {
  const { models, currentModel, switchModel, fetchModels, addModel, deleteModel } = useStore();
  const [showAdd, setShowAdd] = useState(false);
  const [addData, setAddData] = useState({ model_type: '', model_name: '', api_key: '', api_base: '' });
  const [adding, setAdding] = useState(false);
  const [switching, setSwitching] = useState<string | null>(null);

  useEffect(() => {
    fetchModels();
  }, [fetchModels]);

  const handleSwitch = async (name: string) => {
    setSwitching(name);
    try {
      await switchModel(name);
    } finally {
      setSwitching(null);
    }
  };

  const handleAdd = async () => {
    if (!addData.model_type.trim() || !addData.model_name.trim() || !addData.api_key.trim()) return;
    setAdding(true);
    try {
      await addModel({
        model_type: addData.model_type.trim(),
        model_name: addData.model_name.trim(),
        api_key: addData.api_key.trim(),
        api_base: addData.api_base.trim() || undefined,
      });
      setShowAdd(false);
      setAddData({ model_type: '', model_name: '', api_key: '', api_base: '' });
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (name: string) => {
    await deleteModel(name);
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-medium text-[var(--text-primary)]">可用模型</h3>
        <div className="flex items-center gap-2">
          <button onClick={() => setShowAdd(!showAdd)} className="btn-ghost text-xs flex items-center gap-1.5">
            <Plus size={14} />
            添加
          </button>
          <button onClick={fetchModels} className="btn-ghost text-xs flex items-center gap-1.5">
            <RefreshCw size={14} />
            刷新
          </button>
        </div>
      </div>

      {showAdd && (
        <div className="border border-[var(--border-color)] rounded-xl p-4 mb-4 space-y-3 animate-fade-in bg-[var(--bg-secondary)]/30">
          <h4 className="text-xs font-medium text-[var(--text-primary)] flex items-center gap-1.5">
            <Settings2 size={13} />
            添加自定义模型（OpenAI 兼容）
          </h4>
          <input
            value={addData.model_type}
            onChange={(e) => setAddData((p) => ({ ...p, model_type: e.target.value }))}
            placeholder="模型标识（如 my-model，需唯一）"
            className="input-field text-sm"
          />
          <input
            value={addData.model_name}
            onChange={(e) => setAddData((p) => ({ ...p, model_name: e.target.value }))}
            placeholder="模型名称（如 gpt-4o-mini）"
            className="input-field text-sm"
          />
          <input
            value={addData.api_key}
            onChange={(e) => setAddData((p) => ({ ...p, api_key: e.target.value }))}
            placeholder="API 密钥"
            type="password"
            className="input-field text-sm"
          />
          <input
            value={addData.api_base}
            onChange={(e) => setAddData((p) => ({ ...p, api_base: e.target.value }))}
            placeholder="API 基础 URL（可选，默认使用 OpenAI）"
            className="input-field text-sm"
          />
          <div className="flex gap-2">
            <button onClick={() => setShowAdd(false)} className="btn-ghost text-sm flex-1">
              取消
            </button>
            <button
              onClick={handleAdd}
              disabled={adding || !addData.model_type || !addData.model_name || !addData.api_key}
              className="btn-primary text-sm flex-1 flex items-center justify-center gap-1.5"
            >
              {adding ? <Loader2 size={14} className="animate-spin" /> : <Plus size={14} />}
              添加
            </button>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        {models.map((model) => (
          <div
            key={model.name}
            className={`rounded-xl p-4 transition-all border ${
              model.is_current
                ? 'border-[var(--accent)] bg-[var(--accent)]/5 ring-1 ring-[var(--accent)]/20'
                : 'border-[var(--border-color)] bg-[var(--bg-secondary)]/30 hover:border-[var(--text-muted)]/40'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-2 min-w-0">
                <span className="text-sm font-medium text-[var(--text-primary)] truncate">
                  {model.display_name}
                </span>
                <span className={`tag text-xs shrink-0 ${BUILTIN_MODELS.includes(model.name) ? 'tag-blue' : 'tag-amber'}`}>
                  {BUILTIN_MODELS.includes(model.name) ? '内置' : '自定义'}
                </span>
              </div>
              {model.is_current && (
                <CheckCircle2 size={15} className="text-[var(--accent-hover)] shrink-0 ml-1" />
              )}
            </div>
            <div className="text-xs text-[var(--text-muted)] mb-3 truncate">{model.name}</div>
            <div className="flex items-center gap-2">
              {!model.is_current ? (
                <button
                  onClick={() => handleSwitch(model.name)}
                  disabled={switching === model.name}
                  className="btn-primary text-xs !py-1.5 !px-3 flex items-center gap-1.5"
                >
                  {switching === model.name ? (
                    <Loader2 size={12} className="animate-spin" />
                  ) : (
                    <Cpu size={12} />
                  )}
                  使用
                </button>
              ) : (
                <span className="text-xs text-[var(--accent-hover)] font-medium px-2">当前使用</span>
              )}
              {!BUILTIN_MODELS.includes(model.name) && (
                <button
                  onClick={() => handleDelete(model.name)}
                  className="btn-ghost text-xs !py-1.5 !px-2 text-red-400 hover:text-red-300 ml-auto"
                >
                  <Trash2 size={12} />
                </button>
              )}
            </div>
          </div>
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
  const [switching, setSwitching] = useState<string | null>(null);
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

  const handleSwitch = async (name: string) => {
    setSwitching(name);
    try {
      await switchSystemPrompt(name);
    } finally {
      setSwitching(null);
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
      if (selectedContent?.name === name) setSelectedContent(null);
    } catch {
      // silent
    }
  };

  return (
    <div className="grid grid-cols-1 gap-5">
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

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {systemPrompts.map((p) => (
            <div
              key={p.name}
              className={`border rounded-xl p-4 transition-all ${
                p.is_current ? 'border-[var(--cyan)] ring-1 ring-[var(--cyan)]/20' : 'border-[var(--border-color)] bg-[var(--bg-secondary)]/20 hover:border-[var(--text-muted)]/40'
              }`}
            >
              <div className="flex items-center justify-between mb-1.5">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-sm font-medium text-[var(--text-primary)] truncate">{p.name}</span>
                  <span className={`tag shrink-0 ${p.category === 'recommendation' ? 'tag-cyan' : p.category === 'general' ? 'tag-blue' : 'tag-amber'} text-xs`}>
                    {p.category}
                  </span>
                </div>
                {p.is_current && <span className="text-[10px] text-[var(--cyan)] shrink-0 ml-1">当前</span>}
              </div>
              <p className="text-xs text-[var(--text-muted)] mb-3 line-clamp-2">{p.description}</p>
              <div className="flex items-center gap-1.5">
                {!p.is_current ? (
                  <button
                    onClick={() => handleSwitch(p.name)}
                    disabled={switching === p.name}
                    className="btn-primary text-xs !py-1.5 !px-3 flex items-center gap-1.5"
                  >
                    {switching === p.name ? (
                      <Loader2 size={12} className="animate-spin" />
                    ) : (
                      <FileText size={12} />
                    )}
                    使用
                  </button>
                ) : (
                  <span className="text-xs text-[var(--cyan)] font-medium px-2">当前使用</span>
                )}
                <button onClick={() => viewContent(p.name)} className="btn-ghost text-xs !py-1.5 !px-2 flex items-center gap-1">
                  {loading === p.name ? <Loader2 size={12} className="animate-spin" /> : <Eye size={12} />}
                  查看
                </button>
                {!['streamer_recommender', 'general_assistant', 'code_expert'].includes(p.name) && (
                  <button onClick={() => deletePrompt(p.name)} className="btn-ghost text-xs !py-1.5 !px-2 text-red-400 hover:text-red-300 ml-auto">
                    <Trash2 size={12} />
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedContent && (
        <PromptEditModal
          prompt={selectedContent}
          onClose={() => setSelectedContent(null)}
          onSaved={() => {
            fetchSystemPrompts();
          }}
        />
      )}
    </div>
  );
}

/* ---------- Custom Prompt Manager ---------- */

const BUILTIN_PROMPTS = ['streamer_recommendation', 'content_summary', 'question_answering'];

function CustomPromptManager() {
  const [prompts, setPrompts] = useState<CustomPromptInfo[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [editing, setEditing] = useState<CustomPromptInfo | null>(null);
  const [editTemplate, setEditTemplate] = useState('');
  const [editDesc, setEditDesc] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editVariables, setEditVariables] = useState('');
  const [saving, setSaving] = useState(false);

  const fetchPrompts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await api.getCustomPrompts();
      setPrompts(data.prompts);
      setError(null);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchPrompts();
  }, [fetchPrompts]);

  const openEdit = (p: CustomPromptInfo) => {
    setEditing(p);
    setEditTemplate('');
    setEditDesc(p.description || '');
    setEditCategory(p.category || 'default');
    setEditVariables((p.input_variables || []).join(', '));
  };

  const editDetail = async (p: CustomPromptInfo) => {
    setEditing(p);
    setEditDesc(p.description || '');
    setEditCategory(p.category || 'default');
    setEditVariables((p.input_variables || []).join(', '));
    setEditTemplate('');
    setSaving(false);
  };

  const doSave = async () => {
    if (!editing) return;
    setSaving(true);
    try {
      const vars = editVariables
        .split(',')
        .map((v) => v.trim())
        .filter(Boolean);

      await api.editCustomPrompt(editing.name, {
        description: editDesc || undefined,
        category: editCategory || undefined,
        input_variables: vars.length > 0 ? vars : undefined,
        template: editTemplate || undefined,
      });
      setEditing(null);
      fetchPrompts();
    } catch {
      // silent
    } finally {
      setSaving(false);
    }
  };

  const deletePrompt = async (name: string) => {
    if (!window.confirm(`确定要删除提示词 "${name}" 吗？`)) return;
    try {
      const res = await fetch(`http://localhost:8000/api/v1/custom-prompts/${name}`, { method: 'DELETE' });
      if (!res.ok) throw new Error('Delete failed');
      fetchPrompts();
    } catch {
      // silent
    }
  };

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
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {prompts.map((p) => (
            <div key={p.name} className="border border-[var(--border-color)] rounded-xl p-4 bg-[var(--bg-secondary)]/20">
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-sm font-medium text-[var(--text-primary)]">{p.name}</span>
                  <span className={`tag text-xs shrink-0 ${BUILTIN_PROMPTS.includes(p.name) ? 'tag-blue' : 'tag-amber'}`}>
                    {BUILTIN_PROMPTS.includes(p.name) ? '内置' : '自定义'}
                  </span>
                </div>
                {!BUILTIN_PROMPTS.includes(p.name) && (
                  <div className="flex items-center gap-1 shrink-0 ml-2">
                    <button onClick={() => editDetail(p)} className="btn-ghost text-[10px] !py-1 !px-1.5">
                      <Pencil size={11} />
                    </button>
                    <button onClick={() => deletePrompt(p.name)} className="btn-ghost text-[10px] !py-1 !px-1.5 text-red-400 hover:text-red-300">
                      <Trash2 size={11} />
                    </button>
                  </div>
                )}
              </div>
              {p.description && (
                <p className="text-xs text-[var(--text-muted)] mb-2">{p.description}</p>
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

      {/* Edit Modal */}
      {editing && (
        <div className="fixed inset-0 z-50 flex items-center justify-center" onClick={() => setEditing(null)}>
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" />
          <div
            className="relative w-[560px] max-w-[92vw] max-h-[85vh] bg-[var(--bg-primary)] border border-[var(--border-color)] rounded-2xl shadow-2xl flex flex-col animate-fade-in"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between px-5 py-4 border-b border-[var(--border-color)] shrink-0">
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                编辑: {editing.name}
              </h3>
              <button onClick={() => setEditing(null)} className="p-1.5 rounded-lg hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors">
                <X size={16} />
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-5 space-y-4">
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">描述</label>
                <input
                  value={editDesc}
                  onChange={(e) => setEditDesc(e.target.value)}
                  placeholder="模板描述"
                  className="input-field text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">分类</label>
                <input
                  value={editCategory}
                  onChange={(e) => setEditCategory(e.target.value)}
                  placeholder="recommendation / general / content / default"
                  className="input-field text-sm"
                />
              </div>
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">变量（逗号分隔）</label>
                <input
                  value={editVariables}
                  onChange={(e) => setEditVariables(e.target.value)}
                  placeholder="name, tags, content"
                  className="input-field text-sm"
                />
                <p className="text-[10px] text-[var(--text-muted)] mt-1">输入变量名，用逗号分隔。如: streamer_name, streamer_tags</p>
              </div>
              <div>
                <label className="block text-xs text-[var(--text-secondary)] mb-1">模板内容</label>
                <textarea
                  value={editTemplate}
                  onChange={(e) => setEditTemplate(e.target.value)}
                  placeholder="留空则保持原内容..."
                  rows={6}
                  className="input-field text-sm resize-none font-mono w-full"
                />
              </div>
            </div>
            <div className="flex items-center justify-end gap-2 px-5 py-3 border-t border-[var(--border-color)] shrink-0">
              <button onClick={() => setEditing(null)} className="btn-ghost text-sm">取消</button>
              <button onClick={doSave} disabled={saving} className="btn-primary text-sm flex items-center gap-1.5">
                {saving ? <Loader2 size={14} className="animate-spin" /> : <Save size={14} />}
                保存
              </button>
            </div>
          </div>
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
  const [metaEntries, setMetaEntries] = useState<{ key: string; value: string }[]>([]);

  const [documents, setDocuments] = useState<KnowledgeDocumentInfo[]>([]);
  const [docTotal, setDocTotal] = useState(0);
  const [docLoading, setDocLoading] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);

  const [files, setFiles] = useState<{ source: string; chunk_count: number }[]>([]);
  const [filesTotal, setFilesTotal] = useState(0);
  const [filesLoading, setFilesLoading] = useState(false);
  const [expandedFile, setExpandedFile] = useState<string | null>(null);
  const [expandedChunks, setExpandedChunks] = useState<KnowledgeDocumentInfo[]>([]);
  const [expandedLoading, setExpandedLoading] = useState(false);
  const [deletingFile, setDeletingFile] = useState<string | null>(null);

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

  const fetchDocuments = useCallback(async () => {
    setDocLoading(true);
    try {
      const res = await api.getKnowledgeDocuments(100, 0);
      setDocuments(res.documents);
      setDocTotal(res.total);
    } catch {
      // silent
    } finally {
      setDocLoading(false);
    }
  }, []);

  const fetchFiles = useCallback(async () => {
    setFilesLoading(true);
    try {
      const res = await api.getKnowledgeFiles();
      setFiles(res.files);
      setFilesTotal(res.total);
    } catch {
      // silent
    } finally {
      setFilesLoading(false);
    }
  }, []);

  const expandFile = async (source: string) => {
    if (expandedFile === source) {
      setExpandedFile(null);
      setExpandedChunks([]);
      return;
    }
    setExpandedFile(source);
    setExpandedLoading(true);
    try {
      const res = await api.getKnowledgeFileDetail(source);
      setExpandedChunks(res.documents || []);
    } catch (e) {
      console.error('获取文件详情失败:', source, e);
      setExpandedChunks([]);
    } finally {
      setExpandedLoading(false);
    }
  };

  const handleDeleteFile = async (source: string) => {
    if (!window.confirm(`确定要删除文件 "${source}" 的所有文档块吗？`)) return;
    setDeletingFile(source);
    try {
      await api.deleteKnowledgeFile(source);
      if (expandedFile === source) {
        setExpandedFile(null);
        setExpandedChunks([]);
      }
      fetchFiles();
      fetchStatus();
    } catch {
      // silent
    } finally {
      setDeletingFile(null);
    }
  };

  useEffect(() => {
    fetchStatus();
    fetchDocuments();
    fetchFiles();
  }, [fetchStatus, fetchDocuments, fetchFiles]);

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
      const metaObj: Record<string, string> = {};
      for (const entry of metaEntries) {
        if (entry.key.trim()) {
          metaObj[entry.key.trim()] = entry.value;
        }
      }
      const res = await api.uploadDocument(file, metaObj);
      setUploadResult(`上传成功: ${res.file_name} (${res.chunk_count} 个分块)`);
      setMetaEntries([]);
      fetchStatus();
      fetchDocuments();
    } catch (e) {
      setUploadResult(`上传失败: ${(e as Error).message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    setDeletingId(docId);
    try {
      await api.deleteKnowledgeDocument(docId);
      setDocuments((prev) => prev.filter((d) => d.id !== docId));
      setDocTotal((prev) => prev - 1);
      fetchStatus();
    } catch {
      // silent
    } finally {
      setDeletingId(null);
    }
  };

  const handleClear = async () => {
    if (!window.confirm('确定要清空整个知识库吗？此操作不可恢复。')) return;
    setClearing(true);
    try {
      await api.clearKnowledgeBase();
      setDocuments([]);
      setDocTotal(0);
      setFiles([]);
      setFilesTotal(0);
      setExpandedFile(null);
      setExpandedChunks([]);
      fetchStatus();
    } catch {
      // silent
    } finally {
      setClearing(false);
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
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
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

        {/* Metadata Editor */}
        <div className="mt-3">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-[var(--text-secondary)]">元数据（可选）</span>
            <button
              onClick={() => setMetaEntries((prev) => [...prev, { key: '', value: '' }])}
              className="btn-ghost text-[10px] flex items-center gap-1 !py-0.5 !px-1.5"
            >
              <Plus size={10} />
              添加字段
            </button>
          </div>
          {metaEntries.length > 0 && (
            <div className="space-y-1.5">
              {metaEntries.map((entry, i) => (
                <div key={i} className="flex items-center gap-1.5">
                  <input
                    value={entry.key}
                    onChange={(e) =>
                      setMetaEntries((prev) =>
                        prev.map((m, j) => (j === i ? { ...m, key: e.target.value } : m))
                      )
                    }
                    placeholder="字段名"
                    className="input-field text-xs flex-1 min-w-0"
                  />
                  <input
                    value={entry.value}
                    onChange={(e) =>
                      setMetaEntries((prev) =>
                        prev.map((m, j) => (j === i ? { ...m, value: e.target.value } : m))
                      )
                    }
                    placeholder="值"
                    className="input-field text-xs flex-1 min-w-0"
                  />
                  <button
                    onClick={() => setMetaEntries((prev) => prev.filter((_, j) => j !== i))}
                    className="p-1 rounded hover:bg-red-500/10 text-[var(--text-muted)] hover:text-red-400 shrink-0"
                  >
                    <Trash2 size={11} />
                  </button>
                </div>
              ))}
            </div>
          )}
          {metaEntries.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {metaEntries
                .filter((m) => m.key.trim())
                .map((m, i) => (
                  <span key={i} className="text-[10px] text-[var(--cyan)] bg-[var(--cyan)]/10 px-1.5 py-0.5 rounded">
                    {m.key.trim()}: {m.value || '(空)'}
                  </span>
                ))}
            </div>
          )}
        </div>
        {uploadResult && (
          <div className={`flex items-center gap-2 mt-3 text-xs ${uploadResult.includes('失败') ? 'text-red-400' : 'text-[var(--cyan)]'}`}>
            {uploadResult.includes('失败') ? <Trash2 size={12} /> : <CheckCircle2 size={12} />}
            {uploadResult}
          </div>
        )}
      </div>

      {/* File Management */}
      <div className="border border-[var(--border-color)] rounded-xl p-4 bg-[var(--bg-secondary)]/20">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-medium text-[var(--text-primary)] flex items-center gap-2">
            <Database size={16} className="text-[var(--accent-hover)]" />
            文件管理
            {filesTotal > 0 && (
              <span className="text-[10px] text-[var(--text-muted)] font-normal">共 {filesTotal} 个文件</span>
            )}
          </h3>
          <div className="flex items-center gap-2">
            <button onClick={fetchFiles} className="btn-ghost text-xs flex items-center gap-1">
              <RefreshCw size={12} className={filesLoading ? 'animate-spin' : ''} />
              刷新
            </button>
            {filesTotal > 0 && (
              <button onClick={handleClear} disabled={clearing} className="btn-ghost text-xs flex items-center gap-1 text-red-400 hover:text-red-300">
                {clearing ? <Loader2 size={12} className="animate-spin" /> : <Trash2 size={12} />}
                清空全部
              </button>
            )}
          </div>
        </div>
        {filesLoading ? (
          <div className="flex items-center justify-center py-6">
            <Loader2 size={18} className="animate-spin text-[var(--text-muted)]" />
          </div>
        ) : filesTotal === 0 ? (
          <p className="text-xs text-[var(--text-muted)] py-4 text-center">知识库为空，上传文档后即可查看</p>
        ) : (
          <div className="space-y-2">
            {files.map((f) => (
              <div key={f.source} className="border border-[var(--border-color)] rounded-xl overflow-hidden">
                <div className="flex items-center justify-between px-4 py-3 bg-[var(--bg-secondary)]/30 hover:bg-[var(--bg-secondary)]/50 transition-colors">
                  <div className="flex items-center gap-3 min-w-0 flex-1" onClick={() => expandFile(f.source)}>
                    <button
                      className={`p-1 rounded transition-transform ${expandedFile === f.source ? 'rotate-90' : ''}`}
                    >
                      <ChevronRight size={14} className="text-[var(--text-muted)]" />
                    </button>
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-[var(--text-primary)] truncate">{f.source}</p>
                      <p className="text-xs text-[var(--text-muted)]">{f.chunk_count} 个文档块</p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDeleteFile(f.source)}
                    disabled={deletingFile === f.source}
                    className="shrink-0 p-1.5 rounded-lg text-[var(--text-muted)] hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    {deletingFile === f.source ? (
                      <Loader2 size={14} className="animate-spin" />
                    ) : (
                      <Trash2 size={14} />
                    )}
                  </button>
                </div>

                {expandedFile === f.source && (
                  <div className="border-t border-[var(--border-color)] animate-fade-in">
                    {expandedLoading ? (
                      <div className="flex items-center justify-center py-4">
                        <Loader2 size={16} className="animate-spin text-[var(--text-muted)]" />
                      </div>
                    ) : expandedChunks.length === 0 ? (
                      <div className="px-4 py-6 text-center text-xs text-[var(--text-muted)]">
                        该文件没有可显示的文档块内容
                      </div>
                    ) : (
                      <div className="divide-y divide-[var(--border-color)]">
                        {expandedChunks.map((chunk) => (
                          <div key={chunk.id} className="px-4 py-3 group hover:bg-[var(--bg-secondary)]/20">
                            <div className="flex items-start justify-between gap-2">
                              <div className="flex-1 min-w-0">
                                <p className="text-xs text-[var(--text-secondary)] leading-relaxed line-clamp-3 break-words">
                                  {chunk.content || '(空)'}
                                </p>
                                <div className="flex items-center gap-2 mt-1.5">
                                  {chunk.metadata?.page && (
                                    <span className="text-[10px] text-[var(--text-muted)]">第 {String(chunk.metadata.page)} 页</span>
                                  )}
                                  <span className="text-[10px] text-[var(--text-muted)] font-mono">ID: {chunk.id.slice(0, 8)}...</span>
                                </div>
                              </div>
                              <button
                                onClick={() => {
                                  if (window.confirm(`确定要删除此文档块吗？`)) {
                                    api.deleteKnowledgeDocument(chunk.id).then(() => {
                                      setExpandedChunks((prev) => prev.filter((d) => d.id !== chunk.id));
                                      fetchFiles();
                                      fetchStatus();
                                    });
                                  }
                                }}
                                className="shrink-0 p-1 rounded opacity-0 group-hover:opacity-100 hover:bg-red-500/10 text-red-400 hover:text-red-300 transition-all"
                              >
                                <Trash2 size={11} />
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
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