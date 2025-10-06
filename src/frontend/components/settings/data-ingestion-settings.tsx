"use client"

import { useState, useEffect } from "react"
import { Calendar, Database, Clock, CheckCircle, AlertCircle, Loader2 } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Badge } from "../ui/badge"
import { Separator } from "../ui/separator"
import { Progress } from "../ui/progress"
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
  const [backfillMonths, setBackfillMonths] = useState(7)
  const [isBackfilling, setIsBackfilling] = useState(false)
  const [notionIndexScope, setNotionIndexScope] = useState<'all' | 'recent'>('recent')
  const [notionIndexHours, setNotionIndexHours] = useState(24)
  const [isIndexing, setIsIndexing] = useState(false)
  const [progress, setProgress] = useState<{ [key: string]: number }>({})
  const [progressMessage, setProgressMessage] = useState<{ [key: string]: string }>({})

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
    const key = 'calendar'
    try {
      setImporting(prev => ({ ...prev, calendar: true }))
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: 'Starting calendar import...' }))

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => ({ ...prev, [key]: Math.min((prev[key] || 0) + 10, 90) }))
      }, 500)

      const result = await apiClient.importCalendarData({
        hours_since_last_update: calendarHours
      })

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setProgressMessage(prev => ({ ...prev, [key]: `Imported ${result.imported_count} events!` }))

      toast.success(`✅ Calendar import completed: ${result.imported_count} events imported`)
      await loadImportStatus()

      // Clear progress after delay
      setTimeout(() => {
        setProgress(prev => ({ ...prev, [key]: 0 }))
        setProgressMessage(prev => ({ ...prev, [key]: '' }))
      }, 2000)
    } catch (error) {
      console.error('Calendar import failed:', error)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: '' }))
      toast.error(`❌ Calendar import failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setImporting(prev => ({ ...prev, calendar: false }))
    }
  }

  const handleNotionImport = async () => {
    const key = 'notion'
    try {
      setImporting(prev => ({ ...prev, notion: true }))
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: 'Starting Notion import...' }))

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => ({ ...prev, [key]: Math.min((prev[key] || 0) + 10, 90) }))
      }, 500)

      const result = await apiClient.importNotionData({
        hours_since_last_update: notionHours
      })

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setProgressMessage(prev => ({ ...prev, [key]: `Imported ${result.imported_count} blocks!` }))

      toast.success(`✅ Notion import completed: ${result.imported_count} blocks imported`)
      await loadImportStatus()

      // Clear progress after delay
      setTimeout(() => {
        setProgress(prev => ({ ...prev, [key]: 0 }))
        setProgressMessage(prev => ({ ...prev, [key]: '' }))
      }, 2000)
    } catch (error) {
      console.error('Notion import failed:', error)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: '' }))
      toast.error(`❌ Notion import failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setImporting(prev => ({ ...prev, notion: false }))
    }
  }

  const handleBackfillCalendar = async () => {
    const key = 'backfill'
    try {
      setIsBackfilling(true)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: `Backfilling ${backfillMonths} months...` }))

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => ({ ...prev, [key]: Math.min((prev[key] || 0) + 10, 90) }))
      }, 500)

      const result = await apiClient.backfillCalendar(backfillMonths)

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setProgressMessage(prev => ({ ...prev, [key]: `Backfilled ${result.imported_count} events!` }))

      toast.success(`✅ Calendar backfill completed: ${result.imported_count} events from ${result.date_range.start} to ${result.date_range.end}`)
      await loadImportStatus()

      // Clear progress after delay
      setTimeout(() => {
        setProgress(prev => ({ ...prev, [key]: 0 }))
        setProgressMessage(prev => ({ ...prev, [key]: '' }))
      }, 2000)
    } catch (error) {
      console.error('Calendar backfill failed:', error)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: '' }))
      toast.error(`❌ Calendar backfill failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsBackfilling(false)
    }
  }

  const handleIndexNotion = async () => {
    const key = 'index'
    try {
      setIsIndexing(true)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: 'Indexing Notion blocks...' }))

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => ({ ...prev, [key]: Math.min((prev[key] || 0) + 10, 90) }))
      }, 500)

      const result = await apiClient.indexNotionBlocks(notionIndexScope, notionIndexHours)

      clearInterval(progressInterval)
      setProgress(prev => ({ ...prev, [key]: 100 }))
      setProgressMessage(prev => ({ ...prev, [key]: `Indexed ${result.indexed_count} blocks!` }))

      toast.success(`✅ Notion indexing completed: ${result.indexed_count} blocks indexed`)

      // Clear progress after delay
      setTimeout(() => {
        setProgress(prev => ({ ...prev, [key]: 0 }))
        setProgressMessage(prev => ({ ...prev, [key]: '' }))
      }, 2000)
    } catch (error) {
      console.error('Notion indexing failed:', error)
      setProgress(prev => ({ ...prev, [key]: 0 }))
      setProgressMessage(prev => ({ ...prev, [key]: '' }))
      toast.error(`❌ Notion indexing failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setIsIndexing(false)
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
      case 'no_data':
        return <Badge variant="outline" className="border-amber-500 text-amber-700 dark:text-amber-400">No Data</Badge>
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

      {/* Getting Started Guide */}
      <Card className="border-blue-200 bg-blue-50/50 dark:border-blue-900 dark:bg-blue-950/20">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-blue-900 dark:text-blue-100">
            <CheckCircle className="h-5 w-5" />
            Getting Started - 3 Steps
          </CardTitle>
          <CardDescription className="text-blue-800 dark:text-blue-200">
            Follow these steps in order to set up your data for AI-powered tag generation
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-sm">
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white font-semibold text-xs">
              1
            </div>
            <div>
              <p className="font-medium text-blue-900 dark:text-blue-100">Import Calendar Events</p>
              <p className="text-blue-700 dark:text-blue-300">
                Use <strong>Calendar Backfill</strong> below to import historical events (recommended: 6 months), or use <strong>Calendar Import</strong> for recent updates.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white font-semibold text-xs">
              2
            </div>
            <div>
              <p className="font-medium text-blue-900 dark:text-blue-100">Import Notion Content</p>
              <p className="text-blue-700 dark:text-blue-300">
                Click <strong>Import Notion Data</strong> to sync your pages and blocks. This provides context for AI tagging.
              </p>
            </div>
          </div>
          <div className="flex items-start gap-3">
            <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white font-semibold text-xs">
              3
            </div>
            <div>
              <p className="font-medium text-blue-900 dark:text-blue-100">Index Notion Blocks</p>
              <p className="text-blue-700 dark:text-blue-300">
                Use <strong>Notion Block Indexing</strong> to generate embeddings for semantic search. This enables better tag generation.
              </p>
            </div>
          </div>
          <Separator className="my-2" />
          <p className="text-xs text-blue-600 dark:text-blue-400">
            ✨ After completing these steps, go to <strong>Tag Generation</strong> to create AI-powered tags for your activities!
          </p>
        </CardContent>
      </Card>

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
          {(importing.calendar || progress['calendar'] > 0) && (
            <div className="space-y-2">
              <Progress value={progress['calendar'] || 0} className="h-2" />
              <p className="text-sm text-muted-foreground">{progressMessage['calendar']}</p>
            </div>
          )}
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
          {(importing.notion || progress['notion'] > 0) && (
            <div className="space-y-2">
              <Progress value={progress['notion'] || 0} className="h-2" />
              <p className="text-sm text-muted-foreground">{progressMessage['notion']}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Calendar Backfill */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="h-5 w-5" />
            Calendar Backfill
          </CardTitle>
          <CardDescription>
            Backfill historical calendar events for a specified number of months
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="backfill-months">Number of Months</Label>
              <Input
                id="backfill-months"
                type="number"
                min="1"
                max="24"
                value={backfillMonths}
                onChange={(e) => setBackfillMonths(parseInt(e.target.value) || 7)}
                className="w-full"
              />
              <p className="text-xs text-muted-foreground">
                Backfill the last {backfillMonths} months of calendar events (max 24 months)
              </p>
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleBackfillCalendar}
                disabled={isBackfilling}
                variant="outline"
                className="w-full"
              >
                {isBackfilling ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Backfilling...
                  </>
                ) : (
                  <>
                    <Clock className="h-4 w-4 mr-2" />
                    Backfill {backfillMonths} Months
                  </>
                )}
              </Button>
            </div>
          </div>
          {(isBackfilling || progress['backfill'] > 0) && (
            <div className="space-y-2">
              <Progress value={progress['backfill'] || 0} className="h-2" />
              <p className="text-sm text-muted-foreground">{progressMessage['backfill']}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Notion Indexing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Notion Block Indexing
          </CardTitle>
          <CardDescription>
            Generate abstracts and embeddings for Notion blocks to enable semantic search
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label>Index Scope</Label>
              <div className="flex gap-2">
                <Button
                  variant={notionIndexScope === 'recent' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setNotionIndexScope('recent')}
                  className="flex-1"
                >
                  Recent
                </Button>
                <Button
                  variant={notionIndexScope === 'all' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setNotionIndexScope('all')}
                  className="flex-1"
                >
                  All
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="index-hours">Hours (for Recent)</Label>
              <Input
                id="index-hours"
                type="number"
                min="1"
                max="2160"
                value={notionIndexHours}
                onChange={(e) => setNotionIndexHours(parseInt(e.target.value) || 24)}
                disabled={notionIndexScope === 'all'}
              />
            </div>
            <div className="flex items-end">
              <Button
                onClick={handleIndexNotion}
                disabled={isIndexing}
                variant="outline"
                className="w-full"
              >
                {isIndexing ? (
                  <>
                    <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                    Indexing...
                  </>
                ) : (
                  <>
                    <Database className="h-4 w-4 mr-2" />
                    Index Blocks
                  </>
                )}
              </Button>
            </div>
          </div>
          <p className="text-xs text-muted-foreground">
            {notionIndexScope === 'all'
              ? 'Index all Notion blocks in the database'
              : `Index Notion blocks modified in the last ${notionIndexHours} hours`}
          </p>
          {(isIndexing || progress['index'] > 0) && (
            <div className="space-y-2 mt-4">
              <Progress value={progress['index'] || 0} className="h-2" />
              <p className="text-sm text-muted-foreground">{progressMessage['index']}</p>
            </div>
          )}
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