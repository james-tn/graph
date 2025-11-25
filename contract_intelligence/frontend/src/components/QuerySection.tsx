import React, { useState } from 'react';
import { Search, Loader2, Sparkles } from 'lucide-react';
import { runQuery } from '../api';

interface QuerySectionProps {
  onResult: (result: any) => void;
}

const SAMPLE_QUERIES = [
  "Summarize all contracts, key obligations, SLAs, renewal dates, and unusual terms.",
  "Which contracts don't have a DPA or data breach notification clause?",
  "Compare the termination conditions between Acme Corp and Vanguard Solutions contracts.",
  "What are the liability caps across all vendor agreements?",
  "Which contracts with Contoso Enterprises have the most restrictive IP assignment clauses?",
  "Identify all contracts mentioning Phoenix Industries and their renewal dates."
];

export const QuerySection: React.FC<QuerySectionProps> = ({ onResult }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSearch = async (q: string) => {
    setQuery(q);
    setLoading(true);
    try {
      const result = await runQuery(q);
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
          <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">Query Contracts</span>
        </h2>
        <span className="text-xs text-purple-300 bg-purple-500/20 px-4 py-2 rounded-full border border-purple-400/30 font-semibold">Step 2</span>
      </div>

      <div className="flex gap-4 mb-8">
        <div className="flex-1 relative group">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Ask anything about your contracts..."
            className="w-full p-5 bg-slate-900/50 border-2 border-purple-500/30 rounded-2xl focus:ring-4 focus:ring-purple-500/30 focus:border-purple-500 outline-none text-lg text-white placeholder-blue-300/50 transition-all backdrop-blur-sm"
            onKeyDown={(e) => e.key === 'Enter' && handleSearch(query)}
          />
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-600/20 to-pink-600/20 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
        </div>
        <button
          onClick={() => handleSearch(query)}
          disabled={!query || loading}
          className="px-10 py-5 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-2xl hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-3 font-bold text-lg shadow-2xl shadow-purple-500/50 transition-all duration-300 transform hover:scale-105"
        >
          {loading ? <Loader2 className="w-6 h-6 animate-spin" /> : 'Search'}
        </button>
      </div>

      <div className="space-y-4">
        <p className="text-base font-semibold text-blue-300 mb-4 flex items-center gap-2">
          <Sparkles className="w-5 h-5" />
          Try these sophisticated queries:
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {SAMPLE_QUERIES.map((q, i) => (
            <button
              key={i}
              onClick={() => handleSearch(q)}
              className="group relative px-5 py-4 bg-slate-900/50 border-2 border-purple-500/20 hover:border-purple-500/60 text-blue-200 hover:text-white rounded-2xl text-sm text-left shadow-lg hover:shadow-purple-500/30 transition-all duration-300 transform hover:scale-105 backdrop-blur-sm"
            >
              <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-purple-600/10 to-pink-600/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
              <span className="relative block font-semibold leading-relaxed">{q}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};
