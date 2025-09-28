"use client"

import { useState } from "react"
import { Trash2, GitMerge, Target, AlertTriangle, Loader2, CheckCircle, Eye } from "lucide-react"
import { Button } from "../ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../ui/card"
import { Input } from "../ui/input"
import { Label } from "../ui/label"
import { Switch } from "../ui/switch"
import { Badge } from "../ui/badge"
import { Progress } from "../ui/progress"
import { ScrollArea } from "../ui/scroll-area"
import { Separator } from "../ui/separator"
import { apiClient } from "../../lib/api-client"
import { toast } from "sonner"

interface CleanupParams {
  dry_run: boolean
  removal_threshold: number
  merge_threshold: number
  date_start: string
  date_end: string
}

interface CleanupAction {
  name: string
  reason: string
  confidence: number
  target?: string
}

interface CleanupResult {
  status: string
  total_analyzed: number
  marked_for_removal: number
  marked_for_merge: number
  removed: number
  merged: number
  dry_run: boolean
  scope: {
    date_start?: string
    date_end?: string
  }
  tags_to_remove: CleanupAction[]
  tags_to_merge: CleanupAction[]
}

export function TagCleanupSettings() {
  const [cleanupParams, setCleanupParams] = useState<CleanupParams>({
    dry_run: true,
    removal_threshold: 0.7,
    merge_threshold: 0.8,
    date_start: "",
    date_end: "",
  })

  const [isProcessing, setIsProcessing] = useState(false)
  const [lastResult, setLastResult] = useState<CleanupResult | null>(null)

  const handleCleanup = async () => {
    try {
      setIsProcessing(true)

      // Prepare parameters, excluding empty date strings
      const params: any = {
        dry_run: cleanupParams.dry_run,
        removal_threshold: cleanupParams.removal_threshold,
        merge_threshold: cleanupParams.merge_threshold,
      }

      if (cleanupParams.date_start) {
        params.date_start = cleanupParams.date_start
      }
      if (cleanupParams.date_end) {
        params.date_end = cleanupParams.date_end
      }

      const result = await apiClient.cleanupTags(params)
      setLastResult(result)

      if (cleanupParams.dry_run) {
        toast.success(`Dry run completed: ${result.marked_for_removal} tags marked for removal, ${result.marked_for_merge} for merge`)
      } else {
        toast.success(`Cleanup completed: ${result.removed} tags removed, ${result.merged} tags merged`)
      }

    } catch (error) {
      console.error('Tag cleanup failed:', error)
      toast.error("Tag cleanup failed")
    } finally {
      setIsProcessing(false)
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return "text-red-600"
    if (confidence >= 0.6) return "text-orange-600"
    return "text-yellow-600"
  }

  const getConfidenceBadge = (confidence: number) => {
    const percentage = Math.round(confidence * 100)
    if (confidence >= 0.8) return <Badge variant="destructive">{percentage}%</Badge>
    if (confidence >= 0.6) return <Badge variant="default" className="bg-orange-500 hover:bg-orange-600">{percentage}%</Badge>
    return <Badge variant="secondary">{percentage}%</Badge>
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold mb-2">Tag Cleanup</h2>
        <p className="text-muted-foreground">
          Remove meaningless tags and merge similar ones using AI analysis. Always run in dry-run mode first.
        </p>
      </div>

      {/* Cleanup Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5" />
            Cleanup Configuration
          </CardTitle>
          <CardDescription>
            Configure thresholds and scope for tag cleanup analysis
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Dry Run Toggle */}
          <div className="flex items-center justify-between p-4 border rounded-lg bg-yellow-50/50 border-yellow-200">
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                <Eye className="h-4 w-4 text-yellow-600" />
                <Label htmlFor="dry-run" className="font-medium">Dry Run Mode</Label>
                {cleanupParams.dry_run && <Badge variant="outline" className="text-yellow-700 border-yellow-300">Recommended</Badge>}
              </div>
              <p className="text-xs text-muted-foreground">
                {cleanupParams.dry_run ? "Analyze and preview changes without making actual modifications" : "⚠️ Will permanently remove and merge tags"}
              </p>
            </div>
            <Switch
              id="dry-run"
              checked={cleanupParams.dry_run}
              onCheckedChange={(checked) =>
                setCleanupParams(prev => ({ ...prev, dry_run: checked }))
              }
            />
          </div>

          {/* Thresholds */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="removal-threshold">Removal Threshold</Label>
              <div className="space-y-1">
                <Input
                  id="removal-threshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={cleanupParams.removal_threshold}
                  onChange={(e) =>
                    setCleanupParams(prev => ({ ...prev, removal_threshold: parseFloat(e.target.value) || 0.7 }))
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Confidence threshold for removing meaningless tags (0.0 - 1.0)
                </p>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="merge-threshold">Merge Threshold</Label>
              <div className="space-y-1">
                <Input
                  id="merge-threshold"
                  type="number"
                  min="0"
                  max="1"
                  step="0.1"
                  value={cleanupParams.merge_threshold}
                  onChange={(e) =>
                    setCleanupParams(prev => ({ ...prev, merge_threshold: parseFloat(e.target.value) || 0.8 }))
                  }
                />
                <p className="text-xs text-muted-foreground">
                  Confidence threshold for merging similar tags (0.0 - 1.0)
                </p>
              </div>
            </div>
          </div>

          {/* Date Range */}
          <div className="space-y-3">
            <Label>Date Range (Optional)</Label>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="start-date" className="text-sm">Start Date</Label>
                <Input
                  id="start-date"
                  type="date"
                  value={cleanupParams.date_start}
                  onChange={(e) =>
                    setCleanupParams(prev => ({ ...prev, date_start: e.target.value }))
                  }
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="end-date" className="text-sm">End Date</Label>
                <Input
                  id="end-date"
                  type="date"
                  value={cleanupParams.date_end}
                  onChange={(e) =>
                    setCleanupParams(prev => ({ ...prev, date_end: e.target.value }))
                  }
                />
              </div>
            </div>
            <p className="text-xs text-muted-foreground">
              Leave empty to analyze all tags. Use date range to scope cleanup to specific time periods.
            </p>
          </div>

          {/* Run Button */}
          <Button
            onClick={handleCleanup}
            disabled={isProcessing}
            className={`w-full ${!cleanupParams.dry_run ? 'bg-red-600 hover:bg-red-700' : ''}`}
          >
            {isProcessing ? (
              <>
                <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                Analyzing Tags...
              </>
            ) : cleanupParams.dry_run ? (
              <>
                <Eye className="h-4 w-4 mr-2" />
                Run Dry Run Analysis
              </>
            ) : (
              <>
                <AlertTriangle className="h-4 w-4 mr-2" />
                Execute Cleanup (Permanent)
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Results */}
      {lastResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              {lastResult.dry_run ? (
                <>
                  <Eye className="h-5 w-5" />
                  Dry Run Results
                </>
              ) : (
                <>
                  <CheckCircle className="h-5 w-5 text-green-600" />
                  Cleanup Results
                </>
              )}
            </CardTitle>
            <CardDescription>
              {lastResult.dry_run ? "Preview of proposed changes" : "Summary of executed changes"}
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Summary Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold">{lastResult.total_analyzed}</div>
                <div className="text-xs text-muted-foreground">Tags Analyzed</div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-red-600">
                  {lastResult.dry_run ? lastResult.marked_for_removal : lastResult.removed}
                </div>
                <div className="text-xs text-muted-foreground">
                  {lastResult.dry_run ? "Marked for Removal" : "Removed"}
                </div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-orange-600">
                  {lastResult.dry_run ? lastResult.marked_for_merge : lastResult.merged}
                </div>
                <div className="text-xs text-muted-foreground">
                  {lastResult.dry_run ? "Marked for Merge" : "Merged"}
                </div>
              </div>
              <div className="text-center p-3 border rounded-lg">
                <div className="text-2xl font-bold text-green-600">
                  {lastResult.total_analyzed - (lastResult.dry_run ? lastResult.marked_for_removal + lastResult.marked_for_merge : lastResult.removed + lastResult.merged)}
                </div>
                <div className="text-xs text-muted-foreground">Kept</div>
              </div>
            </div>

            {/* Scope Info */}
            {(lastResult.scope.date_start || lastResult.scope.date_end) && (
              <div className="text-sm text-muted-foreground">
                Scope: {lastResult.scope.date_start || "All time"} to {lastResult.scope.date_end || "Present"}
              </div>
            )}

            {/* Actions Lists */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {/* Removal Actions */}
              {lastResult.tags_to_remove.length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <Trash2 className="h-4 w-4 text-red-600" />
                      Tags to Remove ({lastResult.tags_to_remove.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <ScrollArea className="h-64">
                      <div className="space-y-2">
                        {lastResult.tags_to_remove.map((action, index) => (
                          <div key={index} className="border rounded-md p-2 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-sm">{action.name}</span>
                              {getConfidenceBadge(action.confidence)}
                            </div>
                            <p className="text-xs text-muted-foreground">{action.reason}</p>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}

              {/* Merge Actions */}
              {lastResult.tags_to_merge.length > 0 && (
                <Card>
                  <CardHeader className="pb-3">
                    <CardTitle className="text-sm flex items-center gap-2">
                      <GitMerge className="h-4 w-4 text-orange-600" />
                      Tags to Merge ({lastResult.tags_to_merge.length})
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <ScrollArea className="h-64">
                      <div className="space-y-2">
                        {lastResult.tags_to_merge.map((action, index) => (
                          <div key={index} className="border rounded-md p-2 space-y-1">
                            <div className="flex items-center justify-between">
                              <span className="font-medium text-sm">{action.name}</span>
                              {getConfidenceBadge(action.confidence)}
                            </div>
                            {action.target && (
                              <div className="text-xs">
                                → Merge into: <span className="font-medium">{action.target}</span>
                              </div>
                            )}
                            <p className="text-xs text-muted-foreground">{action.reason}</p>
                          </div>
                        ))}
                      </div>
                    </ScrollArea>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* No Actions */}
            {lastResult.tags_to_remove.length === 0 && lastResult.tags_to_merge.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
                <p>No tags need cleanup with current thresholds!</p>
                <p className="text-xs">All tags appear to be meaningful and well-organized.</p>
              </div>
            )}
          </CardContent>
        </Card>
      )}

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
              <span>Always run in dry-run mode first to preview changes</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Start with conservative thresholds (0.7-0.8) and adjust based on results</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Use date ranges to scope cleanup to specific time periods</span>
            </div>
            <div className="flex items-start gap-2">
              <CheckCircle className="h-4 w-4 mt-0.5 text-green-500" />
              <span>Review the analysis carefully before executing permanent changes</span>
            </div>
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-4 w-4 mt-0.5 text-orange-500" />
              <span>Cleanup operations are permanent and cannot be undone</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}