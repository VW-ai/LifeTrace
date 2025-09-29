"use client"

import { useEffect, useRef } from "react"
import * as d3 from "d3"
import { useDashboardStore, useFilteredEvents, useTagStats } from "../../lib/store/dashboard-store"
import { getTagColor } from "../../lib/utils/colors"
import { TagFrequencyCards } from "../timeline/tag-frequency-cards"

interface Node {
  id: string
  name: string
  type: "tag" | "event"
  count?: number
  color: string
  x?: number
  y?: number
  fx?: number | null
  fy?: number | null
}

interface Link {
  source: string | Node
  target: string | Node
  value: number
}

export function GalaxyView({ height = 600 }: { height?: number }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const events = useFilteredEvents()
  const tagStats = useTagStats()
  const { toggleTag, filters } = useDashboardStore()

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = svgRef.current.clientWidth
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom

    // Create nodes and links
    const nodes: Node[] = []
    const links: Link[] = []
    const tagConnections = new Map<string, Map<string, number>>()

    // Add tag nodes
    tagStats.forEach(({ tag, count }) => {
      nodes.push({
        id: tag,
        name: tag,
        type: "tag",
        count,
        color: getTagColor(tag),
      })
      tagConnections.set(tag, new Map())
    })

    // Calculate tag co-occurrences
    events.forEach((event) => {
      const eventTags = event.selected_tags
      for (let i = 0; i < eventTags.length; i++) {
        for (let j = i + 1; j < eventTags.length; j++) {
          const tag1 = eventTags[i]
          const tag2 = eventTags[j]

          if (tagConnections.has(tag1) && tagConnections.has(tag2)) {
            const connections1 = tagConnections.get(tag1)!
            const connections2 = tagConnections.get(tag2)!

            connections1.set(tag2, (connections1.get(tag2) || 0) + 1)
            connections2.set(tag1, (connections2.get(tag1) || 0) + 1)
          }
        }
      }
    })

    // Create links from co-occurrences
    tagConnections.forEach((connections, tag1) => {
      connections.forEach((count, tag2) => {
        if (tag1 < tag2) {
          // Avoid duplicate links
          links.push({
            source: tag1,
            target: tag2,
            value: count,
          })
        }
      })
    })

    // Create force simulation
    const simulation = d3
      .forceSimulation<Node>(nodes)
      .force(
        "link",
        d3
          .forceLink<Node, Link>(links)
          .id((d) => d.id)
          .strength(0.3),
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(innerWidth / 2, innerHeight / 2))
      .force(
        "collision",
        d3.forceCollide().radius((d) => Math.sqrt((d as Node).count || 1) * 3 + 10),
      )

    const g = svg.append("g").attr("transform", `translate(${margin.left},${margin.top})`)

    // Add zoom behavior
    const zoom = d3
      .zoom<SVGSVGElement, unknown>()
      .scaleExtent([0.1, 4])
      .on("zoom", (event) => {
        g.attr("transform", event.transform)
      })

    svg.call(zoom)

    // Create links
    const link = g
      .append("g")
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .attr("stroke-width", (d) => Math.sqrt(d.value) * 2)

    // Create nodes
    const node = g
      .append("g")
      .selectAll("g")
      .data(nodes)
      .join("g")
      .style("cursor", "pointer")
      .call(
        d3
          .drag<SVGGElement, Node>()
          .on("start", (event, d) => {
            if (!event.active) simulation.alphaTarget(0.3).restart()
            d.fx = d.x
            d.fy = d.y
          })
          .on("drag", (event, d) => {
            d.fx = event.x
            d.fy = event.y
          })
          .on("end", (event, d) => {
            if (!event.active) simulation.alphaTarget(0)
            d.fx = null
            d.fy = null
          }),
      )

    // Add circles to nodes
    node
      .append("circle")
      .attr("r", (d) => Math.sqrt(d.count || 1) * 3 + 8)
      .attr("fill", (d) => d.color)
      .attr("stroke", (d) => (filters.selectedTags.includes(d.id) ? "#000" : "none"))
      .attr("stroke-width", 3)
      .style("opacity", 0.8)

    // Add labels to nodes - dynamically size text to fit within circles
    node
      .append("text")
      .text((d) => d.name.replace(/_/g, ' '))
      .attr("x", 0)
      .attr("y", 0)
      .attr("text-anchor", "middle")
      .attr("dominant-baseline", "middle")
      .style("font-size", (d) => {
        const radius = Math.sqrt(d.count || 1) * 3 + 8
        const displayName = d.name.replace(/_/g, ' ')
        const textLength = displayName.length
        // Calculate font size to fit text within circle diameter
        const maxFontSize = Math.min(radius * 1.4, (radius * 2) / (textLength * 0.6))
        return `${Math.max(8, Math.min(16, maxFontSize))}px`
      })
      .style("font-weight", "600")
      .style("fill", "white")
      .style("text-shadow", "0 1px 2px rgba(0,0,0,0.8)")
      .style("pointer-events", "none")

    // Add click handler for tag filtering
    node.on("click", (event, d) => {
      event.stopPropagation()
      toggleTag(d.id)
    })

    // Add hover effects - 1.75x zoom for both circle and text
    node
      .on("mouseenter", function (event, d) {
        const originalRadius = Math.sqrt(d.count || 1) * 3 + 8
        const originalFontSize = parseFloat(d3.select(this).select("text").style("font-size"))

        d3.select(this)
          .select("circle")
          .transition()
          .duration(200)
          .style("opacity", 1)
          .attr("r", originalRadius * 1.75)

        d3.select(this)
          .select("text")
          .transition()
          .duration(200)
          .style("font-size", `${originalFontSize * 1.75}px`)
      })
      .on("mouseleave", function (event, d) {
        const originalRadius = Math.sqrt(d.count || 1) * 3 + 8
        const displayName = d.name.replace(/_/g, ' ')
        const textLength = displayName.length
        const maxFontSize = Math.min(originalRadius * 1.4, (originalRadius * 2) / (textLength * 0.6))
        const originalFontSize = Math.max(8, Math.min(16, maxFontSize))

        d3.select(this)
          .select("circle")
          .transition()
          .duration(200)
          .style("opacity", 0.8)
          .attr("r", originalRadius)

        d3.select(this)
          .select("text")
          .transition()
          .duration(200)
          .style("font-size", `${originalFontSize}px`)
      })

    // Update positions on simulation tick
    simulation.on("tick", () => {
      link
        .attr("x1", (d) => (d.source as Node).x!)
        .attr("y1", (d) => (d.source as Node).y!)
        .attr("x2", (d) => (d.target as Node).x!)
        .attr("y2", (d) => (d.target as Node).y!)

      node.attr("transform", (d) => `translate(${d.x},${d.y})`)
    })

    return () => {
      simulation.stop()
    }
  }, [events, tagStats, filters.selectedTags, toggleTag, height])

  return (
    <div className="space-y-6">
      <div className="w-full bg-card rounded-lg border p-4">
        <div className="mb-4">
          <h3 className="text-lg font-semibold">Galaxy View</h3>
          <p className="text-sm text-muted-foreground">
            Tag relationships as an interactive network. Node size represents usage frequency, connections show
            co-occurrence patterns. Click tags to filter, drag to explore.
          </p>
        </div>
        <svg ref={svgRef} width="100%" height={height} className="border rounded" />
      </div>

      <TagFrequencyCards limit={10} />
    </div>
  )
}
