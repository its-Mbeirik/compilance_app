import React, { useState, useRef, useEffect } from 'react';
import clsx from 'clsx';
import { ComplianceReport } from '@/types';

export interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  report?: ComplianceReport;
}

interface ChatInterfaceProps {
  messages: Message[];
  onSendMessage: (content: string, file?: File) => Promise<void>;
  onFileUpload: (file: File) => Promise<void>;
  loading?: boolean;
  error?: string | null;
}

export const ChatInterface: React.FC<ChatInterfaceProps> = ({
  messages,
  onSendMessage,
  onFileUpload,
  loading = false,
  error = null,
}) => {

  const [input, setInput] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim() && !selectedFile) return;

    const currentInput = input;
    const currentFile = selectedFile;
    
    setInput('');
    setSelectedFile(null);

    try {
      if (currentFile) {
        await onFileUpload(currentFile);
      } else {
        await onSendMessage(currentInput);
      }
    } catch (err) {
      console.error('Error:', err);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div className="flex flex-col h-full bg-gradient-to-br from-gray-900 via-gray-900 to-slate-900">
      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-4 md:p-6 space-y-6 scroll-smooth">
        {messages.map((message) => (
          <div
            key={message.id}
            className={clsx('flex', message.type === 'user' ? 'justify-end' : 'justify-start')}
          >
            <div
              className={clsx(
                'max-w-[85%] sm:max-w-xl px-5 py-4 rounded-2xl shadow-sm backdrop-blur-sm transition-all',
                message.type === 'user'
                  ? 'bg-gradient-to-br from-indigo-500 to-indigo-600 text-white rounded-br-sm shadow-indigo-500/20'
                  : 'bg-white/5 border border-white/10 text-gray-100 rounded-bl-sm shadow-black/10'
              )}
            >
              <div className="prose prose-invert max-w-none text-sm leading-relaxed prose-p:my-1 prose-strong:text-indigo-300">
                <p className="whitespace-pre-wrap">{message.content}</p>
              </div>

              {message.report && (
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="bg-black/20 rounded-xl p-3 text-xs space-y-2 font-medium">
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Status</span>
                      <span className={clsx(
                        'px-2 py-1 rounded-full text-[10px] uppercase tracking-wider',
                        message.report.overall_status === 'compliant' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-rose-500/20 text-rose-400'
                      )}>
                        {message.report.overall_status.replace('_', ' ')}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Compliance Score</span>
                      <span className="text-white">{message.report.compliance_score.toFixed(1)}%</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-gray-400">Total Issues</span>
                      <span className="text-white bg-white/10 px-2 py-0.5 rounded-md">{message.report.total_issues}</span>
                    </div>
                  </div>
                </div>
              )}

              <p className={clsx('text-[10px] mt-3 opacity-60 font-medium tracking-wide', message.type === 'user' ? 'text-indigo-100 text-right' : 'text-gray-400')}>
                {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </p>
            </div>
          </div>
        ))}

        {error && (
          <div className="flex justify-center">
            <div className="bg-rose-500/10 border border-rose-500/20 text-rose-200 rounded-2xl px-5 py-4 max-w-xl text-sm flex items-start gap-3 backdrop-blur-sm shadow-lg">
              <svg className="w-5 h-5 shrink-0 text-rose-400 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{error}</span>
            </div>
          </div>
        )}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-white/5 border border-white/10 rounded-2xl rounded-bl-sm px-6 py-5 shadow-sm backdrop-blur-sm">
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.15s' }}></div>
                <div className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{ animationDelay: '0.3s' }}></div>
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* File Selection Preview */}
      {selectedFile && (
        <div className="px-4 py-3 bg-black/20 backdrop-blur-md border-t border-white/5">
          <div className="flex items-center justify-between bg-white/5 border border-white/10 rounded-xl px-4 py-2 max-w-md mx-auto sm:mx-0">
            <div className="flex items-center gap-3 text-sm text-gray-200">
              <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
                </svg>
              </div>
              <span className="truncate font-medium">{selectedFile.name}</span>
            </div>
            <button
              onClick={() => setSelectedFile(null)}
              className="p-1.5 text-gray-400 hover:text-rose-400 transition-colors rounded-full hover:bg-rose-400/10"
            >
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" /></svg>
            </button>
          </div>
        </div>
      )}

      {/* Input Area */}
      <div className="p-4 md:p-6 bg-black/20 backdrop-blur-xl border-t border-white/5 relative z-10">
        <div className="max-w-4xl mx-auto">
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.docx,.doc"
            className="hidden"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />

          <div className="flex items-end gap-2 bg-white/5 border border-white/10 p-2 rounded-2xl shadow-inner focus-within:ring-2 focus-within:ring-indigo-500/50 focus-within:border-indigo-500/50 transition-all">
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-3 rounded-xl hover:bg-white/10 text-gray-400 hover:text-indigo-400 transition-colors shrink-0"
              title="Upload document"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
              </svg>
            </button>

            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about compliance, or attach a document..."
              className="flex-1 bg-transparent text-gray-100 px-2 py-3 text-sm placeholder-gray-500 focus:outline-none resize-none max-h-32 min-h-[44px]"
              rows={1}
              disabled={loading}
              style={{ height: 'auto' }}
            />

            <button
              onClick={handleSendMessage}
              disabled={loading || (!input.trim() && !selectedFile)}
              className="p-3 rounded-xl bg-indigo-600 hover:bg-indigo-500 disabled:bg-white/5 disabled:text-gray-600 text-white shadow-lg shadow-indigo-500/20 disabled:shadow-none transition-all shrink-0"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          <p className="text-center text-[11px] text-gray-500 mt-3 font-medium tracking-wide">
            AI assistance for Mauritanian compliance. Verify legal information independently.
          </p>
        </div>
      </div>
    </div>
  );
};
