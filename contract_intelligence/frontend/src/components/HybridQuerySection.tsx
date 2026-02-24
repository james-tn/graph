import React, { useState } from 'react';
import { Search, Loader2, Sparkles, GitBranch, Database, Brain, ChevronDown, ChevronUp, Grid3x3, List } from 'lucide-react';
import { runHybridQuery } from '../api';

interface HybridQuerySectionProps {
  onResult: (result: any) => void;
}

const SAMPLE_QUERIES = [
  // A. Vendor Risk and Exposure (PostgreSQL: SQL joins + aggregations)
  {
    text: "Compare the risk profiles of Phoenix Industries and Zenith Technologies — how many contracts do we have with each, how many high-risk clauses, and which clause types are most often flagged?",
    type: "postgres",
    desc: "SQL aggregation: multi-vendor risk comparison with GROUP BY",
    category: "vendor-risk"
  },
  {
    text: "Rank our vendors by the number of high-impact obligations we owe them.",
    type: "postgres",
    desc: "SQL join + ranking: obligations → parties → contracts",
    category: "vendor-risk"
  },
  {
    text: "For Quantum Labs LLC, show all high-impact obligations grouped by contract, with a description of each.",
    type: "postgres",
    desc: "SQL filtering: vendor-specific obligation drill-down",
    category: "vendor-risk"
  },
  
  // B. Contract Families and Hierarchies (PostgreSQL: Cypher/AGE graph traversal)
  {
    text: "Show the complete contract family tree for the Zenith Technologies Master Services Agreement MSA-ZEN-202403-197 — all SOWs, amendments, and work orders beneath it.",
    type: "postgres",
    desc: "Apache AGE Cypher: multi-hop hierarchy traversal (SOW_OF, AMENDS, WORK_ORDER_OF)",
    category: "families"
  },
  {
    text: "How many active SOWs and work orders sit under each Master Services Agreement? Show me which MSAs have become the most complex.",
    type: "postgres",
    desc: "Cypher: aggregate child counts per MSA using typed edges",
    category: "families"
  },
  {
    text: "Show the amendment history for our Pinnacle Services Data Processing Agreement DPA-PIN-202411-069.",
    type: "postgres",
    desc: "Cypher: AMENDS/ADDENDUM_TO edges on a specific contract",
    category: "families"
  },
  {
    text: "Which contract families have the highest concentration of high-risk clauses when you sum across the MSA and all its children?",
    type: "postgres",
    desc: "Cypher + SQL: traverse family tree, aggregate risk across hierarchy",
    category: "families"
  },
  
  // C. Clause-Level Risk Analysis (PostgreSQL: SQL filtering + aggregation)
  {
    text: "Which clause types have the most high-risk flags across our portfolio? Show the breakdown by clause type.",
    type: "postgres",
    desc: "SQL GROUP BY: clause_types × risk_level distribution",
    category: "clause-risk"
  },
  {
    text: "Show me all high-risk Termination and Payment Terms clauses, with the contract and vendor for each.",
    type: "postgres",
    desc: "SQL join: clauses → contracts → parties, filtered by risk + type",
    category: "clause-risk"
  },
  {
    text: "Which vendors have the highest number of high-risk Confidentiality or Data Protection clauses?",
    type: "postgres",
    desc: "SQL aggregation: vendor risk ranking by specific clause types",
    category: "clause-risk"
  },
  
  // D. Monetary Exposure (PostgreSQL: SQL aggregation on typed numeric fields)
  {
    text: "What are our largest monetary exposures? Show the top 10 contracts by value with the vendor name and value type.",
    type: "postgres",
    desc: "SQL ORDER BY amount DESC: monetary_values → contracts → parties",
    category: "monetary"
  },
  {
    text: "What is the total contract value by vendor, ranked from highest to lowest?",
    type: "postgres",
    desc: "SQL SUM + GROUP BY: financial portfolio overview",
    category: "monetary"
  },
  {
    text: "Which contracts combine a large monetary value (over $5M) with high-risk clauses? Show the vendor, amount, and risk summary.",
    type: "postgres",
    desc: "SQL join: monetary_values + clauses + risk filtering",
    category: "monetary"
  },
  
  // E. Obligations, Rights & Expirations (PostgreSQL: date filtering + relationship joins)
  {
    text: "Which contracts are expiring in 2026? Show the reference number, expiration date, and vendor.",
    type: "postgres",
    desc: "SQL date range filter: active contracts approaching expiration",
    category: "obligations"
  },
  {
    text: "Find all contracts with auto-renewal clauses — which vendors are they with and what are the notice periods?",
    type: "postgres",
    desc: "SQL text search: auto-renewal detection in clause content",
    category: "obligations"
  },
  {
    text: "Who are the parties responsible for the most high-impact obligations? Rank by count and show their top contract.",
    type: "postgres",
    desc: "SQL aggregation: obligations → responsible_party + is_high_impact",
    category: "obligations"
  },
  
  // F. Jurisdiction & Governing Law (PostgreSQL: SQL GROUP BY on structured fields)
  {
    text: "How does our risk profile differ by governing law? Compare contracts governed by England and Wales, California, and Delaware — how many high, medium, and low-risk clauses does each have?",
    type: "postgres",
    desc: "SQL cross-tab: governing_law × risk_level pivot",
    category: "regional"
  },
  {
    text: "Which vendors do we have the most contracts with under Singapore governing law?",
    type: "postgres",
    desc: "SQL filter + GROUP BY: jurisdiction-specific vendor analysis",
    category: "regional"
  },
  
  // G. Semantic Search (PostgreSQL: pgvector embedding similarity)
  {
    text: "Find clauses that discuss limitations on liability for indirect or consequential damages.",
    type: "postgres",
    desc: "pgvector semantic search: conceptual clause matching by meaning, not keywords",
    category: "semantic"
  },
  {
    text: "Search for clauses related to data breach notification requirements and timelines.",
    type: "postgres",
    desc: "pgvector semantic search: find similar language across contracts",
    category: "semantic"
  },
  
  // H. Strategic Insights & Portfolio-Wide Patterns (GraphRAG: community summarization)
  {
    text: "What are the common risk themes and patterns that emerge across our entire contract portfolio?",
    type: "graphrag",
    desc: "GraphRAG global search: community-level risk pattern synthesis across 700+ contracts",
    category: "portfolio"
  },
  {
    text: "How do our vendor contracts typically structure liability and indemnification obligations? What patterns emerge across different vendor types?",
    type: "graphrag",
    desc: "GraphRAG global search: cross-community thematic analysis of liability language",
    category: "portfolio"
  },
  {
    text: "Provide a high-level narrative summary of how intellectual property ownership and work product rights are handled across our technology vendor contracts.",
    type: "graphrag",
    desc: "GraphRAG global search: abstractive synthesis from community reports — not a keyword search",
    category: "portfolio"
  },
  {
    text: "What are the strategic implications of our data protection and confidentiality obligations across different vendor relationships? Where are the biggest gaps?",
    type: "graphrag",
    desc: "GraphRAG global search: strategic narrative synthesis across data protection communities",
    category: "portfolio"
  },
  {
    text: "Looking across all our contracts, what thematic differences exist between our IT services agreements and our consulting agreements?",
    type: "graphrag",
    desc: "GraphRAG global search: cross-community comparison — qualitative, not quantitative",
    category: "portfolio"
  }
];

export const HybridQuerySection: React.FC<HybridQuerySectionProps> = ({ onResult }) => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [strategy, setStrategy] = useState<'auto' | 'postgres' | 'graphrag' | 'hybrid'>('postgres');
  const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
  const [viewMode, setViewMode] = useState<'compact' | 'full'>('compact');

  const toggleCategory = (category: string) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(category)) {
      newExpanded.delete(category);
    } else {
      newExpanded.add(category);
    }
    setExpandedCategories(newExpanded);
  };

  const categories = [
    { id: 'vendor-risk', name: 'A. Vendor Risk & Exposure', icon: Database, color: 'red', count: SAMPLE_QUERIES.filter(q => q.category === 'vendor-risk').length },
    { id: 'families', name: 'B. Contract Families & Hierarchies', icon: GitBranch, color: 'blue', count: SAMPLE_QUERIES.filter(q => q.category === 'families').length },
    { id: 'clause-risk', name: 'C. Clause-Level Risk Analysis', icon: Database, color: 'orange', count: SAMPLE_QUERIES.filter(q => q.category === 'clause-risk').length },
    { id: 'monetary', name: 'D. Monetary Exposure', icon: Database, color: 'yellow', count: SAMPLE_QUERIES.filter(q => q.category === 'monetary').length },
    { id: 'obligations', name: 'E. Obligations, Rights & Expirations', icon: Database, color: 'green', count: SAMPLE_QUERIES.filter(q => q.category === 'obligations').length },
    { id: 'regional', name: 'F. Governing Law & Jurisdiction', icon: Database, color: 'cyan', count: SAMPLE_QUERIES.filter(q => q.category === 'regional').length },
    { id: 'semantic', name: 'G. Semantic Clause Search', icon: Brain, color: 'teal', count: SAMPLE_QUERIES.filter(q => q.category === 'semantic').length },
    { id: 'portfolio', name: 'H. Strategic Insights (GraphRAG)', icon: Sparkles, color: 'purple', count: SAMPLE_QUERIES.filter(q => q.category === 'portfolio').length }
  ];

  // Filter queries based on selected strategy
  const getFilteredQueries = (categoryId: string) => {
    const allQueries = SAMPLE_QUERIES.filter(q => q.category === categoryId);
    
    if (strategy === 'postgres') {
      // PostgreSQL: Show A-G (exclude H which is graphrag-focused)
      return categoryId === 'portfolio' ? [] : allQueries;
    } else if (strategy === 'graphrag') {
      // GraphRAG: Show only H (portfolio/strategic insights)
      return categoryId === 'portfolio' ? allQueries : [];
    } else {
      // Auto/Hybrid: Show all categories
      return allQueries;
    }
  };

  const getVisibleCategories = () => {
    if (strategy === 'postgres') {
      return categories.filter(cat => cat.id !== 'portfolio');
    } else if (strategy === 'graphrag') {
      return categories.filter(cat => cat.id === 'portfolio');
    } else {
      return categories;
    }
  };

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

  // Helper to get color classes based on category
  const getColorClasses = (color: string) => {
    const colorMap = {
      red: {
        icon: 'text-red-400',
        title: 'text-red-300',
        badge: 'bg-red-500/20 text-red-300 border-red-400/30',
        bg: 'bg-red-900/20',
        border: 'border-red-500/10 hover:border-red-400/30',
        hover: 'hover:bg-red-900/20',
        fullBg: 'hover:from-red-900/30',
        fullBorder: 'border-red-500/20 hover:border-red-400/50',
        shadow: 'hover:shadow-red-500/20',
        text: 'text-red-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-red-500/20 text-red-300 border-red-400/30'
      },
      blue: {
        icon: 'text-blue-400',
        title: 'text-blue-300',
        badge: 'bg-blue-500/20 text-blue-300 border-blue-400/30',
        bg: 'bg-blue-900/20',
        border: 'border-blue-500/10 hover:border-blue-400/30',
        hover: 'hover:bg-blue-900/20',
        fullBg: 'hover:from-blue-900/30',
        fullBorder: 'border-blue-500/20 hover:border-blue-400/50',
        shadow: 'hover:shadow-blue-500/20',
        text: 'text-blue-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-blue-500/20 text-blue-300 border-blue-400/30'
      },
      green: {
        icon: 'text-green-400',
        title: 'text-green-300',
        badge: 'bg-green-500/20 text-green-300 border-green-400/30',
        bg: 'bg-green-900/20',
        border: 'border-green-500/10 hover:border-green-400/30',
        hover: 'hover:bg-green-900/20',
        fullBg: 'hover:from-green-900/30',
        fullBorder: 'border-green-500/20 hover:border-green-400/50',
        shadow: 'hover:shadow-green-500/20',
        text: 'text-green-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-green-500/20 text-green-300 border-green-400/30'
      },
      yellow: {
        icon: 'text-yellow-400',
        title: 'text-yellow-300',
        badge: 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30',
        bg: 'bg-yellow-900/20',
        border: 'border-yellow-500/10 hover:border-yellow-400/30',
        hover: 'hover:bg-yellow-900/20',
        fullBg: 'hover:from-yellow-900/30',
        fullBorder: 'border-yellow-500/20 hover:border-yellow-400/50',
        shadow: 'hover:shadow-yellow-500/20',
        text: 'text-yellow-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-yellow-500/20 text-yellow-300 border-yellow-400/30'
      },
      purple: {
        icon: 'text-purple-400',
        title: 'text-purple-300',
        badge: 'bg-purple-500/20 text-purple-300 border-purple-400/30',
        bg: 'bg-purple-900/20',
        border: 'border-purple-500/10 hover:border-purple-400/30',
        hover: 'hover:bg-purple-900/20',
        fullBg: 'hover:from-purple-900/30',
        fullBorder: 'border-purple-500/20 hover:border-purple-400/50',
        shadow: 'hover:shadow-purple-500/20',
        text: 'text-purple-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-purple-500/20 text-purple-300 border-purple-400/30'
      },
      orange: {
        icon: 'text-orange-400',
        title: 'text-orange-300',
        badge: 'bg-orange-500/20 text-orange-300 border-orange-400/30',
        bg: 'bg-orange-900/20',
        border: 'border-orange-500/10 hover:border-orange-400/30',
        hover: 'hover:bg-orange-900/20',
        fullBg: 'hover:from-orange-900/30',
        fullBorder: 'border-orange-500/20 hover:border-orange-400/50',
        shadow: 'hover:shadow-orange-500/20',
        text: 'text-orange-100',
        textHover: 'group-hover:text-white',
        desc: 'bg-orange-500/20 text-orange-300 border-orange-400/30'
      }
    };
    return colorMap[color as keyof typeof colorMap] || colorMap.blue;
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
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-purple-300">Sample Queries</h3>
            <span className="text-xs text-purple-400 bg-purple-500/10 px-3 py-1 rounded-full border border-purple-400/30">
              {getVisibleCategories().reduce((sum, cat) => sum + getFilteredQueries(cat.id).length, 0)} queries • {getVisibleCategories().length} categories
            </span>
          </div>
          <div className="flex gap-2">
            <button
              onClick={() => setViewMode('compact')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'compact' ? 'bg-purple-600 text-white' : 'bg-slate-800/50 text-purple-300 hover:bg-slate-700/50'}`}
              title="Compact View"
            >
              <List className="w-4 h-4" />
            </button>
            <button
              onClick={() => setViewMode('full')}
              className={`p-2 rounded-lg transition-all ${viewMode === 'full' ? 'bg-purple-600 text-white' : 'bg-slate-800/50 text-purple-300 hover:bg-slate-700/50'}`}
              title="Full View"
            >
              <Grid3x3 className="w-4 h-4" />
            </button>
          </div>
        </div>
        
        {/* Collapsible Categories */}
        <div className="space-y-2">
          {getVisibleCategories().map((cat) => {
            const Icon = cat.icon;
            const isExpanded = expandedCategories.has(cat.id);
            const queries = getFilteredQueries(cat.id);
            const colors = getColorClasses(cat.color);

            // Skip if no queries for this category in current mode
            if (queries.length === 0) return null;

            return (
              <div key={cat.id} className="border border-slate-700/50 rounded-xl overflow-hidden bg-slate-800/30">
                {/* Category Header */}
                <button
                  onClick={() => toggleCategory(cat.id)}
                  className={`w-full p-4 flex items-center justify-between hover:bg-slate-700/30 transition-all ${
                    isExpanded ? colors.bg : ''
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <Icon className={`w-5 h-5 ${colors.icon}`} />
                    <h4 className={`text-sm font-bold ${colors.title} uppercase tracking-wider`}>
                      {cat.name}
                    </h4>
                    <span className={`text-xs px-2 py-1 rounded-full ${colors.badge}`}>
                      {cat.count}
                    </span>
                  </div>
                  {isExpanded ? (
                    <ChevronUp className={`w-5 h-5 ${colors.icon}`} />
                  ) : (
                    <ChevronDown className={`w-5 h-5 ${colors.icon}`} />
                  )}
                </button>

                {/* Category Content */}
                {isExpanded && (
                  <div className="p-2 space-y-2 bg-slate-900/30">
                    {viewMode === 'compact' ? (
                      // Compact View - Just query text
                      queries.map((sample, idx) => (
                        <button
                          key={`${cat.id}-${idx}`}
                          onClick={() => handleSearch(sample.text, sample.type)}
                          disabled={loading}
                          className={`w-full text-left px-4 py-2 rounded-lg ${colors.hover} ${colors.border} transition-all group disabled:opacity-50`}
                        >
                          <p className={`text-sm ${colors.text} ${colors.textHover} transition-colors line-clamp-2`}>
                            {sample.text}
                          </p>
                        </button>
                      ))
                    ) : (
                      // Full View - Query with description
                      queries.map((sample, idx) => (
                        <button
                          key={`${cat.id}-${idx}`}
                          onClick={() => handleSearch(sample.text, sample.type)}
                          disabled={loading}
                          className={`w-full text-left p-4 bg-slate-800/50 hover:bg-gradient-to-r ${colors.fullBg} hover:to-slate-800/50 rounded-xl ${colors.fullBorder} transition-all duration-300 group disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg ${colors.shadow}`}
                        >
                          <div className="flex items-start justify-between gap-3">
                            <div className="flex-1">
                              <p className={`${colors.text} ${colors.textHover} transition-colors font-medium mb-2 text-sm`}>
                                {sample.text}
                              </p>
                              <span className={`text-xs px-3 py-1 rounded-full font-semibold ${colors.desc}`}>
                                {sample.desc}
                              </span>
                            </div>
                            <Search className={`w-5 h-5 ${colors.icon} opacity-0 group-hover:opacity-100 transition-opacity flex-shrink-0`} />
                          </div>
                        </button>
                      ))
                    )}
                  </div>
                )}
              </div>
            );
          })}
          
          {/* Expand/Collapse All */}
          <div className="flex gap-2 justify-center pt-2">
            <button
              onClick={() => setExpandedCategories(new Set(categories.map(c => c.id)))}
              className="text-xs px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 text-purple-300 rounded-lg border border-purple-500/20 hover:border-purple-400/40 transition-all"
            >
              Expand All
            </button>
            <button
              onClick={() => setExpandedCategories(new Set())}
              className="text-xs px-4 py-2 bg-slate-800/50 hover:bg-slate-700/50 text-purple-300 rounded-lg border border-purple-500/20 hover:border-purple-400/40 transition-all"
            >
              Collapse All
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
