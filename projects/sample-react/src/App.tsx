import { useState } from 'react';

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'services'>('overview');

  const services = [
    { name: 'Nginx Ingress', port: '80/443', status: 'Healthy', icon: '🌐' },
    { name: 'PostgreSQL', port: '5432', status: 'Healthy', icon: '🐘' },
    { name: 'MongoDB', port: '27017', status: 'Healthy', icon: '🍃' },
    { name: 'Redis Cache', port: '6379', status: 'Healthy', icon: '⚡' },
    { name: 'Neo4j Graph', port: '7474', status: 'Healthy', icon: '🕸️' },
    { name: 'Ollama LLM', port: '11434', status: 'Healthy', icon: '🤖' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-800/60 backdrop-blur-md sticky top-0 z-50 bg-slate-950/70 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">🚀</span>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
              DevForge Workspace
            </h1>
            <p className="text-xs text-slate-400">NodeJS Development Environment</p>
          </div>
        </div>
        <div className="flex bg-slate-900/80 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-300 ${
              activeTab === 'overview'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('services')}
            className={`px-4 py-1.5 rounded-md text-sm font-medium transition-all duration-300 ${
              activeTab === 'services'
                ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-600/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Services
          </button>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-6xl w-full mx-auto p-6 md:p-8 flex flex-col justify-center">
        {activeTab === 'overview' ? (
          <div className="space-y-8 animate-fadeIn">
            <div className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-xl p-8 rounded-2xl shadow-2xl relative overflow-hidden">
              <div className="absolute top-0 right-0 w-96 h-96 bg-indigo-500/10 rounded-full blur-3xl -mr-20 -mt-20"></div>
              <div className="relative z-10 space-y-4">
                <span className="bg-indigo-500/10 text-indigo-400 text-xs px-3 py-1 rounded-full border border-indigo-500/20 font-mono">
                  Environment: Active
                </span>
                <h2 className="text-3xl md:text-4xl font-extrabold tracking-tight">
                  Welcome to your{' '}
                  <span className="bg-gradient-to-r from-blue-400 to-indigo-400 bg-clip-text text-transparent">
                    React Frontend
                  </span>
                </h2>
                <p className="text-slate-400 max-w-2xl text-base leading-relaxed">
                  This React template is built with Vite, TypeScript, and Tailwind CSS.
                  It includes hot module replacement (HMR) running inside docker containers.
                  Edit <code className="text-indigo-300 font-mono bg-slate-950 px-1.5 py-0.5 rounded">src/App.tsx</code> to start coding!
                </p>
                <div className="flex flex-wrap gap-4 pt-4">
                  <a
                    href="http://localhost"
                    target="_blank"
                    rel="noreferrer"
                    className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-xl font-semibold shadow-lg shadow-indigo-600/25 transition-all hover:-translate-y-0.5"
                  >
                    Control Panel
                  </a>
                  <a
                    href="https://vitejs.dev"
                    target="_blank"
                    rel="noreferrer"
                    className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-6 py-2.5 rounded-xl font-semibold transition-all hover:-translate-y-0.5 border border-slate-700/50"
                  >
                    Vite Documentation
                  </a>
                </div>
              </div>
            </div>

            {/* Quick stats / Features */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-slate-900/30 border border-slate-800/50 backdrop-blur-md p-6 rounded-xl hover:border-indigo-500/30 transition-colors">
                <div className="text-2xl mb-2">⚡</div>
                <h3 className="font-semibold text-lg mb-1">Instant Dev Server</h3>
                <p className="text-sm text-slate-400">
                  Vite starts instantly and reloads updates instantly via WebSockets HMR.
                </p>
              </div>
              <div className="bg-slate-900/30 border border-slate-800/50 backdrop-blur-md p-6 rounded-xl hover:border-indigo-500/30 transition-colors">
                <div className="text-2xl mb-2">🛡️</div>
                <h3 className="font-semibold text-lg mb-1">TypeScript Strict</h3>
                <p className="text-sm text-slate-400">
                  Fully typed components and state definitions to prevent runtime issues.
                </p>
              </div>
              <div className="bg-slate-900/30 border border-slate-800/50 backdrop-blur-md p-6 rounded-xl hover:border-indigo-500/30 transition-colors">
                <div className="text-2xl mb-2">🎨</div>
                <h3 className="font-semibold text-lg mb-1">Tailwind CSS</h3>
                <p className="text-sm text-slate-400">
                  Utility-first styling system to rapidly build custom user interfaces.
                </p>
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-6 animate-fadeIn">
            <h2 className="text-2xl font-bold tracking-tight">Active Platform Infrastructure</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
              {services.map((svc) => (
                <div
                  key={svc.name}
                  className="bg-slate-900/50 border border-slate-800 p-5 rounded-xl flex items-center justify-between hover:border-slate-700 transition-all duration-300"
                >
                  <div className="flex items-center gap-3">
                    <span className="text-2xl bg-slate-950 p-2.5 rounded-lg">{svc.icon}</span>
                    <div>
                      <h4 className="font-medium text-slate-200">{svc.name}</h4>
                      <p className="text-xs text-slate-400">Internal Port: {svc.port}</p>
                    </div>
                  </div>
                  <div className="flex flex-col items-end gap-1.5">
                    <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                      {svc.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900/80 py-6 px-6 text-center text-xs text-slate-500 mt-auto bg-slate-950/20">
        <p>© 2026 DevForge Development Platform. Created by the DevForge Authors.</p>
      </footer>
    </div>
  );
}
