"use client"

import { useState, useEffect } from "react"
import { Brain, Zap, Database, Settings, Loader2, PlayCircle, CheckCircle } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Switch } from "../ui/switch"
import { Badge } from "../ui/badge"
import { Progress } from "../ui/progress"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface ProcessingStatus {
  job_id: string
  status: string
  progress?: number
  started_at: string
  completed_at?: string
  error_message?: string
}

interface TaxonomyBuildParams {
  date_start: string
  date_end: string
  force_rebuild: boolean
}

interface ProcessingParams {
  use_database: boolean
  regenerate_system_tags: boolean
}

export function TagGenerationSettings() {
  const [loading, setLoading] = useState(false)
  const [processingHistory, setProcessingHistory] = useState<ProcessingStatus[]>([])
  const [currentJob, setCurrentJob] = useState<ProcessingStatus | null>(null)

  // Processing parameters
  const [processingParams, setProcessingParams] = useState<ProcessingParams>({
    use_database: true,
    regenerate_system_tags: false,
  })

  // Taxonomy parameters
  const [taxonomyParams, setTaxonomyParams] = useState<TaxonomyBuildParams>({
    date_start: "",
    date_end: "",
    force_rebuild: false,
  })

  // Processing states
  const [isProcessing, setIsProcessing] = useState(false)
  const [isBuildingTaxonomy, setIsBuildingTaxonomy] = useState(false)

  const loadProcessingHistory = async () => {
    try {
      setLoading(true)
      const history = await apiClient.getProcessingHistory(10)
      setProcessingHistory(history)

      // Check if there's a running job
      const runningJob = history.find(job => job.status === 'running')
      if (runningJob) {
        setCurrentJob(runningJob)
        // Poll for updates if there's a running job
        const interval = setInterval(async () => {
          try {
            const status = await apiClient.getProcessingStatus(runningJob.job_id)
            setCurrentJob(status)
            if (status.status !== 'running') {
              clearInterval(interval)
              await loadProcessingHistory()
            }
          } catch (error) {
            clearInterval(interval)
          }
        }, 2000)
      }
    } catch (error) {
      console.error('Failed to load processing history:', error)
      toast.error("Failed to load processing history")
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadProcessingHistory()

    // Set default date range (last 30 days)
    const end = new Date()
    const start = new Date()
    start.setDate(start.getDate() - 30)

    setTaxonomyParams(prev => ({
      ...prev,
      date_start: start.toISOString().split('T')[0],
      date_end: end.toISOString().split('T')[0],
    }))
  }, [])

  const handleTriggerProcessing = async () => {
    try {
      setIsProcessing(true)
      const result = await apiClient.triggerDailyProcessing(processingParams)

      setCurrentJob({
        job_id: result.job_id,
        status: 'running',
        started_at: new Date().toISOString(),
      })

      toast.success(`Processing started: ${result.processed_counts.raw_activities} raw activities to process`)

      // Start polling for updates
      const interval = setInterval(async () => {
        try {
          const status = await apiClient.getProcessingStatus(result.job_id)
          setCurrentJob(status)
          if (status.status !== 'running') {
            clearInterval(interval)
            await loadProcessingHistory()
            setIsProcessing(false)
            if (status.status === 'completed') {
              toast.success("Tag generation completed successfully")
            } else if (status.status === 'failed') {
              toast.error(`Processing failed: ${status.error_message}`)
            }
          }
        } catch (error) {
          clearInterval(interval)
          setIsProcessing(false)
        }
      }, 2000)

    } catch (error) {
      console.error('Failed to trigger processing:', error)
      toast.error("Failed to start tag generation")
      setIsProcessing(false)
    }
  }

  const handleBuildTaxonomy = async () => {
    try {
      setIsBuildingTaxonomy(true)
      const result = await apiClient.buildTaxonomy(taxonomyParams)

      toast.success(`Taxonomy build completed: ${result.files_generated.length} files generated`)

      if (result.taxonomy_size) {
        toast.info(`Generated taxonomy with ${result.taxonomy_size} categories and ${result.synonyms_count} synonyms`)
      }

    } catch (error) {
      console.error('Failed to build taxonomy:', error)
      toast.error("Failed to build taxonomy")
    } finally {
      setIsBuildingTaxonomy(false)
    }
  }

  const getStatusBadge = (status: string) => {
    if (!status) return <Badge variant="outline">Unknown</Badge>

    switch (status.toLowerCase()) {
      case 'completed':
        return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Completed</Badge>
      case 'running':
        return <Badge variant="secondary">Running</Badge>
      case 'failed':
        return <Badge variant="destructive">Failed</Badge>
      default:
        return <Badge variant="outline">{status}</Badge>
    }
  }

  const formatDateTime = (dateTime: string) => {
    return new Date(dateTime).toLocaleString()
  }

  if (loading && processingHistory.length === 0) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Tag Generation</h2>
        <p className="text-muted-foreground">
          Process activities and generate intelligent tags. Build taxonomy for better organization.
        </p>
      </div>

      {/* Current Job Status */}
      {currentJob && currentJob.status === 'running' && (
        <Card className="border-orange-200 bg-orange-50/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-orange-700">
              <PlayCircle className="h-5 w-5" />
              Processing in Progress
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <div className="flex items-center justify-between">
                <span className="text-sm font-medium">Job ID: {currentJob.job_id}</span>
                <Badge variant="secondary">Running</Badge>
              </div>
              {currentJob.progress !== undefined && (
                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Progress</span>
                    <span>{Math.round(currentJob.progress * 100)}%</span>
                  </div>
                  <Progress value={currentJob.progress * 100} />
                </div>
              )}
              <p className="text-xs text-muted-foreground">
                Started: {formatDateTime(currentJob.started_at)}
              </p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Tag Processing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Tag Processing
          </CardTitle>
          <CardDescription>
            Process raw activities and generate intelligent tags using AI analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="use-database">Use Database</Label>
                <p className="text-xs text-muted-foreground">Process activities from the database</p>
              </div>
              <Switch
                id="use-database"
                checked={processingParams.use_database}
                onCheckedChange={(checked) =>
                  setProcessingParams(prev => ({ ...prev, use_database: checked }))
                }
              />
            </div>

            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <Label htmlFor="regenerate-tags">Regenerate System Tags</Label>
                <p className="text-xs text-muted-foreground">Force regeneration of all system tags</p>
              </div>
              <Switch
                id="regenerate-tags"
                checked={processingParams.regenerate_system_tags}
                onCheckedChange={(checked) =>
                  setProcessingParams(prev => ({ ...prev, regenerate_system_tags: checked }))
                }
              />
            </div>
          </div>

          <Button
            onClick={handleTriggerProcessing}
            disabled={isProcessing || (currentJob?.status === 'running')}
            className="w-full"
          >
            {isProcessing || (currentJob?.status === 'running') ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Processing...
              </>
            ) : (
              <>
                <Zap className="h-4 w-4 mr-2" />
                Start Tag Generation
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Taxonomy Building */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Taxonomy Building
          </CardTitle>
          <CardDescription>
            Build AI-generated taxonomy for better tag organization. Run before tag generation for global context.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="tax-start-date">Start Date (Optional)</Label>
              <Input
                id="tax-start-date"
                type="date"
                value={taxonomyParams.date_start}
                onChange={(e) =>
                  setTaxonomyParams(prev => ({ ...prev, date_start: e.target.value }))
                }
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="tax-end-date">End Date (Optional)</Label>
              <Input
                id="tax-end-date"
                type="date"
                value={taxonomyParams.date_end}
                onChange={(e) =>
                  setTaxonomyParams(prev => ({ ...prev, date_end: e.target.value }))
                }
              />
            </div>
          </div>

          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <Label htmlFor="force-rebuild">Force Rebuild</Label>
              <p className="text-xs text-muted-foreground">Rebuild even if recent taxonomy exists</p>
            </div>
            <Switch
              id="force-rebuild"
              checked={taxonomyParams.force_rebuild}
              onCheckedChange={(checked) =>
                setTaxonomyParams(prev => ({ ...prev, force_rebuild: checked }))
              }
            />
          </div>

          <Button
            onClick={handleBuildTaxonomy}
            disabled={isBuildingTaxonomy}
            variant="outline"
            className="w-full"
          >
            {isBuildingTaxonomy ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Building Taxonomy...
              </>
            ) : (
              <>
                <Database className="h-4 w-4 mr-2" />
                Build Taxonomy
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Processing History */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Settings className="h-5 w-5" />
            Recent Processing Jobs
          </CardTitle>
          <CardDescription>
            History of recent tag generation and processing jobs
          </CardDescription>
        </CardHeader>
        <CardContent>
          {processingHistory.length === 0 ? (
            <p className="text-muted-foreground text-center py-4">No processing jobs found</p>
          ) : (
            <div className="space-y-2">
              {processingHistory.slice(0, 5).map((job) => (
                <div key={job.job_id} className="flex items-center justify-between p-3 border rounded-md">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-mono text-xs">{job.job_id}</span>
                      {getStatusBadge(job.status)}
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Started: {formatDateTime(job.started_at)}
                      {job.completed_at && ` • Completed: ${formatDateTime(job.completed_at)}`}
                    </p>
                    {job.error_message && (
                      <p className="text-xs text-red-600">{job.error_message}</p>
                    )}
                  </div>
                  {job.progress !== undefined && job.status === 'running' && (
                    <div className="w-24">
                      <Progress value={job.progress * 100} className="h-2" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <CheckCircle className="h-5 w-5" />
            Workflow Tips
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 text-sm">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Build taxonomy first for better tag categorization (optional)</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Use "Regenerate System Tags" only when needed - it processes all activities</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Monitor job progress and check processing logs for detailed information</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Run tag generation after data ingestion for optimal results</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}