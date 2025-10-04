import { create } from "zustand"
import { subscribeWithSelector } from "zustand/middleware"
import { apiClient } from "../api-client"
import { getDateRange } from "../utils/date"

export interface Event {
  id: string
  date: string
  time: string
  source: string
  summary: string
  details: string
  selected_tags: string[]
  duration?: number
}

export interface Tag {
  id: string
  name: string
  color: string
  usage_count: number
  last_used: string
}

export interface FilterState {
  dateRange: {
    start: string
    end: string
  }
  selectedTags: string[]
  selectedSources: string[]
  searchQuery: string
  timePeriod: "1w" | "1m" | "3m" | "1y" | "all"
}

export interface DashboardState {
  // Data
  events: Event[]
  tags: Tag[]
  insights: any
  timeDistribution: any[]

  // UI State
  filters: FilterState
  selectedEvents: string[]
  activeView: "timeline" | "galaxy" | "river" | "calendar" | "chords" | "stories"
  isLoading: boolean
  error: string | null

  // Event Drawer
  drawerOpen: boolean
  selectedEventId: string | null

  // Timeline brush state
  brushSelection: {
    start: string
    end: string
  } | null

  // Actions
  setFilters: (filters: Partial<FilterState>) => void
  setTimePeriod: (period: "1w" | "1m" | "3m" | "1y" | "all") => void
  toggleTag: (tagName: string) => void
  clearFilters: () => void
  setActiveView: (view: DashboardState["activeView"]) => void
  setBrushSelection: (selection: { start: string; end: string } | null) => void

  // Data fetching
  fetchEvents: () => Promise<void>
  fetchTags: () => Promise<void>
  fetchInsights: () => Promise<void>
  fetchTimeDistribution: () => Promise<void>
  initializeData: () => Promise<void>

  // Event Drawer
  openDrawer: (eventId?: string) => void
  closeDrawer: () => void
  selectEvent: (eventId: string) => void
  toggleEventSelection: (eventId: string) => void
  clearEventSelection: () => void
}

const initialFilters: FilterState = {
  dateRange: getDateRange("1m"),
  selectedTags: [],
  selectedSources: [],
  searchQuery: "",
  timePeriod: "1m",
}

// Mock data for development when API is not available
const mockEvents: Event[] = [
  {
    id: "1",
    date: "2025-09-25",
    time: "09:00",
    source: "Notion Calendar",
    summary: "Team standup meeting",
    details: "Daily standup with the development team to discuss progress and blockers",
    selected_tags: ["meeting", "work", "team"],
    duration: 30,
  },
  {
    id: "2",
    date: "2025-09-25",
    time: "10:30",
    source: "Notion",
    summary: "Code review session",
    details: "Reviewing pull requests and providing feedback on new features",
    selected_tags: ["coding", "review", "work"],
    duration: 60,
  },
  {
    id: "3",
    date: "2025-09-25",
    time: "14:00",
    source: "Notion",
    summary: "Design system documentation",
    details: "Writing documentation for the new design system components",
    selected_tags: ["documentation", "design", "work"],
    duration: 90,
  },
  {
    id: "4",
    date: "2025-09-26",
    time: "09:30",
    source: "Notion Calendar",
    summary: "Client presentation",
    details: "Presenting the new dashboard features to the client",
    selected_tags: ["presentation", "client", "work"],
    duration: 45,
  },
  {
    id: "5",
    date: "2025-09-26",
    time: "15:00",
    source: "Notion",
    summary: "Personal learning time",
    details: "Learning about new React patterns and best practices",
    selected_tags: ["learning", "react", "personal"],
    duration: 120,
  },
]

const mockTags: Tag[] = [
  { id: "1", name: "work", color: "#3b82f6", usage_count: 15, last_used: "2024-01-16" },
  { id: "2", name: "meeting", color: "#ef4444", usage_count: 8, last_used: "2024-01-15" },
  { id: "3", name: "coding", color: "#10b981", usage_count: 12, last_used: "2024-01-16" },
  { id: "4", name: "design", color: "#f59e0b", usage_count: 6, last_used: "2024-01-15" },
  { id: "5", name: "learning", color: "#8b5cf6", usage_count: 4, last_used: "2024-01-16" },
]

export const useDashboardStore = create<DashboardState>()(
  subscribeWithSelector((set, get) => ({
    // Initial state
    events: [],
    tags: [],
    insights: null,
    timeDistribution: [],

    filters: initialFilters,
    selectedEvents: [],
    activeView: "timeline",
    isLoading: false,
    error: null,

    drawerOpen: false,
    selectedEventId: null,
    brushSelection: null,

    // Filter actions
    setFilters: (newFilters) => {
      set((state) => ({
        filters: { ...state.filters, ...newFilters },
      }))
    },

    setTimePeriod: (period) => {
      const dateRange = getDateRange(period)
      set((state) => ({
        filters: {
          ...state.filters,
          timePeriod: period,
          dateRange,
        },
      }))
      // Trigger data refetch with new date range
      const { fetchEvents, fetchInsights, fetchTimeDistribution } = get()
      Promise.all([fetchEvents(), fetchInsights(), fetchTimeDistribution()])
    },

    toggleTag: (tagName) => {
      set((state) => {
        const selectedTags = state.filters.selectedTags.includes(tagName)
          ? state.filters.selectedTags.filter((tag) => tag !== tagName)
          : [...state.filters.selectedTags, tagName]

        return {
          filters: {
            ...state.filters,
            selectedTags,
          },
        }
      })
    },

    clearFilters: () => {
      set({ filters: initialFilters })
    },

    setActiveView: (view) => {
      set({ activeView: view })

      // Optional: Track view changes for analytics
      if (typeof window !== "undefined") {
        console.log(`[Dashboard] Switched to ${view} view`)
      }
    },

    setBrushSelection: (selection) => {
      set({ brushSelection: selection })

      if (selection) {
        // Update date range filter based on brush selection
        set((state) => ({
          filters: {
            ...state.filters,
            dateRange: {
              start: selection.start,
              end: selection.end,
            },
          },
        }))
      }
    },

    // Data fetching actions
    fetchEvents: async () => {
      try {
        set({ isLoading: true, error: null })
        const { filters } = get()

        const response = await apiClient.getProcessedActivities({
          start_date: filters.dateRange.start,
          end_date: filters.dateRange.end,
          tags: filters.selectedTags.length > 0 ? filters.selectedTags : undefined,
          sources: filters.selectedSources.length > 0 ? filters.selectedSources : undefined,
        })

        set({
          events: response.activities || [],
          isLoading: false,
        })
      } catch (error) {
        console.warn("API not available, using mock data")
        // Use mock data when API is not available
        set({
          events: mockEvents,
          isLoading: false,
          error: null, // Don't show error for expected API unavailability
        })
      }
    },

    fetchTags: async () => {
      try {
        const response = await apiClient.getTags()
        set({ tags: response.data || [] })
      } catch (error) {
        console.warn("API not available, using mock tags")
        set({ tags: mockTags })
      }
    },

    fetchInsights: async () => {
      try {
        const { filters } = get()

        const response = await apiClient.getInsightOverview({
          start_date: filters.dateRange.start,
          end_date: filters.dateRange.end,
          tags: filters.selectedTags.length > 0 ? filters.selectedTags : undefined,
        })

        set({ insights: response.data })
      } catch (error) {
        console.warn("API not available, using mock insights")
        set({
          insights: {
            totalActivities: mockEvents.length,
            uniqueTags: mockTags.length,
          },
        })
      }
    },

    fetchTimeDistribution: async () => {
      try {
        const { filters } = get()

        const response = await apiClient.getTimeDistribution({
          start_date: filters.dateRange.start,
          end_date: filters.dateRange.end,
          tags: filters.selectedTags.length > 0 ? filters.selectedTags : undefined,
          granularity: "day",
        })

        set({ timeDistribution: response.data || [] })
      } catch (error) {
        console.warn("API not available, using mock time distribution")
        set({ timeDistribution: [] })
      }
    },

    initializeData: async () => {
      const state = get()
      if (state.isLoading) return // Prevent multiple simultaneous calls

      await Promise.all([state.fetchEvents(), state.fetchTags(), state.fetchInsights(), state.fetchTimeDistribution()])
    },

    // Event Drawer actions
    openDrawer: (eventId) => {
      set({
        drawerOpen: true,
        selectedEventId: eventId || null,
      })
    },

    closeDrawer: () => {
      set({
        drawerOpen: false,
        selectedEventId: null,
      })
    },

    selectEvent: (eventId) => {
      set({ selectedEventId: eventId })
    },

    toggleEventSelection: (eventId) => {
      set((state) => {
        const selectedEvents = state.selectedEvents.includes(eventId)
          ? state.selectedEvents.filter((id) => id !== eventId)
          : [...state.selectedEvents, eventId]

        return { selectedEvents }
      })
    },

    clearEventSelection: () => {
      set({ selectedEvents: [] })
    },
  })),
)

// Selectors for derived state
export const useFilteredEvents = () => {
  const { events, filters } = useDashboardStore()

  return events.filter((event) => {
    // Date range filter - CRITICAL for time period and brush filtering
    if (filters.dateRange.start && filters.dateRange.end) {
      const eventDate = new Date(event.date)
      const startDate = new Date(filters.dateRange.start)
      const endDate = new Date(filters.dateRange.end)

      if (eventDate < startDate || eventDate > endDate) {
        return false
      }
    }

    // Search query filter
    if (filters.searchQuery) {
      const query = filters.searchQuery.toLowerCase()
      const matchesSearch =
        event.summary.toLowerCase().includes(query) ||
        event.details.toLowerCase().includes(query) ||
        event.selected_tags.some((tag) => tag.toLowerCase().includes(query))

      if (!matchesSearch) return false
    }

    // Source filter
    if (filters.selectedSources.length > 0) {
      if (!filters.selectedSources.includes(event.source)) return false
    }

    // Tag filter
    if (filters.selectedTags.length > 0) {
      const hasSelectedTag = filters.selectedTags.some((tag) => event.selected_tags.includes(tag))
      if (!hasSelectedTag) return false
    }

    return true
  })
}

export const useTagStats = () => {
  const events = useFilteredEvents()
  const tagCounts = new Map<string, number>()

  events.forEach((event) => {
    event.selected_tags.forEach((tag) => {
      tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1)
    })
  })

  return Array.from(tagCounts.entries())
    .map(([tag, count]) => ({ tag, count }))
    .sort((a, b) => b.count - a.count)
}
