const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface ApiResponse<T> {
  data: T
}

interface Event {
  id: string
  date: string
  time: string
  source: string
  summary: string
  details: string
  selected_tags: string[]
  duration?: number
}

interface BackendProcessedActivity {
  id: number
  date: string
  time?: string
  total_duration_minutes: number
  combined_details: string
  sources: string[]
  tags: Array<{
    id: number
    name: string
    description?: string
    color?: string
    usage_count: number
    confidence?: number
    created_at: string
    updated_at: string
  }>
  raw_activity_ids: number[]
  created_at: string
}

interface InsightOverview {
  total_events: number
  total_duration: number
  date_range: {
    start: string
    end: string
  }
  top_activities: Array<{
    activity: string
    duration: number
    percentage: number
  }>
  activity_trends: Array<{
    date: string
    duration: number
  }>
}

interface TimeDistribution {
  date: string
  hour: number
  activity_count: number
  total_duration: number
  top_tags: string[]
}

interface Tag {
  id: string
  name: string
  color: string
  usage_count: number
  last_used: string
}

interface TagSummary {
  total_tags: number
  top_tags: Array<{
    tag: string
    count: number
    percentage: number
  }>
  color_map: Record<string, string>
}

interface TagCooccurrence {
  tag1: string
  tag2: string
  strength: number
  count: number
}

interface TagTransition {
  from_tag: string
  to_tag: string
  strength: number
  count: number
}

interface TagTimeSeries {
  tag: string
  date: string
  hour?: number
  count: number
  duration: number
}

function transformBackendActivityToFrontend(backendActivity: BackendProcessedActivity): Event {
  // Extract first sentence or up to 100 chars for summary
  const fullDetails = backendActivity.combined_details
  const sentences = fullDetails.split(/[.!?]+/)
  const summary = sentences.length > 0 && sentences[0].trim()
    ? sentences[0].trim()
    : fullDetails.substring(0, 100).trim() + (fullDetails.length > 100 ? '...' : '')

  return {
    id: backendActivity.id.toString(),
    date: backendActivity.date,
    time: backendActivity.time || '',
    source: backendActivity.sources.join(', '),
    summary,
    details: fullDetails,
    selected_tags: backendActivity.tags.map(tag => tag.name),
    duration: backendActivity.total_duration_minutes,
  }
}

export class ApiClient {
  private baseUrl: string

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`

    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`)
    }

    return response.json()
  }

  // Core activity endpoints
  async getRawActivities(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    sources?: string[]
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.sources?.length) searchParams.set("sources", params.sources.join(","))
    if (params?.limit) searchParams.set("limit", params.limit.toString())
    if (params?.offset) searchParams.set("offset", params.offset.toString())

    const query = searchParams.toString()
    return this.request<ApiResponse<Event[]>>(`/api/v1/activities/raw${query ? `?${query}` : ""}`)
  }

  async getProcessedActivities(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    sources?: string[]
    limit?: number
    offset?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.sources?.length) searchParams.set("sources", params.sources.join(","))
    if (params?.limit) searchParams.set("limit", params.limit.toString())
    if (params?.offset) searchParams.set("offset", params.offset.toString())

    const query = searchParams.toString()
    const backendResponse = await this.request<{activities: BackendProcessedActivity[], total_count: number, page_info: any}>(`/api/v1/activities/processed${query ? `?${query}` : ""}`)

    // Transform backend data to frontend format
    const transformedActivities = backendResponse.activities.map(transformBackendActivityToFrontend)

    return {
      activities: transformedActivities,
      total_count: backendResponse.total_count,
      page_info: backendResponse.page_info
    }
  }

  // Insights endpoints
  async getInsightOverview(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))

    const query = searchParams.toString()
    return this.request<ApiResponse<InsightOverview>>(`/api/v1/insights/overview${query ? `?${query}` : ""}`)
  }

  async getTimeDistribution(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    granularity?: "hour" | "day" | "week"
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.granularity) searchParams.set("granularity", params.granularity)

    const query = searchParams.toString()
    return this.request<ApiResponse<TimeDistribution[]>>(
      `/api/v1/insights/time-distribution${query ? `?${query}` : ""}`,
    )
  }

  // Tag endpoints
  async getTags(params?: {
    limit?: number
    offset?: number
    search?: string
  }) {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set("limit", params.limit.toString())
    if (params?.offset) searchParams.set("offset", params.offset.toString())
    if (params?.search) searchParams.set("search", params.search)

    const query = searchParams.toString()
    return this.request<ApiResponse<Tag[]>>(`/api/v1/tags${query ? `?${query}` : ""}`)
  }

  async getTagSummary(params?: {
    start_date?: string
    end_date?: string
    limit?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.limit) searchParams.set("limit", params.limit.toString())

    const query = searchParams.toString()
    return this.request<TagSummary>(`/api/v1/tags/summary${query ? `?${query}` : ""}`)
  }

  async getTagCooccurrence(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    threshold?: number
    limit?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.threshold) searchParams.set("threshold", params.threshold.toString())
    if (params?.limit) searchParams.set("limit", params.limit.toString())

    const query = searchParams.toString()
    return this.request<{data: TagCooccurrence[]}>(`/api/v1/tags/cooccurrence${query ? `?${query}` : ""}`)
  }

  async getTagTransitions(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    limit?: number
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.limit) searchParams.set("limit", params.limit.toString())

    const query = searchParams.toString()
    return this.request<{data: TagTransition[]}>(`/api/v1/tags/transitions${query ? `?${query}` : ""}`)
  }

  async getTagTimeSeries(params?: {
    start_date?: string
    end_date?: string
    tags?: string[]
    granularity?: "hour" | "day"
    mode?: "absolute" | "normalized" | "share"
  }) {
    const searchParams = new URLSearchParams()
    if (params?.start_date) searchParams.set("start_date", params.start_date)
    if (params?.end_date) searchParams.set("end_date", params.end_date)
    if (params?.tags?.length) searchParams.set("tags", params.tags.join(","))
    if (params?.granularity) searchParams.set("granularity", params.granularity)
    if (params?.mode) searchParams.set("mode", params.mode)

    const query = searchParams.toString()
    return this.request<{data: TagTimeSeries[]}>(`/api/v1/tags/time-series${query ? `?${query}` : ""}`)
  }

  // Workflow Management Endpoints
  async importCalendarData(params: {
    hours_since_last_update?: number
  }) {
    return this.request<{
      status: string
      message: string
      imported_count: number
    }>('/api/v1/import/calendar', {
      method: 'POST',
      body: JSON.stringify(params)
    })
  }

  async importNotionData(params: {
    hours_since_last_update?: number
  }) {
    return this.request<{
      status: string
      message: string
      imported_count: number
    }>('/api/v1/import/notion', {
      method: 'POST',
      body: JSON.stringify(params)
    })
  }

  async getImportStatus() {
    return this.request<{
      calendar: {
        last_sync: string | null
        status: string
        total_imported: number
      }
      notion: {
        last_sync: string | null
        status: string
        total_imported: number
      }
    }>('/api/v1/import/status')
  }

  async triggerDailyProcessing(params: {
    use_database?: boolean
    regenerate_system_tags?: boolean
  }) {
    return this.request<{
      status: string
      job_id: string
      processed_counts: {
        raw_activities: number
        processed_activities: number
      }
      tag_analysis: {
        total_unique_tags: number
        average_tags_per_activity: number
      }
    }>('/api/v1/process/daily', {
      method: 'POST',
      body: JSON.stringify(params)
    })
  }

  async getProcessingStatus(jobId: string) {
    return this.request<{
      job_id: string
      status: string
      progress?: number
      started_at: string
      completed_at?: string
      error_message?: string
    }>(`/api/v1/process/status/${jobId}`)
  }

  async getProcessingHistory(limit: number = 50) {
    return this.request<Array<{
      job_id: string
      status: string
      progress?: number
      started_at: string
      completed_at?: string
      error_message?: string
    }>>(`/api/v1/process/history?limit=${limit}`)
  }

  async buildTaxonomy(params: {
    date_start?: string
    date_end?: string
    force_rebuild?: boolean
  }) {
    return this.request<{
      status: string
      message: string
      files_generated: string[]
      taxonomy_size?: number
      synonyms_count?: number
      data_scope: {
        date_start?: string
        date_end?: string
      }
    }>('/api/v1/taxonomy/build', {
      method: 'POST',
      body: JSON.stringify(params)
    })
  }

  async cleanupTags(params: {
    dry_run?: boolean
    removal_threshold?: number
    merge_threshold?: number
    date_start?: string
    date_end?: string
  }) {
    return this.request<{
      status: string
      total_analyzed: number
      marked_for_removal: number
      marked_for_merge: number
      removed: number
      merged: number
      dry_run: boolean
      scope: {
        date_start?: string
        date_end?: string
      }
      tags_to_remove: Array<{
        name: string
        reason: string
        confidence: number
        target?: string
      }>
      tags_to_merge: Array<{
        name: string
        reason: string
        confidence: number
        target?: string
      }>
    }>('/api/v1/tags/cleanup', {
      method: 'POST',
      body: JSON.stringify(params)
    })
  }

  async getProcessingLogs(params?: {
    limit?: number
    offset?: number
    level?: 'DEBUG' | 'INFO' | 'WARN' | 'ERROR'
    source?: string
  }) {
    const searchParams = new URLSearchParams()
    if (params?.limit) searchParams.set("limit", params.limit.toString())
    if (params?.offset) searchParams.set("offset", params.offset.toString())
    if (params?.level) searchParams.set("level", params.level)
    if (params?.source) searchParams.set("source", params.source)

    const query = searchParams.toString()
    return this.request<{
      logs: Array<{
        timestamp: string
        level: string
        message: string
        source: string
        context?: Record<string, any>
      }>
      total_count: number
      page_info: {
        limit: number
        offset: number
        has_more: boolean
      }
    }>(`/api/v1/processing/logs${query ? `?${query}` : ""}`)
  }
}

// Export singleton instance
export const apiClient = new ApiClient()
