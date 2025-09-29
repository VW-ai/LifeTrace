"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"
import { useFilteredEvents, useDashboardStore } from "../../lib/store/dashboard-store"
import { getTagColor } from "../../lib/utils/colors"
import { TagFrequencyCards } from "../timeline/tag-frequency-cards"

interface StreamData {
  date: Date
  [key: string]: number | Date
}

export function RiverView({ height = 500 }: { height?: number }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const events = useFilteredEvents()
  const { toggleTag } = useDashboardStore()

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = svgRef.current.clientWidth
    const margin = { top: 20, right: 20, bottom: 40, left: 20 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    // Process data for stream graph
    const tagsByDate = new Map<string, Map<string, number>>()
    const allTags = new Set<string>()

    events.forEach((event) => {
      const date = event.date
      if (!tagsByDate.has(date)) {
        tagsByDate.set(date, new Map())
      }
      const dayTags = tagsByDate.get(date)!

      event.selected_tags.forEach((tag) => {
        allTags.add(tag)
        dayTags.set(tag, (dayTags.get(tag) || 0) + (event.duration || 30))
      })
    })

    // Convert to array format for D3
    const dates = Array.from(tagsByDate.keys()).sort()
    const tags = Array.from(allTags)

    const data: StreamData[] = dates.map((date) => {
      const dayData: StreamData = { date: new Date(date) }
      tags.forEach((tag) => {
        dayData[tag] = tagsByDate.get(date)?.get(tag) || 0
      })
      return dayData
    })

    // Create scales
    const xScale = d3
      .scaleTime()
      .domain(d3.extent(data, (d) => d.date) as [Date, Date])
      .range([0, innerWidth])

    const stack = d3.stack<StreamData>().keys(tags).offset(d3.stackOffsetWiggle).order(d3.stackOrderInsideOut)

    const stackedData = stack(data)

    const yScale = d3
      .scaleLinear()
      .domain(d3.extent(stackedData.flat(2)) as [number, number])
      .range([innerHeight, 0])

    // Create area generator
    const area = d3
      .area<d3.SeriesPoint<StreamData>>()
      .x((d) => xScale(d.data.date))
      .y0((d) => yScale(d[0]))
      .y1((d) => yScale(d[1]))
      .curve(d3.curveBasis)

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    // Create tooltip
    const tooltip = d3
      .select("body")
      .append("div")
      .attr("class", "river-tooltip")
      .style("position", "absolute")
      .style("visibility", "hidden")
      .style("background", "hsl(var(--popover))")
      .style("border", "1px solid hsl(var(--border))")
      .style("border-radius", "8px")
      .style("padding", "12px")
      .style("font-size", "14px")
      .style("box-shadow", "0 4px 12px rgba(0,0,0,0.15)")
      .style("z-index", "1000")
      .style("max-width", "200px")

    // Add streams
    g.selectAll("path")
      .data(stackedData)
      .join("path")
      .attr("d", area)
      .attr("fill", (d, i) => getTagColor(d.key))
      .attr("opacity", 0.8)
      .style("cursor", "pointer")
      .on("mouseenter", function (event, d) {
        d3.select(this).transition().duration(200).attr("opacity", 1).attr("stroke", "#000").attr("stroke-width", 1)

        // Show tooltip with tag name
        const tagName = d.key.replace(/_/g, ' ')
        tooltip
          .style("visibility", "visible")
          .html(`
            <div style="font-weight: 600; margin-bottom: 4px;">${tagName}</div>
            <div style="color: hsl(var(--muted-foreground)); font-size: 12px;">
              Click to filter by this tag
            </div>
          `)
          .style("left", event.pageX + 10 + "px")
          .style("top", event.pageY - 10 + "px")
      })
      .on("mousemove", (event) => {
        tooltip.style("left", event.pageX + 10 + "px").style("top", event.pageY - 10 + "px")
      })
      .on("mouseleave", function () {
        d3.select(this).transition().duration(200).attr("opacity", 0.8).attr("stroke", "none")
        tooltip.style("visibility", "hidden")
      })
      .on("click", function (event, d) {
        event.stopPropagation()
        toggleTag(d.key)
        tooltip.style("visibility", "hidden")
      })

    // Add axes with timeline-style formatting
    const xAxis = d3.axisBottom(xScale)
      .tickFormat(d3.timeFormat("%m/%d"))
      .tickSize(8)
      .tickPadding(12)

    const xAxisGroup = g.append("g")
      .attr("class", "river-x-axis")
      .attr("transform", `translate(0,${innerHeight})`)
      .call(xAxis)

    // Style x-axis with timeline design
    xAxisGroup.select(".domain").remove()

    // Add custom domain line
    xAxisGroup.append("line")
      .attr("x1", 0)
      .attr("x2", innerWidth)
      .attr("y1", 0)
      .attr("y2", 0)
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.6")

    // Style x-axis ticks
    xAxisGroup.selectAll(".tick line")
      .style("stroke", "hsl(var(--border))")
      .style("stroke-width", "1px")
      .style("stroke-opacity", "0.4")

    // Style x-axis text
    xAxisGroup.selectAll("text")
      .style("font-family", "ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif")
      .style("font-size", "13px")
      .style("font-weight", "600")
      .style("fill", "hsl(var(--muted-foreground))")
      .style("cursor", "default")
      .style("user-select", "none")


    // Cleanup tooltip on unmount
    return () => {
      d3.select(".river-tooltip").remove()
    }
  }, [events, height, toggleTag])

  return (
    <div className="space-y-6">
      <div className="w-full bg-card rounded-lg border p-4">
        <div className="mb-4">
          <h3 className="text-lg font-semibold">River View</h3>
          <p className="text-sm text-muted-foreground">
            Temporal flow of activities showing how different tags ebb and flow over time. Stream thickness represents
            time spent on each activity type.
          </p>
        </div>
        <svg ref={svgRef} width="100%" height={height} className="border rounded" />
      </div>

      <TagFrequencyCards limit={10} />
    </div>
  )
}
