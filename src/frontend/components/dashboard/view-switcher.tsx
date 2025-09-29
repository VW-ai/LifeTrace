"use client"

import { useDashboardStore } from "../../lib/store/dashboard-store"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { Baseline as Timeline, Network, Waves, Calendar, GitBranch, BookOpen } from "lucide-react"
import { useFilteredEvents } from "../../lib/store/dashboard-store"

const views = [
  {
    id: "timeline" as const,
    name: "Timeline",
    icon: Timeline,
    description: "Chronological view with brushable timeline",
    shortDesc: "Chronological events",
  },
  {
    id: "galaxy" as const,
    name: "Galaxy",
    icon: Network,
    description: "Tag relationships as network graph",
    shortDesc: "Tag relationships",
  },
  {
    id: "river" as const,
    name: "River",
    icon: Waves,
    description: "Temporal flow visualization",
    shortDesc: "Activity flow",
  },
  {
    id: "calendar" as const,
    name: "Calendar",
    icon: Calendar,
    description: "Heatmap with detailed day view",
    shortDesc: "Daily patterns",
  },
  {
    id: "chords" as const,
    name: "Chords",
    icon: GitBranch,
    description: "Tag co-occurrence patterns",
    shortDesc: "Tag connections",
  },
  {
    id: "stories" as const,
    name: "Stories",
    icon: BookOpen,
    description: "Narrative sequences and patterns",
    shortDesc: "Activity narratives",
  },
]

export function ViewSwitcher() {
  const { activeView, setActiveView } = useDashboardStore()
  const events = useFilteredEvents()

  const getViewMetrics = (viewId: string) => {
    switch (viewId) {
      case "timeline":
        return events.length
      case "galaxy":
        return new Set(events.flatMap((e) => e.selected_tags)).size
      case "river":
        return new Set(events.map((e) => e.date)).size
      case "calendar":
        return new Set(events.map((e) => e.date)).size
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
        return tagPairs.size
      case "stories":
        // Simple pattern detection count
        const patterns = new Set<string>()
        const tagsByDate = new Map<string, string[]>()
        events.forEach((event) => {
          if (!tagsByDate.has(event.date)) {
            tagsByDate.set(event.date, [])
          }
          tagsByDate.get(event.date)!.push(...event.selected_tags)
        })
        return Math.min(8, Array.from(tagsByDate.values()).filter((tags) => tags.length >= 2).length)
      default:
        return 0
    }
  }

  return (
    <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 p-4 bg-card rounded-lg border">
      <div className="flex-1">
        <h2 className="text-lg font-semibold">Visualization Views</h2>
        <p className="text-sm text-muted-foreground">
          {views.find((v) => v.id === activeView)?.description || "Select a view to explore your data"}
        </p>
      </div>

      <div className="flex flex-wrap items-center gap-2">
        {views.map((view) => {
          const Icon = view.icon
          const isActive = activeView === view.id
          const metrics = getViewMetrics(view.id)

          return (
            <Button
              key={view.id}
              variant={isActive ? "default" : "outline"}
              size="sm"
              onClick={() => setActiveView(view.id)}
              className={`
                flex items-center gap-2 px-3 py-2 text-sm font-medium transition-all relative
                ${
                  isActive
                    ? "bg-primary text-primary-foreground shadow-sm"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted"
                }
              `}
              title={`${view.description} • ${metrics} items`}
            >
              <Icon className="h-4 w-4" />
              <span className="hidden md:inline">{view.name}</span>
              {metrics > 0 && (
                <Badge
                  variant="secondary"
                  className={`ml-1 text-xs px-1.5 py-0.5 ${
                    isActive ? "bg-primary-foreground/20 text-primary-foreground" : "bg-muted text-muted-foreground"
                  }`}
                >
                  {metrics}
                </Badge>
              )}
            </Button>
          )
        })}
      </div>
    </div>
  )
}
