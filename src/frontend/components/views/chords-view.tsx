"use client"

import { useEffect, useRef, useState } from "react"
import * as d3 from "d3"
import { useFilteredEvents, useDashboardStore } from "../../lib/store/dashboard-store"
import { getTagColor } from "../../lib/utils/colors"
import { Card, CardContent, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import type { Record } from "immutable"

interface ChordData {
  source: number
  target: number
  value: number
}

interface TagNode {
  name: string
  color: string
  index: number
  count: number
}

export function ChordsView({ height = 600 }: { height?: number }) {
  const svgRef = useRef<SVGSVGElement>(null)
  const events = useFilteredEvents()
  const { toggleTag, filters } = useDashboardStore()
  const [hoveredTag, setHoveredTag] = useState<string | null>(null)
  const [selectedConnection, setSelectedConnection] = useState<{ source: string; target: string } | null>(null)

  useEffect(() => {
    if (!svgRef.current || events.length === 0) return

    const svg = d3.select(svgRef.current)
    svg.selectAll("*").remove()

    const width = svgRef.current.clientWidth
    const margin = { top: 20, right: 20, bottom: 20, left: 20 }
    const innerWidth = width - margin.left - margin.right
    const innerHeight = height - margin.top - margin.bottom
    const radius = Math.min(innerWidth, innerHeight) / 2 - 40

    // Calculate tag co-occurrences
    const tagCounts = new Map<string, number>()
    const coOccurrences = new Map<string, Map<string, number>>()

    // Count individual tags
    events.forEach((event) => {
      event.selected_tags.forEach((tag) => {
        tagCounts.set(tag, (tagCounts.get(tag) || 0) + 1)
        if (!coOccurrences.has(tag)) {
          coOccurrences.set(tag, new Map())
        }
      })
    })

    // Count co-occurrences
    events.forEach((event) => {
      const tags = event.selected_tags
      for (let i = 0; i < tags.length; i++) {
        for (let j = i + 1; j < tags.length; j++) {
          const tag1 = tags[i]
          const tag2 = tags[j]

          const map1 = coOccurrences.get(tag1)!
          const map2 = coOccurrences.get(tag2)!

          map1.set(tag2, (map1.get(tag2) || 0) + 1)
          map2.set(tag1, (map2.get(tag1) || 0) + 1)
        }
      }
    })

    // Get top tags (limit to prevent overcrowding)
    const topTags = Array.from(tagCounts.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 12)
      .map(([tag]) => tag)

    if (topTags.length < 2) return

    // Create tag nodes
    const tagNodes: TagNode[] = topTags.map((tag, index) => ({
      name: tag,
      color: getTagColor(tag),
      index,
      count: tagCounts.get(tag) || 0,
    }))

    // Create matrix for chord diagram
    const matrix: number[][] = Array(topTags.length)
      .fill(0)
      .map(() => Array(topTags.length).fill(0))

    topTags.forEach((tag1, i) => {
      topTags.forEach((tag2, j) => {
        if (i !== j) {
          const coOccurrence = coOccurrences.get(tag1)?.get(tag2) || 0
          matrix[i][j] = coOccurrence
        }
      })
    })

    // Create chord layout
    const chord = d3.chord().padAngle(0.05).sortSubgroups(d3.descending)

    const chords = chord(matrix)

    const g = svg
      .append("g")
      .attr("transform", `translate(${margin.left + innerWidth / 2},${margin.top + innerHeight / 2})`)

    // Create arc generator for groups
    const arc = d3
      .arc<d3.ChordGroup>()
      .innerRadius(radius - 20)
      .outerRadius(radius)

    // Create ribbon generator for chords
    const ribbon = d3.ribbon<d3.Chord, d3.ChordSubgroup>().radius(radius - 20)

    // Add groups (tag arcs)
    const group = g.append("g").selectAll("g").data(chords.groups).join("g").style("cursor", "pointer")

    group
      .append("path")
      .attr("d", arc)
      .attr("fill", (d) => tagNodes[d.index].color)
      .attr("stroke", (d) => (filters.selectedTags.includes(tagNodes[d.index].name) ? "#000" : "none"))
      .attr("stroke-width", 2)
      .style("opacity", 0.8)

    // Add group labels
    group.append("text").each((d) => {
      const angle = (d.startAngle + d.endAngle) / 2
      const x = Math.cos(angle - Math.PI / 2) * (radius + 10)
      const y = Math.sin(angle - Math.PI / 2) * (radius + 10)
      d3.select(group.nodes()[d.index])
        .select("text")
        .attr("x", x)
        .attr("y", y)
        .attr("text-anchor", x > 0 ? "start" : "end")
        .attr("dominant-baseline", "middle")
        .style("font-size", "12px")
        .style("font-weight", "500")
        .text(tagNodes[d.index].name.replace(/_/g, ' '))
    })

    // Add ribbons (connections)
    const ribbons = g
      .append("g")
      .selectAll("path")
      .data(chords)
      .join("path")
      .attr("d", ribbon)
      .attr("fill", (d) => tagNodes[d.source.index].color)
      .style("opacity", 0.6)
      .style("cursor", "pointer")

    // Add interactions
    group
      .on("mouseenter", (event, d) => {
        const tagName = tagNodes[d.index].name
        setHoveredTag(tagName)

        // Highlight related ribbons
        ribbons.style("opacity", (chord) =>
          chord.source.index === d.index || chord.target.index === d.index ? 0.8 : 0.1,
        )

        // Highlight the hovered group
        group.select("path").style("opacity", (groupData) => (groupData.index === d.index ? 1 : 0.3))
      })
      .on("mouseleave", () => {
        setHoveredTag(null)
        ribbons.style("opacity", 0.6)
        group.select("path").style("opacity", 0.8)
      })
      .on("click", (event, d) => {
        event.stopPropagation()
        toggleTag(tagNodes[d.index].name)
      })

    ribbons
      .on("mouseenter", (event, d) => {
        const sourceName = tagNodes[d.source.index].name
        const targetName = tagNodes[d.target.index].name
        setSelectedConnection({ source: sourceName, target: targetName })

        d3.select(event.currentTarget).style("opacity", 1).attr("stroke", "#000").attr("stroke-width", 1)
      })
      .on("mouseleave", (event) => {
        setSelectedConnection(null)
        d3.select(event.currentTarget).style("opacity", 0.6).attr("stroke", "none")
      })

    // Add center text
    const centerText = g.append("g").attr("text-anchor", "middle")

    centerText
      .append("text")
      .attr("y", -10)
      .style("font-size", "14px")
      .style("font-weight", "600")
      .style("fill", "#666")
      .text("Tag Co-occurrence")

    centerText
      .append("text")
      .attr("y", 10)
      .style("font-size", "12px")
      .style("fill", "#999")
      .text(`${topTags.length} tags • ${chords.length} connections`)
  }, [events, filters.selectedTags, toggleTag, height])

  // Calculate connection stats
  const connectionStats = selectedConnection
    ? events.filter(
        (event) =>
          event.selected_tags.includes(selectedConnection.source) &&
          event.selected_tags.includes(selectedConnection.target),
      )
    : []

  return (
    <div className="w-full space-y-6">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Chord Diagram */}
        <div className="lg:col-span-2">
          <Card>
            <CardHeader>
              <CardTitle>Tag Co-occurrence Patterns</CardTitle>
              <p className="text-sm text-muted-foreground">
                Chord diagram showing how tags appear together. Thicker connections indicate stronger relationships.
                Hover over tags or connections to explore patterns.
              </p>
            </CardHeader>
            <CardContent>
              <svg ref={svgRef} width="100%" height={height} />
            </CardContent>
          </Card>
        </div>

        {/* Connection Details */}
        <div className="lg:col-span-1">
          <Card>
            <CardHeader>
              <CardTitle>
                {hoveredTag ? `Tag: ${hoveredTag}` : selectedConnection ? `Connection Details` : "Hover to Explore"}
              </CardTitle>
            </CardHeader>
            <CardContent>
              {hoveredTag ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge
                      style={{
                        backgroundColor: getTagColor(hoveredTag) + "20",
                        color: getTagColor(hoveredTag),
                        borderColor: getTagColor(hoveredTag) + "40",
                      }}
                    >
                      {hoveredTag.replace(/_/g, ' ')}
                    </Badge>
                    <span className="text-sm text-muted-foreground">
                      {events.filter((e) => e.selected_tags.includes(hoveredTag)).length} activities
                    </span>
                  </div>
                  <div>
                    <h4 className="font-medium mb-2">Most Connected Tags:</h4>
                    <div className="space-y-1">
                      {Object.entries(
                        events
                          .filter((e) => e.selected_tags.includes(hoveredTag))
                          .flatMap((e) => e.selected_tags.filter((t) => t !== hoveredTag))
                          .reduce(
                            (acc, tag) => {
                              acc[tag] = (acc[tag] || 0) + 1
                              return acc
                            },
                            {} as Record<string, number>,
                          ),
                      )
                        .sort((a, b) => b[1] - a[1])
                        .slice(0, 5)
                        .map(([tag, count]) => (
                          <div key={tag} className="flex items-center justify-between text-sm">
                            <Badge variant="outline" className="text-xs">
                              {tag.replace(/_/g, ' ')}
                            </Badge>
                            <span className="text-muted-foreground">{count}x</span>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>
              ) : selectedConnection ? (
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Badge
                      style={{
                        backgroundColor: getTagColor(selectedConnection.source) + "20",
                        color: getTagColor(selectedConnection.source),
                      }}
                    >
                      {selectedConnection.source.replace(/_/g, ' ')}
                    </Badge>
                    <span className="text-muted-foreground">+</span>
                    <Badge
                      style={{
                        backgroundColor: getTagColor(selectedConnection.target) + "20",
                        color: getTagColor(selectedConnection.target),
                      }}
                    >
                      {selectedConnection.target.replace(/_/g, ' ')}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-sm text-muted-foreground mb-2">
                      {connectionStats.length} activities use both tags
                    </p>
                    <div className="space-y-2 max-h-48 overflow-y-auto">
                      {connectionStats.slice(0, 5).map((event) => (
                        <div key={event.id} className="p-2 bg-muted/50 rounded text-sm">
                          <div className="font-medium">{event.summary}</div>
                          <div className="text-xs text-muted-foreground">{event.date}</div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <p className="text-sm">Hover over tags or connections to see detailed relationships</p>
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
