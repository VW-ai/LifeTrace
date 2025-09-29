"use client"
import { Clock, Database, Zap } from "lucide-react"
import { useDashboardStore } from "../../lib/store/dashboard-store"
import { formatDate } from "../../lib/utils/date"

export function StatusBar() {
  const { filters, events, isLoading } = useDashboardStore()

  return (
    <div className="border-t bg-muted/30 px-4 py-2">
      <div className="container mx-auto">
        <div className="flex items-center justify-between text-xs text-muted-foreground">
          {/* Time Window */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-1">
              <Clock className="h-3 w-3" />
              <span>
                {formatDate(filters.dateRange.start)} - {formatDate(filters.dateRange.end)}
              </span>
            </div>

            <div className="flex items-center gap-1">
              <Database className="h-3 w-3" />
              <span>{events.length} events</span>
            </div>
          </div>

          {/* Performance Info */}
          <div className="flex items-center gap-4">
            {isLoading && (
              <div className="flex items-center gap-1">
                <div className="animate-spin rounded-full h-3 w-3 border-b border-primary"></div>
                <span>Loading...</span>
              </div>
            )}

            <div className="flex items-center gap-1">
              <Zap className="h-3 w-3" />
              <span>Ready</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
