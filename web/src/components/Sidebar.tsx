import { NavLink } from 'react-router-dom';
import {
  MessageSquare,
  Settings,
  Database,
  Sparkles,
} from 'lucide-react';

const navItems = [
  { to: '/', icon: MessageSquare, label: '对话' },
  { to: '/settings', icon: Settings, label: '管理' },
  { to: '/knowledge', icon: Database, label: '知识库' },
];

export default function Sidebar() {
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

      <nav className="flex-1 px-3 py-4 space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/'}
            className={({ isActive }) =>
              `flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-all duration-200 ${
                isActive
                  ? 'bg-[var(--accent)]/10 text-[var(--accent-hover)] font-medium'
                  : 'text-[var(--text-secondary)] hover:bg-white/5 hover:text-[var(--text-primary)]'
              }`
            }
          >
            <item.icon size={18} />
            {item.label}
          </NavLink>
        ))}
      </nav>

      <div className="px-4 py-3 border-t border-[var(--border-color)]">
        <p className="text-[10px] text-[var(--text-muted)]">v1.0.0 • LangGraph</p>
      </div>
    </aside>
  );
}