import React, { useState } from 'react';
import { Search, Loader2, Sparkles, GitBranch, Database, Brain } from 'lucide-react';
import { runHybridQuery } from '../api';

interface HybridQuerySectionProps {
  onResult: (result: any) => void;
}

const SAMPLE_QUERIES = [
  // A. Vendor Risk and Exposure
  {
    text: "For each of our main vendors, how many contracts do we have with them, and how many of those include high-risk clauses? Which vendors look riskiest overall?",
    type: "postgres",
    desc: "Vendor risk aggregation + high-risk clause counting",
    category: "vendor-risk"
  },
  {
    text: "For vendors like Acme Corp and Phoenix Industries, how does their risk profile compare? I'd like to see: how many contracts we have with each, how many high-risk clauses they have, and which types of risk show up most often for each vendor.",
    type: "postgres",
    desc: "Multi-vendor risk comparison + risk type analysis",
    category: "vendor-risk"
  },
  {
    text: "Which vendors do we owe the largest number of high-impact obligations to? Please rank our vendors by how many high-impact obligations we have in their contracts.",
    type: "postgres",
    desc: "Vendor obligation ranking + high-impact filtering",
    category: "vendor-risk"
  },
  {
    text: "For a specific vendor, for example Atlas Ventures, show me all of our high-impact obligations to them, grouped by contract, with a short description of each obligation.",
    type: "postgres",
    desc: "Vendor-specific obligation analysis + contract grouping",
    category: "vendor-risk"
  },
  
  // B. Contract Families and Relationship Complexity
  {
    text: "Show the complete contract family tree for Zenith Technologies Master Services Agreement MSA-ZEN-202403-197",
    type: "postgres",
    desc: "Master agreement → SOWs → Amendments hierarchy",
    category: "families"
  },
  {
    text: "Among our larger vendor relationships, which contract families (for example, an MSA and its SOWs, work orders, amendments, and addenda) have the highest number of high-risk clauses overall?",
    type: "postgres",
    desc: "Contract family risk aggregation + hierarchical analysis",
    category: "families"
  },
  {
    text: "Show me the contract family trees for our biggest vendors, and for each family give me: how many related documents there are, and a simple summary of how many high-risk clauses appear in that family.",
    type: "postgres",
    desc: "Multi-family analysis + risk concentration",
    category: "families"
  },
  {
    text: "Which Master Services Agreements have an unusually large number of related documents (SOWs, work orders, amendments, addenda)? I want to see where the relationship has become complex and potentially harder to manage.",
    type: "postgres",
    desc: "Relationship complexity detection + document counting",
    category: "families"
  },
  
  // C. Clause-Level Risk Patterns
  {
    text: "Across our entire contract portfolio, which types of clauses are most often marked as high risk? For example, is it more often limitation of liability, termination, payment terms, or service levels?",
    type: "postgres",
    desc: "Portfolio-wide clause type risk distribution",
    category: "clause-risk"
  },
  {
    text: "Which vendors have the highest number of high-risk 'Data Protection' or 'Confidentiality' clauses in their contracts?",
    type: "postgres",
    desc: "Vendor risk ranking by specific clause types",
    category: "clause-risk"
  },
  {
    text: "For our top 10 vendors, summarize for me: how many high-risk termination clauses they have, how many high-risk payment terms, and how many high-risk service level clauses.",
    type: "postgres",
    desc: "Multi-vendor clause-specific risk breakdown",
    category: "clause-risk"
  },
  
  // D. Monetary Exposure vs Risk
  {
    text: "Which individual contracts combine a large contract value with high-risk clauses? Show me the top set by contract value, along with the vendor and a brief risk summary for each.",
    type: "postgres",
    desc: "Financial exposure + risk correlation analysis",
    category: "monetary"
  },
  {
    text: "By vendor, how much total contract value is tied to contracts that contain at least one high-risk clause? I'd like a ranking of vendors by 'high-risk contract value'.",
    type: "postgres",
    desc: "Vendor financial risk exposure aggregation",
    category: "monetary"
  },
  {
    text: "Which vendors have a lot of contract value with us, but only low- or medium-risk clauses? I'd like to see where our commercial exposure is high but the legal risk looks relatively low.",
    type: "postgres",
    desc: "High-value low-risk vendor identification",
    category: "monetary"
  },
  
  // E. Obligations and Rights
  {
    text: "Which vendors are associated with the largest number of high-impact obligations across all of their contracts with us?",
    type: "postgres",
    desc: "Vendor obligation burden analysis",
    category: "obligations"
  },
  {
    text: "Which contracts grant us important rights that are due to expire in the next six months, and which vendors are those contracts with?",
    type: "postgres",
    desc: "Rights expiration tracking + vendor identification",
    category: "obligations"
  },
  
  // F. Governing Law and Regional Risk
  {
    text: "How does our overall risk profile differ by governing law? For example, compare contracts governed by England and Wales, Delaware, and California in terms of how many high-, medium-, and low-risk clauses they contain.",
    type: "postgres",
    desc: "Jurisdictional risk comparison + distribution analysis",
    category: "regional"
  },
  {
    text: "For contracts governed by England and Wales, which vendors do we have the most high-risk clauses with?",
    type: "postgres",
    desc: "Jurisdiction-specific vendor risk ranking",
    category: "regional"
  },
  
  // G. Portfolio-Level Summaries
  {
    text: "Across our whole portfolio, which counterparties (customers or vendors) have the most contracts with us, and what does the risk breakdown look like for each (high, medium, low)?",
    type: "postgres",
    desc: "Portfolio-wide party analysis + risk distribution",
    category: "portfolio"
  },
  {
    text: "Which contracts have the highest concentration of high-risk clauses—for example, more than three high-risk clauses in a single contract? Show these with the party name and contract type.",
    type: "postgres",
    desc: "High-risk concentration detection + contract identification",
    category: "portfolio"
  },
  {
    text: "For our largest service or consulting contracts, summarize for each: total contract value, number of high-risk clauses, and number of high-impact obligations, so we can see where the biggest risks are.",
    type: "postgres",
    desc: "Comprehensive risk + financial + obligation analysis",
    category: "portfolio"
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
            {SAMPLE_QUERIES.length} queries across 7 categories
          </span>
        </div>
        
        {/* Query Categories */}
        <div className="space-y-6">
          {/* A. Vendor Risk and Exposure */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-red-400" />
              <h4 className="text-sm font-bold text-red-300 uppercase tracking-wider">A. Vendor Risk and Exposure</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-red-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'vendor-risk').map((sample, idx) => (
              <button
                key={`vendor-risk-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-red-900/30 hover:to-slate-800/50 rounded-xl border border-red-500/20 hover:border-red-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-red-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-red-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-red-500/20 text-red-300 border border-red-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-red-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* B. Contract Families */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <GitBranch className="w-4 h-4 text-blue-400" />
              <h4 className="text-sm font-bold text-blue-300 uppercase tracking-wider">B. Contract Families and Relationship Complexity</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-blue-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'families').map((sample, idx) => (
              <button
                key={`families-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-blue-900/30 hover:to-slate-800/50 rounded-xl border border-blue-500/20 hover:border-blue-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-blue-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-blue-500/20 text-blue-300 border border-blue-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* C. Clause-Level Risk */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-orange-400" />
              <h4 className="text-sm font-bold text-orange-300 uppercase tracking-wider">C. Clause-Level Risk Patterns</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-orange-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'clause-risk').map((sample, idx) => (
              <button
                key={`clause-risk-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-orange-900/30 hover:to-slate-800/50 rounded-xl border border-orange-500/20 hover:border-orange-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-orange-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-orange-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-orange-500/20 text-orange-300 border border-orange-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-orange-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* D. Monetary Exposure */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-yellow-400" />
              <h4 className="text-sm font-bold text-yellow-300 uppercase tracking-wider">D. Monetary Exposure vs Risk</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-yellow-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'monetary').map((sample, idx) => (
              <button
                key={`monetary-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-yellow-900/30 hover:to-slate-800/50 rounded-xl border border-yellow-500/20 hover:border-yellow-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-yellow-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-yellow-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-yellow-500/20 text-yellow-300 border border-yellow-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-yellow-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* E. Obligations and Rights */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-green-400" />
              <h4 className="text-sm font-bold text-green-300 uppercase tracking-wider">E. Obligations and Rights</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-green-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'obligations').map((sample, idx) => (
              <button
                key={`obligations-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-green-900/30 hover:to-slate-800/50 rounded-xl border border-green-500/20 hover:border-green-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-green-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-green-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-green-500/20 text-green-300 border border-green-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-green-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* F. Regional Risk */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Database className="w-4 h-4 text-cyan-400" />
              <h4 className="text-sm font-bold text-cyan-300 uppercase tracking-wider">F. Governing Law and Regional Risk</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-cyan-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'regional').map((sample, idx) => (
              <button
                key={`regional-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r hover:from-cyan-900/30 hover:to-slate-800/50 rounded-xl border border-cyan-500/20 hover:border-cyan-400/50 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-cyan-500/20"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-cyan-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-cyan-500/20 text-cyan-300 border border-cyan-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Search className="w-5 h-5 text-cyan-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
          
          {/* G. Portfolio Summaries */}
          <div className="space-y-2">
            <div className="flex items-center gap-2 mb-3">
              <Sparkles className="w-4 h-4 text-purple-400" />
              <h4 className="text-sm font-bold text-purple-300 uppercase tracking-wider">G. Portfolio-Level Summaries</h4>
              <div className="flex-1 h-px bg-gradient-to-r from-purple-500/30 to-transparent"></div>
            </div>
            {SAMPLE_QUERIES.filter(q => q.category === 'portfolio').map((sample, idx) => (
              <button
                key={`portfolio-${idx}`}
                onClick={() => handleSearch(sample.text, sample.type)}
                disabled={loading}
                className="w-full text-left p-4 bg-gradient-to-r from-purple-900/30 to-pink-900/30 hover:from-purple-900/50 hover:to-pink-900/50 rounded-xl border border-purple-500/30 hover:border-purple-400/60 transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-purple-500/30"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="flex-1">
                    <p className="text-purple-100 group-hover:text-white transition-colors font-medium mb-2 text-sm">
                      {sample.text}
                    </p>
                    <span className="text-xs px-3 py-1 rounded-full font-semibold bg-gradient-to-r from-purple-500/20 to-pink-500/20 text-purple-300 border border-purple-400/30">
                      {sample.desc}
                    </span>
                  </div>
                  <Sparkles className="w-5 h-5 text-purple-400 opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0" />
                </div>
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
