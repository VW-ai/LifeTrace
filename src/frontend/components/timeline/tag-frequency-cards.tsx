"use client"
import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import { useDashboardStore, useTagStats } from "../../lib/store/dashboard-store"
import { generateTagColor } from "../../lib/utils/colors"
import { formatTagName } from "../../lib/utils"

interface TagFrequencyCardsProps {
  limit?: number
  className?: string
}

export function TagFrequencyCards({ limit = 10, className = "" }: TagFrequencyCardsProps) {
  const [showAll, setShowAll] = useState(false)
  const tagStats = useTagStats()
  const { toggleTag, filters } = useDashboardStore()

  const displayLimit = showAll ? tagStats.length : limit
  const topTags = tagStats.slice(0, displayLimit)
  const totalEvents = tagStats.reduce((sum, stat) => sum + stat.count, 0)

  if (topTags.length === 0) {
    return (
      <Card className={className}>
        <CardHeader>
          <CardTitle>Top Tags</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">No tags found in the current time range</div>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle>Top Tags</CardTitle>
        <p className="text-sm text-muted-foreground">Most frequently used tags in your activities</p>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {topTags.map((stat, index) => {
            const isSelected = filters.selectedTags.includes(stat.tag)
            const percentage = totalEvents > 0 ? (stat.count / totalEvents) * 100 : 0
            const tagColor = generateTagColor(stat.tag)

            return (
              <div
                key={stat.tag}
                className={`flex items-center p-3 rounded-lg border cursor-pointer transition-all hover:bg-accent/50 ${
                  isSelected ? "bg-accent border-primary" : "bg-card hover:border-accent-foreground/20"
                }`}
                onClick={() => toggleTag(stat.tag)}
              >
                {/* Left side: rank and color indicator - with proper spacing */}
                <div className="flex items-center gap-2 flex-shrink-0 mr-3">
                  <div className="text-xs font-medium text-muted-foreground min-w-[24px] text-right">#{index + 1}</div>
                  <div className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ backgroundColor: tagColor }} />
                </div>

                {/* Middle: tag name - takes maximum space */}
                <div className="flex-1 min-w-0 mr-2">
                  <Badge
                    variant={isSelected ? "default" : "secondary"}
                    className="font-medium text-left w-full justify-start px-2 py-1"
                    style={isSelected ? { backgroundColor: tagColor, color: "white" } : {}}
                  >
                    <span className="block truncate text-left">{formatTagName(stat.tag)}</span>
                  </Badge>
                </div>

                {/* Right side: compact stats */}
                <div className="flex flex-col items-end flex-shrink-0 min-w-[40px]">
                  <div className="text-xs font-semibold">{stat.count}</div>
                  <div className="text-[10px] text-muted-foreground">{percentage.toFixed(0)}%</div>
                </div>
              </div>
            )
          })}
        </div>

        {tagStats.length > limit && (
          <div className="mt-4 text-center">
            <button
              onClick={() => setShowAll(!showAll)}
              className="text-sm text-muted-foreground hover:text-foreground transition-colors"
            >
              {showAll ? `Show top ${limit} tags ↑` : `View all ${tagStats.length} tags →`}
            </button>
          </div>
        )}
      </CardContent>
    </Card>
  )
}
