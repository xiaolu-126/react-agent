import { useState, useRef, useEffect } from 'react';
import {
  MessageSquare,
  Sparkles,
  Plus,
  Trash2,
  Check,
  X,
  Pencil,
  Settings,
} from 'lucide-react';
import { useStore } from '../store';
import type { Conversation } from '../types';

function ConversationItem({ conv }: { conv: Conversation }) {
  const { activeConversationId, switchConversation, deleteConversation, renameConversation } = useStore();
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(conv.name);
  const inputRef = useRef<HTMLInputElement>(null);
  const isActive = conv.id === activeConversationId;

  useEffect(() => {
    if (editing && inputRef.current) {
      inputRef.current.focus();
      inputRef.current.select();
    }
  }, [editing]);

  const saveRename = () => {
    const name = editName.trim() || '新对话';
    renameConversation(conv.id, name);
    setEditing(false);
  };

  const cancelRename = () => {
    setEditName(conv.name);
    setEditing(false);
  };

  return (
    <div
      className={`group flex items-center gap-2 px-3 py-2 rounded-lg cursor-pointer transition-all duration-200 text-sm ${
        isActive
          ? 'bg-[var(--accent)]/10 text-[var(--accent-hover)] font-medium'
          : 'text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]'
      }`}
      onClick={() => switchConversation(conv.id)}
    >
      <MessageSquare size={15} className="shrink-0" />

      {editing ? (
        <div className="flex-1 flex items-center gap-1 min-w-0" onClick={(e) => e.stopPropagation()}>
          <input
            ref={inputRef}
            value={editName}
            onChange={(e) => setEditName(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') saveRename();
              if (e.key === 'Escape') cancelRename();
            }}
            className="flex-1 bg-[var(--bg-primary)] border border-[var(--border-color)] rounded px-1.5 py-0.5 text-xs text-[var(--text-primary)] outline-none min-w-0"
          />
          <button onClick={saveRename} className="text-[var(--cyan)] hover:text-[var(--cyan)] shrink-0">
            <Check size={13} />
          </button>
          <button onClick={cancelRename} className="text-[var(--text-muted)] hover:text-[var(--text-primary)] shrink-0">
            <X size={13} />
          </button>
        </div>
      ) : (
        <>
          <span className="flex-1 truncate text-xs">{conv.name}</span>
          <div className="hidden group-hover:flex items-center gap-0.5 shrink-0">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setEditName(conv.name);
                setEditing(true);
              }}
              className="p-0.5 rounded hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--text-primary)]"
            >
              <Pencil size={12} />
            </button>
            <button
              onClick={(e) => {
                e.stopPropagation();
                deleteConversation(conv.id);
              }}
              className="p-0.5 rounded hover:bg-white/10 text-[var(--text-muted)] hover:text-red-400"
            >
              <Trash2 size={12} />
            </button>
          </div>
        </>
      )}
    </div>
  );
}

export default function Sidebar() {
  const { conversations, createConversation, setSettingsPanel } = useStore();

  return (
    <aside className="flex flex-col h-full bg-[#0b1120] border-r border-[var(--border-color)] w-[220px] shrink-0">
      <div className="flex items-center gap-2.5 px-5 py-5 border-b border-[var(--border-color)]">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent)] to-[var(--cyan)] flex items-center justify-center">
          <Sparkles size={16} className="text-white" />
        </div>
        <div>
          <h1 className="text-sm font-semibold text-[var(--text-primary)]">AI Agent</h1>
          <p className="text-[10px] text-[var(--text-muted)]">智能助手</p>
        </div>
      </div>

      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex items-center justify-between px-3 pt-3 pb-1">
          <span className="text-[10px] font-medium text-[var(--text-muted)] uppercase tracking-wider">对话列表</span>
          <button
            onClick={createConversation}
            className="p-1 rounded hover:bg-white/10 text-[var(--text-muted)] hover:text-[var(--accent-hover)] transition-colors"
            title="新建对话"
          >
            <Plus size={14} />
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-2 py-1 space-y-0.5">
          {conversations.map((conv) => (
            <ConversationItem key={conv.id} conv={conv} />
          ))}
        </div>
      </div>

      <div className="px-3 py-3 border-t border-[var(--border-color)]">
        <button
          onClick={() => setSettingsPanel(true)}
          className="flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm w-full transition-all duration-200 text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]"
        >
          <Settings size={18} />
          <span>设置</span>
        </button>
      </div>
    </aside>
  );
}