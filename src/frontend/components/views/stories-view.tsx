"use client"

import { useMemo, useState } from "react"
import { useFilteredEvents, useDashboardStore } from "../../lib/store/dashboard-store"
import { getTagColor } from "../../lib/utils/colors"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import { Button } from "../ui/button"
import { ScrollArea } from "../ui/scroll-area"
import { Separator } from "../ui/separator"
import { Clock, Calendar, ArrowRight, TrendingUp, Repeat } from "lucide-react"

interface Story {
  id: string
  title: string
  description: string
  pattern: "sequence" | "routine" | "burst" | "trend"
  events: Array<{
    id: string
    date: string
    summary: string
    tags: string[]
    duration: number
  }>
  tags: string[]
  frequency: number
  totalDuration: number
  dateRange: {
    start: string
    end: string
  }
}

export function StoriesView() {
  const events = useFilteredEvents()
  const { openDrawer } = useDashboardStore()
  const [selectedStory, setSelectedStory] = useState<Story | null>(null)

  const stories = useMemo(() => {
    if (events.length === 0) return []

    const storyList: Story[] = []

    // 1. Detect Sequences (same tags appearing in order)
    const tagSequences = new Map<string, Array<{ date: string; events: typeof events }>>()

    events.forEach((event) => {
      event.selected_tags.forEach((tag) => {
        if (!tagSequences.has(tag)) {
          tagSequences.set(tag, [])
        }
        const existing = tagSequences.get(tag)!.find((seq) => seq.date === event.date)
        if (existing) {
          existing.events.push(event)
        } else {
          tagSequences.get(tag)!.push({ date: event.date, events: [event] })
        }
      })
    })

    tagSequences.forEach((sequences, tag) => {
      if (sequences.length >= 3) {
        const sortedSequences = sequences.sort((a, b) => a.date.localeCompare(b.date))
        const allEvents = sortedSequences.flatMap((seq) => seq.events)

        storyList.push({
          id: `sequence-${tag}`,
          title: `${tag.replace(/_/g, ' ').charAt(0).toUpperCase() + tag.replace(/_/g, ' ').slice(1)} Journey`,
          description: `A sequence of ${tag}-related activities spanning multiple days`,
          pattern: "sequence",
          events: allEvents.map((e) => ({
            id: e.id,
            date: e.date,
            summary: e.summary,
            tags: e.selected_tags,
            duration: e.duration || 30,
          })),
          tags: [tag],
          frequency: sequences.length,
          totalDuration: allEvents.reduce((sum, e) => sum + (e.duration || 30), 0),
          dateRange: {
            start: sortedSequences[0].date,
            end: sortedSequences[sortedSequences.length - 1].date,
          },
        })
      }
    })

    // 2. Detect Routines (recurring patterns)
    const dailyPatterns = new Map<string, number>()
    events.forEach((event) => {
      const dayOfWeek = new Date(event.date).getDay()
      const pattern = `${dayOfWeek}-${event.selected_tags.sort().join(",")}`
      dailyPatterns.set(pattern, (dailyPatterns.get(pattern) || 0) + 1)
    })

    dailyPatterns.forEach((count, pattern) => {
      if (count >= 2) {
        const [dayOfWeek, tagsStr] = pattern.split("-")
        const tags = tagsStr.split(",")
        const patternEvents = events.filter((e) => {
          const eventDay = new Date(e.date).getDay()
          return eventDay === Number.parseInt(dayOfWeek) && tags.every((tag) => e.selected_tags.includes(tag))
        })

        const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]

        storyList.push({
          id: `routine-${pattern}`,
          title: `${dayNames[Number.parseInt(dayOfWeek)]} Routine`,
          description: `Regular ${tags.map(t => t.replace(/_/g, ' ')).join(" + ")} activities on ${dayNames[Number.parseInt(dayOfWeek)]}s`,
          pattern: "routine",
          events: patternEvents.map((e) => ({
            id: e.id,
            date: e.date,
            summary: e.summary,
            tags: e.selected_tags,
            duration: e.duration || 30,
          })),
          tags,
          frequency: count,
          totalDuration: patternEvents.reduce((sum, e) => sum + (e.duration || 30), 0),
          dateRange: {
            start: patternEvents[0]?.date || "",
            end: patternEvents[patternEvents.length - 1]?.date || "",
          },
        })
      }
    })

    // 3. Detect Activity Bursts (high activity periods)
    const dailyActivity = new Map<string, typeof events>()
    events.forEach((event) => {
      if (!dailyActivity.has(event.date)) {
        dailyActivity.set(event.date, [])
      }
      dailyActivity.get(event.date)!.push(event)
    })

    const highActivityDays = Array.from(dailyActivity.entries())
      .filter(([, dayEvents]) => dayEvents.length >= 3)
      .sort((a, b) => b[1].length - a[1].length)

    highActivityDays.slice(0, 3).forEach(([date, dayEvents], index) => {
      const uniqueTags = [...new Set(dayEvents.flatMap((e) => e.selected_tags))]

      storyList.push({
        id: `burst-${date}`,
        title: `Productive Day: ${new Date(date).toLocaleDateString()}`,
        description: `High activity day with ${dayEvents.length} activities across ${uniqueTags.length} different areas`,
        pattern: "burst",
        events: dayEvents.map((e) => ({
          id: e.id,
          date: e.date,
          summary: e.summary,
          tags: e.selected_tags,
          duration: e.duration || 30,
        })),
        tags: uniqueTags.slice(0, 5),
        frequency: dayEvents.length,
        totalDuration: dayEvents.reduce((sum, e) => sum + (e.duration || 30), 0),
        dateRange: {
          start: date,
          end: date,
        },
      })
    })

    // 4. Detect Trends (increasing/decreasing activity in tags)
    const weeklyTagActivity = new Map<string, Map<string, number>>()

    events.forEach((event) => {
      const weekStart = new Date(event.date)
      weekStart.setDate(weekStart.getDate() - weekStart.getDay())
      const weekKey = weekStart.toISOString().split("T")[0]

      event.selected_tags.forEach((tag) => {
        if (!weeklyTagActivity.has(tag)) {
          weeklyTagActivity.set(tag, new Map())
        }
        const tagWeeks = weeklyTagActivity.get(tag)!
        tagWeeks.set(weekKey, (tagWeeks.get(weekKey) || 0) + (event.duration || 30))
      })
    })

    weeklyTagActivity.forEach((weeks, tag) => {
      const weekEntries = Array.from(weeks.entries()).sort((a, b) => a[0].localeCompare(b[0]))
      if (weekEntries.length >= 3) {
        const values = weekEntries.map(([, value]) => value)
        const isIncreasing = values[values.length - 1] > values[0] * 1.5

        if (isIncreasing) {
          const trendEvents = events.filter((e) => e.selected_tags.includes(tag))

          storyList.push({
            id: `trend-${tag}`,
            title: `Growing Focus: ${tag.replace(/_/g, ' ').charAt(0).toUpperCase() + tag.replace(/_/g, ' ').slice(1)}`,
            description: `Increasing time spent on ${tag.replace(/_/g, ' ')} activities over recent weeks`,
            pattern: "trend",
            events: trendEvents.map((e) => ({
              id: e.id,
              date: e.date,
              summary: e.summary,
              tags: e.selected_tags,
              duration: e.duration || 30,
            })),
            tags: [tag],
            frequency: trendEvents.length,
            totalDuration: trendEvents.reduce((sum, e) => sum + (e.duration || 30), 0),
            dateRange: {
              start: weekEntries[0][0],
              end: weekEntries[weekEntries.length - 1][0],
            },
          })
        }
      }
    })

    return storyList.sort((a, b) => b.totalDuration - a.totalDuration).slice(0, 8)
  }, [events])

  const getPatternIcon = (pattern: Story["pattern"]) => {
    switch (pattern) {
      case "sequence":
        return <ArrowRight className="h-4 w-4" />
      case "routine":
        return <Repeat className="h-4 w-4" />
      case "burst":
        return <Clock className="h-4 w-4" />
      case "trend":
        return <TrendingUp className="h-4 w-4" />
    }
  }

  const getPatternColor = (pattern: Story["pattern"]) => {
    switch (pattern) {
      case "sequence":
        return "bg-blue-100 text-blue-800 border-blue-200"
      case "routine":
        return "bg-green-100 text-green-800 border-green-200"
      case "burst":
        return "bg-orange-100 text-orange-800 border-orange-200"
      case "trend":
        return "bg-purple-100 text-purple-800 border-purple-200"
    }
  }

  return (
    <div className="w-full space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stories List */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Activity Stories</CardTitle>
              <p className="text-sm text-muted-foreground">
                Discovered patterns and narratives from your activity data. Click on a story to explore the details.
              </p>
            </CardHeader>
            <CardContent>
              <ScrollArea className="h-96">
                <div className="space-y-4">
                  {stories.map((story) => (
                    <div
                      key={story.id}
                      className={`p-4 border rounded-lg cursor-pointer transition-all hover:shadow-md ${
                        selectedStory?.id === story.id ? "ring-2 ring-primary" : ""
                      }`}
                      onClick={() => setSelectedStory(story)}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <Badge className={`${getPatternColor(story.pattern)} border`}>
                            {getPatternIcon(story.pattern)}
                            <span className="ml-1 capitalize">{story.pattern}</span>
                          </Badge>
                        </div>
                        <div className="text-right text-sm text-muted-foreground">
                          <div>{Math.round(story.totalDuration / 60)}h total</div>
                          <div>{story.events.length} activities</div>
                        </div>
                      </div>

                      <h3 className="font-semibold mb-2">{story.title}</h3>
                      <p className="text-sm text-muted-foreground mb-3">{story.description}</p>

                      <div className="flex items-center justify-between">
                        <div className="flex flex-wrap gap-1">
                          {story.tags.slice(0, 4).map((tag) => (
                            <Badge
                              key={tag}
                              variant="outline"
                              className="text-xs"
                              style={{
                                backgroundColor: getTagColor(tag) + "20",
                                color: getTagColor(tag),
                                borderColor: getTagColor(tag) + "40",
                              }}
                            >
                              {tag.replace(/_/g, ' ')}
                            </Badge>
                          ))}
                          {story.tags.length > 4 && (
                            <Badge variant="outline" className="text-xs">
                              +{story.tags.length - 4}
                            </Badge>
                          )}
                        </div>
                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                          <Calendar className="h-3 w-3" />
                          <span>
                            {new Date(story.dateRange.start).toLocaleDateString()} -{" "}
                            {new Date(story.dateRange.end).toLocaleDateString()}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}

                  {stories.length === 0 && (
                    <div className="text-center py-8 text-muted-foreground">
                      <p>No patterns detected yet. Add more activities to discover stories!</p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </CardContent>
          </Card>
        </div>

        {/* Story Details */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>{selectedStory ? selectedStory.title : "Select a Story"}</CardTitle>
              {selectedStory && (
                <div className="flex items-center gap-2">
                  <Badge className={`${getPatternColor(selectedStory.pattern)} border`}>
                    {getPatternIcon(selectedStory.pattern)}
                    <span className="ml-1 capitalize">{selectedStory.pattern}</span>
                  </Badge>
                </div>
              )}
            </CardHeader>
            <CardContent>
              {selectedStory ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                      <div className="font-medium">Duration</div>
                      <div className="text-muted-foreground">{Math.round(selectedStory.totalDuration / 60)}h</div>
                    </div>
                    <div>
                      <div className="font-medium">Activities</div>
                      <div className="text-muted-foreground">{selectedStory.events.length}</div>
                    </div>
                    <div>
                      <div className="font-medium">Frequency</div>
                      <div className="text-muted-foreground">{selectedStory.frequency}x</div>
                    </div>
                    <div>
                      <div className="font-medium">Tags</div>
                      <div className="text-muted-foreground">{selectedStory.tags.length}</div>
                    </div>
                  </div>

                  <Separator />

                  <div>
                    <h4 className="font-medium mb-2">Recent Activities</h4>
                    <ScrollArea className="h-48">
                      <div className="space-y-2">
                        {selectedStory.events.slice(0, 10).map((event) => (
                          <div
                            key={event.id}
                            className="p-2 bg-muted/50 rounded cursor-pointer hover:bg-muted transition-colors"
                            onClick={() => openDrawer(event.id)}
                          >
                            <div className="font-medium text-sm">{event.summary}</div>
                            <div className="flex items-center justify-between mt-1">
                              <div className="text-xs text-muted-foreground">{event.date}</div>
                              <div className="text-xs text-muted-foreground">{event.duration}m</div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </div>

                  <Button
                    variant="outline"
                    size="sm"
                    className="w-full bg-transparent"
                    onClick={() => {
                      // Filter to show only events from this story
                      // This would integrate with the filter system
                    }}
                  >
                    View All Activities
                  </Button>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p className="text-sm">Click on a story to see detailed information and related activities</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
