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

export const runIndex = async (runPostgres: boolean = true, runGraphrag: boolean = false) => {
  const response = await api.post('/index', { 
    run_postgres: runPostgres,
    run_graphrag: runGraphrag 
  });
  return response.data;
};

export const getIndexStatus = async (taskId: string) => {
  const response = await api.get(`/index/status/${taskId}`);
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

// ---------------------------------------------------------------------------
// ML hierarchy linker review queue
// ---------------------------------------------------------------------------

export interface ContractSummary {
  id: number;
  contract_identifier?: string | null;
  reference_number?: string | null;
  title?: string | null;
  contract_type?: string | null;
  effective_date?: string | null;
  expiration_date?: string | null;
}

export interface FeatureContribution {
  feature: string;
  contribution: number;
}

export interface ReviewItem {
  id: number;
  status: string;
  confidence_score?: number | null;
  model_version?: string | null;
  relationship_type?: string | null;
  extracted_parent_reference?: string | null;
  created_at?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  review_notes?: string | null;
  child: ContractSummary;
  candidate_parent?: ContractSummary | null;
  top_features: FeatureContribution[];
}

export interface ReviewListResponse {
  total: number;
  limit: number;
  offset: number;
  items: ReviewItem[];
}

export interface ReviewStatsResponse {
  pending: number;
  confirmed: number;
  rejected: number;
  relinked: number;
  total: number;
}

export const getReviewStats = async (): Promise<ReviewStatsResponse> => {
  const response = await api.get('/review-queue/stats');
  return response.data;
};

export const listReviewItems = async (params?: {
  status?: string;
  limit?: number;
  offset?: number;
  sort?: 'confidence_desc' | 'confidence_asc' | 'newest' | 'oldest';
}): Promise<ReviewListResponse> => {
  const response = await api.get('/review-queue', { params });
  return response.data;
};

export const getReviewItem = async (reviewId: number): Promise<ReviewItem> => {
  const response = await api.get(`/review-queue/${reviewId}`);
  return response.data;
};

export const decideReviewItem = async (
  reviewId: number,
  body: {
    action: 'confirm' | 'reject' | 'relink';
    new_parent_contract_id?: number;
    notes?: string;
  }
) => {
  const response = await api.post(`/review-queue/${reviewId}/decide`, body);
  return response.data;
};

// ---------------------------------------------------------------------------
// Contracts search (used by the relink picker)
// ---------------------------------------------------------------------------

export interface ContractSearchHit {
  id: number;
  contract_identifier?: string | null;
  reference_number?: string | null;
  title?: string | null;
  contract_type?: string | null;
  effective_date?: string | null;
  expiration_date?: string | null;
  score: number;
}

export interface ContractSearchResponse {
  query: string;
  total: number;
  items: ContractSearchHit[];
}

export const searchContracts = async (params: {
  q: string;
  limit?: number;
  contract_type?: string;
}): Promise<ContractSearchResponse> => {
  const response = await api.get('/contracts/search', { params });
  return response.data;
};
