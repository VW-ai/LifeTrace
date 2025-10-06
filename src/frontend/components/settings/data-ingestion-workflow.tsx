"use client"

import { useState, useEffect } from "react"
import { Calendar, Database, Clock, CheckCircle, AlertCircle, Loader2, ArrowRight, Info } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Badge } from "../ui/badge"
import { Progress } from "../ui/progress"
import { Alert, AlertDescription } from "../ui/alert"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface WorkflowStep {
  id: string
  title: string
  description: string
  completed: boolean
  inProgress: boolean
}

export function DataIngestionWorkflow() {
  const [currentStep, setCurrentStep] = useState(1)
  const [importing, setImporting] = useState(false)
  const [progress, setProgress] = useState(0)
  const [progressMessage, setProgressMessage] = useState("")

  // Step 1: Calendar Backfill (for first-time users)
  const [backfillMonths, setBackfillMonths] = useState(3)
  const [backfillComplete, setBackfillComplete] = useState(false)

  // Step 2: Notion Import
  const [notionHours, setNotionHours] = useState(2160) // 90 days
  const [notionComplete, setNotionComplete] = useState(false)

  // Step 3: Notion Indexing
  const [indexComplete, setIndexComplete] = useState(false)

  const steps: WorkflowStep[] = [
    {
      id: "step1",
      title: "Import Calendar Events",
      description: "Import your Google Calendar events (recommended: last 3-6 months)",
      completed: backfillComplete,
      inProgress: currentStep === 1 && importing
    },
    {
      id: "step2",
      title: "Import Notion Content",
      description: "Import your Notion pages and blocks for context",
      completed: notionComplete,
      inProgress: currentStep === 2 && importing
    },
    {
      id: "step3",
      title: "Index Notion Blocks",
      description: "Generate searchable abstracts for AI tagging",
      completed: indexComplete,
      inProgress: currentStep === 3 && importing
    }
  ]

  const handleCalendarBackfill = async () => {
    try {
      setImporting(true)
      setProgress(0)
      setProgressMessage("Starting calendar backfill...")

      // Simulate progress updates
      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90))
      }, 500)

      const result = await apiClient.backfillCalendar(backfillMonths)

      clearInterval(progressInterval)
      setProgress(100)
      setProgressMessage(`Imported ${result.imported_count} events!`)

      toast.success(`✅ Calendar backfill completed: ${result.imported_count} events from ${result.date_range.start} to ${result.date_range.end}`)

      setBackfillComplete(true)

      // Auto-advance to next step after 1.5 seconds
      setTimeout(() => {
        setCurrentStep(2)
        setProgress(0)
        setProgressMessage("")
      }, 1500)

    } catch (error: any) {
      console.error('Calendar backfill failed:', error)
      toast.error(error?.message || "Calendar backfill failed. Please check your Google Calendar connection.")
      setProgress(0)
      setProgressMessage("")
    } finally {
      setImporting(false)
    }
  }

  const handleNotionImport = async () => {
    try {
      setImporting(true)
      setProgress(0)
      setProgressMessage("Starting Notion import...")

      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 10, 90))
      }, 500)

      const result = await apiClient.importNotionData({
        hours_since_last_update: notionHours
      })

      clearInterval(progressInterval)
      setProgress(100)
      setProgressMessage(`Imported ${result.imported_count} blocks!`)

      toast.success(`✅ Notion import completed: ${result.imported_count} blocks imported`)

      setNotionComplete(true)

      setTimeout(() => {
        setCurrentStep(3)
        setProgress(0)
        setProgressMessage("")
      }, 1500)

    } catch (error: any) {
      console.error('Notion import failed:', error)
      toast.error(error?.message || "Notion import failed. Please check your Notion connection.")
      setProgress(0)
      setProgressMessage("")
    } finally {
      setImporting(false)
    }
  }

  const handleNotionIndexing = async () => {
    try {
      setImporting(true)
      setProgress(0)
      setProgressMessage("Indexing Notion blocks...")

      const progressInterval = setInterval(() => {
        setProgress(prev => Math.min(prev + 8, 90))
      }, 800)

      const result = await apiClient.indexNotionBlocks('all', 24)

      clearInterval(progressInterval)
      setProgress(100)
      setProgressMessage(`Indexed ${result.indexed_count} blocks!`)

      toast.success(`✅ Notion indexing completed: ${result.indexed_count} blocks indexed`)

      setIndexComplete(true)

      setTimeout(() => {
        setProgress(0)
        setProgressMessage("")
      }, 1500)

    } catch (error: any) {
      console.error('Notion indexing failed:', error)
      toast.error(error?.message || "Notion indexing failed")
      setProgress(0)
      setProgressMessage("")
    } finally {
      setImporting(false)
    }
  }

  const allStepsComplete = backfillComplete && notionComplete && indexComplete

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Data Import Workflow</h2>
        <p className="text-muted-foreground">
          Follow these 3 steps to import your data and start tracking your activities with AI.
        </p>
      </div>

      {/* Progress Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Import Progress</CardTitle>
          <CardDescription>
            Complete all steps to enable AI tag generation
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center gap-3">
                <div className={`flex items-center justify-center w-8 h-8 rounded-full border-2 ${
                  step.completed
                    ? 'bg-green-500 border-green-500'
                    : step.inProgress
                    ? 'bg-blue-500 border-blue-500 animate-pulse'
                    : 'bg-background border-muted-foreground'
                }`}>
                  {step.completed ? (
                    <CheckCircle className="h-5 w-5 text-white" />
                  ) : step.inProgress ? (
                    <Loader2 className="h-4 w-4 text-white animate-spin" />
                  ) : (
                    <span className="text-sm font-medium text-muted-foreground">{index + 1}</span>
                  )}
                </div>
                <div className="flex-1">
                  <div className="font-medium">{step.title}</div>
                  <div className="text-sm text-muted-foreground">{step.description}</div>
                </div>
                {step.completed && (
                  <Badge variant="default" className="bg-green-500">
                    <CheckCircle className="h-3 w-3 mr-1" />
                    Done
                  </Badge>
                )}
                {step.inProgress && (
                  <Badge variant="secondary">
                    <Loader2 className="h-3 w-3 mr-1 animate-spin" />
                    In Progress
                  </Badge>
                )}
              </div>
            ))}
          </div>

          {allStepsComplete && (
            <Alert className="mt-4 bg-green-50 border-green-200">
              <CheckCircle className="h-4 w-4 text-green-600" />
              <AlertDescription className="text-green-800">
                <strong>All data imported!</strong> You can now go to Tag Generation to process your activities.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Step 1: Calendar Backfill */}
      {currentStep === 1 && (
        <Card className="border-blue-200 shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white font-bold">
                1
              </div>
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Calendar className="h-5 w-5" />
                  Import Calendar Events
                </CardTitle>
                <CardDescription>
                  Import your Google Calendar events to track your time
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>First-time setup:</strong> Import 3-6 months of calendar history to build a comprehensive activity database.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="backfill-months">How many months to import?</Label>
              <Input
                id="backfill-months"
                type="number"
                min="1"
                max="12"
                value={backfillMonths}
                onChange={(e) => setBackfillMonths(parseInt(e.target.value) || 3)}
                className="w-full"
                disabled={importing}
              />
              <p className="text-xs text-muted-foreground">
                Recommended: 3-6 months (more months = more data but takes longer)
              </p>
            </div>

            {importing && progress > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{progressMessage}</span>
                  <span className="font-medium">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            )}

            <Button
              onClick={handleCalendarBackfill}
              disabled={importing || backfillComplete}
              className="w-full"
              size="lg"
            >
              {importing ? (
                <>
                  <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                  Importing {backfillMonths} months...
                </>
              ) : backfillComplete ? (
                <>
                  <CheckCircle className="h-5 w-5 mr-2" />
                  Completed
                </>
              ) : (
                <>
                  <Calendar className="h-5 w-5 mr-2" />
                  Import {backfillMonths} Months of Calendar Events
                </>
              )}
            </Button>

            {backfillComplete && (
              <Button
                onClick={() => setCurrentStep(2)}
                variant="outline"
                className="w-full"
              >
                Continue to Next Step
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 2: Notion Import */}
      {currentStep === 2 && (
        <Card className="border-blue-200 shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white font-bold">
                2
              </div>
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Database className="h-5 w-5" />
                  Import Notion Content
                </CardTitle>
                <CardDescription>
                  Import your Notion pages to provide context for AI tagging
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>Why Notion?</strong> Your notes provide context to help AI understand what you were working on and generate better tags.
              </AlertDescription>
            </Alert>

            <div className="space-y-2">
              <Label htmlFor="notion-hours">Import Notion content from last...</Label>
              <div className="flex gap-2">
                <Button
                  variant={notionHours === 720 ? "default" : "outline"}
                  size="sm"
                  onClick={() => setNotionHours(720)}
                  disabled={importing}
                  className="flex-1"
                >
                  30 days
                </Button>
                <Button
                  variant={notionHours === 2160 ? "default" : "outline"}
                  size="sm"
                  onClick={() => setNotionHours(2160)}
                  disabled={importing}
                  className="flex-1"
                >
                  90 days
                </Button>
                <Button
                  variant={notionHours === 4320 ? "default" : "outline"}
                  size="sm"
                  onClick={() => setNotionHours(4320)}
                  disabled={importing}
                  className="flex-1"
                >
                  180 days
                </Button>
              </div>
              <p className="text-xs text-muted-foreground">
                Recommended: 90 days for good context coverage
              </p>
            </div>

            {importing && progress > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{progressMessage}</span>
                  <span className="font-medium">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={() => setCurrentStep(1)}
                variant="outline"
                disabled={importing}
              >
                Back
              </Button>
              <Button
                onClick={handleNotionImport}
                disabled={importing || notionComplete}
                className="flex-1"
                size="lg"
              >
                {importing ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Importing Notion...
                  </>
                ) : notionComplete ? (
                  <>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Completed
                  </>
                ) : (
                  <>
                    <Database className="h-5 w-5 mr-2" />
                    Import Notion Content
                  </>
                )}
              </Button>
            </div>

            {notionComplete && (
              <Button
                onClick={() => setCurrentStep(3)}
                variant="outline"
                className="w-full"
              >
                Continue to Final Step
                <ArrowRight className="h-4 w-4 ml-2" />
              </Button>
            )}
          </CardContent>
        </Card>
      )}

      {/* Step 3: Notion Indexing */}
      {currentStep === 3 && (
        <Card className="border-blue-200 shadow-md">
          <CardHeader>
            <div className="flex items-center gap-2">
              <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-500 text-white font-bold">
                3
              </div>
              <div>
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  Index Notion Blocks
                </CardTitle>
                <CardDescription>
                  Generate searchable abstracts for AI-powered tagging
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <Alert>
              <Info className="h-4 w-4" />
              <AlertDescription>
                <strong>What is indexing?</strong> This creates AI-generated summaries of your Notion blocks, enabling smart context search during tag generation.
              </AlertDescription>
            </Alert>

            {importing && progress > 0 && (
              <div className="space-y-2">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-muted-foreground">{progressMessage}</span>
                  <span className="font-medium">{progress}%</span>
                </div>
                <Progress value={progress} className="h-2" />
              </div>
            )}

            <div className="flex gap-2">
              <Button
                onClick={() => setCurrentStep(2)}
                variant="outline"
                disabled={importing}
              >
                Back
              </Button>
              <Button
                onClick={handleNotionIndexing}
                disabled={importing || indexComplete}
                className="flex-1"
                size="lg"
              >
                {importing ? (
                  <>
                    <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                    Indexing Blocks...
                  </>
                ) : indexComplete ? (
                  <>
                    <CheckCircle className="h-5 w-5 mr-2" />
                    Completed
                  </>
                ) : (
                  <>
                    <Clock className="h-5 w-5 mr-2" />
                    Index All Notion Blocks
                  </>
                )}
              </Button>
            </div>

            {indexComplete && (
              <Alert className="bg-green-50 border-green-200">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <AlertDescription className="text-green-800">
                  <strong>Setup complete!</strong> Go to Settings → Tag Generation to start processing your activities.
                </AlertDescription>
              </Alert>
            )}
          </CardContent>
        </Card>
      )}

      {/* Quick Actions for returning users */}
      {!importing && (currentStep > 1 || backfillComplete) && (
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Jump to any step or start over</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep(1)}
              >
                Step 1: Calendar
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep(2)}
                disabled={!backfillComplete}
              >
                Step 2: Notion
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setCurrentStep(3)}
                disabled={!notionComplete}
              >
                Step 3: Indexing
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}
