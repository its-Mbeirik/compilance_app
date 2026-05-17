import React, { useState, ReactNode } from 'react';
import clsx from 'clsx';

interface ChatLayoutProps {
  children: ReactNode;
  sidebarOpen?: boolean;
}

export const ChatLayout: React.FC<ChatLayoutProps> = ({ children, sidebarOpen: initialOpen = true }) => {
  const [sidebarOpen, setSidebarOpen] = useState(initialOpen);

  return (
    <div className="flex h-screen bg-black font-sans selection:bg-indigo-500/30">
      {/* Sidebar */}
      <aside
        className={clsx(
          'fixed top-0 left-0 z-40 w-72 h-screen bg-[#0a0a0a] border-r border-white/5 transition-transform duration-300 ease-in-out md:relative md:translate-x-0 flex flex-col',
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        )}
      >
        <div className="flex flex-col h-full bg-gradient-to-b from-white/[0.02] to-transparent">
          {/* Logo/Title */}
          <div className="p-6">
            <h1 className="text-white font-bold text-xl tracking-tight flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
                <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              Conformité AI
            </h1>
            <p className="text-gray-400 text-xs font-medium mt-2 pl-10">Mauritanian Legal Assistant</p>
          </div>

          {/* New Chat Button */}
          <div className="px-4 mb-2">
            <button className="w-full px-4 py-3 rounded-xl bg-white/5 hover:bg-white/10 text-white text-sm font-medium flex items-center gap-3 transition-all border border-white/5 hover:border-white/10">
              <div className="bg-indigo-500/20 p-1.5 rounded-md text-indigo-400">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                </svg>
              </div>
              New verification
            </button>
          </div>

          {/* Chat History */}
          <nav className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
            <div className="text-gray-500 text-[11px] font-semibold px-3 py-2 uppercase tracking-wider">Recent</div>
            <div className="px-3 py-4 text-center">
              <p className="text-xs text-gray-500">No recent verifications yet.</p>
            </div>
          </nav>

          {/* Footer */}
          <div className="border-t border-white/5 p-4 space-y-1">
            <button className="w-full px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-white/5 text-sm flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
              Settings
            </button>
            <button className="w-full px-3 py-2.5 rounded-lg text-gray-400 hover:text-gray-200 hover:bg-white/5 text-sm flex items-center gap-3 transition-colors">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              Help & Support
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 bg-[#030712]">
        {/* Mobile Header */}
        <div className="md:hidden bg-[#0a0a0a]/80 backdrop-blur-md border-b border-white/5 p-4 flex items-center justify-between sticky top-0 z-30">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-white/10 rounded-xl text-gray-300 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <span className="text-white font-semibold text-sm tracking-wide">Conformité AI</span>
          <div className="w-9" />
        </div>

        {/* Chat Content */}
        <div className="flex-1 overflow-hidden relative">
          {children}
        </div>
      </div>

      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black/60 backdrop-blur-sm z-30 md:hidden transition-opacity"
          onClick={() => setSidebarOpen(false)}
        />
      )}
    </div>
  );
};
