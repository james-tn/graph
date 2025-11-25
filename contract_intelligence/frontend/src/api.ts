import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

export const uploadFile = async (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const runIndex = async () => {
  const response = await api.post('/index');
  return response.data;
};

export const runQuery = async (query: string) => {
  const response = await api.post('/query', { query });
  return response.data;
};

// Hybrid Search API
export const runHybridQuery = async (query: string, strategy: string = 'auto') => {
  const response = await api.post('/query', { query, strategy });
  return response.data;
};

export const analyzeQuery = async (query: string) => {
  const response = await api.post('/analyze', { query });
  return response.data;
};

export const getStats = async () => {
  const response = await api.get('/stats');
  return response.data;
};

export const runIngestion = async (runPostgres: boolean = true, runGraphrag: boolean = true) => {
  const response = await api.post('/ingest', { 
    run_postgres: runPostgres,
    run_graphrag: runGraphrag
  });
  return response.data;
};
