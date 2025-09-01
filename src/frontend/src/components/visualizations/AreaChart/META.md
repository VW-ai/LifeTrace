# AreaChart Component

## Purpose
Professional area chart component for displaying activity trends over time with artistic gradients. Built with Recharts and styled-components.

## Features
- **Artistic gradients**: Each data series gets gradient fills inspired by template design
- **Custom tooltip**: Glass-morphism tooltip with activity details
- **Responsive design**: Automatically adapts to container size
- **Professional styling**: Orange artistic theme with subtle shadows
- **Accessibility**: Proper color contrast and readable text

## Usage
```tsx
import { AreaChart } from './components/visualizations/AreaChart';

const data = [
  { date: 'Week 1', 'Work': 35, 'Study': 25, 'Exercise': 15 },
  { date: 'Week 2', 'Work': 40, 'Study': 30, 'Exercise': 12 },
];

const categories = [
  { key: 'Work', name: 'Work Projects', color: '#ffcc00' },
  { key: 'Study', name: 'Study Time', color: '#ff6600' },
  { key: 'Exercise', name: 'Exercise', color: '#ff3300' },
];

<AreaChart 
  data={data}
  categories={categories}
  height={320}
/>
```

## Integration
- **Dashboard**: Main trend visualization component
- **Time filtering**: Works with different time ranges (weeks, months, years)
- **Data transformation**: Accepts processed activity data from backend API