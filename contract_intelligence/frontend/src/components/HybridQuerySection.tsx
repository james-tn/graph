import React, { useState } from 'react';
import { Search, Loader2, Sparkles, GitBranch, Database, Brain, Shield } from 'lucide-react';
import { runHybridQuery } from '../api';

interface HybridQuerySectionProps {
  onResult: (result: any) => void;
}

const SAMPLE_QUERIES = [
  // Graph Traversal Queries (PostgreSQL + Apache AGE)
  {
    text: "Map all obligations and penalties for Acme Corp across their contracts",
    type: "postgres",
    desc: "Multi-hop graph: Party → Contract → Clause → Obligations",
    icon: "graph"
  },
  {
    text: "Find all parties with indemnification obligations and trace to which contracts",
    type: "postgres",
    desc: "Reverse graph: Obligation ← Clause ← Contract ← Party",
    icon: "graph"
  },
  {
    text: "Show termination rights granted to each party and their triggering conditions",
    type: "postgres",
    desc: "Rights traversal: Party → Right ← Clause ← Contract",
    icon: "graph"
  },
  
  // Legal Domain Queries (SQL + Vector Search)
  {
    text: "Identify high-risk liability limitations clauses across all service agreements",
    type: "postgres",
    desc: "Risk analysis + semantic search",
    icon: "risk"
  },
  {
    text: "Find contracts with unusual warranty disclaimer language compared to industry standards",
    type: "postgres",
    desc: "Vector similarity + deviation detection",
    icon: "semantic"
  },
  {
    text: "List all force majeure clauses and group by coverage scope (COVID, natural disasters, etc.)",
    type: "postgres",
    desc: "Full-text search + semantic clustering",
    icon: "semantic"
  },
  
  // Compliance & Due Diligence (Graph + Knowledge)
  {
    text: "Audit trail: Which contracts have mutual confidentiality obligations vs one-way?",
    type: "postgres",
    desc: "Bilateral relationship analysis",
    icon: "graph"
  },
  {
    text: "Find all auto-renewal clauses and their notice periods across vendor contracts",
    type: "postgres",
    desc: "Temporal clause extraction + grouping",
    icon: "temporal"
  },
  {
    text: "Map intellectual property ownership chains: who owns what in which contracts?",
    type: "postgres",
    desc: "IP rights graph traversal",
    icon: "graph"
  },
  
  // Cross-Document Pattern Analysis (Microsoft GraphRAG)
  {
    text: "What are the common dispute resolution patterns across our contract portfolio?",
    type: "graphrag",
    desc: "Global knowledge graph reasoning",
    icon: "knowledge"
  },
  {
    text: "Compare payment term structures: identify outliers and benchmark against portfolio",
    type: "graphrag",
    desc: "Cross-document comparison + clustering",
    icon: "knowledge"
  },
  {
    text: "Summarize all data privacy and GDPR compliance obligations across contracts",
    type: "graphrag",
    desc: "Multi-document synthesis + legal analysis",
    icon: "knowledge"
  },
  
  // Hybrid Intelligence Queries
  {
    text: "Full risk assessment: high-risk clauses + cross-contract inconsistencies + missing protections",
    type: "hybrid",
    desc: "SQL risk filter + GraphRAG pattern detection",
    icon: "hybrid"
  },
  {
    text: "Contract relationship network: show dependencies, cross-references, and conflicting terms",
    type: "hybrid",
    desc: "Graph structure + semantic conflict detection",
    icon: "hybrid"
  },
  {
    text: "Generate negotiation leverage report: find weak positions and favorable terms to replicate",
    type: "hybrid",
    desc: "Graph power analysis + GraphRAG benchmarking",
    icon: "hybrid"
  }
];

export const HybridQuerySection: React.FC<HybridQuerySectionProps> = ({ onResult }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [strategy, setStrategy] = useState<'auto' | 'postgres' | 'graphrag' | 'hybrid'>('auto');

  const handleSearch = async (q: string, forceStrategy?: string) => {
    setQuery(q);
    setLoading(true);
    try {
      const result = await runHybridQuery(q, forceStrategy || strategy);
      onResult(result);
    } catch (error) {
      console.error(error);
      onResult({ error: 'Failed to fetch results' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="glass-dark p-8 rounded-3xl shadow-2xl border border-purple-500/20 backdrop-blur-xl hover:border-purple-500/40 transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-white flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl shadow-lg shadow-purple-500/50">
            <Search className="w-7 h-7 text-white" />
          </div>
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Hybrid Search</span>
        </h2>
        <span className="text-xs text-purple-300 bg-purple-500/20 px-4 py-2 rounded-full border border-purple-400/30 font-semibold">Intelligent Routing</span>
      </div>

      {/* Strategy Selector */}
      <div className="mb-6">
        <label className="text-sm font-semibold text-purple-300 mb-3 block">Search Strategy</label>
        <div className="grid grid-cols-4 gap-3">
          <button
            onClick={() => setStrategy('auto')}
            className={`p-4 rounded-xl transition-all duration-300 flex flex-col items-center gap-2 ${
              strategy === 'auto'
                ? 'bg-gradient-to-br from-purple-600 to-pink-600 text-white shadow-lg shadow-purple-500/50 scale-105'
                : 'bg-slate-800/50 text-purple-300 hover:bg-slate-700/50 border border-purple-500/20'
            }`}
          >
            <GitBranch className="w-5 h-5" />
            <span className="text-xs font-bold">Auto Route</span>
          </button>
          
          <button
            onClick={() => setStrategy('postgres')}
            className={`p-4 rounded-xl transition-all duration-300 flex flex-col items-center gap-2 ${
              strategy === 'postgres'
                ? 'bg-gradient-to-br from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/50 scale-105'
                : 'bg-slate-800/50 text-blue-300 hover:bg-slate-700/50 border border-blue-500/20'
            }`}
          >
            <Database className="w-5 h-5" />
            <span className="text-xs font-bold">PostgreSQL</span>
          </button>
          
          <button
            onClick={() => setStrategy('graphrag')}
            className={`p-4 rounded-xl transition-all duration-300 flex flex-col items-center gap-2 ${
              strategy === 'graphrag'
                ? 'bg-gradient-to-br from-green-600 to-emerald-600 text-white shadow-lg shadow-green-500/50 scale-105'
                : 'bg-slate-800/50 text-green-300 hover:bg-slate-700/50 border border-green-500/20'
            }`}
          >
            <Brain className="w-5 h-5" />
            <span className="text-xs font-bold">GraphRAG</span>
          </button>
          
          <button
            onClick={() => setStrategy('hybrid')}
            className={`p-4 rounded-xl transition-all duration-300 flex flex-col items-center gap-2 ${
              strategy === 'hybrid'
                ? 'bg-gradient-to-br from-purple-600 via-pink-600 to-orange-600 text-white shadow-lg shadow-purple-500/50 scale-105'
                : 'bg-slate-800/50 text-purple-300 hover:bg-slate-700/50 border border-purple-500/20'
            }`}
          >
            <Sparkles className="w-5 h-5" />
            <span className="text-xs font-bold">Hybrid</span>
          </button>
        </div>
      </div>

      {/* Search Input */}
      <div className="flex gap-4 mb-8">
        <div className="flex-1 relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && !loading && query && handleSearch(query)}
            placeholder="Ask anything about your contracts..."
            className="w-full px-6 py-5 bg-slate-900/70 text-white placeholder-purple-400/50 rounded-2xl border-2 border-purple-500/30 focus:border-purple-500 focus:outline-none focus:ring-4 focus:ring-purple-500/20 transition-all duration-300 text-lg backdrop-blur-sm group-hover:border-purple-500/50 shadow-inner"
            disabled={loading}
          />
          <div className="absolute right-4 top-1/2 transform -translate-y-1/2 text-purple-400/50 text-sm font-medium">
            {strategy.toUpperCase()}
          </div>
        </div>
        
        <button
          onClick={() => handleSearch(query)}
          disabled={loading || !query}
          className="px-10 py-5 bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 bg-[length:200%_100%] hover:bg-[position:100%_0] text-white font-bold rounded-2xl disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-500 shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/70 hover:scale-105 flex items-center gap-3 group"
        >
          {loading ? (
            <><Loader2 className="w-6 h-6 animate-spin" /><span>Searching...</span></>
          ) : (
            <><Search className="w-6 h-6 group-hover:scale-110 transition-transform" /><span>Search</span></>
          )}
        </button>
      </div>

      {/* Sample Queries */}
      <div>
        <div className="flex items-center gap-3 mb-4">
          <Sparkles className="w-5 h-5 text-purple-400" />
          <h3 className="text-lg font-bold text-purple-300">Real-World Legal Intelligence Queries</h3>
          <span className="text-xs text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-400/30">
            {SAMPLE_QUERIES.length} sophisticated examples
          </span>
        </div>
        
        {/* Query Categories */}
        <div className="space-y-6">
          {/* Graph Traversal Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <GitBranch className="w-4 h-4 text-blue-400" />
              <h4 className="text-sm font-bold text-blue-300 uppercase tracking-wider">Graph Traversal Queries</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-blue-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.slice(0, 3).map((sample, idx) => (
              <button
                key={idx}
                onClick={() => handleSearch(sample.text, 'auto')}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-blue-900/30 hover:to-slate-800/50 rounded-xl border border-blue-500/20 hover:border-blue-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-blue-100 group-hover:text-white transition-colors font-medium mb-2">
                      {sample.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-3 py-1 rounded-full font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30">
                        {sample.desc}
                      </span>
                      <span className="text-xs text-blue-400/60">Apache AGE</span>
                    </div>
                  </div>
                  <Search className="w-5 h-5 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
          
          {/* SQL + Vector Search Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-cyan-400" />
              <h4 className="text-sm font-bold text-cyan-300 uppercase tracking-wider">Legal Domain Analysis</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-cyan-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.slice(3, 6).map((sample, idx) => (
              <button
                key={idx + 3}
                onClick={() => handleSearch(sample.text, 'auto')}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-cyan-900/30 hover:to-slate-800/50 rounded-xl border border-cyan-500/20 hover:border-cyan-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-cyan-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-cyan-100 group-hover:text-white transition-colors font-medium mb-2">
                      {sample.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-3 py-1 rounded-full font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-400/30">
                        {sample.desc}
                      </span>
                      <span className="text-xs text-cyan-400/60">PostgreSQL + Vectors</span>
                    </div>
                  </div>
                  <Search className="w-5 h-5 text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
          
          {/* Compliance Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Shield className="w-4 h-4 text-amber-400" />
              <h4 className="text-sm font-bold text-amber-300 uppercase tracking-wider">Compliance & Due Diligence</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-amber-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.slice(6, 9).map((sample, idx) => (
              <button
                key={idx + 6}
                onClick={() => handleSearch(sample.text, 'auto')}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-amber-900/30 hover:to-slate-800/50 rounded-xl border border-amber-500/20 hover:border-amber-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-amber-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-amber-100 group-hover:text-white transition-colors font-medium mb-2">
                      {sample.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-3 py-1 rounded-full font-semibold bg-amber-500/20 text-amber-300 border border-amber-400/30">
                        {sample.desc}
                      </span>
                      <span className="text-xs text-amber-400/60">Graph + SQL</span>
                    </div>
                  </div>
                  <Search className="w-5 h-5 text-amber-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
          
          {/* GraphRAG Knowledge Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Brain className="w-4 h-4 text-green-400" />
              <h4 className="text-sm font-bold text-green-300 uppercase tracking-wider">Cross-Document Intelligence</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-green-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.slice(9, 12).map((sample, idx) => (
              <button
                key={idx + 9}
                onClick={() => handleSearch(sample.text, 'auto')}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-green-900/30 hover:to-slate-800/50 rounded-xl border border-green-500/20 hover:border-green-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-green-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-green-100 group-hover:text-white transition-colors font-medium mb-2">
                      {sample.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-3 py-1 rounded-full font-semibold bg-green-500/20 text-green-300 border border-green-400/30">
                        {sample.desc}
                      </span>
                      <span className="text-xs text-green-400/60">Microsoft GraphRAG</span>
                    </div>
                  </div>
                  <Search className="w-5 h-5 text-green-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
          
          {/* Hybrid Intelligence Section */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <h4 className="text-sm font-bold text-purple-300 uppercase tracking-wider">Hybrid Intelligence</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-purple-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.slice(12, 15).map((sample, idx) => (
              <button
                key={idx + 12}
                onClick={() => handleSearch(sample.text, 'auto')}
                disabled={loading}
                className="w-full text-left p-4 bg-gradient-to-r from-purple-900/30 to-pink-900/30 hover:from-purple-900/50 hover:to-pink-900/50 rounded-xl border border-purple-500/30 hover:border-purple-400/60 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/30"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-purple-100 group-hover:text-white transition-colors font-medium mb-2">
                      {sample.text}
                    </p>
                    <div className="flex items-center gap-2">
                      <span className="text-xs px-3 py-1 rounded-full font-semibold bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border border-purple-400/30">
                        {sample.desc}
                      </span>
                      <span className="text-xs bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent font-bold">PostgreSQL + GraphRAG</span>
                    </div>
                  </div>
                  <Sparkles className="w-5 h-5 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
