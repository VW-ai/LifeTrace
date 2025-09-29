"use client"

import { useState, useEffect } from "react"
import { FileText, Filter, RefreshCw, Download, AlertCircle, Info, AlertTriangle, Bug } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Badge } from "../ui/badge"
import { ScrollArea } from "../ui/scroll-area"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "../ui/select"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface LogEntry {
  timestamp: string
  level: string
  message: string
  source: string
  context?: Record<string, any>
}

interface LogsResponse {
  logs: LogEntry[]
  total_count: number
  page_info: {
    limit: number
    offset: number
    has_more: boolean
  }
}

export function ProcessingLogs() {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)
  const [totalCount, setTotalCount] = useState(0)
  const [hasMore, setHasMore] = useState(false)

  // Filters
  const [filters, setFilters] = useState({
    level: '',
    source: '',
    limit: 100,
    offset: 0,
  })

  const [searchTerm, setSearchTerm] = useState('')

  const loadLogs = async (reset = false) => {
    try {
      setLoading(true)
      const params = {
        ...filters,
        offset: reset ? 0 : filters.offset,
      }

      // Only include non-empty filters
      const cleanParams: any = { limit: params.limit, offset: params.offset }
      if (params.level) cleanParams.level = params.level as any
      if (params.source) cleanParams.source = params.source

      const response = await apiClient.getProcessingLogs(cleanParams)

      if (reset) {
        setLogs(response.logs)
      } else {
        setLogs(prev => [...prev, ...response.logs])
      }

      setTotalCount(response.total_count)
      setHasMore(response.page_info.has_more)
      setFilters(prev => ({ ...prev, offset: response.page_info.offset + response.page_info.limit }))

    } catch (error) {
      console.error('Failed to load logs:', error)
      toast.error("Failed to load processing logs")
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value, offset: 0 }))
  }

  const handleRefresh = () => {
    setFilters(prev => ({ ...prev, offset: 0 }))
    loadLogs(true)
  }

  const handleLoadMore = () => {
    loadLogs(false)
  }

  useEffect(() => {
    loadLogs(true)
  }, [filters.level, filters.source, filters.limit])

  const getLevelIcon = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return <AlertCircle className="h-4 w-4 text-red-500" />
      case 'WARN':
        return <AlertTriangle className="h-4 w-4 text-orange-500" />
      case 'INFO':
        return <Info className="h-4 w-4 text-blue-500" />
      case 'DEBUG':
        return <Bug className="h-4 w-4 text-gray-500" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getLevelBadge = (level: string) => {
    switch (level.toUpperCase()) {
      case 'ERROR':
        return <Badge variant="destructive">ERROR</Badge>
      case 'WARN':
        return <Badge variant="default" className="bg-orange-500 hover:bg-orange-600">WARN</Badge>
      case 'INFO':
        return <Badge variant="default" className="bg-blue-500 hover:bg-blue-600">INFO</Badge>
      case 'DEBUG':
        return <Badge variant="secondary">DEBUG</Badge>
      default:
        return <Badge variant="outline">{level}</Badge>
    }
  }

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp)
    return date.toLocaleString()
  }

  const filteredLogs = logs.filter(log => {
    if (!searchTerm) return true
    const searchLower = searchTerm.toLowerCase()
    return (
      log.message.toLowerCase().includes(searchLower) ||
      log.source.toLowerCase().includes(searchLower) ||
      log.level.toLowerCase().includes(searchLower)
    )
  })

  const getUniqueValues = (key: keyof LogEntry) => {
    const values = Array.from(new Set(logs.map(log => log[key] as string)))
    return values.filter(Boolean).sort()
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Processing Logs</h2>
        <p className="text-muted-foreground">
          View system processing logs for debugging and monitoring workflow operations.
        </p>
      </div>

      {/* Filters and Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Filters & Controls
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            {/* Search */}
            <div className="space-y-2">
              <Label htmlFor="search">Search</Label>
              <Input
                id="search"
                placeholder="Search logs..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>

            {/* Level Filter */}
            <div className="space-y-2">
              <Label>Log Level</Label>
              <Select value={filters.level || 'all'} onValueChange={(value) => handleFilterChange('level', value === 'all' ? '' : value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All levels</SelectItem>
                  <SelectItem value="ERROR">ERROR</SelectItem>
                  <SelectItem value="WARN">WARN</SelectItem>
                  <SelectItem value="INFO">INFO</SelectItem>
                  <SelectItem value="DEBUG">DEBUG</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Source Filter */}
            <div className="space-y-2">
              <Label>Source</Label>
              <Select value={filters.source || 'all'} onValueChange={(value) => handleFilterChange('source', value === 'all' ? '' : value)}>
                <SelectTrigger>
                  <SelectValue placeholder="All sources" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All sources</SelectItem>
                  {getUniqueValues('source').map(source => (
                    <SelectItem key={source} value={source}>{source}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Limit */}
            <div className="space-y-2">
              <Label>Limit</Label>
              <Select value={filters.limit.toString()} onValueChange={(value) => handleFilterChange('limit', value)}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="50">50</SelectItem>
                  <SelectItem value="100">100</SelectItem>
                  <SelectItem value="200">200</SelectItem>
                  <SelectItem value="500">500</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="text-sm text-muted-foreground">
              Showing {filteredLogs.length} of {totalCount} total logs
            </div>
            <div className="flex gap-2">
              <Button variant="outline" size="sm" onClick={handleRefresh}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Logs Display */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Logs
          </CardTitle>
          <CardDescription>
            Processing logs from system operations and workflows
          </CardDescription>
        </CardHeader>
        <CardContent>
          {filteredLogs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              {loading ? "Loading logs..." : "No logs found matching current filters"}
            </div>
          ) : (
            <ScrollArea className="h-96">
              <div className="space-y-2">
                {filteredLogs.map((log, index) => (
                  <div key={index} className="border rounded-md p-3 space-y-2">
                    {/* Header */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {getLevelIcon(log.level)}
                        {getLevelBadge(log.level)}
                        <Badge variant="outline" className="text-xs">
                          {log.source}
                        </Badge>
                      </div>
                      <span className="text-xs text-muted-foreground">
                        {formatTimestamp(log.timestamp)}
                      </span>
                    </div>

                    {/* Message */}
                    <div className="text-sm">
                      {log.message}
                    </div>

                    {/* Context */}
                    {log.context && Object.keys(log.context).length > 0 && (
                      <details className="text-xs">
                        <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
                          Show context data
                        </summary>
                        <pre className="mt-2 p-2 bg-muted rounded text-xs overflow-x-auto">
                          {JSON.stringify(log.context, null, 2)}
                        </pre>
                      </details>
                    )}
                  </div>
                ))}
              </div>
            </ScrollArea>
          )}

          {/* Load More */}
          {hasMore && !loading && searchTerm === '' && (
            <div className="text-center mt-4">
              <Button variant="outline" onClick={handleLoadMore}>
                Load More
              </Button>
            </div>
          )}

          {loading && (
            <div className="text-center py-4">
              <div className="inline-flex items-center gap-2 text-muted-foreground">
                <RefreshCw className="h-4 w-4 animate-spin" />
                Loading logs...
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Log Level Legend */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Log Level Reference</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
            <div className="flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-red-500" />
              <span><strong>ERROR:</strong> Critical failures</span>
            </div>
            <div className="flex items-center gap-2">
              <AlertTriangle className="h-4 w-4 text-orange-500" />
              <span><strong>WARN:</strong> Important notices</span>
            </div>
            <div className="flex items-center gap-2">
              <Info className="h-4 w-4 text-blue-500" />
              <span><strong>INFO:</strong> General information</span>
            </div>
            <div className="flex items-center gap-2">
              <Bug className="h-4 w-4 text-gray-500" />
              <span><strong>DEBUG:</strong> Detailed tracing</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}