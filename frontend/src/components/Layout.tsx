import React, { ReactNode } from 'react';
import clsx from 'clsx';

interface LayoutProps {
  children: ReactNode;
  title?: string;
}

export const Layout: React.FC<LayoutProps> = ({ children, title }) => {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Compliance Verification System
              </h1>
              {title && (
                <p className="mt-2 text-sm text-gray-600">{title}</p>
              )}
            </div>
            <div className="text-sm text-gray-500">
              ISCAE Mauritanie | PFE 2026
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-sm text-gray-500">
            Système Agentique de Vérification de Conformité Contractuelle
            <br />
            Supervised by Dr. Mohamed Ould Djibril
          </p>
        </div>
      </footer>
    </div>
  );
};
