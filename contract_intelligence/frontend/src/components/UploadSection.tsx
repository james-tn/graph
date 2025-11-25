import React, { useState } from 'react';
import { Upload, FileText, Loader2, CheckCircle, AlertCircle, RefreshCw } from 'lucide-react';
import { uploadFile, runIndex } from '../api';

interface IndexStatus {
  status: 'idle' | 'running' | 'complete' | 'error';
  message: string;
}

export const UploadSection: React.FC = () => {
  const [files, setFiles] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [indexStatus, setIndexStatus] = useState<IndexStatus>({ status: 'idle', message: '' });
  const [message, setMessage] = useState<string | null>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
      setMessage(null);
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setUploading(true);
    let successCount = 0;
    
    try {
      for (const file of files) {
        await uploadFile(file);
        successCount++;
      }
      setMessage(`${successCount} file(s) uploaded successfully. Ready to index.`);
      setFiles([]);
    } catch (error) {
      setMessage(`Error uploading files. ${successCount} of ${files.length} uploaded.`);
      console.error(error);
    } finally {
      setUploading(false);
    }
  };

  const handleIndex = async () => {
    setIndexStatus({ status: 'running', message: 'Starting indexing process...' });
    setMessage('Indexing started in background. This may take several minutes.');
    
    // Start indexing in background
    runIndex()
      .then(() => {
        setIndexStatus({ status: 'complete', message: 'Indexing completed successfully!' });
      })
      .catch((error) => {
        setIndexStatus({ status: 'error', message: `Indexing failed: ${error.message}` });
      });
  };

  const handleCheckStatus = async () => {
    // This would call a status endpoint if we implement one
    setMessage(`Current status: ${indexStatus.status}`);
  };

  return (
    <div className="glass-dark p-8 rounded-3xl shadow-2xl border border-blue-500/20 backdrop-blur-xl hover:border-blue-500/40 transition-all duration-300">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-3xl font-bold text-white flex items-center gap-4">
          <div className="p-3 bg-gradient-to-br from-blue-500 to-purple-600 rounded-2xl shadow-lg shadow-blue-500/50">
            <Upload className="w-7 h-7 text-white" />
          </div>
          <span className="bg-gradient-to-r from-blue-400 to-purple-400 bg-clip-text text-transparent">Upload & Index</span>
        </h2>
      </div>
      
      <div className="flex flex-col gap-6">
        {/* File Upload Section */}
        <div className="space-y-4">
          <label className="block text-blue-200 font-semibold mb-2">Select Contract Files</label>
          <div className="flex items-center gap-4">
            <input
              type="file"
              multiple
              onChange={handleFileChange}
              className="block w-full text-sm text-blue-200
                file:mr-4 file:py-3 file:px-6
                file:rounded-xl file:border-0
                file:text-sm file:font-bold
                file:bg-gradient-to-r file:from-blue-600 file:to-purple-600
                file:text-white file:shadow-lg
                hover:file:from-blue-700 hover:file:to-purple-700
                file:transition-all file:duration-300
                file:cursor-pointer"
            />
            <button
              onClick={handleUpload}
              disabled={files.length === 0 || uploading}
              className="px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 font-semibold shadow-lg shadow-blue-500/50 transition-all duration-300 transform hover:scale-105 whitespace-nowrap"
            >
              {uploading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Upload className="w-5 h-5" />}
              Upload {files.length > 0 && `(${files.length})`}
            </button>
          </div>
          
          {files.length > 0 && !uploading && (
            <div className="text-sm text-blue-300">
              {files.length} file{files.length !== 1 && 's'} selected: {files.map(f => f.name).join(', ')}
            </div>
          )}
        </div>

        {/* Indexing Section */}
        <div className="border-t border-blue-500/20 pt-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-xl font-bold text-white">GraphRAG Indexing</h3>
            {indexStatus.status !== 'idle' && (
              <button
                onClick={handleCheckStatus}
                className="px-4 py-2 bg-slate-700 text-blue-300 rounded-lg hover:bg-slate-600 transition-all flex items-center gap-2 text-sm"
              >
                <RefreshCw className="w-4 h-4" />
                Check Status
              </button>
            )}
          </div>
          
          <button
            onClick={handleIndex}
            disabled={indexStatus.status === 'running'}
            className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl hover:from-green-700 hover:to-emerald-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-3 font-bold text-lg shadow-2xl shadow-green-500/50 transition-all duration-300 transform hover:scale-105"
          >
            {indexStatus.status === 'running' ? (
              <>
                <Loader2 className="w-6 h-6 animate-spin" />
                Indexing in Progress...
              </>
            ) : (
              <>
                <FileText className="w-6 h-6" />
                Run Indexing Pipeline
              </>
            )}
          </button>

          {/* Status Display */}
          {indexStatus.status !== 'idle' && (
            <div className={`p-4 rounded-xl text-sm font-medium border-2 flex items-start gap-3 ${
              indexStatus.status === 'error' 
                ? 'bg-red-500/10 text-red-300 border-red-500/30' 
                : indexStatus.status === 'complete'
                ? 'bg-green-500/10 text-green-300 border-green-500/30'
                : 'bg-blue-500/10 text-blue-300 border-blue-500/30'
            }`}>
              {indexStatus.status === 'running' && <Loader2 className="w-5 h-5 animate-spin flex-shrink-0 mt-0.5" />}
              {indexStatus.status === 'complete' && <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />}
              {indexStatus.status === 'error' && <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />}
              <div>
                <div className="font-bold mb-1">
                  {indexStatus.status === 'running' && 'Indexing in Progress'}
                  {indexStatus.status === 'complete' && 'Indexing Complete'}
                  {indexStatus.status === 'error' && 'Indexing Failed'}
                </div>
                <div>{indexStatus.message}</div>
              </div>
            </div>
          )}
        </div>

        {message && (
          <div className={`p-4 rounded-xl text-sm font-medium border-2 ${
            message.includes('Error') 
              ? 'bg-red-500/10 text-red-300 border-red-500/30' 
              : 'bg-green-500/10 text-green-300 border-green-500/30'
          }`}>
            {message}
          </div>
        )}
      </div>
    </div>
  );
};
