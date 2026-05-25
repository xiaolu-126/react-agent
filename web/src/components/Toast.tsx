import { useEffect } from 'react';
import { X, CheckCircle, AlertCircle } from 'lucide-react';
import { useStore } from '../store';

export default function Toast() {
  const { error, setError } = useStore();

  useEffect(() => {
    if (error) {
      const timer = setTimeout(() => setError(null), 4000);
      return () => clearTimeout(timer);
    }
  }, [error, setError]);

  if (!error) return null;

  const isSuccess = error.includes('✓');
  const displayMsg = error.replace('✓ ', '');

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-in">
      <div className="glass-card rounded-xl px-4 py-3 flex items-center gap-3 shadow-2xl border-[var(--border-color)]">
        {isSuccess ? (
          <CheckCircle size={18} className="text-[var(--cyan)] shrink-0" />
        ) : (
          <AlertCircle size={18} className="text-[var(--amber)] shrink-0" />
        )}
        <span className="text-sm text-[var(--text-primary)]">{displayMsg}</span>
        <button onClick={() => setError(null)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
          <X size={16} />
        </button>
      </div>
    </div>
  );
}