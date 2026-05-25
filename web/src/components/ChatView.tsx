import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Sparkles, User, Bot, Loader2, PanelRightClose, PanelRightOpen, Mic, Square } from 'lucide-react';
import { useStore } from '../store';
import { api } from '../api';
import type { Message } from '../types';
import StatusBar from './StatusBar';

function generateId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

export default function ChatView() {
  const { messages, addMessage, clearMessages, streamerPanelOpen, setStreamerPanel } = useStore();
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Streamer form
  const [sName, setSName] = useState('');
  const [sTags, setSTags] = useState('');
  const [sContent, setSContent] = useState('');
  const [sPref, setSPref] = useState('');
  const [genLoading, setGenLoading] = useState(false);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, scrollToBottom]);

  const sendMessage = useCallback(async () => {
    const text = input.trim();
    if (!text || isLoading) return;
    setInput('');

    const userMsg: Message = { id: generateId(), role: 'user', content: text, timestamp: Date.now() };
    addMessage(userMsg);
    setIsLoading(true);
    setStreamingText('');

    abortRef.current = new AbortController();

    try {
      const res = await api.chatStream({ message: text });
      if (!res.ok) throw new Error('Stream request failed');
      const reader = res.body?.getReader();
      if (!reader) throw new Error('No reader');

      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter((l) => l.startsWith('data: '));
        for (const line of lines) {
          const data = line.slice(6);
          if (data === '[DONE]') break;
          fullText += data;
          setStreamingText(fullText);
        }
      }

      setStreamingText('');
      addMessage({ id: generateId(), role: 'assistant', content: fullText, timestamp: Date.now() });
    } catch (e) {
      if ((e as Error).name === 'AbortError') return;
      addMessage({ id: generateId(), role: 'assistant', content: `抱歉，请求出错: ${(e as Error).message}`, timestamp: Date.now() });
    } finally {
      setIsLoading(false);
      abortRef.current = null;
    }
  }, [input, isLoading, addMessage]);

  const stopGeneration = () => {
    abortRef.current?.abort();
    if (streamingText) {
      addMessage({ id: generateId(), role: 'assistant', content: streamingText, timestamp: Date.now() });
      setStreamingText('');
    }
    setIsLoading(false);
  };

  const generateRecommendation = async () => {
    if (!sName.trim() || genLoading) return;
    setGenLoading(true);

    const userMsg: Message = {
      id: generateId(),
      role: 'user',
      content: `请生成主播「${sName}」的推荐理由`,
      timestamp: Date.now(),
    };
    addMessage(userMsg);
    setIsLoading(true);
    setStreamingText('');

    try {
      const res = await api.generateStream({
        streamer_name: sName,
        tags: sTags,
        content: sContent,
        preferences: sPref,
      });
      if (!res.ok) throw new Error('Generate stream failed');
      const reader = res.body?.getReader();
      if (!reader) throw new Error('No reader');

      const decoder = new TextDecoder();
      let fullText = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n').filter((l) => l.startsWith('data: '));
        for (const line of lines) {
          const data = line.slice(6);
          if (data === '[DONE]') break;
          fullText += data;
          setStreamingText(fullText);
        }
      }

      setStreamingText('');
      addMessage({ id: generateId(), role: 'assistant', content: fullText, timestamp: Date.now() });
    } catch (e) {
      addMessage({
        id: generateId(),
        role: 'assistant',
        content: `生成推荐失败: ${(e as Error).message}`,
        timestamp: Date.now(),
      });
    } finally {
      setIsLoading(false);
      setGenLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const hasStreaming = isLoading && streamingText;

  return (
    <div className="flex flex-col h-full">
      <StatusBar />

      <div className="flex flex-1 overflow-hidden">
        {/* Messages */}
        <div className="flex-1 flex flex-col min-w-0">
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-4">
            {messages.length === 0 && !hasStreaming && (
              <div className="flex flex-col items-center justify-center h-full text-center">
                <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-[var(--accent)]/20 to-[var(--cyan)]/20 flex items-center justify-center mb-4">
                  <Sparkles size={32} className="text-[var(--accent-hover)]" />
                </div>
                <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-2">你好！有什么可以帮你的？</h2>
                <p className="text-sm text-[var(--text-muted)] max-w-md">
                  我可以帮你生成主播推荐理由、回答问题和搜索信息
                </p>
              </div>
            )}

            {messages.map((msg) => (
              <div key={msg.id} className="animate-fade-in flex gap-3 max-w-3xl mx-auto">
                <div
                  className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                    msg.role === 'user'
                      ? 'bg-[var(--accent)]/20 text-[var(--accent-hover)]'
                      : 'bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 text-[var(--cyan)]'
                  }`}
                >
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[var(--text-muted)] mb-1">
                    {msg.role === 'user' ? '你' : 'AI 助手'}
                  </div>
                  <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap break-words">
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}

            {hasStreaming && (
              <div className="animate-fade-in flex gap-3 max-w-3xl mx-auto">
                <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 flex items-center justify-center">
                  <Bot size={16} className="text-[var(--cyan)]" />
                </div>
                <div className="flex-1 min-w-0">
                  <div className="text-xs text-[var(--text-muted)] mb-1">AI 助手</div>
                  <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap break-words">
                    {streamingText}
                  </div>
                </div>
              </div>
            )}

            {isLoading && !streamingText && (
              <div className="flex gap-3 max-w-3xl mx-auto animate-fade-in">
                <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 flex items-center justify-center">
                  <Bot size={16} className="text-[var(--cyan)]" />
                </div>
                <div className="flex items-center gap-1.5 py-2">
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                  <span className="typing-dot" />
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-[var(--border-color)] px-4 py-3">
            <div className="max-w-3xl mx-auto">
              <div className="flex gap-2 items-end">
                <div className="flex-1 relative">
                  <textarea
                    ref={inputRef}
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="输入消息，Enter 发送，Shift+Enter 换行..."
                    rows={1}
                    className="input-field resize-none pr-10 py-3 text-sm min-h-[44px] max-h-[120px]"
                    onInput={(e) => {
                      const el = e.currentTarget;
                      el.style.height = 'auto';
                      el.style.height = `${Math.min(el.scrollHeight, 120)}px`;
                    }}
                  />
                  <button
                    onClick={clearMessages}
                    className="absolute right-2.5 bottom-2.5 text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
                    title="清空对话"
                  >
                    <Loader2 size={14} className="rotate-0" />
                  </button>
                </div>
                {isLoading ? (
                  <button
                    onClick={stopGeneration}
                    className="btn-primary flex items-center gap-2 shrink-0 !bg-red-500/20 !text-red-400 hover:!bg-red-500/30"
                  >
                    <Square size={16} />
                    <span className="text-sm">停止</span>
                  </button>
                ) : (
                  <>
                    <button
                      onClick={() => setStreamerPanel(!streamerPanelOpen)}
                      className="btn-ghost flex items-center gap-2 shrink-0"
                      title="主播推荐面板"
                    >
                      {streamerPanelOpen ? <PanelRightClose size={18} /> : <PanelRightOpen size={18} />}
                    </button>
                    <button
                      onClick={sendMessage}
                      disabled={!input.trim()}
                      className="btn-primary flex items-center gap-2 shrink-0"
                    >
                      <Send size={16} />
                      <span className="text-sm hidden sm:inline">发送</span>
                    </button>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Streamer Panel */}
        {streamerPanelOpen && (
          <div className="w-80 border-l border-[var(--border-color)] bg-[var(--bg-secondary)]/30 overflow-y-auto animate-slide-in shrink-0">
            <div className="p-4">
              <div className="flex items-center gap-2 mb-4">
                <Sparkles size={18} className="text-[var(--accent-hover)]" />
                <h3 className="text-sm font-semibold text-[var(--text-primary)]">生成推荐理由</h3>
              </div>

              <div className="space-y-3">
                <div>
                  <label className="block text-xs text-[var(--text-secondary)] mb-1.5">主播名称 *</label>
                  <input
                    value={sName}
                    onChange={(e) => setSName(e.target.value)}
                    placeholder="例如: 岑先生"
                    className="input-field text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[var(--text-secondary)] mb-1.5">主播标签</label>
                  <input
                    value={sTags}
                    onChange={(e) => setSTags(e.target.value)}
                    placeholder="游戏主播、技术分享"
                    className="input-field text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[var(--text-secondary)] mb-1.5">主播内容</label>
                  <textarea
                    value={sContent}
                    onChange={(e) => setSContent(e.target.value)}
                    placeholder="专注于游戏攻略和技术教学"
                    rows={2}
                    className="input-field text-sm resize-none"
                  />
                </div>
                <div>
                  <label className="block text-xs text-[var(--text-secondary)] mb-1.5">你的偏好</label>
                  <textarea
                    value={sPref}
                    onChange={(e) => setSPref(e.target.value)}
                    placeholder="喜欢技术型主播"
                    rows={2}
                    className="input-field text-sm resize-none"
                  />
                </div>
                <button
                  onClick={generateRecommendation}
                  disabled={!sName.trim() || genLoading}
                  className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
                >
                  {genLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Sparkles size={16} />
                  )}
                  <span>{genLoading ? '生成中...' : '生成推荐理由'}</span>
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}