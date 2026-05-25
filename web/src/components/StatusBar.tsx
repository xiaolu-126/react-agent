import { useState, useRef, useEffect } from 'react';
import { useStore } from '../store';
import { Cpu, FileText, MessageSquare, Check } from 'lucide-react';

export default function StatusBar() {
  const conversations = useStore(s => s.conversations);
  const activeConversationId = useStore(s => s.activeConversationId);
  const { currentModel, currentSystemPrompt, models, switchModel, fetchModels } = useStore();
  const messages = conversations.find(c => c.id === activeConversationId)?.messages ?? [];
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (models.length === 0) {
      fetchModels();
    }
  }, [models.length, fetchModels]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setDropdownOpen(false);
      }
    };
    if (dropdownOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [dropdownOpen]);

  const handleSelect = async (name: string) => {
    await switchModel(name);
    setDropdownOpen(false);
  };

  return (
    <div className="flex items-center gap-4 px-5 py-2.5 border-b border-[var(--border-color)] bg-[var(--bg-secondary)]/40">
      <div className="flex items-center gap-1.5 relative" ref={dropdownRef}>
        <Cpu size={13} className="text-[var(--accent-hover)]" />
        <span className="text-xs text-[var(--text-secondary)]">模型:</span>
        <button
          onClick={() => setDropdownOpen(!dropdownOpen)}
          className="tag tag-blue text-[11px] cursor-pointer hover:brightness-125 transition-all"
        >
          {currentModel}
        </button>

        {dropdownOpen && (
          <div className="absolute top-full left-0 mt-1.5 w-44 bg-[var(--bg-secondary)] border border-[var(--border-color)] rounded-xl shadow-2xl z-50 py-1 animate-fade-in">
            {models.map((model) => (
              <button
                key={model.name}
                onClick={() => handleSelect(model.name)}
                className={`flex items-center justify-between w-full px-3 py-2 text-xs text-left transition-colors ${
                  model.is_current
                    ? 'text-[var(--accent-hover)] bg-[var(--accent)]/5'
                    : 'text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]'
                }`}
              >
                <span>{model.display_name}</span>
                {model.is_current && <Check size={12} className="text-[var(--accent-hover)] shrink-0" />}
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="flex items-center gap-1.5">
        <FileText size={13} className="text-[var(--cyan)]" />
        <span className="text-xs text-[var(--text-secondary)]">提示词:</span>
        <span className="tag tag-cyan text-[11px]">{currentSystemPrompt}</span>
      </div>
      <div className="flex items-center gap-1.5">
        <MessageSquare size={13} className="text-[var(--text-muted)]" />
        <span className="text-xs text-[var(--text-secondary)]">对话:</span>
        <span className="text-xs text-[var(--text-muted)]">{Math.ceil(messages.length / 2)} 轮</span>
      </div>
    </div>
  );
}