# Dashboard Component

## Purpose
Main dashboard component that integrates all visualization components to display comprehensive activity analytics with real-time backend data consumption.

## Features
- **Real-time data**: Loads processed activities and tags from backend API
- **Time range filtering**: Week, month, year views with automatic data refresh
- **Comprehensive metrics**: Total hours, activities, tags, daily averages
- **Multiple visualizations**: Area charts for trends, pie charts for composition
- **Error handling**: Graceful error states with retry functionality
- **Loading states**: Professional loading indicators during data fetch
- **Responsive design**: Adapts to different screen sizes

## Data Integration
- **API Client**: Uses typed API client for all backend communication
- **Data transformation**: Converts raw backend data to chart-ready formats
- **Real-time updates**: Automatically refreshes when time range changes
- **Tag aggregation**: Groups activities by tags for meaningful insights

## Visual Components Used
- `MetricCard`: Key statistics display
- `AreaChart`: Activity trends over time
- `PieChart`: Activity composition breakdown
- `ProfessionalButton`: Time range selection and actions

## Usage
```tsx
import { Dashboard } from './components/dashboard/Dashboard';

<Dashboard />
```

## Architecture
- **Atomic structure**: Follows REGULATION.md principles
- **Professional theme**: Uses artistic orange theme from template
- **TypeScript**: Full type safety with backend data models
- **Error boundaries**: Handles API failures gracefully
- **Performance**: Efficient data processing and chart rendering