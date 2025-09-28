"use client"

import { useState, useEffect } from "react"
import { Calendar, Database, Clock, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Badge } from "../ui/badge"
import { Separator } from "../ui/separator"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface ImportStatus {
  calendar: {
    last_sync: string | null
    status: string
    total_imported: number
  }
  notion: {
    last_sync: string | null
    status: string
    total_imported: number
  }
}

export function DataIngestionSettings() {
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null)
  const [loading, setLoading] = useState(false)
  const [calendarHours, setCalendarHours] = useState(168) // 1 week default
  const [notionHours, setNotionHours] = useState(168)
  const [importing, setImporting] = useState<{ calendar: boolean; notion: boolean }>({
    calendar: false,
    notion: false,
  })

  const loadImportStatus = async () => {
    try {
      setLoading(true)
      const status = await apiClient.getImportStatus()
      setImportStatus(status)
    } catch (error) {
      console.error('Failed to load import status:', error)
      toast.error("Failed to load import status")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadImportStatus()
  }, [])

  const handleCalendarImport = async () => {
    try {
      setImporting(prev => ({ ...prev, calendar: true }))
      const result = await apiClient.importCalendarData({
        hours_since_last_update: calendarHours
      })
      toast.success(`Calendar import completed: ${result.imported_count} events imported`)
      await loadImportStatus()
    } catch (error) {
      console.error('Calendar import failed:', error)
      toast.error("Calendar import failed")
    } finally {
      setImporting(prev => ({ ...prev, calendar: false }))
    }
  }

  const handleNotionImport = async () => {
    try {
      setImporting(prev => ({ ...prev, notion: true }))
      const result = await apiClient.importNotionData({
        hours_since_last_update: notionHours
      })
      toast.success(`Notion import completed: ${result.imported_count} blocks imported`)
      await loadImportStatus()
    } catch (error) {
      console.error('Notion import failed:', error)
      toast.error("Notion import failed")
    } finally {
      setImporting(prev => ({ ...prev, notion: false }))
    }
  }

  const getStatusBadge = (status: string) => {
    if (!status) return <Badge variant="outline">Unknown</Badge>

    switch (status.toLowerCase()) {
      case 'healthy':
      case 'completed':
        return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Active</Badge>
      case 'running':
        return <Badge variant="secondary">Running</Badge>
      case 'error':
      case 'failed':
        return <Badge variant="destructive">Error</Badge>
      default:
        return <Badge variant="outline">Unknown</Badge>
    }
  }

  const formatLastSync = (lastSync: string | null) => {
    if (!lastSync) return "Never"
    const date = new Date(lastSync)
    const now = new Date()
    const diffHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60))

    if (diffHours < 1) return "Just now"
    if (diffHours < 24) return `${diffHours} hours ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays} days ago`
  }

  if (loading && !importStatus) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Data Ingestion</h2>
        <p className="text-muted-foreground">
          Import and sync data from your connected services. Configure date ranges and manage deduplication.
        </p>
      </div>

      {/* Status Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Import Status
          </CardTitle>
          <CardDescription>
            Current status of data imports from connected services
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Google Calendar Status */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Calendar className="h-4 w-4" />
                  <span className="font-medium">Google Calendar</span>
                </div>
                {importStatus?.calendar && getStatusBadge(importStatus.calendar.status)}
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Last sync: {importStatus?.calendar ? formatLastSync(importStatus.calendar.last_sync) : "Loading..."}</div>
                <div>Total imported: {importStatus?.calendar?.total_imported || 0} events</div>
              </div>
            </div>

            {/* Notion Status */}
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Database className="h-4 w-4" />
                  <span className="font-medium">Notion</span>
                </div>
                {importStatus?.notion && getStatusBadge(importStatus.notion.status)}
              </div>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Last sync: {importStatus?.notion ? formatLastSync(importStatus.notion.last_sync) : "Loading..."}</div>
                <div>Total imported: {importStatus?.notion?.total_imported || 0} blocks</div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Google Calendar Import */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Google Calendar Import
          </CardTitle>
          <CardDescription>
            Import calendar events from Google Calendar. Deduplication ensures no duplicate entries.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="calendar-hours">Hours since last update</Label>
              <Input
                id="calendar-hours"
                type="number"
                min="1"
                max="8760"
                value={calendarHours}
                onChange={(e) => setCalendarHours(parseInt(e.target.value) || 168)}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Import events from the last {calendarHours} hours (max 8760 = 1 year)
              </p>
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleCalendarImport}
                disabled={importing.calendar}
                className="w-full"
              >
                {importing.calendar ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Calendar className="h-4 w-4 mr-2" />
                    Import Calendar Data
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Notion Import */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Notion Import
          </CardTitle>
          <CardDescription>
            Import blocks and pages from Notion. Automatically detects and handles duplicate content.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="notion-hours">Hours since last update</Label>
              <Input
                id="notion-hours"
                type="number"
                min="1"
                max="8760"
                value={notionHours}
                onChange={(e) => setNotionHours(parseInt(e.target.value) || 168)}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Import content modified in the last {notionHours} hours (max 8760 = 1 year)
              </p>
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleNotionImport}
                disabled={importing.notion}
                className="w-full"
              >
                {importing.notion ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Importing...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Import Notion Data
                  </>
                )}
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Best Practices
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Run imports separately to monitor progress and catch errors early</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Use shorter time windows (24-168 hours) for regular updates</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Deduplication automatically prevents duplicate entries</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Track recently added content for efficient tag generation</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}