import { useStore } from '../store';
import { Cpu, FileText, MessageSquare } from 'lucide-react';

export default function StatusBar() {
  const { currentModel, currentSystemPrompt, messages } = useStore();

  return (
    <div className="flex items-center gap-4 px-5 py-2.5 border-b border-[var(--border-color)] bg-[var(--bg-secondary)]/40">
      <div className="flex items-center gap-1.5">
        <Cpu size={13} className="text-[var(--accent-hover)]" />
        <span className="text-xs text-[var(--text-secondary)]">模型:</span>
        <span className="tag tag-blue text-[11px]">{currentModel}</span>
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