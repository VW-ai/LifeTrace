"use client"

import { useState } from "react"
import { ArrowLeft, ArrowDown } from "lucide-react"
import { Button } from "../../components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "../../components/ui/card"
import { DataIngestionSettings } from "../../components/settings/data-ingestion-settings"
import { TagGenerationSettings } from "../../components/settings/tag-generation-settings"
import { TagCleanupSettings } from "../../components/settings/tag-cleanup-settings"
import { ProcessingLogs } from "../../components/settings/processing-logs"

export default function SettingsPage() {
  const [activeSection, setActiveSection] = useState<string>("ingestion")

  const sections = [
    { id: "ingestion", label: "Data Ingestion", description: "Import Data" },
    { id: "generation", label: "Tag Generation", description: "Process activities and generate tags" },
    { id: "cleanup", label: "Tag Cleanup", description: "Clean up and merge tags" },
    { id: "logs", label: "Processing Logs", description: "View system processing logs" },
  ]

  const renderActiveSection = () => {
    switch (activeSection) {
      case "ingestion":
        return <DataIngestionSettings />
      case "generation":
        return <TagGenerationSettings />
      case "cleanup":
        return <TagCleanupSettings />
      case "logs":
        return <ProcessingLogs />
      default:
        return <DataIngestionSettings />
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card/50 backdrop-blur supports-[backdrop-filter]:bg-card/50">
        <div className="container mx-auto px-4">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-4">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => window.history.back()}
                className="gap-2"
              >
                <ArrowLeft className="h-4 w-4" />
                Back to Dashboard
              </Button>
              <div>
                <h1 className="text-xl font-bold">Tagging Workflow Settings</h1>
                <p className="text-sm text-muted-foreground">
                  Manage data ingestion, tag generation, and cleanup processes
                </p>
              </div>
            </div>
          </div>
        </div>
      </header>

      <div className="container mx-auto px-4 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Navigation */}
          <div className="lg:col-span-1">
            <div className="space-y-2">
              {sections.map((section) => (
                <Button
                  key={section.id}
                  variant={activeSection === section.id ? "default" : "ghost"}
                  className="w-full justify-start"
                  onClick={() => setActiveSection(section.id)}
                >
                  <div className="text-left">
                    <div className="font-medium">{section.label}</div>
                    <div className="text-xs text-muted-foreground">
                      {section.description}
                    </div>
                  </div>
                </Button>
              ))}
            </div>

            {/* Workflow Overview */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle className="text-sm">Workflow Overview</CardTitle>
              </CardHeader>
              <CardContent className="text-xs space-y-3">
                <div className="group relative">
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer transition-colors">
                    <div className="w-3 h-3 bg-blue-500 rounded-full" />
                    <span className="font-medium">Ingest raw data</span>
                  </div>
                  <div className="absolute left-0 top-full mt-1 p-2 bg-popover border rounded-md shadow-md text-xs w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                    <div className="font-medium text-foreground mb-1">Data Ingestion</div>
                    <div className="text-muted-foreground">Import events from Google Calendar and blocks from Notion. Handles deduplication automatically.</div>
                  </div>
                </div>

                <div className="flex justify-center py-1">
                  <ArrowDown className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="group relative">
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer transition-colors">
                    <div className="w-3 h-3 bg-green-500 rounded-full" />
                    <span className="font-medium">Generate tags</span>
                  </div>
                  <div className="absolute left-0 top-full mt-1 p-2 bg-popover border rounded-md shadow-md text-xs w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                    <div className="font-medium text-foreground mb-1">Tag Generation</div>
                    <div className="text-muted-foreground">AI-powered analysis of activities to create meaningful, contextual tags for better organization.</div>
                  </div>
                </div>

                <div className="flex justify-center py-1">
                  <ArrowDown className="h-4 w-4 text-muted-foreground" />
                </div>

                <div className="group relative">
                  <div className="flex items-center gap-2 p-2 rounded hover:bg-muted/50 cursor-pointer transition-colors">
                    <div className="w-3 h-3 bg-orange-500 rounded-full" />
                    <span className="font-medium">Clean up tags</span>
                  </div>
                  <div className="absolute left-0 top-full mt-1 p-2 bg-popover border rounded-md shadow-md text-xs w-48 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200 z-10">
                    <div className="font-medium text-foreground mb-1">Tag Cleanup</div>
                    <div className="text-muted-foreground">Merge duplicate tags, remove unused ones, and maintain a clean, organized tag taxonomy.</div>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            {renderActiveSection()}
          </div>
        </div>
      </div>
    </div>
  )
}