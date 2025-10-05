"use client"

import { useState, useEffect } from "react"
import { Key, CheckCircle, XCircle, AlertCircle, Loader2, RefreshCw, Settings } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Badge } from "../ui/badge"
import { Separator } from "../ui/separator"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface SystemHealth {
  status: string
  database: {
    connected: boolean
    type: string
  }
  apis: {
    notion: {
      configured: boolean
      connected: boolean
    }
    google_calendar: {
      configured: boolean
      connected: boolean
    }
  }
  timestamp: string
}

interface SystemStats {
  database: {
    raw_activities_count: number
    processed_activities_count: number
    tags_count: number
    notion_pages_count: number
    notion_blocks_count: number
  }
  date_ranges: {
    raw_activities: {
      earliest: string | null
      latest: string | null
    }
    processed_activities: {
      earliest: string | null
      latest: string | null
    }
  }
}

export function ApiConfigurationSettings() {
  const [health, setHealth] = useState<SystemHealth | null>(null)
  const [stats, setStats] = useState<SystemStats | null>(null)
  const [loading, setLoading] = useState(false)

  const loadSystemInfo = async () => {
    try {
      setLoading(true)
      const [healthData, statsData] = await Promise.all([
        apiClient.getSystemHealth().catch(err => {
          console.error('Health check failed:', err)
          return null
        }),
        apiClient.getSystemStats().catch(err => {
          console.error('Stats fetch failed:', err)
          return null
        })
      ])
      if (healthData) setHealth(healthData)
      if (statsData) setStats(statsData)

      if (!healthData && !statsData) {
        toast.error("Failed to load system information. Please check if the backend is running.")
      }
    } catch (error) {
      console.error('Failed to load system info:', error)
      toast.error("Failed to load system information")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadSystemInfo()
  }, [])

  const getConnectionBadge = (configured: boolean, connected: boolean) => {
    if (!configured) {
      return <Badge variant="outline" className="gap-1"><XCircle className="h-3 w-3" /> Not Configured</Badge>
    }
    if (connected) {
      return <Badge variant="default" className="bg-green-500 hover:bg-green-600 gap-1"><CheckCircle className="h-3 w-3" /> Connected</Badge>
    }
    return <Badge variant="destructive" className="gap-1"><AlertCircle className="h-3 w-3" /> Error</Badge>
  }

  const formatDate = (date: string | null) => {
    if (!date) return "N/A"
    return new Date(date).toLocaleDateString()
  }

  if (loading && !health && !stats) {
    return (
      <div className="space-y-6">
        <div>
          <h2 className="text-2xl font-bold mb-2">API Configuration & Status</h2>
          <p className="text-muted-foreground">
            Monitor API connections and configure authentication settings for external services.
          </p>
        </div>
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-6 w-6 animate-spin" />
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">API Configuration & Status</h2>
        <p className="text-muted-foreground">
          Monitor API connections and configure authentication settings for external services.
        </p>
      </div>

      {/* Backend Connection Warning */}
      {!health && !loading && (
        <Card className="border-orange-200 bg-orange-50/50">
          <CardContent className="pt-6">
            <div className="flex items-start gap-3">
              <AlertCircle className="h-5 w-5 text-orange-600 mt-0.5" />
              <div>
                <h3 className="font-medium text-orange-900 mb-1">Backend Not Responding</h3>
                <p className="text-sm text-orange-800">
                  Unable to connect to the backend API. Please ensure the backend server is running on <code className="bg-orange-100 px-1 rounded">http://localhost:8000</code>
                </p>
                <p className="text-sm text-orange-800 mt-2">
                  Start the backend: <code className="bg-orange-100 px-1 rounded">./runner/deploy.sh local</code>
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Health Overview */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              System Health
            </CardTitle>
            <Button variant="outline" size="sm" onClick={loadSystemInfo}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Refresh
            </Button>
          </div>
          <CardDescription>
            Current status of system components and API connections
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Database Status */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium">Database</span>
              {health?.database.connected ? (
                <Badge variant="default" className="bg-green-500 hover:bg-green-600 gap-1">
                  <CheckCircle className="h-3 w-3" /> Connected
                </Badge>
              ) : (
                <Badge variant="destructive" className="gap-1">
                  <XCircle className="h-3 w-3" /> Disconnected
                </Badge>
              )}
            </div>
            <p className="text-sm text-muted-foreground">
              Type: {health?.database.type || "Unknown"}
            </p>
          </div>

          <Separator />

          {/* API Connections */}
          <div className="space-y-4">
            <h3 className="font-medium">External API Connections</h3>

            {/* Notion */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Notion API</span>
                {health?.apis?.notion ? getConnectionBadge(
                  health.apis.notion.configured,
                  health.apis.notion.connected
                ) : (
                  <Badge variant="outline">Loading...</Badge>
                )}
              </div>
              {health?.apis?.notion && !health.apis.notion.configured && (
                <p className="text-sm text-muted-foreground">
                  Configure NOTION_API_KEY in your environment variables
                </p>
              )}
            </div>

            {/* Google Calendar */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="font-medium">Google Calendar</span>
                {health?.apis?.google_calendar ? getConnectionBadge(
                  health.apis.google_calendar.configured,
                  health.apis.google_calendar.connected
                ) : (
                  <Badge variant="outline">Loading...</Badge>
                )}
              </div>
              {health?.apis?.google_calendar && !health.apis.google_calendar.configured && (
                <p className="text-sm text-muted-foreground">
                  Configure credentials.json and token.json in project root
                </p>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Database Statistics */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Key className="h-5 w-5" />
            Database Statistics
          </CardTitle>
          <CardDescription>
            Overview of data stored in the system
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            <div className="text-center p-3 border rounded-lg">
              <div className="text-2xl font-bold">{stats?.database.raw_activities_count || 0}</div>
              <div className="text-xs text-muted-foreground">Raw Activities</div>
            </div>
            <div className="text-center p-3 border rounded-lg">
              <div className="text-2xl font-bold">{stats?.database.processed_activities_count || 0}</div>
              <div className="text-xs text-muted-foreground">Processed Activities</div>
            </div>
            <div className="text-center p-3 border rounded-lg">
              <div className="text-2xl font-bold">{stats?.database.tags_count || 0}</div>
              <div className="text-xs text-muted-foreground">Tags</div>
            </div>
            <div className="text-center p-3 border rounded-lg">
              <div className="text-2xl font-bold">{stats?.database.notion_pages_count || 0}</div>
              <div className="text-xs text-muted-foreground">Notion Pages</div>
            </div>
            <div className="text-center p-3 border rounded-lg">
              <div className="text-2xl font-bold">{stats?.database.notion_blocks_count || 0}</div>
              <div className="text-xs text-muted-foreground">Notion Blocks</div>
            </div>
          </div>

          <Separator className="my-4" />

          {/* Date Ranges */}
          <div className="space-y-3">
            <h3 className="font-medium text-sm">Data Date Ranges</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
              <div className="p-2 bg-muted rounded">
                <div className="font-medium mb-1">Raw Activities</div>
                <div className="text-xs text-muted-foreground">
                  {formatDate(stats?.date_ranges.raw_activities.earliest)} → {formatDate(stats?.date_ranges.raw_activities.latest)}
                </div>
              </div>
              <div className="p-2 bg-muted rounded">
                <div className="font-medium mb-1">Processed Activities</div>
                <div className="text-xs text-muted-foreground">
                  {formatDate(stats?.date_ranges.processed_activities.earliest)} → {formatDate(stats?.date_ranges.processed_activities.latest)}
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Configuration Instructions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Configuration Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4 text-sm">
            <div>
              <h4 className="font-medium mb-2">Google Calendar Setup</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Create OAuth 2.0 credentials in Google Cloud Console</li>
                <li>Download credentials.json to project root</li>
                <li>Run authentication flow to generate token.json</li>
                <li>Restart the backend server</li>
              </ol>
            </div>

            <Separator />

            <div>
              <h4 className="font-medium mb-2">Notion API Setup</h4>
              <ol className="list-decimal list-inside space-y-1 text-muted-foreground">
                <li>Create an integration at developers.notion.com</li>
                <li>Copy the Internal Integration Token</li>
                <li>Add NOTION_API_KEY to .env file</li>
                <li>Grant integration access to your workspace</li>
                <li>Restart the backend server</li>
              </ol>
            </div>

            <Separator />

            <div className="bg-blue-50 border border-blue-200 rounded p-3">
              <p className="text-blue-900 text-xs">
                📖 For detailed setup instructions, see SETUP.md in the project root directory.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
