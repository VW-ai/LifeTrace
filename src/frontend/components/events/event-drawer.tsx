"use client"

import { useMemo } from "react"
import { Clock, Calendar, Tag, FileText, ExternalLink } from "lucide-react"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { ScrollArea } from "../ui/scroll-area"
import { Separator } from "../ui/separator"
import { Sheet, SheetContent, SheetHeader, SheetTitle } from "../ui/sheet"
import { useDashboardStore, useFilteredEvents } from "../../lib/store/dashboard-store"
import { generateTagColor } from "../../lib/utils/colors"
import { formatDate, formatTime, formatDuration } from "../../lib/utils/date"

export function EventDrawer() {
  const { drawerOpen, selectedEventId, closeDrawer, toggleTag, filters } = useDashboardStore()

  const events = useFilteredEvents()

  const selectedEvent = useMemo(() => {
    return selectedEventId ? events.find((event) => event.id === selectedEventId) : null
  }, [events, selectedEventId])

  const relatedEvents = useMemo(() => {
    if (!selectedEvent) return []

    // Find events with similar tags or from the same source
    return events
      .filter(
        (event) =>
          event.id !== selectedEvent.id &&
          (event.source === selectedEvent.source ||
            event.selected_tags.some((tag) => selectedEvent.selected_tags.includes(tag))),
      )
      .slice(0, 5)
  }, [events, selectedEvent])

  if (!selectedEvent) {
    return (
      <Sheet open={drawerOpen} onOpenChange={closeDrawer}>
        <SheetContent className="w-[400px] sm:w-[540px]">
          <SheetHeader>
            <SheetTitle>Event Details</SheetTitle>
          </SheetHeader>
          <div className="flex items-center justify-center h-64 text-muted-foreground">No event selected</div>
        </SheetContent>
      </Sheet>
    )
  }

  return (
    <Sheet open={drawerOpen} onOpenChange={closeDrawer}>
      <SheetContent className="w-[400px] sm:w-[540px]">
        <SheetHeader>
          <SheetTitle className="text-left">Event Details</SheetTitle>
        </SheetHeader>

        <ScrollArea className="h-[calc(100vh-80px)] pr-4">
          <div className="space-y-6">
            {/* Event Summary */}
            <div className="space-y-3">
              <h3 className="text-lg font-semibold leading-tight">{selectedEvent.summary}</h3>

              {selectedEvent.details && (
                <p className="text-muted-foreground leading-relaxed">{selectedEvent.details}</p>
              )}
            </div>

            <Separator />

            {/* Event Metadata */}
            <div className="space-y-4">
              <div className="flex items-center gap-3 text-sm">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{formatDate(selectedEvent.date)}</span>
              </div>

              <div className="flex items-center gap-3 text-sm">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">
                  {formatTime(selectedEvent.time)}
                  {selectedEvent.duration && (
                    <span className="text-muted-foreground ml-2">({formatDuration(selectedEvent.duration)})</span>
                  )}
                </span>
              </div>

              <div className="flex items-center gap-3 text-sm">
                <ExternalLink className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium">{selectedEvent.source}</span>
              </div>
            </div>

            <Separator />

            {/* Tags */}
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Tag className="h-4 w-4 text-muted-foreground" />
                <span className="font-medium text-sm">Tags</span>
              </div>

              {selectedEvent.selected_tags.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {selectedEvent.selected_tags.map((tag) => {
                    const isSelected = filters.selectedTags.includes(tag)
                    const tagColor = generateTagColor(tag)

                    return (
                      <Badge
                        key={tag}
                        variant={isSelected ? "default" : "secondary"}
                        className="cursor-pointer hover:opacity-80 transition-opacity"
                        style={isSelected ? { backgroundColor: tagColor, color: "white" } : {}}
                        onClick={() => toggleTag(tag)}
                      >
                        {tag}
                      </Badge>
                    )
                  })}
                </div>
              ) : (
                <p className="text-sm text-muted-foreground">No tags assigned</p>
              )}
            </div>

            {/* Related Events */}
            {relatedEvents.length > 0 && (
              <>
                <Separator />
                <div className="space-y-3">
                  <h4 className="font-medium text-sm">Related Events</h4>
                  <div className="space-y-2">
                    {relatedEvents.map((event) => (
                      <div
                        key={event.id}
                        className="p-3 rounded-lg border bg-card hover:bg-accent/50 cursor-pointer transition-colors"
                        onClick={() => {
                          // Switch to this event
                          useDashboardStore.getState().selectEvent(event.id)
                        }}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1 min-w-0">
                            <p className="font-medium text-sm truncate">{event.summary}</p>
                            <p className="text-xs text-muted-foreground">
                              {formatDate(event.date)} at {formatTime(event.time)}
                            </p>
                          </div>
                          <div className="flex-shrink-0">
                            <Badge variant="outline" className="text-xs">
                              {event.source}
                            </Badge>
                          </div>
                        </div>

                        {event.selected_tags.length > 0 && (
                          <div className="flex flex-wrap gap-1 mt-2">
                            {event.selected_tags.slice(0, 3).map((tag) => (
                              <Badge
                                key={tag}
                                variant="secondary"
                                className="text-xs"
                                style={{ backgroundColor: generateTagColor(tag), color: "white" }}
                              >
                                {tag}
                              </Badge>
                            ))}
                            {event.selected_tags.length > 3 && (
                              <Badge variant="secondary" className="text-xs">
                                +{event.selected_tags.length - 3}
                              </Badge>
                            )}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}

            {/* Actions */}
            <Separator />
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // Filter by this event's tags
                  selectedEvent.selected_tags.forEach((tag) => {
                    if (!filters.selectedTags.includes(tag)) {
                      toggleTag(tag)
                    }
                  })
                }}
                disabled={selectedEvent.selected_tags.every((tag) => filters.selectedTags.includes(tag))}
              >
                <Tag className="h-3 w-3 mr-1" />
                Filter by Tags
              </Button>

              <Button
                variant="outline"
                size="sm"
                onClick={() => {
                  // Copy event details to clipboard
                  const eventText = `${selectedEvent.summary}\n${formatDate(selectedEvent.date)} at ${formatTime(selectedEvent.time)}\nSource: ${selectedEvent.source}\nTags: ${selectedEvent.selected_tags.join(", ")}\n\n${selectedEvent.details}`
                  navigator.clipboard.writeText(eventText)
                }}
              >
                <FileText className="h-3 w-3 mr-1" />
                Copy Details
              </Button>
            </div>
          </div>
        </ScrollArea>
      </SheetContent>
    </Sheet>
  )
}
