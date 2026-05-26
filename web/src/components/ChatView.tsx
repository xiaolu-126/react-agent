import { useState, useRef, useEffect, useCallback } from 'react';
import { Send, Sparkles, User, Bot, Loader2, PanelRightClose, PanelRightOpen, Square } from 'lucide-react';
import { useStore } from '../store';
import { api } from '../api';
import type { Message } from '../types';
import StatusBar from './StatusBar';

function generateId() {
  return `msg-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;
}

function varToLabel(v: string): string {
  const labels: Record<string, string> = {
    streamer_name: '主播名称',
    streamer_tags: '主播标签',
    streamer_content: '主播内容',
    user_preferences: '用户偏好',
    context: '上下文',
    question: '问题',
    content: '内容',
    name: '名称',
    tags: '标签',
    preference: '偏好',
    follower_count: '粉丝数',
    streaming_schedule: '直播时间',
    interaction_style: '互动特点',
  };
  return labels[v] || v.replace(/_/g, ' ');
}

function varToPlaceholder(v: string): string {
  const placeholders: Record<string, string> = {
    streamer_name: '例如: 岑先生',
    streamer_tags: '游戏主播、技术分享',
    streamer_content: '专注于游戏攻略和技术教学',
    user_preferences: '喜欢轻松幽默风格的直播',
    name: '输入名称',
    content: '输入内容',
  };
  return placeholders[v] || `请输入${varToLabel(v)}`;
}

export default function ChatView() {
  const conversations = useStore(s => s.conversations);
  const activeConversationId = useStore(s => s.activeConversationId);
  const currentSystemPrompt = useStore(s => s.currentSystemPrompt);
  const { addMessage, clearActiveConversation, streamerPanelOpen, setStreamerPanel } = useStore();
  const messages = conversations.find(c => c.id === activeConversationId)?.messages ?? [];
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [streamingText, setStreamingText] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const abortRef = useRef<AbortController | null>(null);

  // Dynamic template variables form
  const [templateInfo, setTemplateInfo] = useState<{
    name: string;
    description: string;
    input_variables: string[];
    template_content: string;
  } | null>(null);
  const [templateLoading, setTemplateLoading] = useState(false);
  const [varValues, setVarValues] = useState<Record<string, string>>({});
  const [genLoading, setGenLoading] = useState(false);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingText, scrollToBottom]);

  // Fetch template info when panel opens or prompt changes
  useEffect(() => {
    if (!streamerPanelOpen) return;
    setTemplateLoading(true);
    api.getPromptTemplate(currentSystemPrompt)
      .then((info) => {
        setTemplateInfo(info);
        const init: Record<string, string> = {};
        for (const v of info.input_variables) {
          init[v] = '';
        }
        setVarValues(init);
      })
      .catch(() => setTemplateInfo(null))
      .finally(() => setTemplateLoading(false));
  }, [streamerPanelOpen, currentSystemPrompt]);

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

  const generateFromTemplate = async () => {
    if (!templateInfo || genLoading) return;

    const requiredVars = templateInfo.input_variables;
    const filled = requiredVars.filter((v) => !varValues[v]?.trim());
    if (filled.length > 0 && filled.length === requiredVars.length) return;

    setGenLoading(true);

    const userMsg: Message = {
      id: generateId(),
      role: 'user',
      content: `使用 ${templateInfo.name} 模板生成`,
      timestamp: Date.now(),
    };
    addMessage(userMsg);
    setIsLoading(true);
    setStreamingText('');

    abortRef.current = new AbortController();

    try {
      const variables: Record<string, string> = {};
      for (const v of requiredVars) {
        if (varValues[v]?.trim()) {
          variables[v] = varValues[v].trim();
        }
      }

      const res = await api.generateFromTemplateStream({
        template_name: templateInfo.name,
        variables,
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
      if ((e as Error).name === 'AbortError') return;
      addMessage({
        id: generateId(),
        role: 'assistant',
        content: `生成失败: ${(e as Error).message}`,
        timestamp: Date.now(),
      });
    } finally {
      setIsLoading(false);
      setGenLoading(false);
      abortRef.current = null;
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
              <div key={msg.id} className={`animate-fade-in flex gap-3 ${msg.role === 'user' ? 'ml-auto flex-row-reverse' : 'mr-auto'} max-w-[80%] w-fit`}>
                <div
                  className={`shrink-0 w-8 h-8 rounded-lg flex items-center justify-center ${
                    msg.role === 'user'
                      ? 'bg-[var(--accent)]/20 text-[var(--accent-hover)]'
                      : 'bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 text-[var(--cyan)]'
                  }`}
                >
                  {msg.role === 'user' ? <User size={16} /> : <Bot size={16} />}
                </div>
                <div className="max-w-[70%]">
                  <div className={`text-xs mb-1 ${msg.role === 'user' ? 'text-right text-[var(--accent-hover)]' : 'text-[var(--text-muted)]'}`}>
                    {msg.role === 'user' ? '你' : 'AI 助手'}
                  </div>
                  <div className={`text-sm leading-relaxed whitespace-pre-wrap break-words ${
                    msg.role === 'user' 
                      ? 'bg-[var(--accent)]/10 text-[var(--text-primary)] rounded-lg px-3 py-2 rounded-tr-sm' 
                      : 'bg-[var(--bg-secondary)]/50 text-[var(--text-primary)] rounded-lg px-3 py-2 rounded-tl-sm'
                  }`}>
                    {msg.content}
                  </div>
                </div>
              </div>
            ))}

            {hasStreaming && (
              <div className="animate-fade-in flex gap-3 justify-start max-w-4xl mx-auto w-full">
                <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 flex items-center justify-center">
                  <Bot size={16} className="text-[var(--cyan)]" />
                </div>
                <div className="max-w-[70%]">
                  <div className="text-xs text-[var(--text-muted)] mb-1">AI 助手</div>
                  <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap break-words bg-[var(--bg-secondary)]/50 rounded-lg px-3 py-2 rounded-tl-sm">
                    {streamingText}
                  </div>
                </div>
              </div>
            )}

            {isLoading && !streamingText && (
              <div className="flex gap-3 justify-start max-w-4xl mx-auto w-full animate-fade-in">
                <div className="shrink-0 w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--cyan)]/20 to-[var(--accent)]/20 flex items-center justify-center">
                  <Bot size={16} className="text-[var(--cyan)]" />
                </div>
                <div className="bg-[var(--bg-secondary)]/50 rounded-lg px-3 py-2 rounded-tl-sm">
                  <div className="flex items-center gap-1.5">
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                    <span className="typing-dot" />
                  </div>
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
                    onClick={clearActiveConversation}
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
        <div className={`${streamerPanelOpen ? 'w-80' : 'w-0'} overflow-hidden border-l border-[var(--border-color)] bg-[var(--bg-secondary)]/30 shrink-0 transition-all duration-300 ease-in-out`}>
          <div className="p-4 min-w-80">
            <div className="flex items-center gap-2 mb-4">
              <Sparkles size={18} className="text-[var(--accent-hover)]" />
              <h3 className="text-sm font-semibold text-[var(--text-primary)]">
                {templateInfo ? templateInfo.name : '模板生成'}
              </h3>
            </div>

            {templateLoading ? (
              <div className="flex items-center justify-center py-6">
                <Loader2 size={18} className="animate-spin text-[var(--text-muted)]" />
              </div>
            ) : templateInfo && templateInfo.input_variables.length > 0 ? (
              <div className="space-y-3">
                {templateInfo.input_variables.map((v) => (
                  <div key={v}>
                    <label className="block text-xs text-[var(--text-secondary)] mb-1.5">{varToLabel(v)} *</label>
                    {v.includes('content') || v.includes('preference') || v.includes('question') || v.includes('context') ? (
                      <textarea
                        value={varValues[v] || ''}
                        onChange={(e) => setVarValues((prev) => ({ ...prev, [v]: e.target.value }))}
                        placeholder={varToPlaceholder(v)}
                        rows={2}
                        className="input-field text-sm resize-none"
                      />
                    ) : (
                      <input
                        value={varValues[v] || ''}
                        onChange={(e) => setVarValues((prev) => ({ ...prev, [v]: e.target.value }))}
                        placeholder={varToPlaceholder(v)}
                        className="input-field text-sm"
                      />
                    )}
                  </div>
                ))}
                <div className="text-xs text-[var(--text-muted)] mt-1 break-words leading-relaxed">
                  {templateInfo.description}
                </div>
                <button
                  onClick={generateFromTemplate}
                  disabled={genLoading}
                  className="btn-primary w-full flex items-center justify-center gap-2 mt-2"
                >
                  {genLoading ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Sparkles size={16} />
                  )}
                  <span>{genLoading ? '生成中...' : '生成'}</span>
                </button>
              </div>
            ) : (
              <div className="text-xs text-[var(--text-muted)] py-4 text-center">
                {templateInfo ? '当前提示词无变量输入' : '请在设置中选择一个提示词'}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}