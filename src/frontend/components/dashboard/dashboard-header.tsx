"use client"
import { BarChart3, Calendar, Network, Activity, Clock, BookOpen, Settings } from "lucide-react"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { ShareButton } from "./share-button"
import { useDashboardStore, useFilteredEvents } from "../../lib/store/dashboard-store"

const viewIcons = {
  timeline: BarChart3,
  galaxy: Network,
  river: Activity,
  calendar: Calendar,
  chords: Clock,
  stories: BookOpen,
}

const viewLabels = {
  timeline: "Timeline",
  galaxy: "Galaxy",
  river: "River",
  calendar: "Calendar",
  chords: "Chords",
  stories: "Stories",
}

export function DashboardHeader() {
  const { activeView, setActiveView, filters } = useDashboardStore()
  const events = useFilteredEvents()

  const getViewContext = () => {
    const uniqueTags = new Set(events.flatMap((e) => e.selected_tags)).size
    const uniqueDates = new Set(events.map((e) => e.date)).size

    switch (activeView) {
      case "timeline":
        return `${events.length} events across ${uniqueDates} days`
      case "galaxy":
        return `${uniqueTags} tags with ${events.length} connections`
      case "river":
        return `${uniqueDates} days of activity flow`
      case "calendar":
        return `${uniqueDates} active days`
      case "chords":
        const tagPairs = new Set<string>()
        events.forEach((event) => {
          const tags = event.selected_tags
          for (let i = 0; i < tags.length; i++) {
            for (let j = i + 1; j < tags.length; j++) {
              tagPairs.add([tags[i], tags[j]].sort().join("-"))
            }
          }
        })
        return `${tagPairs.size} tag relationships`
      case "stories":
        return `Narrative patterns from ${events.length} activities`
      default:
        return `${events.length} events`
    }
  }

  return (
    <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between py-4">
          {/* Logo and Title */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
                <BarChart3 className="h-5 w-5 text-primary-foreground" />
              </div>
              <div>
                <h1 className="text-xl font-bold">Time Insights</h1>
                <p className="text-sm text-muted-foreground">
                  {viewLabels[activeView]} • {getViewContext()}
                </p>
              </div>
            </div>
          </div>

          {/* View Navigation */}
          <nav className="hidden md:flex items-center gap-1 bg-muted/50 rounded-lg p-1">
            {Object.entries(viewIcons).map(([view, Icon]) => {
              const isActive = activeView === view
              const isImplemented = true

              return (
                <Button
                  key={view}
                  variant={isActive ? "default" : "ghost"}
                  size="sm"
                  className={`gap-2 transition-all duration-200 ${!isImplemented ? "opacity-50" : ""}`}
                  onClick={() => isImplemented && setActiveView(view as any)}
                  disabled={!isImplemented}
                >
                  <Icon className="h-4 w-4" />
                  {viewLabels[view as keyof typeof viewLabels]}
                </Button>
              )
            })}
          </nav>

          {/* Actions */}
          <div className="flex items-center gap-3">
            {/* Event Count */}
            <div className="hidden sm:flex items-center gap-2 text-sm text-muted-foreground">
              <span>{events.length} events</span>
              {filters.selectedTags.length > 0 && (
                <Badge variant="secondary" className="text-xs">
                  {filters.selectedTags.length} tag{filters.selectedTags.length !== 1 ? "s" : ""}
                </Badge>
              )}
            </div>

            <ShareButton />

            <Button variant="ghost" size="sm">
              <Settings className="h-4 w-4" />
            </Button>
          </div>
        </div>

        {/* Mobile View Navigation */}
        <div className="md:hidden pb-4">
          <div className="flex items-center gap-2 overflow-x-auto">
            {Object.entries(viewIcons).map(([view, Icon]) => {
              const isActive = activeView === view
              const isImplemented = true

              return (
                <Button
                  key={view}
                  variant={isActive ? "default" : "outline"}
                  size="sm"
                  className={`gap-2 flex-shrink-0 transition-all duration-200 ${!isImplemented ? "opacity-50" : ""}`}
                  onClick={() => isImplemented && setActiveView(view as any)}
                  disabled={!isImplemented}
                >
                  <Icon className="h-4 w-4" />
                  {viewLabels[view as keyof typeof viewLabels]}
                </Button>
              )
            })}
          </div>
        </div>
      </div>
    </header>
  )
}
