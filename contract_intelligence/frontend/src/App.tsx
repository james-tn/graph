import { useState } from 'react'
import { UploadSection } from './components/UploadSection'
import { HybridQuerySection } from './components/HybridQuerySection'
import { HybridResultSection } from './components/HybridResultSection'
import { Brain, Search, Upload, Database, GitBranch } from 'lucide-react'

function App() {
  const [result, setResult] = useState(null);
  const [activeTab, setActiveTab] = useState<'query' | 'upload'>('query');

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-blue-950 to-indigo-950 relative overflow-hidden">
      {/* Animated Background Elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-20 left-10 w-72 h-72 bg-blue-500/30 rounded-full filter blur-3xl animate-float"></div>
        <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/30 rounded-full filter blur-3xl animate-float" style={{animationDelay: '1s'}}></div>
        <div className="absolute top-1/2 left-1/3 w-64 h-64 bg-pink-500/20 rounded-full filter blur-3xl animate-float" style={{animationDelay: '2s'}}></div>
      </div>

      {/* Grid Pattern Overlay */}
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#80808012_1px,transparent_1px),linear-gradient(to_bottom,#80808012_1px,transparent_1px)] bg-[size:24px_24px]"></div>

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Stunning Hero Header */}
        <header className="mb-12 text-center">
          <div className="flex justify-center mb-8">
            <div className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-full blur-2xl opacity-75 group-hover:opacity-100 transition duration-1000 animate-glow"></div>
              <div className="relative bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 p-6 rounded-3xl shadow-2xl transform group-hover:scale-110 transition duration-300">
                <Brain className="w-16 h-16 text-white animate-pulse" />
              </div>
            </div>
          </div>
          
          <div className="mb-6">
            <h1 className="text-7xl font-black mb-4 leading-tight">
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-pink-400 bg-clip-text text-transparent animate-pulse">
                Contract Intelligence
              </span>
            </h1>
            <p className="text-2xl font-light text-blue-200/90 max-w-3xl mx-auto leading-relaxed">
              Hybrid graph search combining <span className="font-bold text-blue-300">PostgreSQL</span> + <span className="font-bold text-purple-300">Microsoft GraphRAG</span>
            </p>
          </div>
          
          {/* Feature Pills with Glow */}
          <div className="flex flex-wrap justify-center gap-4 mt-8">
            <div className="group glass-dark px-6 py-3 rounded-full shadow-lg hover:shadow-blue-500/50 transition-all duration-300 transform hover:scale-105">
              <div className="flex items-center gap-3">
                <Database className="w-5 h-5 text-blue-400 group-hover:text-blue-300" />
                <span className="text-sm font-semibold text-blue-200">PostgreSQL + Apache AGE</span>
              </div>
            </div>
            <div className="group glass-dark px-6 py-3 rounded-full shadow-lg hover:shadow-purple-500/50 transition-all duration-300 transform hover:scale-105">
              <div className="flex items-center gap-3">
                <Brain className="w-5 h-5 text-purple-400 group-hover:text-purple-300" />
                <span className="text-sm font-semibold text-purple-200">Microsoft GraphRAG</span>
              </div>
            </div>
            <div className="group glass-dark px-6 py-3 rounded-full shadow-lg hover:shadow-pink-500/50 transition-all duration-300 transform hover:scale-105">
              <div className="flex items-center gap-3">
                <GitBranch className="w-5 h-5 text-pink-400 group-hover:text-pink-300" />
                <span className="text-sm font-semibold text-pink-200">Intelligent Routing</span>
              </div>
            </div>
          </div>
        </header>

        {/* Tab Navigation */}
        <div className="flex justify-center mb-8">
          <div className="glass-dark p-2 rounded-2xl flex gap-2">
            <button
              onClick={() => setActiveTab('query')}
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 flex items-center gap-3 ${
                activeTab === 'query'
                  ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/50 scale-105'
                  : 'text-blue-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Search className="w-6 h-6" />
              Hybrid Search
            </button>
            <button
              onClick={() => setActiveTab('upload')}
              className={`px-8 py-4 rounded-xl font-bold text-lg transition-all duration-300 flex items-center gap-3 ${
                activeTab === 'upload'
                  ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg shadow-blue-500/50 scale-105'
                  : 'text-blue-300 hover:text-white hover:bg-slate-800/50'
              }`}
            >
              <Upload className="w-6 h-6" />
              Manage Files
            </button>
          </div>
        </div>

        {/* Main Content */}
        <div className="space-y-8">
          {activeTab === 'query' ? (
            <>
              <HybridQuerySection onResult={setResult} />
              {result && <HybridResultSection result={result} />}
            </>
          ) : (
            <UploadSection />
          )}
        </div>

        {/* Modern Footer */}
        <footer className="mt-20 text-center">
          <div className="glass-dark inline-block px-8 py-4 rounded-2xl">
            <p className="text-sm text-blue-300 font-medium">
              Hybrid Architecture: <span className="text-blue-400 font-bold">PostgreSQL + Apache AGE</span> ⚡ <span className="text-purple-400 font-bold">Microsoft GraphRAG</span> • Built with <span className="text-pink-400">React</span> + <span className="text-green-400">FastAPI</span>
            </p>
          </div>
        </footer>
      </div>
    </div>
  )
}

export default App
