"use client"

import { useState } from "react"
import { Search, Calendar, Filter, X, RotateCcw } from "lucide-react"
import { Input } from "../ui/input"
import { Button } from "../ui/button"
import { Badge } from "../ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover"
import { useDashboardStore } from "../../lib/store/dashboard-store"
import { generateTagColor } from "../../lib/utils/colors"
import { formatDate } from "../../lib/utils/date"
import { formatTagName } from "../../lib/utils"

export function FilterBar() {
  const { filters, setFilters, setTimePeriod, toggleTag, clearFilters, events, tags } = useDashboardStore()

  const [searchInput, setSearchInput] = useState(filters.searchQuery)
  const [isFilterOpen, setIsFilterOpen] = useState(false)

  // Get unique sources from events
  const availableSources = Array.from(new Set(events.map((event) => event.source)))

  const handleSearchChange = (value: string) => {
    setSearchInput(value)
    setFilters({ searchQuery: value })
  }

  const handleTimePeriodChange = (period: string) => {
    setTimePeriod(period as any)
  }

  const toggleSource = (source: string) => {
    const selectedSources = filters.selectedSources.includes(source)
      ? filters.selectedSources.filter((s) => s !== source)
      : [...filters.selectedSources, source]

    setFilters({ selectedSources })
  }

  const hasActiveFilters =
    filters.selectedTags.length > 0 || filters.selectedSources.length > 0 || filters.searchQuery.length > 0

  return (
    <div className="space-y-4">
      {/* Main filter controls */}
      <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center">
        {/* Search */}
        <div className="relative flex-1 min-w-0">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground h-4 w-4" />
          <Input
            placeholder="Search activities, tags, or details..."
            value={searchInput}
            onChange={(e) => handleSearchChange(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Time period selector */}
        <Select value={filters.timePeriod} onValueChange={handleTimePeriodChange}>
          <SelectTrigger className="w-[140px]">
            <Calendar className="h-4 w-4 mr-2" />
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="1w">Last Week</SelectItem>
            <SelectItem value="1m">Last Month</SelectItem>
            <SelectItem value="3m">Last 3 Months</SelectItem>
            <SelectItem value="1y">Last Year</SelectItem>
            <SelectItem value="all">All Time</SelectItem>
          </SelectContent>
        </Select>

        {/* Advanced filters */}
        <Popover open={isFilterOpen} onOpenChange={setIsFilterOpen}>
          <PopoverTrigger asChild>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              Filters
              {hasActiveFilters && (
                <Badge variant="secondary" className="ml-2 h-5 w-5 p-0 text-xs">
                  {filters.selectedTags.length + filters.selectedSources.length}
                </Badge>
              )}
            </Button>
          </PopoverTrigger>
          <PopoverContent className="w-80" align="end">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h4 className="font-medium">Advanced Filters</h4>
                {hasActiveFilters && (
                  <Button variant="ghost" size="sm" onClick={clearFilters} className="h-8 px-2">
                    <RotateCcw className="h-3 w-3 mr-1" />
                    Reset
                  </Button>
                )}
              </div>

              {/* Sources filter */}
              {availableSources.length > 0 && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Sources</label>
                  <div className="flex flex-wrap gap-2">
                    {availableSources.map((source) => {
                      const isSelected = filters.selectedSources.includes(source)
                      return (
                        <Badge
                          key={source}
                          variant={isSelected ? "default" : "outline"}
                          className="cursor-pointer hover:bg-accent"
                          onClick={() => toggleSource(source)}
                        >
                          {source}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Popular tags */}
              {tags.length > 0 && (
                <div>
                  <label className="text-sm font-medium mb-2 block">Popular Tags</label>
                  <div className="flex flex-wrap gap-2 max-h-32 overflow-y-auto">
                    {tags.slice(0, 20).map((tag) => {
                      const isSelected = filters.selectedTags.includes(tag.name)
                      const tagColor = generateTagColor(tag.name)

                      return (
                        <Badge
                          key={tag.id}
                          variant={isSelected ? "default" : "outline"}
                          className="cursor-pointer hover:bg-accent"
                          style={isSelected ? { backgroundColor: tagColor, color: "white" } : {}}
                          onClick={() => toggleTag(tag.name)}
                        >
                          {formatTagName(tag.name)}
                        </Badge>
                      )
                    })}
                  </div>
                </div>
              )}
            </div>
          </PopoverContent>
        </Popover>

        {/* Clear all filters */}
        {hasActiveFilters && (
          <Button
            variant="ghost"
            size="sm"
            onClick={clearFilters}
            className="text-muted-foreground hover:text-foreground"
          >
            <X className="h-4 w-4 mr-1" />
            Clear All
          </Button>
        )}
      </div>

      {/* Active filters display */}
      {hasActiveFilters && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-sm text-muted-foreground">Active filters:</span>

          {/* Selected tags */}
          {filters.selectedTags.map((tag) => (
            <Badge
              key={tag}
              variant="secondary"
              className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground"
              style={{ backgroundColor: generateTagColor(tag), color: "white" }}
              onClick={() => toggleTag(tag)}
            >
              {formatTagName(tag)}
              <X className="h-3 w-3 ml-1" />
            </Badge>
          ))}

          {/* Selected sources */}
          {filters.selectedSources.map((source) => (
            <Badge
              key={source}
              variant="outline"
              className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground hover:border-destructive"
              onClick={() => toggleSource(source)}
            >
              {source}
              <X className="h-3 w-3 ml-1" />
            </Badge>
          ))}

          {/* Search query */}
          {filters.searchQuery && (
            <Badge
              variant="outline"
              className="cursor-pointer hover:bg-destructive hover:text-destructive-foreground hover:border-destructive"
              onClick={() => handleSearchChange("")}
            >
              Search: "{filters.searchQuery}"
              <X className="h-3 w-3 ml-1" />
            </Badge>
          )}
        </div>
      )}

      {/* Filter summary */}
      <div className="flex items-center justify-between text-sm text-muted-foreground">
        <div>
          Showing {events.length} events from {formatDate(filters.dateRange.start)} to{" "}
          {formatDate(filters.dateRange.end)}
        </div>

        {filters.selectedTags.length > 0 && (
          <div>
            {filters.selectedTags.length} tag{filters.selectedTags.length !== 1 ? "s" : ""} selected
          </div>
        )}
      </div>
    </div>
  )
}
