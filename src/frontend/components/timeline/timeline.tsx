"use client"

import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import { useDashboardStore, useFilteredEvents } from "../../lib/store/dashboard-store"
import { generateTagColor } from "../../lib/utils/colors"
import { formatDate, formatTime } from "../../lib/utils/date"
import { formatTagName } from "../../lib/utils"

interface TimelineProps {
  height?: number
  className?: string
}

export function Timeline({ height = 400, className = "" }: TimelineProps) {
  const svgRef = useRef<SVGSVGElement>(null)
  const brushRef = useRef<d3.BrushBehavior<unknown>>()
  const [dimensions, setDimensions] = useState({ width: 800, height })

  const events = useFilteredEvents()
  const { setBrushSelection, brushSelection, openDrawer } = useDashboardStore()

  // Handle resize
  useEffect(() => {
    const handleResize = () => {
      if (svgRef.current) {
        const rect = svgRef.current.getBoundingClientRect()
        setDimensions({ width: rect.width, height })
      }
    }

    handleResize()
    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [height])

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const margin = { top: 20, right: 40, bottom: 60, left: 20 }
    const width = dimensions.width - margin.left - margin.right
    const innerHeight = dimensions.height - margin.top - margin.bottom

    // Create main group
    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    // Create D3 local time parser to avoid timezone issues
    const parseLocal = d3.timeParse("%Y-%m-%d %H:%M")

    // Process data for timeline
    const timelineData = events.map((event, index) => {
      // Handle missing or empty time values
      const timeValue = event.time && event.time.trim() ? event.time : "00:00"

      // Create date string in format that D3 can parse locally
      const dateTimeString = `${event.date} ${timeValue}`
      const datetime = parseLocal(dateTimeString)

      if (index < 3) {
        console.log('Local parsing debug:', {
          originalDate: event.date,
          originalTime: event.time,
          dateTimeString,
          parsedDatetime: datetime,
          localString: datetime?.toString(),
          summary: event.summary
        })
      }

      // Skip events with invalid dates
      if (!datetime || isNaN(datetime.getTime())) {
        console.warn(`Invalid date for event: ${dateTimeString}`, event)
        return null
      }

      return {
        ...event,
        datetime,
        duration: event.duration || 30, // Default 30 minutes if not specified
      }
    }).filter(Boolean) as any[]

    // Sort by datetime
    timelineData.sort((a, b) => a.datetime.getTime() - b.datetime.getTime())

    // Create scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(timelineData, (d) => d.datetime) as [Date, Date])
      .range([0, width])

    // Group events by source for y-axis lanes
    const sources = Array.from(new Set(timelineData.map((d) => d.source)))
    const yScale = d3.scaleBand().domain(sources).range([0, innerHeight]).padding(0.1)

    // Create highly responsive and modern axes with intelligent time formatting
    const timeExtent = d3.extent(timelineData, (d) => d.datetime) as [Date, Date]
    const timeSpan = timeExtent[1].getTime() - timeExtent[0].getTime()
    const daySpan = timeSpan / (1000 * 60 * 60 * 24)

    console.log('Timeline debug:', {
      timeExtent,
      daySpan,
      eventsCount: timelineData.length,
      sampleEvent: timelineData[0]
    })

    // Determine tick count and format based on time span
    let responsiveTickCount: number
    let timeFormat: string

    if (daySpan <= 1) {
      // Same day - show hours
      responsiveTickCount = Math.max(4, Math.min(8, Math.floor(width / 120)))
      timeFormat = width > 600 ? "%H:%M" : "%H:%M"
    } else if (daySpan <= 7) {
      // Week or less - show day and time
      responsiveTickCount = Math.max(4, Math.min(10, Math.floor(width / 100)))
      timeFormat = width > 600 ? "%b %d %H:%M" : "%m/%d %H:%M"
    } else if (daySpan <= 31) {
      // Month or less - show dates
      responsiveTickCount = Math.max(4, Math.min(12, Math.floor(width / 80)))
      timeFormat = width > 600 ? "%b %d" : "%m/%d"
    } else {
      // Longer periods - show months
      responsiveTickCount = Math.max(3, Math.min(8, Math.floor(width / 120)))
      timeFormat = width > 600 ? "%b %Y" : "%m/%y"
    }

    // Ensure axis ticks align with our locally parsed dates
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.timeFormat(timeFormat))
      .ticks(d3.timeDay.every(1)) // Force daily ticks to match our date parsing
      .tickSize(8)
      .tickPadding(12)

    const yAxis = d3.axisLeft(yScale)
      .tickSize(6)
      .tickPadding(16)
      .tickFormat(() => "")

    // X-axis with aggressive modern styling
    const xAxisGroup = g.append("g")
      .attr("class", "timeline-x-axis")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(xAxis)

    // Completely remove default domain line and replace with subtle line
    xAxisGroup.select(".domain").remove()

    // Add custom domain line
    xAxisGroup.append("line")
      .attr("x1", 0)
      .attr("x2", width)
      .attr("y1", 0)
      .attr("y2", 0)
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.6")

    // Style x-axis ticks with modern design
    xAxisGroup.selectAll(".tick line")
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.4")
      .style("stroke-dasharray", "none")

    // X-axis text with comprehensive modern styling - adjust based on time format
    const needsRotation = daySpan > 7 || width < 600

    xAxisGroup.selectAll("text")
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", width > 600 ? "13px" : "11px")
      .style("font-weight", "600")
      .style("fill", "hsl(var(--muted-foreground))")
      .style("text-anchor", needsRotation ? "end" : "middle")
      .attr("transform", needsRotation ? "rotate(-35)" : "rotate(0)")
      .attr("dx", needsRotation ? "-0.5em" : "0")
      .attr("dy", needsRotation ? "0.5em" : "1.2em")
      .style("cursor", "default")
      .style("user-select", "none")

    // Y-axis with aggressive modern styling
    const yAxisGroup = g.append("g")
      .attr("class", "timeline-y-axis")
      .call(yAxis)

    // Remove default domain and replace with custom
    yAxisGroup.select(".domain").remove()

    // Add custom y-axis domain line
    yAxisGroup.append("line")
      .attr("x1", 0)
      .attr("x2", 0)
      .attr("y1", 0)
      .attr("y2", innerHeight)
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.6")

    // Style y-axis ticks
    yAxisGroup.selectAll(".tick line")
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.3")

    // Y-axis text is hidden via tickFormat, no additional styling needed

    // Add modern grid lines with better responsiveness
    const gridGroup = g.append("g")
      .attr("class", "timeline-grid")
      .attr("transform", `translate(0,${innerHeight})`)

    // Vertical grid lines
    gridGroup.call(
      d3.axisBottom(xScale)
        .tickSize(-innerHeight)
        .tickFormat(() => "")
        .ticks(responsiveTickCount)
    )

    // Remove grid domain line
    gridGroup.select(".domain").remove()

    // Style grid lines with modern appearance
    gridGroup.selectAll("line")
      .style("stroke", "hsl(var(--border))")
      .style("stroke-opacity", "0.1")
      .style("stroke-width", "1px")
      .style("stroke-dasharray", width > 600 ? "1,3" : "1,2")

    // Add horizontal grid lines for y-axis
    const horizontalGrid = g.append("g")
      .attr("class", "timeline-horizontal-grid")

    // Create horizontal lines for each source lane
    sources.forEach((source: string) => {
      const y = (yScale(source) || 0) + yScale.bandwidth() / 2
      horizontalGrid.append("line")
        .attr("x1", 0)
        .attr("x2", width)
        .attr("y1", y)
        .attr("y2", y)
        .style("stroke", "hsl(var(--border))")
        .style("stroke-opacity", "0.05")
        .style("stroke-width", "1px")
    })

    // Add brush for time range selection FIRST (so events render on top)
    const brush = d3
      .brushX()
      .extent([
        [0, 0],
        [width, innerHeight],
      ])
      .on("start", (event) => {
        // Prevent event bubbling to avoid conflicts
        event.sourceEvent?.stopPropagation()
      })
      .on("brush", (event) => {
        // Optional: Show preview during brushing
        if (event.selection) {
          const [x0, x1] = event.selection
          const startDate = xScale.invert(x0)
          const endDate = xScale.invert(x1)
          console.log("Brushing:", startDate.toISOString().split("T")[0], "to", endDate.toISOString().split("T")[0])
        }
      })
      .on("end", (event) => {
        if (!event.selection) {
          setBrushSelection(null)
          return
        }

        const [x0, x1] = event.selection
        const startDate = xScale.invert(x0)
        const endDate = xScale.invert(x1)
        setBrushSelection({
          start: startDate.toISOString().split("T")[0],
          end: endDate.toISOString().split("T")[0],
        })
      })

    brushRef.current = brush

    const brushGroup = g.append("g").attr("class", "brush").call(brush)

    // Style brush with modern appearance - make overlay not interfere with event clicks
    brushGroup.selectAll(".overlay")
      .style("fill", "transparent")
      .style("pointer-events", "all") // Ensure brush can still receive events

    brushGroup
      .selectAll(".selection")
      .style("fill", "hsl(var(--primary))")
      .style("fill-opacity", 0.15)
      .style("stroke", "hsl(var(--primary))")
      .style("stroke-width", 2)
      .style("stroke-dasharray", "none")
      .style("rx", 4)

    brushGroup
      .selectAll(".handle")
      .style("fill", "hsl(var(--primary))")
      .style("stroke", "hsl(var(--background))")
      .style("stroke-width", 2)
      .style("rx", 3)

    // Create tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "timeline-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background", "hsl(var(--popover))")
      .style("border", "1px solid hsl(var(--border))")
      .style("border-radius", "8px")
      .style("padding", "12px")
      .style("font-size", "14px")
      .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
      .style("z-index", "1000")
      .style("max-width", "300px")

    // Draw events as modern rounded rectangles with shadows (AFTER brush, so they're on top)
    const eventRects = g
      .selectAll(".event-rect")
      .data(timelineData)
      .enter()
      .append("rect")
      .attr("class", "event-rect")
      .attr("x", (d) => {
        // Try manual offset to fix one-day shift
        const basePosition = xScale(d.datetime)
        console.log('Event position debug:', {
          date: d.date,
          datetime: d.datetime,
          basePosition,
          summary: d.summary
        })
        return basePosition
      })
      .attr("y", (d) => (yScale(d.source) || 0) + 3)
      .attr("width", (d) => Math.max(3, (d.duration / 60) * 25)) // Width based on duration
      .attr("height", yScale.bandwidth() - 6)
      .attr("rx", 6)
      .attr("ry", 6)
      .style("fill", (d) => {
        const color = d.selected_tags.length > 0 ? generateTagColor(d.selected_tags[0]) : "hsl(var(--muted))"
        return color
      })
      .style("stroke", "rgba(255,255,255,0.3)")
      .style("stroke-width", 1)
      .style("filter", "drop-shadow(0 2px 4px rgba(0,0,0,0.1))")
      .style("cursor", "pointer")
      .style("pointer-events", "all")
      .style("transition", "all 0.2s ease")
      .on("mouseover", function (event: any, d: any) {
        // No visual changes to the element, just show tooltip
        const tagList =
          d.selected_tags.length > 0
            ? d.selected_tags
                .map(
                  (tag: any) =>
                    `<span style="background: ${generateTagColor(tag)}; color: white; padding: 2px 6px; border-radius: 4px; font-size: 11px;">${formatTagName(tag)}</span>`,
                )
                .join(" ")
            : '<span style="color: hsl(var(--muted-foreground));">No tags</span>'

        tooltip
          .style("visibility", "visible")
          .html(`
            <div style="font-weight: 600; margin-bottom: 8px;">${d.summary}</div>
            <div style="color: hsl(var(--muted-foreground)); font-size: 12px; margin-bottom: 4px;">
              ${formatDate(d.date)} at ${formatTime(d.time)}
            </div>
            <div style="color: hsl(var(--muted-foreground)); font-size: 12px; margin-bottom: 8px;">
              Source: ${d.source}
            </div>
            <div style="margin-bottom: 4px;">
              ${tagList}
            </div>
            ${d.details ? `<div style="margin-top: 8px; font-size: 12px; color: hsl(var(--muted-foreground));">${d.details}</div>` : ""}
          `)
          .style("left", event.pageX + 10 + "px")
          .style("top", event.pageY - 10 + "px")
      })
      .on("mousemove", (event: any) => {
        tooltip.style("left", event.pageX + 10 + "px").style("top", event.pageY - 10 + "px")
      })
      .on("mouseout", function () {
        // No visual changes to revert, just hide tooltip
        tooltip.style("visibility", "hidden")
      })
      .on("click", (event: any, d: any) => {
        console.log("Event clicked:", d.summary, d.id)
        event.stopPropagation()
        openDrawer(d.id)
      })


    // Add double-click to reset brush
    svg.on("dblclick", () => {
      brushGroup.call(brush.clear)
      setBrushSelection(null)
    })

    // Cleanup tooltip on unmount
    return () => {
      d3.select(".timeline-tooltip").remove()
    }
  }, [events, dimensions, setBrushSelection, openDrawer])

  return (
    <div className={`timeline-container ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Timeline</h3>
        <div className="text-sm text-muted-foreground">
          {events.length} events • Drag to filter by time range • Double-click to reset
        </div>
      </div>

      <div className="border rounded-lg bg-card overflow-hidden">
        <svg ref={svgRef} width="100%" height={height} className="timeline-svg" />
      </div>

      {brushSelection && (
        <div className="mt-2 text-sm text-muted-foreground">
          Selected range: {formatDate(brushSelection.start)} - {formatDate(brushSelection.end)}
        </div>
      )}
    </div>
  )
}
