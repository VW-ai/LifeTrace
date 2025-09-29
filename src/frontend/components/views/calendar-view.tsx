"use client"

import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import { useFilteredEvents, useDashboardStore } from "../../lib/store/dashboard-store"
import { getTagColor } from "../../lib/utils/colors"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import { ScrollArea } from "../ui/scroll-area"

interface CalendarDay {
  date: Date
  dateString: string
  value: number
  events: Array<{
    id: string
    summary: string
    tags: string[]
    duration: number
  }>
}

export function CalendarView({ height = 600 }: { height?: number }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const events = useFilteredEvents()
  const { openDrawer } = useDashboardStore()
  const [selectedDay, setSelectedDay] = useState<CalendarDay | null>(null)

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = svgRef.current.clientWidth
    const margin = { top: 40, right: 20, bottom: 40, left: 60 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    // Process data by day
    const dayData = new Map<string, CalendarDay>()

    events.forEach((event) => {
      const dateString = event.date
      if (!dayData.has(dateString)) {
        dayData.set(dateString, {
          date: new Date(dateString),
          dateString,
          value: 0,
          events: [],
        })
      }

      const day = dayData.get(dateString)!
      day.value += event.duration || 30
      day.events.push({
        id: event.id,
        summary: event.summary,
        tags: event.selected_tags,
        duration: event.duration || 30,
      })
    })

    const calendarData = Array.from(dayData.values()).sort((a, b) => a.date.getTime() - b.date.getTime())

    // Calculate date range for full calendar grid
    const minDate = d3.min(calendarData, (d) => d.date) || new Date()
    const maxDate = d3.max(calendarData, (d) => d.date) || new Date()

    // Extend to full weeks
    const startDate = new Date(minDate)
    startDate.setDate(startDate.getDate() - startDate.getDay())

    const endDate = new Date(maxDate)
    endDate.setDate(endDate.getDate() + (6 - endDate.getDay()))

    // Generate all days in range
    const allDays: CalendarDay[] = []
    const currentDate = new Date(startDate)

    while (currentDate <= endDate) {
      const dateString = currentDate.toISOString().split("T")[0]
      const existingDay = dayData.get(dateString)

      allDays.push(
        existingDay || {
          date: new Date(currentDate),
          dateString,
          value: 0,
          events: [],
        },
      )

      currentDate.setDate(currentDate.getDate() + 1)
    }

    // Calculate proper calendar grid dimensions
    const weeks = Math.ceil(allDays.length / 7)
    const cellSize = Math.min((innerWidth - 60) / 7, (innerHeight - 80) / weeks) - 4

    // Color scale with better design
    const maxValue = d3.max(calendarData, (d) => d.value) || 1
    const colorScale = d3.scaleLinear()
      .domain([0, maxValue * 0.2, maxValue * 0.6, maxValue])
      .range(["hsl(var(--muted))", "hsl(var(--primary) / 0.3)", "hsl(var(--primary) / 0.7)", "hsl(var(--primary))"])

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    // Add month labels with better positioning
    const monthsInRange = d3.timeMonths(startDate, new Date(endDate.getTime() + 1))
    g.selectAll(".month-label")
      .data(monthsInRange)
      .join("text")
      .attr("class", "month-label")
      .attr("x", (d) => {
        const firstDayOfMonth = new Date(d)
        const daysSinceStart = Math.floor((firstDayOfMonth.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24))
        const weekIndex = Math.floor(daysSinceStart / 7)
        return weekIndex * (cellSize + 4) + cellSize * 2
      })
      .attr("y", -15)
      .attr("text-anchor", "start")
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", "14px")
      .style("font-weight", "600")
      .style("fill", "hsl(var(--foreground))")
      .text(d3.timeFormat("%B %Y"))

    // Add day labels (weekday headers)
    const dayLabels = ["S", "M", "T", "W", "T", "F", "S"]
    g.selectAll(".day-label")
      .data(dayLabels)
      .join("text")
      .attr("class", "day-label")
      .attr("x", (d, i) => i * (cellSize + 4) + cellSize / 2)
      .attr("y", -5)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", "12px")
      .style("font-weight", "500")
      .style("fill", "hsl(var(--muted-foreground))")
      .text((d) => d)

    // Create proper calendar grid
    const cells = g
      .selectAll(".day-cell")
      .data(allDays)
      .join("g")
      .attr("class", "day-cell")
      .attr("transform", (d, i) => {
        const week = Math.floor(i / 7)
        const dayOfWeek = i % 7
        return `translate(${dayOfWeek * (cellSize + 4)}, ${week * (cellSize + 4) + 10})`
      })
      .style("cursor", (d) => (d.events.length > 0 ? "pointer" : "default"))

    // Add modern cell backgrounds
    cells
      .append("rect")
      .attr("width", cellSize)
      .attr("height", cellSize)
      .attr("fill", (d) => d.value > 0 ? colorScale(d.value) : "hsl(var(--muted) / 0.5)")
      .attr("stroke", "hsl(var(--border))")
      .attr("stroke-width", 1)
      .attr("rx", 6)
      .style("transition", "all 0.2s ease")

    // Add day numbers with better styling
    cells
      .append("text")
      .attr("x", cellSize / 2)
      .attr("y", cellSize / 2 - 2)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", `${Math.max(10, cellSize / 5)}px`)
      .style("font-weight", "600")
      .style("fill", (d) => {
        if (d.value === 0) return "hsl(var(--muted-foreground))"
        return d.value > maxValue * 0.6 ? "white" : "hsl(var(--foreground))"
      })
      .style("pointer-events", "none")
      .text((d) => d.date.getDate())

    // Add activity indicator dots for days with events
    cells
      .filter((d) => d.events.length > 0)
      .append("circle")
      .attr("cx", cellSize / 2)
      .attr("cy", cellSize - 8)
      .attr("r", 2)
      .attr("fill", (d) => d.value > maxValue * 0.6 ? "white" : "hsl(var(--primary))")
      .style("opacity", 0.8)

    // Add modern click and hover handlers
    cells
      .on("click", (event, d) => {
        if (d.events.length > 0) {
          setSelectedDay(d)
        }
      })
      .on("mouseenter", function (event, d) {
        const rect = d3.select(this).select("rect")
        if (d.events.length > 0) {
          rect.transition()
            .duration(200)
            .attr("stroke-width", 2)
            .attr("stroke", "hsl(var(--primary))")
            .style("filter", "brightness(1.1)")
        } else {
          rect.transition()
            .duration(200)
            .attr("stroke-width", 2)
            .attr("stroke", "hsl(var(--border))")
        }
      })
      .on("mouseleave", function (event, d) {
        d3.select(this).select("rect")
          .transition()
          .duration(200)
          .attr("stroke-width", 1)
          .attr("stroke", "hsl(var(--border))")
          .style("filter", "none")
      })

    // Add modern legend
    const legendY = weeks * (cellSize + 4) + 40
    const legend = g.append("g").attr("transform", `translate(0, ${legendY})`)

    // Legend title
    legend.append("text")
      .attr("x", 0)
      .attr("y", -8)
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", "12px")
      .style("font-weight", "500")
      .style("fill", "hsl(var(--muted-foreground))")
      .text("Activity Level (minutes per day)")

    // Legend color squares
    const legendSteps = [0, maxValue * 0.2, maxValue * 0.6, maxValue]
    const legendLabels = ["None", "Low", "Medium", "High"]

    legend.selectAll(".legend-item")
      .data(legendSteps)
      .join("g")
      .attr("class", "legend-item")
      .attr("transform", (d, i) => `translate(${i * 60}, 5)`)
      .each(function(d, i) {
        const g = d3.select(this)

        // Color square
        g.append("rect")
          .attr("width", 12)
          .attr("height", 12)
          .attr("rx", 2)
          .attr("fill", d === 0 ? "hsl(var(--muted) / 0.5)" : colorScale(d))
          .attr("stroke", "hsl(var(--border))")
          .attr("stroke-width", 1)

        // Label
        g.append("text")
          .attr("x", 16)
          .attr("y", 6)
          .attr("dy", "0.35em")
          .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
          .style("font-size", "11px")
          .style("font-weight", "500")
          .style("fill", "hsl(var(--foreground))")
          .text(legendLabels[i])
      })
  }, [events, height])

  return (
    <div className="w-full space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar Heatmap */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Calendar Heatmap</CardTitle>
              <p className="text-sm text-muted-foreground">
                Activity intensity by day. Darker colors indicate more time spent. Click on a day to see details.
              </p>
            </CardHeader>
            <CardContent>
              <svg ref={svgRef} width="100%" height={height} />
            </CardContent>
          </Card>
        </div>

        {/* Day Details */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>
                {selectedDay
                  ? `${selectedDay.date.toLocaleDateString("en-US", {
                      weekday: "long",
                      year: "numeric",
                      month: "long",
                      day: "numeric",
                    })}`
                  : "Select a Day"}
              </CardTitle>
              {selectedDay && (
                <p className="text-sm text-muted-foreground">
                  {selectedDay.events.length} activities • {selectedDay.value} minutes total
                </p>
              )}
            </CardHeader>
            <CardContent>
              {selectedDay ? (
                <ScrollArea className="h-96">
                  <div className="space-y-3">
                    {selectedDay.events.map((event) => (
                      <div
                        key={event.id}
                        className="p-3 border rounded-lg hover:bg-muted/50 cursor-pointer transition-colors"
                        onClick={() => openDrawer(event.id)}
                      >
                        <div className="font-medium text-sm mb-2">{event.summary}</div>
                        <div className="flex items-center justify-between">
                          <div className="flex flex-wrap gap-1">
                            {event.tags.map((tag) => (
                              <Badge
                                key={tag}
                                variant="secondary"
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
                          </div>
                          <span className="text-xs text-muted-foreground">{event.duration}m</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </ScrollArea>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p>Click on a day in the calendar to see detailed activities</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
