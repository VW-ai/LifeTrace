"use client"

import { useEffect } from "react"
import { DashboardHeader } from "../components/dashboard/dashboard-header"
import { FilterBar } from "../components/filters/filter-bar"
import { Timeline } from "../components/timeline/timeline"
import { TagFrequencyCards } from "../components/timeline/tag-frequency-cards"
import { EventDrawer } from "../components/events/event-drawer"
import { StatusBar } from "../components/dashboard/status-bar"
import { ViewSwitcher } from "../components/dashboard/view-switcher"
import { GalaxyView } from "../components/views/galaxy-view"
import { RiverView } from "../components/views/river-view"
import { CalendarView } from "../components/views/calendar-view"
import { ChordsView } from "../components/views/chords-view"
import { StoriesView } from "../components/views/stories-view"
import { UrlSyncProvider } from "../components/providers/url-sync-provider"
import { useDashboardStore } from "../lib/store/dashboard-store"

function DashboardContent() {
  const { initializeData, isLoading, error, activeView } = useDashboardStore()

  useEffect(() => {
    initializeData()
  }, []) // Empty dependency array to run only once

  if (error) {
    return (
      <div className="min-h-screen bg-background flex flex-col">
        <DashboardHeader />
        <div className="flex-1 container mx-auto px-4 py-8">
          <div className="flex items-center justify-center h-64">
            <div className="text-center space-y-4">
              <h2 className="text-xl font-semibold text-destructive">Error Loading Dashboard</h2>
              <p className="text-muted-foreground max-w-md">{error}</p>
              <p className="text-sm text-muted-foreground">
                This is expected if the backend API is not running. The frontend is fully implemented and ready to
                connect to your FastAPI backend.
              </p>
              <button
                onClick={() => window.location.reload()}
                className="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90"
              >
                Retry Connection
              </button>
            </div>
          </div>
        </div>
        <StatusBar />
      </div>
    )
  }

  const renderActiveView = () => {
    const viewContent = (() => {
      switch (activeView) {
        case "timeline":
          return (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
              {/* Main Timeline - Takes up 3 columns on large screens */}
              <div className="lg:col-span-3 space-y-6">
                <Timeline height={500} />
              </div>
              {/* Sidebar - Takes up 1 column on large screens */}
              <div className="lg:col-span-1 space-y-6">
                <TagFrequencyCards limit={15} />
              </div>
            </div>
          )
        case "galaxy":
          return <GalaxyView height={600} />
        case "river":
          return <RiverView height={500} />
        case "calendar":
          return <CalendarView height={400} />
        case "chords":
          return <ChordsView height={500} />
        case "stories":
          return <StoriesView />
        default:
          return null
      }
    })()

    return <div className="animate-in fade-in-0 duration-300">{viewContent}</div>
  }

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <DashboardHeader />

      {/* Main Content */}
      <main className="flex-1 container mx-auto px-4 py-6 space-y-6">
        {/* Filter Bar */}
        <FilterBar />

        <div className="transition-all duration-300">
          <ViewSwitcher />
        </div>

        {renderActiveView()}

        {/* Loading State */}
        {isLoading && (
          <div className="flex items-center justify-center py-12">
            <div className="flex items-center gap-3 text-muted-foreground">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary"></div>
              <span>Loading dashboard data...</span>
            </div>
          </div>
        )}
      </main>

      {/* Status Bar */}
      <StatusBar />

      {/* Event Drawer */}
      <EventDrawer />
    </div>
  )
}

export default function Dashboard() {
  return (
    <UrlSyncProvider>
      <DashboardContent />
    </UrlSyncProvider>
  )
}
