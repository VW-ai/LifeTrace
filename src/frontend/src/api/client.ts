/**
 * API Client for SmartHistory Backend
 * Handles all communication with FastAPI backend
 * Industry-ready with environment-based configuration
 */

import { API_BASE_URL, DEBUG } from '../config/environment';

const BASE_URL = API_BASE_URL;

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  status: number;
}

export interface Activity {
  id?: number;
  date: string;
  time?: string;
  duration_minutes: number;
  details: string;
  source: string;
  orig_link?: string;
  raw_data?: Record<string, unknown>;
  processed_at?: string;
}

export interface ProcessedActivity {
  id?: number;
  date: string;
  duration_minutes: number;
  description: string;
  tags?: string[];
  sources?: string[];
  raw_activity_ids?: number[];
  confidence_score?: number;
  processed_at?: string;
}

export interface Tag {
  id?: number;
  name: string;
  color?: string;
  description?: string;
  usage_count?: number;
  created_at?: string;
}

export interface ProcessingSession {
  session_id: string;
  status: 'running' | 'completed' | 'failed';
  processed_count?: number;
  total_count?: number;
  error_message?: string;
  started_at?: string;
  completed_at?: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    const requestId = Math.random().toString(36).substr(2, 9);
    
    if (DEBUG) {
      console.log(`🚀 API Request [${requestId}]:`, {
        url,
        method: options.method || 'GET',
        headers: options.headers,
      });
    }

    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          'X-Request-ID': requestId,
          ...options.headers,
        },
        ...options,
      });

      let data = null;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      } else if (response.ok) {
        const text = await response.text();
        data = text || null;
      }

      const result = {
        data: response.ok ? data : null,
        status: response.status,
        error: response.ok ? undefined : `HTTP ${response.status}: ${response.statusText}`,
      };

      if (DEBUG) {
        console.log(`📥 API Response [${requestId}]:`, {
          status: response.status,
          ok: response.ok,
          data: result.data,
          error: result.error,
        });
      }

      // Handle specific error cases
      if (!response.ok) {
        if (response.status === 404) {
          result.error = 'Resource not found';
        } else if (response.status === 500) {
          result.error = 'Server error - please try again later';
        } else if (response.status >= 400 && response.status < 500) {
          result.error = data?.message || result.error;
        }
      }

      return result;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Network error';
      
      if (DEBUG) {
        console.error(`❌ API Error [${requestId}]:`, error);
      }

      return {
        status: 0,
        error: errorMessage.includes('fetch') ? 'Unable to connect to server' : errorMessage,
      };
    }
  }

  // Health check
  async health(): Promise<ApiResponse<{ status: string }>> {
    return this.request('/health');
  }

  // Activities endpoints
  async getRawActivities(
    limit?: number,
    offset?: number,
    source?: string,
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<Activity[]>> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    if (source) params.append('source', source);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return this.request(`/activities/raw${query ? `?${query}` : ''}`);
  }

  async getProcessedActivities(
    limit?: number,
    offset?: number,
    tags?: string[],
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<ProcessedActivity[]>> {
    const params = new URLSearchParams();
    if (limit) params.append('limit', limit.toString());
    if (offset) params.append('offset', offset.toString());
    if (tags) tags.forEach(tag => params.append('tags', tag));
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return this.request(`/activities/processed${query ? `?${query}` : ''}`);
  }

  // Tags endpoints
  async getTags(): Promise<ApiResponse<Tag[]>> {
    return this.request('/tags/');
  }

  async createTag(tag: Omit<Tag, 'id' | 'usage_count' | 'created_at'>): Promise<ApiResponse<Tag>> {
    return this.request('/tags/', {
      method: 'POST',
      body: JSON.stringify(tag),
    });
  }

  async updateTag(id: number, tag: Partial<Tag>): Promise<ApiResponse<Tag>> {
    return this.request(`/tags/${id}`, {
      method: 'PUT',
      body: JSON.stringify(tag),
    });
  }

  async deleteTag(id: number): Promise<ApiResponse<void>> {
    return this.request(`/tags/${id}`, {
      method: 'DELETE',
    });
  }

  // Insights endpoints
  async getTagDistribution(
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<Array<{ tag: string; total_duration: number; activity_count: number }>>> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);

    const query = params.toString();
    return this.request(`/insights/tag-distribution${query ? `?${query}` : ''}`);
  }

  async getTimeDistribution(
    startDate?: string,
    endDate?: string,
    groupBy: 'day' | 'week' | 'month' = 'day'
  ): Promise<ApiResponse<Array<{ date: string; total_duration: number; activity_count: number }>>> {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    params.append('group_by', groupBy);

    const query = params.toString();
    return this.request(`/insights/time-distribution?${query}`);
  }

  // Processing endpoints
  async triggerProcessing(): Promise<ApiResponse<{ session_id: string }>> {
    return this.request('/processing/trigger', {
      method: 'POST',
    });
  }

  async getProcessingStatus(sessionId: string): Promise<ApiResponse<ProcessingSession>> {
    return this.request(`/processing/status/${sessionId}`);
  }
}

export const apiClient = new ApiClient();
export default apiClient;