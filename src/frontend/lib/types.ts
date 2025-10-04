export interface Event {
  id: string
  date: string
  time: string
  source: string
  summary: string
  details: string
  selected_tags: string[]
  duration?: number // in minutes
}

export interface Tag {
  id: string
  name: string
  color: string
  usage_count: number
  last_used: string
}

export interface TagSummary {
  total_tags: number
  top_tags: Tag[]
  color_map: Record<string, string>
}

export interface TagCooccurrence {
  tag1: string
  tag2: string
  strength: number
  count: number
}

export interface TagTransition {
  from_tag: string
  to_tag: string
  strength: number
  count: number
}

export interface TagTimeSeries {
  tag: string
  date: string
  hour?: number
  count: number
  duration: number // in minutes
}

export interface TimeDistribution {
  date: string
  hour: number
  activity_count: number
  total_duration: number
  top_tags: string[]
}

export interface InsightOverview {
  total_events: number
  total_duration: number // in minutes
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

// API Response types
export interface ApiResponse<T> {
  data: T
  status: "success" | "error"
  message?: string
  pagination?: {
    page: number
    limit: number
    total: number
    has_next: boolean
  }
}

// Filter types
export interface DateRange {
  start: string
  end: string
}

export interface FilterState {
  dateRange: DateRange
  selectedTags: string[]
  selectedSources: string[]
  searchQuery: string
}

// Chart data types
export interface ChartDataPoint {
  date: string
  value: number
  label?: string
}

export interface PieChartData {
  name: string
  value: number
  color: string
  percentage: number
}
