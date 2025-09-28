"use client"

import { useEffect, useRef } from "react"
import { useSearchParams, useRouter, usePathname } from "next/navigation"
import { useDashboardStore } from "../lib/store/dashboard-store"

export function useUrlSync() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const pathname = usePathname()
  const { filters, activeView, setFilters, setActiveView } = useDashboardStore()

  const isInitializedRef = useRef(false)
  const lastUrlRef = useRef("")

  // Sync URL to state on mount and when URL changes
  useEffect(() => {
    if (isInitializedRef.current) return

    const urlFilters: any = {}
    let hasChanges = false

    // Parse URL parameters
    const startDate = searchParams.get("start")
    const endDate = searchParams.get("end")
    const tags = searchParams.get("tags")
    const sources = searchParams.get("sources")
    const search = searchParams.get("search")
    const view = searchParams.get("view")
    const period = searchParams.get("period")

    if (startDate && endDate) {
      urlFilters.dateRange = { start: startDate, end: endDate }
      hasChanges = true
    }

    if (tags) {
      urlFilters.selectedTags = tags.split(",").filter(Boolean)
      hasChanges = true
    }

    if (sources) {
      urlFilters.selectedSources = sources.split(",").filter(Boolean)
      hasChanges = true
    }

    if (search) {
      urlFilters.searchQuery = search
      hasChanges = true
    }

    if (period && ["1w", "1m", "3m", "1y", "all"].includes(period)) {
      urlFilters.timePeriod = period
      hasChanges = true
    }

    // Update state if URL has parameters
    if (hasChanges) {
      setFilters(urlFilters)
    }

    // Set active view
    if (view && ["timeline", "galaxy", "river", "calendar", "chords", "stories"].includes(view)) {
      setActiveView(view as any)
    }

    isInitializedRef.current = true
  }, [searchParams, setFilters, setActiveView])

  // Sync state to URL when filters or view change
  useEffect(() => {
    if (!isInitializedRef.current) return

    const params = new URLSearchParams()

    // Add date range
    if (filters.dateRange.start && filters.dateRange.end) {
      params.set("start", filters.dateRange.start)
      params.set("end", filters.dateRange.end)
    }

    // Add selected tags
    if (filters.selectedTags.length > 0) {
      params.set("tags", filters.selectedTags.join(","))
    }

    // Add selected sources
    if (filters.selectedSources.length > 0) {
      params.set("sources", filters.selectedSources.join(","))
    }

    // Add search query
    if (filters.searchQuery) {
      params.set("search", filters.searchQuery)
    }

    // Add time period
    if (filters.timePeriod) {
      params.set("period", filters.timePeriod)
    }

    // Add active view
    if (activeView) {
      params.set("view", activeView)
    }

    // Update URL without triggering navigation
    const newUrl = `${pathname}?${params.toString()}`

    // Only update if the URL actually changed
    if (newUrl !== lastUrlRef.current) {
      lastUrlRef.current = newUrl
      router.replace(newUrl, { scroll: false })
    }
  }, [filters, activeView, router, pathname])

  return {
    // Helper function to create shareable URLs
    createShareableUrl: (customFilters?: any) => {
      const params = new URLSearchParams()
      const filtersToUse = customFilters || filters

      if (filtersToUse.dateRange?.start && filtersToUse.dateRange?.end) {
        params.set("start", filtersToUse.dateRange.start)
        params.set("end", filtersToUse.dateRange.end)
      }

      if (filtersToUse.selectedTags?.length > 0) {
        params.set("tags", filtersToUse.selectedTags.join(","))
      }

      if (filtersToUse.selectedSources?.length > 0) {
        params.set("sources", filtersToUse.selectedSources.join(","))
      }

      if (filtersToUse.searchQuery) {
        params.set("search", filtersToUse.searchQuery)
      }

      if (filtersToUse.timePeriod) {
        params.set("period", filtersToUse.timePeriod)
      }

      if (activeView) {
        params.set("view", activeView)
      }

      if (typeof window !== 'undefined') {
        return `${window.location.origin}${pathname}?${params.toString()}`
      }
      return `${pathname}?${params.toString()}`
    },

    // Helper to get current URL state
    getCurrentUrlState: () => {
      return {
        filters,
        activeView,
        url: `${pathname}?${searchParams.toString()}`,
      }
    },
  }
}
