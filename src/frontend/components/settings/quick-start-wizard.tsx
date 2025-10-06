"use client"

import { useState, useEffect } from "react"
import {
  CheckCircle2,
  Circle,
  Loader2,
  ArrowRight,
  ArrowLeft,
  Zap,
  Database,
  Key,
  Sparkles,
  AlertCircle,
  Calendar,
  FileText,
  Tag
} from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Progress } from "../ui/progress"
import { Badge } from "../ui/badge"
import { Separator } from "../ui/separator"
import { Alert, AlertDescription } from "../ui/alert"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"
import { ApiConfigDialog } from "./api-config-dialog"

type WizardStep = 1 | 2 | 3
type ApiType = 'notion' | 'openai' | 'google_calendar'

interface StepStatus {
  completed: boolean
  skipped: boolean
  canSkip: boolean
}

interface ServiceStatus {
  notion: { configured: boolean; connected: boolean }
  google_calendar: { configured: boolean; connected: boolean }
  openai?: { configured: boolean; connected: boolean }
}

interface ImportStatus {
  calendar: { total_imported: number; status: string }
  notion: { total_imported: number; status: string }
}

interface SystemStats {
  database: {
    processed_activities_count: number
    tags_count: number
  }
}

export function QuickStartWizard() {
  const [currentStep, setCurrentStep] = useState<WizardStep>(1)
  const [stepStatus, setStepStatus] = useState<Record<WizardStep, StepStatus>>({
    1: { completed: false, skipped: false, canSkip: false },
    2: { completed: false, skipped: false, canSkip: true },
    3: { completed: false, skipped: false, canSkip: false }
  })

  // Service connection states
  const [serviceStatus, setServiceStatus] = useState<ServiceStatus | null>(null)
  const [loadingServices, setLoadingServices] = useState(true)

  // Import states
  const [importStatus, setImportStatus] = useState<ImportStatus | null>(null)
  const [importing, setImporting] = useState(false)
  const [importProgress, setImportProgress] = useState(0)
  const [importMessage, setImportMessage] = useState("")

  // Tag generation states
  const [systemStats, setSystemStats] = useState<SystemStats | null>(null)
  const [generating, setGenerating] = useState(false)
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generationMessage, setGenerationMessage] = useState("")
  const [currentActivity, setCurrentActivity] = useState("")
  const [currentTags, setCurrentTags] = useState<string[]>([])
  const [activityCounter, setActivityCounter] = useState({ current: 0, total: 0 })

  // API config dialog
  const [configDialogOpen, setConfigDialogOpen] = useState(false)
  const [selectedApiType, setSelectedApiType] = useState<ApiType>('openai')

  // Load initial status
  useEffect(() => {
    loadAllStatus()
  }, [])

  // Auto-detect step completion
  useEffect(() => {
    detectStepCompletion()
  }, [serviceStatus, importStatus, systemStats])

  const loadAllStatus = async () => {
    await Promise.all([
      loadServiceStatus(),
      loadImportStatus(),
      loadSystemStats()
    ])
  }

  const loadServiceStatus = async () => {
    try {
      setLoadingServices(true)
      const health = await apiClient.getSystemHealth()

      setServiceStatus(health.apis)
    } catch (error) {
      console.error('Failed to load service status:', error)
    } finally {
      setLoadingServices(false)
    }
  }

  const loadImportStatus = async () => {
    try {
      const status = await apiClient.getImportStatus()
      setImportStatus(status)
    } catch (error) {
      console.error('Failed to load import status:', error)
    }
  }

  const loadSystemStats = async () => {
    try {
      const stats = await apiClient.getSystemStats()
      setSystemStats(stats)
    } catch (error) {
      console.error('Failed to load system stats:', error)
    }
  }

  const detectStepCompletion = () => {
    // Step 1: Services connected
    const step1Complete = Boolean(
      serviceStatus?.openai?.connected &&
      (serviceStatus?.google_calendar?.connected || serviceStatus?.notion?.connected)
    )

    // Step 2: Data imported
    const step2Complete = Boolean(
      (importStatus?.calendar?.total_imported || 0) > 0 ||
      (importStatus?.notion?.total_imported || 0) > 0
    )

    // Step 3: Tags generated
    const step3Complete = Boolean(
      (systemStats?.database?.processed_activities_count || 0) > 0 &&
      (systemStats?.database?.tags_count || 0) > 0
    )

    setStepStatus({
      1: { ...stepStatus[1], completed: step1Complete },
      2: { ...stepStatus[2], completed: step2Complete },
      3: { ...stepStatus[3], completed: step3Complete }
    })

    // Auto-advance to first incomplete step
    if (currentStep === 1 && step1Complete && !step2Complete) {
      // Don't auto-advance, let user click Next
    }
  }

  const handleConfigureApi = (apiType: ApiType) => {
    setSelectedApiType(apiType)
    setConfigDialogOpen(true)
  }

  const handleImportAll = async () => {
    // Check if any service is connected
    if (!serviceStatus?.google_calendar?.connected && !serviceStatus?.notion?.connected) {
      toast.error("❌ Please connect at least one data source (Google Calendar or Notion) in Step 1")
      return
    }

    setImporting(true)
    setImportProgress(0)
    setImportMessage("Starting data import...")

    let importedSomething = false

    try {
      // Step 1: Import calendar (if configured)
      if (serviceStatus?.google_calendar?.connected) {
        setImportMessage("Importing calendar events...")
        setImportProgress(10)

        const progressInterval = setInterval(() => {
          setImportProgress(prev => Math.min(prev + 5, 45))
        }, 500)

        try {
          const calendarResult = await apiClient.backfillCalendar(6)
          clearInterval(progressInterval)
          setImportProgress(50)

          if (calendarResult.imported_count > 0) {
            toast.success(`✅ Imported ${calendarResult.imported_count} calendar events`)
            importedSomething = true
          } else {
            toast.info(`ℹ️ No new calendar events found`)
          }
        } catch (err) {
          clearInterval(progressInterval)
          console.error('Calendar import failed:', err)
          toast.error(`❌ Calendar import failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
        }
      }

      // Step 2: Import Notion (if configured)
      if (serviceStatus?.notion?.connected) {
        setImportMessage("Importing Notion content...")
        setImportProgress(55)

        const progressInterval = setInterval(() => {
          setImportProgress(prev => Math.min(prev + 5, 90))
        }, 500)

        try {
          const notionResult = await apiClient.importNotionData({ hours_since_last_update: 720 })
          clearInterval(progressInterval)
          setImportProgress(95)

          if (notionResult.imported_count > 0) {
            toast.success(`✅ Imported ${notionResult.imported_count} Notion blocks`)
            importedSomething = true

            // Step 3: Index Notion blocks
            setImportMessage("Indexing Notion blocks for AI...")
            try {
              const indexResult = await apiClient.indexNotionBlocks('all')
              if (indexResult.indexed_count > 0) {
                toast.success(`✅ Indexed ${indexResult.indexed_count} blocks`)
              }
            } catch (indexErr) {
              console.error('Indexing failed:', indexErr)
              toast.warning(`⚠️ Indexing failed but import succeeded`)
            }
          } else {
            toast.info(`ℹ️ No new Notion content found`)
          }
        } catch (err) {
          clearInterval(progressInterval)
          console.error('Notion import failed:', err)
          toast.error(`❌ Notion import failed: ${err instanceof Error ? err.message : 'Unknown error'}`)
        }
      }

      setImportProgress(100)
      setImportMessage("Import complete!")

      await loadImportStatus()

      if (importedSomething) {
        toast.success("🎉 All data imported successfully!")

        // Auto-advance after delay
        setTimeout(() => {
          setStepStatus(prev => ({ ...prev, 2: { ...prev[2], completed: true } }))
          setCurrentStep(3)
          setImportProgress(0)
          setImportMessage("")
        }, 1500)
      } else {
        toast.warning("⚠️ No new data was imported. You may have already imported everything.")
        setImportProgress(0)
        setImportMessage("")
      }

    } catch (error) {
      console.error('Import failed:', error)
      setImportProgress(0)
      setImportMessage("")
      toast.error(`❌ Import failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
    } finally {
      setImporting(false)
    }
  }

  const handleGenerateTags = async () => {
    setGenerating(true)
    setGenerationProgress(0)
    setGenerationMessage("Starting AI tag generation...")
    setCurrentActivity("")
    setCurrentTags([])
    setActivityCounter({ current: 0, total: 0 })

    try {
      // Trigger processing and get job_id
      const result = await apiClient.triggerDailyProcessing({
        use_database: true,
        regenerate_system_tags: true
      })

      const jobId = result.job_id

      // Poll for progress every 500ms
      const pollInterval = setInterval(async () => {
        try {
          const progress = await apiClient.getProcessingProgress(jobId)

          // Update progress state
          setGenerationProgress(progress.progress)
          setCurrentActivity(progress.current_activity)
          setCurrentTags(progress.current_tags || [])
          setActivityCounter({
            current: progress.activity_index,
            total: progress.total_activities
          })

          if (progress.total_activities > 0) {
            setGenerationMessage(
              `Processing activity ${progress.activity_index} of ${progress.total_activities}...`
            )
          }

          // Check if completed
          if (progress.status === "completed") {
            clearInterval(pollInterval)
            setGenerationProgress(100)
            setGenerationMessage(`Generated tags for ${progress.report?.processed_counts?.processed_activities || 0} activities!`)

            toast.success(
              `🎉 AI Analysis Complete! Generated ${progress.report?.tag_analysis?.total_unique_tags || 0} unique tags`
            )

            await loadSystemStats()

            setTimeout(() => {
              setStepStatus(prev => ({ ...prev, 3: { ...prev[3], completed: true } }))
              setGenerationProgress(0)
              setGenerationMessage("")
              setCurrentActivity("")
              setCurrentTags([])
              setActivityCounter({ current: 0, total: 0 })
            }, 2000)
          }

          // Check if failed
          if (progress.status === "failed") {
            clearInterval(pollInterval)
            toast.error(`Failed to generate tags: ${progress.error || 'Unknown error'}`)
            setGenerationMessage("Failed to generate tags")
            setGenerating(false)
          }
        } catch (error) {
          console.error('Progress polling failed:', error)
          // Continue polling even if one request fails
        }
      }, 500)

      // Safety timeout to stop polling after 10 minutes
      setTimeout(() => {
        clearInterval(pollInterval)
        if (generating) {
          toast.error('Tag generation timeout. Please check processing logs.')
          setGenerating(false)
        }
      }, 10 * 60 * 1000)

    } catch (error) {
      console.error('Tag generation failed:', error)
      setGenerationProgress(0)
      setGenerationMessage("")
      toast.error(`❌ Tag generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
      setGenerating(false)
    }
  }

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep((currentStep + 1) as WizardStep)
    }
  }

  const handleBack = () => {
    if (currentStep > 1) {
      setCurrentStep((currentStep - 1) as WizardStep)
    }
  }

  const handleSkip = () => {
    if (stepStatus[currentStep].canSkip) {
      setStepStatus(prev => ({
        ...prev,
        [currentStep]: { ...prev[currentStep], skipped: true }
      }))
      handleNext()
    }
  }

  const getOverallProgress = () => {
    const completed = Object.values(stepStatus).filter(s => s.completed || s.skipped).length
    return (completed / 3) * 100
  }

  const canProceedToNext = () => {
    return stepStatus[currentStep].completed || stepStatus[currentStep].canSkip
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold mb-2">Quick Start Wizard</h1>
        <p className="text-muted-foreground">
          Get started with LifeTrace in 3 simple steps (about 5 minutes)
        </p>
      </div>

      {/* Overall Progress */}
      <Card className="border-2 border-primary/20">
        <CardContent className="pt-6">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Overall Progress</span>
              <span className="text-sm text-muted-foreground">{Math.round(getOverallProgress())}%</span>
            </div>
            <Progress value={getOverallProgress()} className="h-3" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Step {currentStep} of 3</span>
              <span>{Object.values(stepStatus).filter(s => s.completed).length} completed</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Step Indicators */}
      <div className="grid grid-cols-3 gap-4">
        {[1, 2, 3].map((step) => {
          const stepNum = step as WizardStep
          const status = stepStatus[stepNum]
          const isCurrent = currentStep === stepNum
          const icons = [Key, Database, Sparkles]
          const Icon = icons[step - 1]
          const titles = ["Connect Services", "Import Data", "Generate Tags"]

          return (
            <Card
              key={step}
              className={`cursor-pointer transition-all ${
                isCurrent ? 'ring-2 ring-primary shadow-lg' : ''
              } ${status.completed ? 'border-green-500 bg-green-50/50 dark:bg-green-950/20' : ''}`}
              onClick={() => setCurrentStep(stepNum)}
            >
              <CardContent className="pt-6">
                <div className="flex flex-col items-center text-center space-y-2">
                  {status.completed ? (
                    <CheckCircle2 className="h-8 w-8 text-green-600" />
                  ) : isCurrent ? (
                    <div className="relative">
                      <Icon className="h-8 w-8 text-primary" />
                      <div className="absolute -top-1 -right-1">
                        <Circle className="h-3 w-3 fill-primary text-primary animate-pulse" />
                      </div>
                    </div>
                  ) : (
                    <Icon className="h-8 w-8 text-muted-foreground" />
                  )}
                  <div className="space-y-1">
                    <p className={`text-sm font-medium ${isCurrent ? 'text-primary' : ''}`}>
                      Step {step}
                    </p>
                    <p className="text-xs text-muted-foreground">{titles[step - 1]}</p>
                  </div>
                  {status.completed && (
                    <Badge variant="default" className="bg-green-500 hover:bg-green-600">
                      Complete
                    </Badge>
                  )}
                  {status.skipped && (
                    <Badge variant="outline">Skipped</Badge>
                  )}
                </div>
              </CardContent>
            </Card>
          )
        })}
      </div>

      {/* Step Content */}
      <Card className="min-h-[400px]">
        {/* Step 1: Connect Services */}
        {currentStep === 1 && (
          <>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                Step 1: Connect Your Services
              </CardTitle>
              <CardDescription>
                Configure API connections to enable data import and AI features (2 minutes)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  You need at least <strong>OpenAI</strong> + (<strong>Google Calendar</strong> or <strong>Notion</strong>) to continue
                </AlertDescription>
              </Alert>

              {loadingServices ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin" />
                </div>
              ) : (
                <div className="space-y-4">
                  {/* OpenAI */}
                  <Card className="border-2">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 dark:bg-purple-900">
                            <Sparkles className="h-5 w-5 text-purple-600 dark:text-purple-400" />
                          </div>
                          <div>
                            <CardTitle className="text-base">OpenAI API</CardTitle>
                            <CardDescription className="text-xs">Required for AI tag generation</CardDescription>
                          </div>
                        </div>
                        {serviceStatus?.openai?.connected ? (
                          <Badge variant="default" className="bg-green-500">Connected</Badge>
                        ) : serviceStatus?.openai?.configured ? (
                          <Badge variant="destructive">Error</Badge>
                        ) : (
                          <Badge variant="outline">Not Configured</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Button
                        onClick={() => handleConfigureApi('openai')}
                        variant={serviceStatus?.openai?.connected ? "outline" : "default"}
                        className="w-full"
                      >
                        {serviceStatus?.openai?.connected ? "Reconfigure" : "Configure Now"}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Google Calendar */}
                  <Card className="border-2">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900">
                            <Calendar className="h-5 w-5 text-blue-600 dark:text-blue-400" />
                          </div>
                          <div>
                            <CardTitle className="text-base">Google Calendar</CardTitle>
                            <CardDescription className="text-xs">Import your calendar events</CardDescription>
                          </div>
                        </div>
                        {serviceStatus?.google_calendar?.connected ? (
                          <Badge variant="default" className="bg-green-500">Connected</Badge>
                        ) : serviceStatus?.google_calendar?.configured ? (
                          <Badge variant="destructive">Error</Badge>
                        ) : (
                          <Badge variant="outline">Optional</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Button
                        onClick={() => handleConfigureApi('google_calendar')}
                        variant={serviceStatus?.google_calendar?.connected ? "outline" : "secondary"}
                        className="w-full"
                      >
                        {serviceStatus?.google_calendar?.connected ? "Reconfigure" : "Configure (Optional)"}
                      </Button>
                    </CardContent>
                  </Card>

                  {/* Notion */}
                  <Card className="border-2">
                    <CardHeader>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 dark:bg-gray-800">
                            <FileText className="h-5 w-5 text-gray-600 dark:text-gray-400" />
                          </div>
                          <div>
                            <CardTitle className="text-base">Notion</CardTitle>
                            <CardDescription className="text-xs">Import your Notion pages for context</CardDescription>
                          </div>
                        </div>
                        {serviceStatus?.notion?.connected ? (
                          <Badge variant="default" className="bg-green-500">Connected</Badge>
                        ) : serviceStatus?.notion?.configured ? (
                          <Badge variant="destructive">Error</Badge>
                        ) : (
                          <Badge variant="outline">Optional</Badge>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <Button
                        onClick={() => handleConfigureApi('notion')}
                        variant={serviceStatus?.notion?.connected ? "outline" : "secondary"}
                        className="w-full"
                      >
                        {serviceStatus?.notion?.connected ? "Reconfigure" : "Configure (Optional)"}
                      </Button>
                    </CardContent>
                  </Card>
                </div>
              )}

              {stepStatus[1].completed && (
                <Alert className="border-green-500 bg-green-50 dark:bg-green-950/20">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    Great! Your services are connected. Click <strong>Next</strong> to import your data.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </>
        )}

        {/* Step 2: Import Data */}
        {currentStep === 2 && (
          <>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Step 2: Import Your Data
              </CardTitle>
              <CardDescription>
                One-click import from all connected services (2 minutes)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <AlertCircle className="h-4 w-4" />
                <AlertDescription>
                  This will import the last <strong>6 months</strong> of calendar events and <strong>30 days</strong> of Notion content
                </AlertDescription>
              </Alert>

              {/* Import Stats */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription className="text-xs">Calendar Events</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {importStatus?.calendar?.total_imported || 0}
                    </div>
                    <p className="text-xs text-muted-foreground">events imported</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription className="text-xs">Notion Blocks</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {importStatus?.notion?.total_imported || 0}
                    </div>
                    <p className="text-xs text-muted-foreground">blocks imported</p>
                  </CardContent>
                </Card>
              </div>

              {/* Import Button */}
              <div className="space-y-4">
                <Button
                  onClick={handleImportAll}
                  disabled={importing || (!serviceStatus?.google_calendar?.connected && !serviceStatus?.notion?.connected)}
                  size="lg"
                  className="w-full h-14"
                >
                  {importing ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Importing Data...
                    </>
                  ) : (
                    <>
                      <Zap className="h-5 w-5 mr-2" />
                      One-Click Import All Data
                    </>
                  )}
                </Button>

                {(importing || importProgress > 0) && (
                  <div className="space-y-2">
                    <Progress value={importProgress} className="h-2" />
                    <p className="text-sm text-center text-muted-foreground">{importMessage}</p>
                  </div>
                )}

                {!serviceStatus?.google_calendar?.connected && !serviceStatus?.notion?.connected && !importing && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>No data sources connected.</strong> Please go back to Step 1 and configure at least Google Calendar or Notion.
                    </AlertDescription>
                  </Alert>
                )}

                {(serviceStatus?.google_calendar?.connected || serviceStatus?.notion?.connected) && !importing && importProgress === 0 && (
                  <Alert>
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Ready to import:</strong>
                      {serviceStatus?.google_calendar?.connected && <span className="block">• Calendar: Last 6 months of events</span>}
                      {serviceStatus?.notion?.connected && <span className="block">• Notion: Last 30 days of content</span>}
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              {stepStatus[2].completed && (
                <Alert className="border-green-500 bg-green-50 dark:bg-green-950/20">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    Excellent! Your data is imported. Click <strong>Next</strong> to generate AI tags.
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </>
        )}

        {/* Step 3: Generate Tags */}
        {currentStep === 3 && (
          <>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Tag className="h-5 w-5" />
                Step 3: Generate AI Tags
              </CardTitle>
              <CardDescription>
                Let AI analyze your activities and create smart tags (1 minute)
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <Alert>
                <Sparkles className="h-4 w-4" />
                <AlertDescription>
                  AI will analyze your activities, generate relevant tags, and organize everything for you
                </AlertDescription>
              </Alert>

              {/* Stats */}
              <div className="grid grid-cols-2 gap-4">
                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription className="text-xs">Activities Processed</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {systemStats?.database?.processed_activities_count || 0}
                    </div>
                    <p className="text-xs text-muted-foreground">activities analyzed</p>
                  </CardContent>
                </Card>
                <Card>
                  <CardHeader className="pb-3">
                    <CardDescription className="text-xs">Unique Tags</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">
                      {systemStats?.database?.tags_count || 0}
                    </div>
                    <p className="text-xs text-muted-foreground">tags generated</p>
                  </CardContent>
                </Card>
              </div>

              {/* Generate Button */}
              <div className="space-y-4">
                <Button
                  onClick={handleGenerateTags}
                  disabled={generating || (importStatus?.calendar?.total_imported || 0) + (importStatus?.notion?.total_imported || 0) === 0}
                  size="lg"
                  className="w-full h-14 bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700"
                >
                  {generating ? (
                    <>
                      <Loader2 className="h-5 w-5 mr-2 animate-spin" />
                      Generating Tags...
                    </>
                  ) : (
                    <>
                      <Sparkles className="h-5 w-5 mr-2" />
                      Start AI Analysis
                    </>
                  )}
                </Button>

                {(generating || generationProgress > 0) && (
                  <div className="space-y-4">
                    <Progress value={generationProgress} className="h-2" />
                    <p className="text-sm text-center text-muted-foreground">{generationMessage}</p>

                    {/* Real-time activity display */}
                    {generating && (
                      <Card className="border-blue-200 bg-blue-50 dark:bg-blue-950/20">
                        <CardContent className="pt-4 space-y-3">
                          {activityCounter.total > 0 ? (
                            <>
                              <div className="flex items-center justify-between">
                                <span className="text-sm font-medium text-blue-900 dark:text-blue-100">
                                  Current Activity: {activityCounter.current} of {activityCounter.total}
                                </span>
                                <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                              </div>

                              {currentActivity && (
                                <div className="space-y-2">
                                  <p className="text-sm text-blue-800 dark:text-blue-200 line-clamp-2">
                                    {currentActivity}
                                  </p>

                                  {currentTags.length > 0 && (
                                    <div className="space-y-1">
                                      <span className="text-xs font-medium text-blue-900 dark:text-blue-100">
                                        Generated Tags:
                                      </span>
                                      <div className="flex flex-wrap gap-1">
                                        {currentTags.map((tag, index) => (
                                          <span
                                            key={index}
                                            className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-200 dark:bg-blue-900 text-blue-900 dark:text-blue-100 animate-in fade-in duration-200"
                                          >
                                            {tag}
                                          </span>
                                        ))}
                                      </div>
                                    </div>
                                  )}
                                </div>
                              )}
                            </>
                          ) : (
                            <div className="flex items-center gap-3">
                              <Loader2 className="h-4 w-4 animate-spin text-blue-600" />
                              <span className="text-sm text-blue-800 dark:text-blue-200">
                                Loading activities and preparing for analysis...
                              </span>
                            </div>
                          )}
                        </CardContent>
                      </Card>
                    )}
                  </div>
                )}

                {((importStatus?.calendar?.total_imported || 0) + (importStatus?.notion?.total_imported || 0) === 0) && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription>
                      Please import data in Step 2 before generating tags
                    </AlertDescription>
                  </Alert>
                )}
              </div>

              {stepStatus[3].completed && (
                <Alert className="border-green-500 bg-green-50 dark:bg-green-950/20">
                  <CheckCircle2 className="h-4 w-4 text-green-600" />
                  <AlertDescription className="text-green-800 dark:text-green-200">
                    🎉 <strong>Setup Complete!</strong> Your data is ready. You can now explore your tagged activities and insights!
                  </AlertDescription>
                </Alert>
              )}
            </CardContent>
          </>
        )}
      </Card>

      {/* Navigation */}
      <div className="flex items-center justify-between">
        <Button
          variant="outline"
          onClick={handleBack}
          disabled={currentStep === 1}
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back
        </Button>

        <div className="flex gap-2">
          {stepStatus[currentStep].canSkip && !stepStatus[currentStep].completed && (
            <Button
              variant="ghost"
              onClick={handleSkip}
            >
              Skip this step
            </Button>
          )}

          {currentStep < 3 && (
            <Button
              onClick={handleNext}
              disabled={!canProceedToNext()}
            >
              Next
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}

          {currentStep === 3 && stepStatus[3].completed && (
            <Button
              onClick={() => window.location.href = '/'}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
            >
              View My Dashboard
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          )}
        </div>
      </div>

      {/* API Config Dialog */}
      <ApiConfigDialog
        open={configDialogOpen}
        onOpenChange={setConfigDialogOpen}
        apiType={selectedApiType}
        onSuccess={() => {
          loadServiceStatus()
          toast.success("API configuration updated successfully!")
        }}
      />
    </div>
  )
}
