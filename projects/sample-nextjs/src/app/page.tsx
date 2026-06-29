import Link from 'next/link';

export default function Home() {
  const steps = [
    { title: 'Project Creation', desc: 'Create projects using the DevForge Makefile or CLI scripts.' },
    { title: 'Hot Reloading', desc: 'Docker mounts will automatically update as you edit code on the host.' },
    { title: 'Production Ready', desc: 'Pre-configured with TypeScript, Tailwind CSS, and strict linting rules.' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-slate-100 flex flex-col font-sans">
      {/* Header */}
      <header className="border-b border-slate-900/80 backdrop-blur-md sticky top-0 z-50 bg-slate-950/80 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-3xl">▲</span>
          <div>
            <h1 className="text-xl font-bold bg-gradient-to-r from-blue-400 to-emerald-400 bg-clip-text text-transparent">
              DevForge Next.js
            </h1>
            <p className="text-xs text-slate-400">Production-grade SSR App Router</p>
          </div>
        </div>
        <div className="flex items-center gap-4">
          <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
            Live Reload
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-5xl w-full mx-auto p-6 md:p-12 flex flex-col justify-center gap-12">
        <div className="text-center max-w-3xl mx-auto space-y-6">
          <h2 className="text-4xl md:text-5xl font-extrabold tracking-tight">
            Next-Gen Server Side Rendering in{' '}
            <span className="bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Docker
            </span>
          </h2>
          <p className="text-slate-400 text-lg leading-relaxed">
            This workspace includes the Next.js App Router template pre-wired to communicate with database clusters and local LLM services.
          </p>
        </div>

        {/* Card Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {steps.map((step, idx) => (
            <div
              key={idx}
              className="bg-slate-900/40 border border-slate-800/80 backdrop-blur-lg p-6 rounded-2xl relative hover:border-slate-700/80 transition-all duration-300 group"
            >
              <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-blue-500 to-indigo-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300 origin-left rounded-t-2xl"></div>
              <span className="font-mono text-sm text-indigo-400 font-bold">0{idx + 1}.</span>
              <h3 className="text-lg font-bold text-slate-100 mt-2 mb-1">{step.title}</h3>
              <p className="text-sm text-slate-400 leading-relaxed">{step.desc}</p>
            </div>
          ))}
        </div>

        {/* Action Panel */}
        <div className="bg-slate-900/20 border border-slate-800 p-6 rounded-xl flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-1">
            <h4 className="font-semibold text-slate-200">How to get started?</h4>
            <p className="text-xs text-slate-400">
              Edit <code className="text-blue-300 font-mono">src/app/page.tsx</code> to see updates instantly.
            </p>
          </div>
          <div className="flex gap-4">
            <a
              href="http://localhost"
              target="_blank"
              rel="noreferrer"
              className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-5 py-2 rounded-lg text-sm font-semibold transition-all border border-slate-700"
            >
              Platform Gateway
            </a>
            <a
              href="https://nextjs.org/docs"
              target="_blank"
              rel="noreferrer"
              className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2 rounded-lg text-sm font-semibold transition-all shadow-md shadow-indigo-600/20"
            >
              Next.js Docs
            </a>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900/60 py-6 text-center text-xs text-slate-500 mt-auto bg-slate-950/20">
        <p>© 2026 DevForge Development Platform. Created by the DevForge Authors.</p>
      </footer>
    </div>
  );
}
