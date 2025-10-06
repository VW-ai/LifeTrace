# Real-Time Tag Generation Progress Display

## Feature Name
Real-Time Tag Generation Progress Display

## Date
October 6, 2025

---

## Purpose

### Problem Statement
Currently, Step 3 (Generate AI Tags) in the Quick Start Wizard shows only a generic progress bar (0-100%) with a simple message like "Generating tags...". Users have no visibility into:
- Which activity is currently being processed
- What tags are being generated for each activity
- How many activities remain
- Whether the AI is working correctly

This creates a "black box" experience where users wait 1-5 minutes without knowing what's happening.

### User Request
> "When doing Step 3: Generate AI Tags, I want the frontend to show which activity it is currently reading or generating tags for, and what tags are generated."

### Goals
1. **Transparency**: Show exactly what the AI is doing in real-time
2. **Engagement**: Keep users interested during the 1-5 minute wait
3. **Trust**: Demonstrate that the AI is working and producing results
4. **Debugging**: Help users identify if something goes wrong

---

## Implementation Strategy

### High-Level Approach

We'll implement a **polling-based progress system** since FastAPI doesn't natively support WebSockets in the current setup:

```
Frontend (Wizard)
    ↓ POST /api/v1/process/daily
Backend (Processing Service)
    ↓ Start async processing job
    ↓ Update progress in memory/database
    ↑ Return job_id
Frontend polls /api/v1/process/status/{job_id}
    ↓ GET every 500ms-1s
Backend returns current progress:
    - current_activity (text)
    - current_tags (array)
    - activity_index (N of M)
    - overall_progress (0-100%)
```

### Architecture

#### 1. Backend Changes

**File**: `src/backend/api/services.py`

**Add Progress Tracking to ProcessingService**:
```python
class ProcessingService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._processing_jobs: Dict[str, ProcessingStatus] = {}
        self._job_progress: Dict[str, ProcessingProgress] = {}  # NEW

    async def trigger_daily_processing(self, request):
        job_id = str(uuid.uuid4())

        # Initialize progress tracking
        self._job_progress[job_id] = ProcessingProgress(
            job_id=job_id,
            status="running",
            current_activity=None,
            current_tags=[],
            activity_index=0,
            total_activities=0,
            progress=0
        )

        # Start processing in background
        asyncio.create_task(self._process_with_progress(job_id, request))

        return {"job_id": job_id, "status": "started"}

    async def _process_with_progress(self, job_id, request):
        """Process activities with real-time progress updates."""
        try:
            # Get all raw activities
            activities = self._get_activities_to_process()
            total = len(activities)

            self._job_progress[job_id].total_activities = total

            # Process each activity
            for i, activity in enumerate(activities):
                # Update progress: current activity
                self._job_progress[job_id].activity_index = i + 1
                self._job_progress[job_id].current_activity = activity.details[:100]
                self._job_progress[job_id].progress = int((i / total) * 100)

                # Generate tags (this calls AI)
                tags = await self._generate_tags_for_activity(activity)

                # Update progress: generated tags
                self._job_progress[job_id].current_tags = tags

                # Small delay to allow frontend to poll
                await asyncio.sleep(0.1)

            # Mark complete
            self._job_progress[job_id].status = "completed"
            self._job_progress[job_id].progress = 100

        except Exception as e:
            self._job_progress[job_id].status = "failed"
            self._job_progress[job_id].error = str(e)

    async def get_processing_progress(self, job_id: str):
        """Get real-time progress for a job."""
        return self._job_progress.get(job_id)
```

**Add New Model**:
```python
class ProcessingProgress(BaseModel):
    job_id: str
    status: str  # running, completed, failed
    current_activity: Optional[str] = None
    current_tags: List[str] = []
    activity_index: int = 0
    total_activities: int = 0
    progress: int = 0  # 0-100
    error: Optional[str] = None
```

**Add New Endpoint**:
```python
@app.get(f"{API_V1_PREFIX}/process/progress/{{job_id}}")
async def get_processing_progress(job_id: str):
    """Get real-time progress for tag generation job."""
    progress = await processing_service.get_processing_progress(job_id)
    if not progress:
        raise HTTPException(404, "Job not found")
    return progress
```

#### 2. Frontend Changes

**File**: `src/frontend/components/settings/quick-start-wizard.tsx`

**Add State for Real-Time Progress**:
```typescript
const [generationJobId, setGenerationJobId] = useState<string | null>(null)
const [currentActivity, setCurrentActivity] = useState<string>("")
const [currentTags, setCurrentTags] = useState<string[]>([])
const [activityProgress, setActivityProgress] = useState<{current: number, total: number}>({current: 0, total: 0})
```

**Update handleGenerateTags**:
```typescript
const handleGenerateTags = async () => {
  setGenerating(true)
  setGenerationProgress(0)
  setGenerationMessage("Starting AI tag generation...")

  try {
    // Start processing job
    const result = await apiClient.triggerDailyProcessing({
      use_database: true,
      regenerate_system_tags: true
    })

    const jobId = result.job_id
    setGenerationJobId(jobId)

    // Poll for progress updates
    const pollInterval = setInterval(async () => {
      try {
        const progress = await apiClient.getProcessingProgress(jobId)

        if (progress.status === "running") {
          setGenerationProgress(progress.progress)
          setCurrentActivity(progress.current_activity || "")
          setCurrentTags(progress.current_tags || [])
          setActivityProgress({
            current: progress.activity_index,
            total: progress.total_activities
          })
          setGenerationMessage(
            `Processing activity ${progress.activity_index} of ${progress.total_activities}...`
          )
        } else if (progress.status === "completed") {
          clearInterval(pollInterval)
          setGenerationProgress(100)
          setGenerationMessage("Tag generation complete!")
          toast.success(`🎉 Generated tags for ${progress.total_activities} activities!`)
          await loadSystemStats()

          setTimeout(() => {
            setStepStatus(prev => ({ ...prev, 3: { ...prev[3], completed: true } }))
            setGenerationProgress(0)
            setGenerationMessage("")
          }, 2000)
        } else if (progress.status === "failed") {
          clearInterval(pollInterval)
          throw new Error(progress.error || "Processing failed")
        }
      } catch (err) {
        console.error("Progress polling error:", err)
      }
    }, 500) // Poll every 500ms

  } catch (error) {
    // ... error handling
  } finally {
    setGenerating(false)
  }
}
```

**Add Real-Time Display UI**:
```tsx
{/* Real-time progress display */}
{generating && currentActivity && (
  <Card className="border-primary/50 bg-primary/5">
    <CardContent className="pt-6 space-y-3">
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium">Current Activity:</span>
        <span className="text-xs text-muted-foreground">
          {activityProgress.current} of {activityProgress.total}
        </span>
      </div>

      <div className="p-3 bg-background rounded-md border">
        <p className="text-sm line-clamp-2">{currentActivity}</p>
      </div>

      {currentTags.length > 0 && (
        <>
          <div className="flex items-center gap-2 text-sm font-medium">
            <Sparkles className="h-4 w-4 text-primary" />
            Generated Tags:
          </div>
          <div className="flex flex-wrap gap-2">
            {currentTags.map((tag, i) => (
              <Badge key={i} variant="secondary" className="animate-in fade-in">
                {tag}
              </Badge>
            ))}
          </div>
        </>
      )}
    </CardContent>
  </Card>
)}
```

**Add API Client Method**:
```typescript
// src/frontend/lib/api-client.ts
async getProcessingProgress(jobId: string) {
  return this.request<{
    job_id: string
    status: string
    current_activity: string | null
    current_tags: string[]
    activity_index: number
    total_activities: number
    progress: number
    error: string | null
  }>(`/api/v1/process/progress/${jobId}`)
}
```

---

## Detailed Design

### User Experience Flow

**Step 3 UI Evolution**:

1. **Initial State** (before clicking):
   ```
   ┌─────────────────────────────────────────┐
   │ Step 3: Generate AI Tags                │
   ├─────────────────────────────────────────┤
   │ Let AI analyze your activities...        │
   │                                           │
   │ [Stats Card]  [Stats Card]               │
   │                                           │
   │ ┌─────────────────────────────────────┐ │
   │ │ ✨ Start AI Analysis                │ │
   │ └─────────────────────────────────────┘ │
   └─────────────────────────────────────────┘
   ```

2. **Processing State** (real-time):
   ```
   ┌─────────────────────────────────────────┐
   │ Processing activity 42 of 150...        │
   │ ▓▓▓▓▓▓▓░░░░░░░░ 28%                    │
   ├─────────────────────────────────────────┤
   │ 🔍 Current Activity:        42 of 150   │
   │ ┌─────────────────────────────────────┐ │
   │ │ Meeting with design team to review  │ │
   │ │ Q4 product roadmap and...           │ │
   │ └─────────────────────────────────────┘ │
   │                                           │
   │ ✨ Generated Tags:                       │
   │ [meeting] [design] [product]             │
   │ [roadmap] [planning] [team]              │
   └─────────────────────────────────────────┘
   ```

3. **Completed State**:
   ```
   ┌─────────────────────────────────────────┐
   │ ✅ Tag Generation Complete!              │
   │ ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓ 100%                   │
   ├─────────────────────────────────────────┤
   │ 🎉 Generated 87 unique tags             │
   │ for 150 activities                       │
   │                                           │
   │ [View My Dashboard →]                    │
   └─────────────────────────────────────────┘
   ```

### Data Flow

```
User clicks "Start AI Analysis"
    ↓
Frontend: POST /api/v1/process/daily
    ↓
Backend: Create job_id, start async processing
    ↓
Backend: For each activity:
    1. Update _job_progress[job_id].current_activity
    2. Call AI to generate tags
    3. Update _job_progress[job_id].current_tags
    4. Increment activity_index
    ↓
Frontend: Poll GET /api/v1/process/progress/{job_id} every 500ms
    ↓
Frontend: Update UI with current activity + tags
    ↓
Backend: Mark job complete
    ↓
Frontend: Stop polling, show success
```

---

## Implementation Details

### Backend Implementation

#### Phase 1: Modify ActivityProcessor

**File**: `src/backend/agent/core/activity_processor.py`

Add callback support for progress updates:

```python
class ActivityProcessor:
    def process_daily_activities(
        self,
        use_database=True,
        date_start=None,
        date_end=None,
        progress_callback=None  # NEW
    ):
        """Process activities with optional progress callback."""

        # Get activities
        activities = self._load_activities(...)
        total = len(activities)

        for i, activity in enumerate(activities):
            # Notify progress
            if progress_callback:
                progress_callback(
                    activity_index=i + 1,
                    total_activities=total,
                    current_activity=activity.details,
                    current_tags=[]
                )

            # Generate tags
            tags = self._generate_tags(activity)

            # Notify tags generated
            if progress_callback:
                progress_callback(
                    activity_index=i + 1,
                    total_activities=total,
                    current_activity=activity.details,
                    current_tags=[tag.name for tag in tags]
                )

            # Save to database
            self._save_processed_activity(activity, tags)

        return report
```

#### Phase 2: Update ProcessingService

**File**: `src/backend/api/services.py`

```python
class ProcessingService:
    def __init__(self, db_manager):
        self.db = db_manager
        self._processing_jobs: Dict[str, ProcessingStatus] = {}
        self._job_progress: Dict[str, Dict[str, Any]] = {}
        self._progress_lock = asyncio.Lock()

    async def trigger_daily_processing(self, request: ProcessingRequest):
        """Start tag generation with progress tracking."""
        job_id = str(uuid.uuid4())

        # Initialize progress
        async with self._progress_lock:
            self._job_progress[job_id] = {
                "status": "running",
                "current_activity": None,
                "current_tags": [],
                "activity_index": 0,
                "total_activities": 0,
                "progress": 0,
                "error": None,
                "started_at": datetime.now().isoformat()
            }

        # Start processing in background
        asyncio.create_task(self._process_with_progress(job_id, request))

        return ProcessingResponse(
            status="started",
            job_id=job_id,
            message="Tag generation started. Poll /process/progress/{job_id} for updates."
        )

    async def _process_with_progress(self, job_id: str, request: ProcessingRequest):
        """Process activities with real-time progress updates."""
        def progress_callback(activity_index, total_activities, current_activity, current_tags):
            """Callback to update progress in real-time."""
            try:
                self._job_progress[job_id].update({
                    "activity_index": activity_index,
                    "total_activities": total_activities,
                    "current_activity": current_activity[:200],  # Truncate long text
                    "current_tags": current_tags,
                    "progress": int((activity_index / total_activities) * 100)
                })
            except Exception as e:
                print(f"Progress callback error: {e}")

        try:
            # Run actual processing with callback
            processor = ActivityProcessor()
            processor.enable_system_tag_regeneration = request.regenerate_system_tags

            report = processor.process_daily_activities(
                use_database=True,
                progress_callback=progress_callback
            )

            # Mark complete
            async with self._progress_lock:
                self._job_progress[job_id].update({
                    "status": "completed",
                    "progress": 100,
                    "current_activity": None,
                    "current_tags": [],
                    "completed_at": datetime.now().isoformat(),
                    "result": {
                        "processed_activities": report['processed_counts']['processed_activities'],
                        "total_tags": report['tag_analysis']['total_unique_tags']
                    }
                })

        except Exception as e:
            async with self._progress_lock:
                self._job_progress[job_id].update({
                    "status": "failed",
                    "error": str(e),
                    "failed_at": datetime.now().isoformat()
                })

    async def get_processing_progress(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get real-time progress for a processing job."""
        async with self._progress_lock:
            return self._job_progress.get(job_id)
```

#### Phase 3: Add API Endpoint

**File**: `src/backend/api/server.py`

```python
@app.get(f"{API_V1_PREFIX}/process/progress/{{job_id}}")
async def get_processing_progress(
    job_id: str,
    processing_service: ProcessingService = Depends(get_processing_service)
):
    """
    Get real-time progress for a tag generation job.

    Poll this endpoint every 500ms-1s while status is "running".
    """
    progress = await processing_service.get_processing_progress(job_id)

    if not progress:
        raise HTTPException(status_code=404, detail="Job not found")

    return progress
```

### Frontend Implementation

#### Phase 1: Add Progress State

**File**: `src/frontend/components/settings/quick-start-wizard.tsx`

```typescript
// Add new state variables
const [generationJobId, setGenerationJobId] = useState<string | null>(null)
const [currentActivity, setCurrentActivity] = useState<string>("")
const [currentTags, setCurrentTags] = useState<string[]>([])
const [activityProgress, setActivityProgress] = useState<{
  current: number
  total: number
}>({ current: 0, total: 0 })
```

#### Phase 2: Update Tag Generation Handler

```typescript
const handleGenerateTags = async () => {
  setGenerating(true)
  setGenerationProgress(0)
  setGenerationMessage("Starting AI tag generation...")
  setCurrentActivity("")
  setCurrentTags([])
  setActivityProgress({ current: 0, total: 0 })

  try {
    // Start processing job
    const result = await apiClient.triggerDailyProcessing({
      use_database: true,
      regenerate_system_tags: true
    })

    if (!result.job_id) {
      throw new Error("No job ID returned from server")
    }

    const jobId = result.job_id
    setGenerationJobId(jobId)

    // Poll for progress updates
    let pollCount = 0
    const maxPolls = 600 // 5 minutes max (600 * 500ms)

    const pollInterval = setInterval(async () => {
      try {
        pollCount++

        if (pollCount > maxPolls) {
          clearInterval(pollInterval)
          throw new Error("Tag generation timeout")
        }

        const progress = await apiClient.getProcessingProgress(jobId)

        if (progress.status === "running") {
          // Update all progress state
          setGenerationProgress(progress.progress || 0)
          setCurrentActivity(progress.current_activity || "")
          setCurrentTags(progress.current_tags || [])
          setActivityProgress({
            current: progress.activity_index || 0,
            total: progress.total_activities || 0
          })

          if (progress.total_activities > 0) {
            setGenerationMessage(
              `Processing activity ${progress.activity_index} of ${progress.total_activities}...`
            )
          }
        } else if (progress.status === "completed") {
          clearInterval(pollInterval)
          setGenerationProgress(100)
          setGenerationMessage("Tag generation complete!")

          const totalTags = progress.result?.total_tags || 0
          const totalActivities = progress.result?.processed_activities || activityProgress.total

          toast.success(`🎉 AI Analysis Complete! Generated ${totalTags} unique tags for ${totalActivities} activities`)

          await loadSystemStats()

          setTimeout(() => {
            setStepStatus(prev => ({ ...prev, 3: { ...prev[3], completed: true } }))
            setGenerationProgress(0)
            setGenerationMessage("")
            setCurrentActivity("")
            setCurrentTags([])
          }, 2000)
        } else if (progress.status === "failed") {
          clearInterval(pollInterval)
          throw new Error(progress.error || "Processing failed")
        }
      } catch (pollErr) {
        console.error("Progress polling error:", pollErr)
        // Don't stop polling on temporary errors
      }
    }, 500) // Poll every 500ms

  } catch (error) {
    console.error('Tag generation failed:', error)
    setGenerationProgress(0)
    setGenerationMessage("")
    setCurrentActivity("")
    setCurrentTags([])
    toast.error(`❌ Tag generation failed: ${error instanceof Error ? error.message : 'Unknown error'}`)
  } finally {
    setGenerating(false)
  }
}
```

#### Phase 3: Add Real-Time Display UI

```tsx
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
        {/* ... existing stats cards ... */}
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

        {/* Progress Bar */}
        {(generating || generationProgress > 0) && (
          <div className="space-y-2">
            <Progress value={generationProgress} className="h-2" />
            <p className="text-sm text-center text-muted-foreground">{generationMessage}</p>
          </div>
        )}

        {/* REAL-TIME ACTIVITY DISPLAY */}
        {generating && currentActivity && (
          <Card className="border-primary/50 bg-primary/5 animate-in fade-in">
            <CardContent className="pt-6 space-y-4">
              {/* Activity Counter */}
              <div className="flex items-center justify-between text-sm">
                <span className="font-medium flex items-center gap-2">
                  <Circle className="h-3 w-3 fill-primary text-primary animate-pulse" />
                  Current Activity:
                </span>
                <Badge variant="secondary">
                  {activityProgress.current} of {activityProgress.total}
                </Badge>
              </div>

              {/* Activity Text */}
              <div className="p-3 bg-background rounded-md border">
                <p className="text-sm text-foreground line-clamp-3">{currentActivity}</p>
              </div>

              {/* Generated Tags */}
              {currentTags.length > 0 && (
                <div className="space-y-2">
                  <div className="flex items-center gap-2 text-sm font-medium">
                    <Sparkles className="h-4 w-4 text-primary" />
                    Generated Tags:
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {currentTags.map((tag, i) => (
                      <Badge
                        key={i}
                        variant="secondary"
                        className="animate-in fade-in zoom-in"
                        style={{ animationDelay: `${i * 50}ms` }}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        )}

        {/* Error Alert */}
        {((importStatus?.calendar?.total_imported || 0) + (importStatus?.notion?.total_imported || 0) === 0) && !generating && (
          <Alert variant="destructive">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              Please import data in Step 2 before generating tags
            </AlertDescription>
          </Alert>
        )}
      </div>

      {/* Success Alert */}
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
```

#### Phase 4: Add API Client Method

**File**: `src/frontend/lib/api-client.ts`

```typescript
async getProcessingProgress(jobId: string) {
  return this.request<{
    job_id: string
    status: 'running' | 'completed' | 'failed'
    current_activity: string | null
    current_tags: string[]
    activity_index: number
    total_activities: number
    progress: number
    error: string | null
    result?: {
      processed_activities: number
      total_tags: number
    }
  }>(`/api/v1/process/progress/${jobId}`)
}
```

---

## Impacted Files

### Backend Files
1. **`src/backend/agent/core/activity_processor.py`**
   - Add `progress_callback` parameter to `process_daily_activities()`
   - Call callback at key points (start activity, generate tags, save)

2. **`src/backend/api/services.py`**
   - Add `_job_progress` dictionary to track progress
   - Update `trigger_daily_processing()` to return job_id immediately
   - Add `_process_with_progress()` async method
   - Add `get_processing_progress()` method

3. **`src/backend/api/server.py`**
   - Add `GET /api/v1/process/progress/{job_id}` endpoint

4. **`src/backend/api/models.py`**
   - Add `ProcessingProgressResponse` model (optional, for type safety)

### Frontend Files
1. **`src/frontend/components/settings/quick-start-wizard.tsx`**
   - Add progress state variables
   - Update `handleGenerateTags()` with polling logic
   - Add real-time display UI component

2. **`src/frontend/lib/api-client.ts`**
   - Add `getProcessingProgress(jobId)` method

---

## Dependencies

### External
- None (uses existing asyncio, polling patterns)

### Internal
- Depends on existing `ActivityProcessor`
- Depends on existing `ProcessingService`
- Depends on existing FastAPI infrastructure
- Depends on existing UI components (Card, Badge, Progress)

---

## Testing Requirements

### Backend Tests
1. **Unit Tests**:
   - Test progress callback mechanism
   - Test concurrent job processing
   - Test progress data structure
   - Test job completion/failure states

2. **Integration Tests**:
   - Test full processing flow with progress updates
   - Test polling endpoint with valid/invalid job IDs
   - Test memory cleanup after job completion

### Frontend Tests
1. **Component Tests**:
   - Test real-time UI updates
   - Test polling logic
   - Test error handling during polling
   - Test cleanup on unmount

2. **E2E Tests**:
   - Test complete wizard flow with real-time progress
   - Test user experience during tag generation
   - Test timeout handling (5+ minutes)
   - Test network interruption recovery

---

## Performance Considerations

### Backend
- **Memory**: Progress data stored in memory (cleared after completion)
  - Estimated: ~1KB per job
  - Max concurrent jobs: 10-20 (10-20 KB)
  - Cleanup policy: Remove completed jobs after 1 hour

- **CPU**: Minimal overhead (just updating dictionary)
  - Progress callback: <1ms per call
  - Polling endpoint: <5ms per request

### Frontend
- **Polling Frequency**: 500ms (2 requests/second)
  - Max duration: 5 minutes = 600 requests
  - Bandwidth: ~1KB per request = 600 KB total
  - Acceptable for user experience

- **UI Updates**: React state updates every 500ms
  - Smooth with proper memoization
  - Animation delays stagger tag appearance

---

## Future Enhancements

### Phase 2 (Optional)
1. **WebSocket Support**:
   - Replace polling with WebSocket connection
   - Push updates from backend immediately
   - Reduce latency and bandwidth

2. **Persistent Progress**:
   - Store progress in database
   - Allow resuming interrupted jobs
   - Show progress across browser sessions

3. **Batch Progress**:
   - Group activities into batches (e.g., 10 activities)
   - Show batch-level progress
   - Reduce UI churn for large datasets

4. **Tag Preview**:
   - Show top 5-10 tags in real-time
   - Animate tag cloud during generation
   - Allow user to "like/dislike" tags mid-process

5. **Progress History**:
   - Show history of past processing jobs
   - Allow replaying progress visualization
   - Export progress logs

---

## User Documentation

### For End Users
**Quick Start Guide Update**:

Step 3 now shows:
- Which activity is currently being analyzed
- What tags the AI is generating
- Progress counter (e.g., "42 of 150")
- Real-time tag badges appearing

### For Developers
**API Documentation**:

```
GET /api/v1/process/progress/{job_id}

Response:
{
  "job_id": "uuid",
  "status": "running|completed|failed",
  "current_activity": "Meeting with design...",
  "current_tags": ["meeting", "design", "product"],
  "activity_index": 42,
  "total_activities": 150,
  "progress": 28,
  "error": null
}

Poll this endpoint every 500ms while status is "running".
```

---

## Security Considerations

1. **Rate Limiting**:
   - Polling endpoint should have rate limit (e.g., 10 req/sec per user)
   - Prevent abuse of progress checking

2. **Job ID Validation**:
   - Ensure job_id belongs to authenticated user
   - Don't expose other users' processing jobs

3. **Memory Cleanup**:
   - Auto-delete completed jobs after 1 hour
   - Prevent memory leaks from abandoned jobs

4. **Error Information**:
   - Don't expose sensitive error details
   - Log full errors server-side only

---

## Rollout Plan

### Phase 1: Backend (Week 1)
- [ ] Implement progress callback in ActivityProcessor
- [ ] Add progress tracking to ProcessingService
- [ ] Add progress endpoint to API
- [ ] Test with mock data

### Phase 2: Frontend (Week 1)
- [ ] Add progress state to wizard
- [ ] Implement polling logic
- [ ] Design real-time display UI
- [ ] Test with backend

### Phase 3: Polish (Week 2)
- [ ] Add animations and transitions
- [ ] Optimize polling performance
- [ ] Add error recovery
- [ ] Write documentation

### Phase 4: Release (Week 2)
- [ ] User testing
- [ ] Performance testing
- [ ] Deploy to production
- [ ] Monitor for issues

---

## Success Metrics

### User Experience
- **Engagement**: Users stay on page during processing (>90%)
- **Satisfaction**: User feedback on progress visibility (>4/5)
- **Understanding**: Users understand what's happening (>95%)

### Technical
- **Performance**: No impact on processing time (<5% overhead)
- **Reliability**: Polling works 99% of the time
- **Scalability**: Handles 100+ concurrent jobs

---

## Conclusion

This feature transforms the tag generation experience from a "black box" to a transparent, engaging process. Users will see exactly what the AI is doing, which builds trust and keeps them engaged during the 1-5 minute wait.

The implementation is straightforward using polling (no complex WebSocket infrastructure needed) and provides immediate value to users with minimal performance overhead.

---

## Changelog

### v1.0 - October 6, 2025
- Initial feature specification
- Designed polling-based progress system
- Defined backend and frontend changes
- Created implementation plan
