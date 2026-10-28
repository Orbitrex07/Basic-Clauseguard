import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export function parseUtcDate(dateStr: string | Date | undefined): Date {
  if (!dateStr) return new Date();
  if (dateStr instanceof Date) return dateStr;
  const trimmed = dateStr.trim();
  // If the ISO string lacks timezone offset and 'Z', append 'Z' so browsers parse it as UTC
  if (!trimmed.endsWith('Z') && !/[+-]\d{2}:?\d{2}$/.test(trimmed)) {
    return new Date(trimmed + 'Z');
  }
  return new Date(trimmed);
}

export function formatDateTime(dateStr: string | Date | undefined): string {
  return parseUtcDate(dateStr).toLocaleString();
}

export function formatDate(dateStr: string | Date | undefined): string {
  return parseUtcDate(dateStr).toLocaleDateString();
}

export default api;

// Typed API Helpers
export interface User {
  id: string;
  email: string;
  full_name?: string;
  role: string;
  is_active: boolean;
  created_at: string;
}

export interface DocumentSummary {
  total_clauses: number;
  high_risk_count: number;
  medium_risk_count: number;
  low_risk_count: number;
  needs_review_count: number;
  category_distribution: Record<string, number>;
}

export interface DocumentItem {
  id: string;
  user_id: string;
  filename: string;
  file_size: number;
  page_count: number;
  mime_type: string;
  status: 'queued' | 'parsing' | 'classifying' | 'scoring' | 'done' | 'failed';
  progress: number;
  error_message?: string;
  created_at: string;
  updated_at: string;
  summary?: DocumentSummary;
}

export interface RiskFlag {
  id: string;
  clause_id: string;
  risk_level: 'High' | 'Medium' | 'Low';
  risk_score: number;
  triggered_rules: Array<{
    rule_code: string;
    severity: string;
    points: number;
    reason: string;
    suggestion?: string;
  }>;
  extracted_data: Record<string, any>;
  explanation: string;
  suggestion?: string;
  needs_review: boolean;
  created_at: string;
}

export interface ClauseItem {
  id: string;
  document_id: string;
  clause_number: number;
  heading?: string;
  text: string;
  page_number: number;
  start_pos: number;
  end_pos: number;
  primary_category: string;
  secondary_categories: string[];
  top_3_labels: Array<{ label: string; probability: number }>;
  confidence: number;
  is_reviewed: boolean;
  created_at: string;
  risk_flag?: RiskFlag;
}

export interface RiskRule {
  id: string;
  rule_code: string;
  category: string;
  severity: string;
  points: number;
  pattern_type: string;
  pattern_value: string;
  reason: string;
  suggestion?: string;
  is_enabled: boolean;
}

export interface AuditLogItem {
  id: string;
  user_id?: string;
  action: string;
  entity_type?: string;
  entity_id?: string;
  details: Record<string, any>;
  ip_address?: string;
  created_at: string;
}
