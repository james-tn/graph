import React from 'react';
import ReactMarkdown from 'react-markdown';
import { BookOpen, Quote } from 'lucide-react';

interface Source {
  id: number | string;
  text: string;
  [key: string]: any;
}

interface ResultSectionProps {
  result: {
    answer: string;
    sources: Source[];
    error?: string;
  } | null;
}

export const ResultSection: React.FC<ResultSectionProps> = ({ result }) => {
  if (!result) return null;

  if (result.error) {
    return (
      <div className="glass-dark p-6 rounded-2xl border-2 border-red-500/30 text-red-300">
        {result.error}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <div className="lg:col-span-2 glass-dark p-8 rounded-3xl shadow-2xl border border-green-500/20">
        <div className="flex items-center gap-4 mb-8 pb-6 border-b border-green-500/20">
          <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl shadow-lg shadow-green-500/50">
            <BookOpen className="w-7 h-7 text-white" />
          </div>
          <h2 className="text-3xl font-bold bg-gradient-to-r from-green-400 to-emerald-400 bg-clip-text text-transparent">AI Analysis</h2>
        </div>
        <div className="markdown-content prose prose-lg prose-invert max-w-none">
          <ReactMarkdown
            components={{
              h2: ({node, ...props}) => <h2 className="text-2xl font-bold text-blue-200 mb-4 mt-6" {...props} />,
              h3: ({node, ...props}) => <h3 className="text-xl font-semibold text-blue-300 mb-3 mt-5" {...props} />,
              p: ({node, ...props}) => <p className="text-blue-100 leading-relaxed mb-4" {...props} />,
              strong: ({node, ...props}) => <strong className="text-white font-bold" {...props} />,
              ul: ({node, ...props}) => <ul className="text-blue-100 list-disc list-inside mb-4 space-y-2" {...props} />,
              ol: ({node, ...props}) => <ol className="text-blue-100 list-decimal list-inside mb-4 space-y-2" {...props} />,
              li: ({node, ...props}) => <li className="text-blue-100" {...props} />,
            }}
          >
            {result.answer}
          </ReactMarkdown>
        </div>
      </div>

      <div className="glass-dark p-6 rounded-3xl border-2 border-amber-500/30 h-fit max-h-[80vh] overflow-y-auto shadow-2xl">
        <div className="flex items-center gap-3 mb-6 pb-4 border-b border-amber-500/20">
          <div className="p-2 bg-gradient-to-br from-amber-500 to-orange-600 rounded-xl shadow-lg shadow-amber-500/50">
            <Quote className="w-6 h-6 text-white" />
          </div>
          <h2 className="text-xl font-bold bg-gradient-to-r from-amber-400 to-orange-400 bg-clip-text text-transparent">Citations</h2>
        </div>
        <div className="space-y-4">
          {result.sources.length > 0 ? (
            result.sources.map((source, idx) => (
              <div key={idx} className="group relative bg-slate-900/60 p-5 rounded-2xl border-2 border-amber-500/20 hover:border-amber-500/60 text-sm shadow-lg hover:shadow-amber-500/30 transition-all duration-300 transform hover:scale-105 backdrop-blur-sm">
                <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-amber-600/5 to-orange-600/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                <div className="relative">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-mono text-xs font-bold text-white bg-gradient-to-r from-amber-500 to-orange-500 px-3 py-1.5 rounded-full shadow-lg shadow-amber-500/30">
                      #{source.id}
                    </div>
                    <div className="text-xs text-amber-300 font-medium">Click to expand</div>
                  </div>
                  <div className="text-blue-200 line-clamp-4 group-hover:line-clamp-none transition-all cursor-pointer leading-relaxed">
                    {source.text}
                  </div>
                </div>
              </div>
            ))
          ) : (
            <div className="text-amber-300 italic text-sm bg-amber-500/10 p-5 rounded-2xl border-2 border-amber-500/20">No specific citations returned.</div>
          )}
        </div>
      </div>
    </div>
  );
};
