# API Layer

## Purpose
Handles all communication with the SmartHistory FastAPI backend. Provides a clean, typed interface for consuming REST endpoints.

## Core Components

### `client.ts`
- **ApiClient class**: Main client for backend communication
- **Type definitions**: TypeScript interfaces for all data models
- **Error handling**: Consistent error response format
- **Request abstraction**: Unified request method with proper headers

## Features
- **Complete API coverage**: All 20+ backend endpoints
- **Type safety**: Full TypeScript interface definitions
- **Error handling**: Graceful error responses with status codes
- **Flexible queries**: Support for filtering, pagination, date ranges
- **Health checking**: Real-time backend connection monitoring

## Usage
```tsx
import { apiClient } from './api/client';

// Get processed activities with filters
const { data, error } = await apiClient.getProcessedActivities(
  50, // limit
  0,  // offset
  ['work', 'study'], // tags filter
  '2024-01-01', // start date
  '2024-12-31'  // end date
);

// Check backend health
const health = await apiClient.health();
```

## Integration
- **Dashboard components**: Provides data for all visualizations
- **Real-time updates**: Supports polling for processing status
- **Caching ready**: Response format compatible with React Query/SWR