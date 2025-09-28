# Time Insights Dashboard

A comprehensive tag-driven activity visualization dashboard built with Next.js, TypeScript, and D3.js. This frontend implements Phase 1 (P1) of the Frontend Update Plan, providing a solid foundation for time tracking and activity analysis.

## Features Implemented (Phase 1)

### ✅ Core Infrastructure
- **API Client**: Complete FastAPI integration with type-safe endpoints
- **Global State Management**: Zustand-based state with URL synchronization
- **Design System**: Consistent tokens, colors, and components using shadcn/ui

### ✅ Timeline Visualization
- **Interactive Timeline**: D3.js-powered timeline with brushing for time range selection
- **Event Visualization**: Color-coded events by tags with hover tooltips
- **Multi-source Support**: Lane-based layout for different data sources

### ✅ Filtering & Search
- **Advanced Filter Bar**: Search, time period selection, tag/source filtering
- **Active Filter Display**: Visual chips showing current filters with quick removal
- **Cross-filtering**: Click any element to filter across views

### ✅ Tag Management
- **Tag Frequency Cards**: Top tags with usage statistics and color coding
- **Stable Color System**: HSL-based color generation for consistent tag colors
- **Interactive Selection**: Click tags to add/remove from filters

### ✅ Event Details
- **Event Drawer**: Detailed view with metadata, tags, and related events
- **Related Events**: Smart suggestions based on tags and sources
- **Quick Actions**: Filter by tags, copy details, navigate between events

### ✅ URL State & Sharing
- **URL Synchronization**: All filters and views reflected in shareable URLs
- **Share Button**: Generate shareable links for current dashboard state
- **Browser Navigation**: Back/forward support with state preservation

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS v4 with custom design tokens
- **UI Components**: shadcn/ui with Radix UI primitives
- **Visualization**: D3.js for interactive charts and timeline
- **State Management**: Zustand with URL synchronization
- **Icons**: Lucide React

## Project Structure

\`\`\`
├── app/
│   ├── layout.tsx          # Root layout with fonts and providers
│   ├── page.tsx            # Main dashboard page
│   └── globals.css         # Global styles and design tokens
├── components/
│   ├── dashboard/          # Dashboard-specific components
│   ├── events/             # Event drawer and related components
│   ├── filters/            # Filter bar and controls
│   ├── timeline/           # Timeline and tag frequency components
│   ├── providers/          # React providers (URL sync)
│   └── ui/                 # Reusable UI components (shadcn/ui)
├── lib/
│   ├── store/              # Zustand state management
│   ├── utils/              # Utility functions (colors, dates)
│   ├── api-client.ts       # FastAPI client with type safety
│   └── types.ts            # TypeScript type definitions
└── hooks/
    └── use-url-sync.ts     # URL synchronization hook
\`\`\`

## API Integration

The dashboard is designed to work with a FastAPI backend providing these endpoints:

- `GET /api/v1/activities/raw` - Raw activity data
- `GET /api/v1/activities/processed` - Processed activities with tags
- `GET /api/v1/insights/overview` - Activity insights and statistics
- `GET /api/v1/insights/time-distribution` - Time-based activity distribution
- `GET /api/v1/tags` - Available tags
- `GET /api/v1/tags/summary` - Tag usage statistics
- `GET /api/v1/tags/cooccurrence` - Tag co-occurrence data
- `GET /api/v1/tags/transitions` - Tag transition patterns
- `GET /api/v1/tags/time-series` - Time-series tag data

## Getting Started

1. **Install Dependencies**
   \`\`\`bash
   npm install
   \`\`\`

2. **Set Environment Variables**
   \`\`\`bash
   # .env.local
   NEXT_PUBLIC_API_URL=http://localhost:8000
   \`\`\`

3. **Run Development Server**
   \`\`\`bash
   npm run dev
   \`\`\`

4. **Open Dashboard**
   Navigate to [http://localhost:3000](http://localhost:3000)

## Design System

### Color Tokens
- **Background**: Main app background
- **Surface**: Card and panel backgrounds (3 levels)
- **Text**: Primary, secondary, and muted text colors
- **Accent**: Interactive elements and highlights
- **Tag Colors**: Stable HSL-based colors for consistent tag visualization

### Typography
- **Font**: Inter for UI, IBM Plex for data
- **Scale**: 12/14/16/20/24/28/36px with 1.4-1.6 line heights
- **Tabular Numbers**: For timeline and numeric data

### Spacing & Layout
- **Base Unit**: 8px spacing system
- **Container**: 1200-1440px max width with responsive breakpoints
- **Grid**: CSS Grid for dashboard layout, Flexbox for components

## Accessibility Features

- **Keyboard Navigation**: Full keyboard support for all interactions
- **Screen Reader**: ARIA labels and semantic HTML structure
- **Color Contrast**: AA compliance for all text and essential elements
- **Reduced Motion**: Respects `prefers-reduced-motion` setting

## Performance Optimizations

- **Server-Side Aggregation**: Prefers backend data processing
- **Client-Side Caching**: IndexedDB for API response caching
- **Virtualization**: Large lists use react-virtual
- **Optimistic Updates**: Immediate UI feedback for interactions

## Future Phases

This implementation covers Phase 1 (P1) of the Frontend Update Plan. Future phases will add:

- **Phase 2**: Galaxy view with WebGL force graphs
- **Phase 3**: River streamgraph and calendar heatmap
- **Phase 4**: Chord diagrams and story saving
- **Phase 5**: Polish, accessibility audit, and performance tuning

## Contributing

The codebase follows the Frontend Update Plan specifications:
- Backend-first data approach
- Atomic component design
- Comprehensive TypeScript typing
- Accessibility-first development
- Performance-conscious implementation

For questions or contributions, refer to the Frontend Update Plan document for detailed specifications and implementation guidelines.
