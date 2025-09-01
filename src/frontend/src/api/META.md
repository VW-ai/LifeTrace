# API Client META Documentation

## Purpose
**Atomic REST API client** for consuming the SmartHistory backend. Provides clean, typed interfaces for all 20+ backend endpoints while maintaining REGULATION.md principles of single responsibility and proper error handling.

## Backend Integration
Connects to SmartHistory FastAPI backend running on `http://localhost:8000` (configurable) consuming:
- **Activities API**: Raw and processed activity CRUD operations
- **Tags API**: Tag management with usage tracking  
- **Insights API**: Analytics and productivity metrics
- **Processing API**: Activity processing triggers and status
- **System API**: Health checks and system statistics

## Architecture

### **Client Structure**
Following atomic responsibility principle:
```
api/
├── clients/              # Individual API client classes
│   ├── ActivitiesClient.ts
│   ├── TagsClient.ts  
│   ├── InsightsClient.ts
│   ├── ProcessingClient.ts
│   └── SystemClient.ts
├── types/               # API response/request interfaces
│   ├── activities.ts
│   ├── tags.ts
│   ├── insights.ts
│   └── common.ts
├── utils/               # Shared utilities
│   ├── httpClient.ts    # Base HTTP client with error handling
│   ├── auth.ts          # API key management
│   └── cache.ts         # Response caching utilities
├── hooks/               # React hooks for API integration
│   ├── useActivities.ts
│   ├── useTags.ts
│   ├── useInsights.ts
│   └── useProcessing.ts
└── index.ts            # Main API client export
```

## Core Clients

### `ActivitiesClient`
**Raw and processed activities management**
```typescript
class ActivitiesClient {
  // Raw activities
  getRawActivities(params: ActivityFilters): Promise<PaginatedActivitiesResponse>
  
  // Processed activities  
  getProcessedActivities(params: ProcessedActivityFilters): Promise<PaginatedProcessedActivitiesResponse>
}
```

### `TagsClient` 
**Tag CRUD operations with usage tracking**
```typescript
class TagsClient {
  getTags(params: TagQueryParams): Promise<PaginatedTagsResponse>
  createTag(data: TagCreateRequest): Promise<TagResponse>
  updateTag(id: number, data: TagUpdateRequest): Promise<TagResponse>
  deleteTag(id: number): Promise<void>
}
```

### `InsightsClient`
**Analytics and productivity metrics**
```typescript
class InsightsClient {
  getOverview(params: DateRangeParams): Promise<InsightsOverviewResponse>
  getTimeDistribution(params: TimeDistributionParams): Promise<TimeDistributionResponse>
}
```

### `ProcessingClient`
**Activity processing and job management**
```typescript
class ProcessingClient {
  triggerDailyProcessing(request: ProcessingRequest): Promise<ProcessingResponse>
  getProcessingStatus(jobId: string): Promise<ProcessingStatus>
  getProcessingHistory(limit?: number): Promise<ProcessingStatus[]>
  importCalendarData(request: ImportRequest): Promise<any>
  importNotionData(request: ImportRequest): Promise<any>
}
```

### `SystemClient`
**Health checks and system information**
```typescript
class SystemClient {
  getHealth(): Promise<SystemHealthResponse>
  getStats(): Promise<SystemStatsResponse>
}
```

## Error Handling

### **Dadaist Error Messages**
Creative, helpful error messages that maintain usability:
```typescript
const DadaistErrors = {
  CONNECTION_FAILED: "🎭 The data spirits are sleeping. Please wake them by checking your connection!",
  NOT_FOUND: "🔍 This data has gone on vacation. It might be back soon!",
  SERVER_ERROR: "🎪 The backend is having an artistic moment. Give it space to express itself.",
  RATE_LIMITED: "⏰ Easy there, speed demon! The API needs time to compose its next masterpiece.",
  UNAUTHORIZED: "🎨 Your creative license has expired. Time to renew your authentication!"
}
```

### **Error Recovery**
- **Automatic retry** with exponential backoff for temporary failures
- **Fallback strategies** providing cached data when available
- **User-friendly notifications** with Dadaist styling and recovery suggestions

## Authentication & Security

### **API Key Management**
```typescript
class AuthManager {
  setApiKey(key: string): void
  getApiKey(): string | null
  clearApiKey(): void
  isAuthenticated(): boolean
}
```

### **Development Mode**
- **Mock responses** for development and testing
- **Configurable endpoints** for different environments
- **Request/response logging** with artistic console styling

## Performance & Caching

### **Response Caching**
- **Memory cache** for frequently accessed data
- **TTL-based expiration** respecting data freshness requirements
- **Cache invalidation** on data mutations

### **Optimistic Updates**
- **Immediate UI updates** for create/update operations  
- **Rollback strategies** for failed operations
- **Loading states** with Dadaist animations

## React Integration

### **Custom Hooks**
Providing clean, typed interfaces for components:
```typescript
// Automatic data fetching with loading states
const { activities, isLoading, error } = useActivities(filters)

// Real-time processing status
const { status, progress } = useProcessingStatus(jobId)

// Tag management with optimistic updates
const { tags, createTag, updateTag, deleteTag } = useTags()
```

### **Error Boundaries**
- **Graceful error handling** at component level
- **Artistic error displays** maintaining Dadaist aesthetics
- **Recovery actions** allowing users to retry failed operations

## Testing Strategy
- **Mock API responses** for predictable testing
- **Error scenario testing** covering all failure modes  
- **Performance testing** ensuring acceptable response times
- **Integration testing** with actual backend endpoints