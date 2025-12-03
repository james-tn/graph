import React, { useEffect, useRef } from 'react';
import { CheckCircle2, Database, Brain, AlertCircle, Sparkles, ExternalLink } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import mermaid from 'mermaid';

// Initialize mermaid
if (typeof window !== 'undefined') {
  mermaid.initialize({ 
    startOnLoad: true,
    theme: 'default',  // Use default light theme - clean and universally readable
    themeVariables: {
      fontSize: '14px',
      fontFamily: 'ui-sans-serif, system-ui, sans-serif'
    }
  });
}

// Add CSS to make the mermaid container have a light background
const style = document.createElement('style');
style.textContent = `
  .mermaid svg {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
  }
`;
document.head.appendChild(style);// Mermaid component for rendering diagrams with auto-correction
const MermaidDiagram: React.FC<{ chart: string }> = ({ chart }) => {
  const ref = useRef<HTMLDivElement>(null);
  const [correctedChart, setCorrectedChart] = React.useState<string>(chart);
  const [isFixing, setIsFixing] = React.useState(false);
  const [fixAttempts, setFixAttempts] = React.useState(0);
  const [hasError, setHasError] = React.useState(false);
  const maxAttempts = 3;

  const fixMermaidDiagram = async (code: string, errorMsg: string, currentAttempt: number) => {
    console.log(`[fixMermaidDiagram] Called with attempt ${currentAttempt}, max ${maxAttempts}`);
    
    if (currentAttempt >= maxAttempts) {
      console.error('[fixMermaidDiagram] Max correction attempts reached');
      return null;
    }

    console.log('[fixMermaidDiagram] Setting isFixing=true, incrementing fixAttempts');
    setIsFixing(true);
    setFixAttempts(currentAttempt + 1);

    try {
      console.log(`[fixMermaidDiagram] Sending POST to /api/mermaid/fix (attempt ${currentAttempt + 1}/${maxAttempts})`);
      console.log(`[fixMermaidDiagram] Error message: ${errorMsg}`);
      console.log(`[fixMermaidDiagram] Code length: ${code.length} chars`);
      
      const response = await fetch('/api/mermaid/fix', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          mermaid_code: code,
          error_message: errorMsg
        })
      });

      console.log(`[fixMermaidDiagram] Response status: ${response.status}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fix diagram: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('[fixMermaidDiagram] Received corrected diagram from backend');
      console.log(`[fixMermaidDiagram] Corrected code length: ${data.corrected_code?.length || 0} chars`);
      setIsFixing(false);
      return data.corrected_code;
    } catch (error) {
      console.error('[fixMermaidDiagram] Error during fix:', error);
      setIsFixing(false);
      return null;
    }
  };

  useEffect(() => {
    const renderDiagram = async (diagramCode: string) => {
      if (!ref.current) return;

      // Skip if already showing an error and max attempts reached
      if (hasError && fixAttempts >= maxAttempts) {
        return;
      }

      try {
        // Generate a valid DOM ID (must start with letter, no dots)
        const id = `mermaid-${Date.now()}-${Math.floor(Math.random() * 10000)}`;
        
        console.log('Attempting to render Mermaid diagram...');
        const { svg } = await mermaid.render(id, diagramCode);
        
        if (ref.current) {
          ref.current.innerHTML = svg;
          setHasError(false);
          console.log('Mermaid diagram rendered successfully');
        }
      } catch (error: any) {
        console.error('Mermaid rendering error:', error);
        console.log('[renderDiagram] Error details:', {
          message: error?.message,
          hasError,
          fixAttempts,
          maxAttempts,
          willAttemptFix: fixAttempts < maxAttempts
        });
        setHasError(true);
        
        // Try to fix the diagram automatically
        const errorMessage = error?.message || error?.toString() || 'Unknown rendering error';
        console.log(`[renderDiagram] Calling fixMermaidDiagram with attempt ${fixAttempts}...`);
        const fixed = await fixMermaidDiagram(diagramCode, errorMessage, fixAttempts);
        
        console.log('[renderDiagram] fixMermaidDiagram returned:', {
          hasFixed: !!fixed,
          isDifferent: fixed !== diagramCode,
          fixedLength: fixed?.length || 0,
          originalLength: diagramCode.length
        });
        
        if (fixed && fixed !== diagramCode) {
          // Try rendering the fixed version
          console.log('[renderDiagram] Applying corrected diagram...');
          setCorrectedChart(fixed);
          setHasError(false);
        } else if (ref.current) {
          // Show error if fix failed or max attempts reached
          ref.current.innerHTML = `
            <div class="p-4 bg-red-500/10 border border-red-400/30 rounded-lg">
              <p class="text-red-400 font-semibold mb-2">⚠️ Diagram Rendering Failed</p>
              <p class="text-red-300 text-sm mb-2">${errorMessage}</p>
              ${fixAttempts >= maxAttempts ? '<p class="text-red-300 text-xs mt-2">Max auto-correction attempts reached (3 attempts)</p>' : ''}
              <details class="mt-3">
                <summary class="text-red-300 text-xs cursor-pointer hover:text-red-200">View diagram code</summary>
                <pre class="text-red-200 text-xs mt-2 overflow-x-auto bg-red-900/20 p-2 rounded">${diagramCode}</pre>
              </details>
            </div>
          `;
        }
      }
    };

    if (ref.current && correctedChart) {
      if (isFixing) {
        ref.current.innerHTML = `
          <div class="p-4 bg-yellow-500/10 border border-yellow-400/30 rounded-lg">
            <p class="text-yellow-400 font-semibold">🔧 Auto-correcting diagram...</p>
            <p class="text-yellow-300 text-sm mt-1">Attempt ${fixAttempts + 1} of ${maxAttempts}</p>
          </div>
        `;
      } else {
        renderDiagram(correctedChart);
      }
    }
  }, [correctedChart, isFixing, fixAttempts, hasError]);

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

  const { postgres_result, graphrag_result, unified_response, sources } = result;

  return (
    <div className="space-y-6">
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

      {/* SQL Queries Used (PostgreSQL) */}
      {postgres_result && !postgres_result.error && postgres_result.tool_calls && postgres_result.tool_calls.length > 0 && (
        <div className="glass-dark p-6 rounded-2xl border border-blue-500/20 backdrop-blur-xl">
          <div className="flex items-center gap-3 mb-4">
            <Database className="w-5 h-5 text-blue-400" />
            <h3 className="text-lg font-bold text-blue-300">SQL Queries Executed</h3>
            <span className="text-xs text-blue-400 bg-blue-500/10 px-3 py-1 rounded-full border border-blue-400/30">
              {postgres_result.tool_calls.length} {postgres_result.tool_calls.length > 1 ? 'queries' : 'query'}
            </span>
          </div>
          <div className="space-y-3">
            {postgres_result.tool_calls.map((toolCall: any, idx: number) => (
              <div key={idx} className="p-4 bg-slate-900/50 rounded-xl border border-blue-500/20">
                {postgres_result.tool_calls.length > 1 && (
                  <p className="text-xs text-blue-300 font-semibold mb-3">Query {idx + 1}</p>
                )}
                {toolCall.reasoning && (
                  <div className="mb-3">
                    <p className="text-xs text-blue-400 mb-1 flex items-center gap-1">
                      <span>💭</span> Agent's Reasoning:
                    </p>
                    <p className="text-sm text-blue-200 italic pl-3 border-l-2 border-blue-500/40">
                      {toolCall.reasoning}
                    </p>
                  </div>
                )}
                <div>
                  <p className="text-xs text-blue-400 mb-2 flex items-center gap-1">
                    <span>⚡</span> SQL Query:
                  </p>
                  <pre className="text-sm text-blue-100 bg-slate-950/70 p-3 rounded border border-blue-500/20 overflow-x-auto font-mono">
{toolCall.sql_query}
                  </pre>
                </div>
                {toolCall.need_embedding && toolCall.search_text && (
                  <div className="text-xs text-blue-300 mt-3 flex items-center gap-1">
                    <span>🔍</span> Semantic search: <span className="font-semibold">"{toolCall.search_text}"</span>
                  </div>
                )}
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
            View Raw JSON Responses
          </summary>
          <div className="mt-4 space-y-4">
            {postgres_result && !postgres_result.error && (
              <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-400/30">
                <h4 className="text-blue-300 font-bold mb-2 flex items-center gap-2">
                  <Database className="w-5 h-5" />
                  PostgreSQL Response
                </h4>
                <pre className="text-sm text-blue-100 whitespace-pre-wrap font-mono overflow-x-auto">
                  {JSON.stringify(postgres_result, null, 2)}
                </pre>
              </div>
            )}
            {graphrag_result && !graphrag_result.error && (
              <div className="p-4 bg-green-500/10 rounded-xl border border-green-400/30">
                <h4 className="text-green-300 font-bold mb-2 flex items-center gap-2">
                  <Brain className="w-5 h-5" />
                  GraphRAG Response
                </h4>
                <pre className="text-sm text-green-100 whitespace-pre-wrap font-mono overflow-x-auto">
                  {JSON.stringify(graphrag_result, null, 2)}
                </pre>
              </div>
            )}
          </div>
        </details>
      )}
    </div>
  );
};
