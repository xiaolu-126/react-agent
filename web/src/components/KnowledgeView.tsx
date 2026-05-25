import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Database,
  Upload,
  Search,
  FileText,
  Loader2,
  RefreshCw,
  CheckCircle2,
  Trash2,
} from 'lucide-react';
import { api } from '../api';
import type { KnowledgeStatus, KnowledgeSearchResult } from '../types';

export default function KnowledgeView() {
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
    <div className="flex flex-col h-full">
      <div className="border-b border-[var(--border-color)] px-5 py-3">
        <h2 className="text-base font-semibold text-[var(--text-primary)]">知识库管理</h2>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-5">
        {/* Status */}
        <div className="glass-card rounded-xl p-4">
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
        <div className="glass-card rounded-xl p-4">
          <h3 className="text-sm font-medium text-[var(--text-primary)] flex items-center gap-2 mb-3">
            <Upload size={16} className="text-[var(--accent-hover)]" />
            上传文档
          </h3>

          <div
            className={`border-2 border-dashed rounded-xl p-8 text-center transition-all cursor-pointer ${
              dragOver
                ? 'border-[var(--accent)] bg-[var(--accent)]/5'
                : 'border-[var(--border-color)] hover:border-[var(--text-muted)]'
            }`}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={handleFileDrop}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.md,.yaml,.yml,.json,.csv"
              className="hidden"
              onChange={handleFileSelect}
            />
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
        <div className="glass-card rounded-xl p-4">
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
            <div className="flex items-center justify-center py-6">
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
    </div>
  );
}