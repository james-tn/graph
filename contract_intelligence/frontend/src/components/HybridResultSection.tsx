import React, { useEffect, useRef } from 'react';
import { CheckCircle2, Database, Brain, GitBranch, AlertCircle, Sparkles, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';

// Initialize mermaid
if (typeof window !== 'undefined') {
  mermaid.initialize({ 
    startOnLoad: true, 
    theme: 'dark',
    themeVariables: {
      primaryColor: '#a855f7',
      primaryTextColor: '#fff',
      primaryBorderColor: '#9333ea',
      lineColor: '#c084fc',
      secondaryColor: '#ec4899',
      tertiaryColor: '#3b82f6',
      background: '#1e293b',
      mainBkg: '#1e293b',
      textColor: '#e2e8f0',
      fontSize: '14px'
    }
  });
}

// Mermaid component for rendering diagrams
const MermaidDiagram: React.FC<{ chart: string }> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (ref.current && chart) {
      try {
        mermaid.render(`mermaid-${Math.random()}`, chart).then(({ svg }) => {
          if (ref.current) {
            ref.current.innerHTML = svg;
          }
        });
      } catch (error) {
        console.error('Mermaid rendering error:', error);
        if (ref.current) {
          ref.current.innerHTML = `<pre class="text-red-400">Error rendering diagram</pre>`;
        }
      }
    }
  }, [chart]);

  return <div ref={ref} className="my-6 flex justify-center" />;
};

interface HybridResultSectionProps {
  result: any;
}

export const HybridResultSection: React.FC<HybridResultSectionProps> = ({ result }) => {
  if (!result) return null;

  if (result.error) {
    return (
      <div className="glass-dark p-8 rounded-3xl shadow-2xl border border-red-500/30 backdrop-blur-xl">
        <div className="flex items-center gap-4 mb-4">
          <AlertCircle className="w-8 h-8 text-red-400" />
          <h2 className="text-2xl font-bold text-red-300">Error</h2>
        </div>
        <p className="text-red-200">{result.error}</p>
      </div>
    );
  }

  const { query, routing, postgres_result, graphrag_result, unified_response, sources } = result;

  // Determine strategy colors
  const getStrategyColor = (strategy: string) => {
    switch (strategy) {
      case 'postgres': return 'blue';
      case 'graphrag': return 'green';
      case 'hybrid': return 'purple';
      default: return 'purple';
    }
  };

  const color = getStrategyColor(routing.strategy);

  return (
    <div className="space-y-6">
      {/* Routing Info */}
      <div className={`glass-dark p-6 rounded-2xl border border-${color}-500/30 backdrop-blur-xl`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className={`p-3 bg-gradient-to-br from-${color}-500 to-${color}-600 rounded-xl shadow-lg`}>
              {routing.strategy === 'postgres' ? <Database className="w-6 h-6 text-white" /> :
               routing.strategy === 'graphrag' ? <Brain className="w-6 h-6 text-white" /> :
               <GitBranch className="w-6 h-6 text-white" />}
            </div>
            <div>
              <h3 className={`text-xl font-bold text-${color}-300`}>
                {routing.strategy === 'postgres' ? 'PostgreSQL Database' :
                 routing.strategy === 'graphrag' ? 'Microsoft GraphRAG' :
                 'Hybrid Search'}
              </h3>
              <p className={`text-sm text-${color}-400`}>{routing.reasoning}</p>
            </div>
          </div>
          <div className={`px-4 py-2 bg-${color}-500/20 rounded-full border border-${color}-400/30`}>
            <span className={`text-xs font-bold text-${color}-300 uppercase`}>{routing.strategy}</span>
          </div>
        </div>
      </div>

      {/* Main Response */}
      <div className="glass-dark p-8 rounded-3xl shadow-2xl border border-purple-500/20 backdrop-blur-xl">
        <div className="flex items-center gap-4 mb-6">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-600 rounded-2xl shadow-lg shadow-purple-500/50">
            <CheckCircle2 className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
            Results
          </h2>
        </div>

        {/* Unified Response */}
        <div className="prose prose-invert prose-purple max-w-none">
          <div className="text-purple-100 leading-relaxed space-y-4">
            <ReactMarkdown 
              remarkPlugins={[remarkGfm]}
              components={{
                h1: ({node, ...props}) => <h1 className="text-3xl font-bold text-purple-200 mt-8 mb-4" {...props} />,
                h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-purple-300 mt-6 mb-3" {...props} />,
                h3: ({node, ...props}) => <h3 className="text-xl font-bold text-purple-300 mt-6 mb-3" {...props} />,
                p: ({node, ...props}) => <p className="text-purple-100 mb-4 leading-relaxed" {...props} />,
                strong: ({node, ...props}) => <strong className="text-white font-bold" {...props} />,
                em: ({node, ...props}) => <em className="text-purple-200 italic" {...props} />,
                ul: ({node, ...props}) => <ul className="list-disc list-inside space-y-2 ml-4 mb-4" {...props} />,
                ol: ({node, ...props}) => <ol className="list-decimal list-inside space-y-2 ml-4 mb-4" {...props} />,
                li: ({node, ...props}) => <li className="text-purple-200" {...props} />,
                blockquote: ({node, ...props}) => (
                  <blockquote className="border-l-4 border-purple-500 pl-4 py-2 my-4 bg-purple-900/20 italic text-purple-200" {...props} />
                ),
                hr: ({node, ...props}) => <hr className="my-6 border-purple-500/30" {...props} />,
                table: ({node, ...props}) => (
                  <div className="overflow-x-auto my-6">
                    <table className="min-w-full border-collapse border border-purple-500/30" {...props} />
                  </div>
                ),
                thead: ({node, ...props}) => <thead className="bg-purple-900/40" {...props} />,
                tbody: ({node, ...props}) => <tbody {...props} />,
                tr: ({node, ...props}) => <tr className="border-b border-purple-500/20" {...props} />,
                th: ({node, ...props}) => (
                  <th className="px-4 py-2 text-left font-bold text-purple-300 border border-purple-500/30" {...props} />
                ),
                td: ({node, ...props}) => (
                  <td className="px-4 py-2 text-purple-200 border border-purple-500/20" {...props} />
                ),
                code: ({node, inline, className, children, ...props}: any) => {
                  const match = /language-(\w+)/.exec(className || '');
                  const language = match ? match[1] : null;
                  
                  // Check if it's a mermaid diagram
                  if (!inline && language === 'mermaid') {
                    return <MermaidDiagram chart={String(children).replace(/\n$/, '')} />;
                  }
                  
                  // Regular code block
                  if (!inline) {
                    return (
                      <pre className="bg-slate-900/70 p-4 rounded-lg my-4 overflow-x-auto border border-purple-500/20">
                        <code className="text-pink-300 font-mono text-sm" {...props}>
                          {children}
                        </code>
                      </pre>
                    );
                  }
                  
                  // Inline code
                  return <code className="bg-slate-800/70 px-2 py-1 rounded text-pink-300 font-mono text-sm" {...props}>{children}</code>;
                },
                a: ({node, ...props}) => (
                  <a className="text-blue-400 hover:text-blue-300 underline" target="_blank" rel="noopener noreferrer" {...props} />
                ),
              }}
            >
              {unified_response}
            </ReactMarkdown>
          </div>
        </div>
      </div>

      {/* Source Attribution */}
      {sources && sources.length > 0 && (
        <div className="glass-dark p-6 rounded-2xl border border-purple-500/20 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-4">
            <Sparkles className="w-5 h-5 text-purple-400" />
            <h3 className="text-lg font-bold text-purple-300">Sources Used</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {sources.map((source: any, idx: number) => (
              <div key={idx} className={`p-4 rounded-xl border ${
                source.type === 'postgres' 
                  ? 'bg-blue-500/10 border-blue-400/30'
                  : 'bg-green-500/10 border-green-400/30'
              }`}>
                <div className="flex items-start gap-3">
                  {source.type === 'postgres' ? (
                    <Database className="w-5 h-5 text-blue-400 mt-1" />
                  ) : (
                    <Brain className="w-5 h-5 text-green-400 mt-1" />
                  )}
                  <div>
                    <h4 className={`font-bold mb-1 ${
                      source.type === 'postgres' ? 'text-blue-300' : 'text-green-300'
                    }`}>
                      {source.name}
                    </h4>
                    <p className={`text-sm ${
                      source.type === 'postgres' ? 'text-blue-200' : 'text-green-200'
                    }`}>
                      {source.description}
                    </p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Detailed Results (Expandable) */}
      {(postgres_result || graphrag_result) && (
        <details className="glass-dark p-6 rounded-2xl border border-purple-500/20 backdrop-blur-xl">
          <summary className="cursor-pointer text-purple-300 font-bold hover:text-purple-200 transition-colors flex items-center gap-2">
            <ExternalLink className="w-4 h-4" />
            View Detailed Source Responses
          </summary>
          <div className="mt-4 space-y-4">
            {postgres_result && !postgres_result.error && (
              <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-400/30">
                <h4 className="text-blue-300 font-bold mb-2 flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  PostgreSQL Response
                </h4>
                {postgres_result.tool_calls && postgres_result.tool_calls.length > 0 && (
                  <div className="mb-3 space-y-3">
                    <p className="text-xs text-blue-400 font-semibold">
                      {postgres_result.tool_calls.length > 1 ? `${postgres_result.tool_calls.length} Tool Calls` : 'Tool Call'}:
                    </p>
                    {postgres_result.tool_calls.map((toolCall: any, idx: number) => (
                      <div key={idx} className="p-3 bg-slate-900/50 rounded border border-blue-500/20 space-y-2">
                        {postgres_result.tool_calls.length > 1 && (
                          <p className="text-xs text-blue-300 font-semibold mb-2">Tool Call {idx + 1}</p>
                        )}
                        {toolCall.reasoning && (
                          <div className="mb-2">
                            <p className="text-xs text-blue-400 mb-1">🤔 Model's Reasoning:</p>
                            <p className="text-sm text-blue-200 italic pl-3 border-l-2 border-blue-500/40">
                              {toolCall.reasoning}
                            </p>
                          </div>
                        )}
                        <div>
                          <p className="text-xs text-blue-400 mb-1">📝 SQL Query:</p>
                          <pre className="text-xs text-blue-200 whitespace-pre-wrap font-mono overflow-x-auto pl-3">
                            {toolCall.sql_query}
                          </pre>
                        </div>
                        {toolCall.need_embedding && toolCall.search_text && (
                          <div className="text-xs text-blue-300/70 mt-2">
                            🔍 Semantic search for: "{toolCall.search_text}"
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
                <details className="mt-2">
                  <summary className="cursor-pointer text-xs text-blue-400 hover:text-blue-300">
                    View Full Response JSON
                  </summary>
                  <pre className="text-sm text-blue-100 whitespace-pre-wrap font-mono mt-2">
                    {JSON.stringify(postgres_result, null, 2)}
                  </pre>
                </details>
              </div>
            )}
            {graphrag_result && !graphrag_result.error && (
              <div className="p-4 bg-green-500/10 rounded-xl border border-green-400/30">
                <h4 className="text-green-300 font-bold mb-2 flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  GraphRAG Response
                </h4>
                <div className="text-sm text-green-100 space-y-2">
                  <p><strong>Search Type:</strong> {graphrag_result.search_type}</p>
                  <p><strong>Completion Time:</strong> {graphrag_result.completion_time?.toFixed(2)}s</p>
                  <p><strong>LLM Calls:</strong> {graphrag_result.llm_calls}</p>
                  {graphrag_result.response && (
                    <div className="mt-2 p-3 bg-slate-900/50 rounded">
                      <p className="whitespace-pre-wrap">{graphrag_result.response}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
};
