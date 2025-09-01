# PieChart Component

## Purpose
Professional pie chart component for displaying activity composition with artistic gradients and interactive legend.

## Features
- **Artistic gradients**: Each slice uses gradient fills with transparency effects
- **Interactive legend**: Shows percentages with hover effects
- **Custom tooltip**: Glass-morphism tooltip with activity details
- **Responsive design**: Automatically adapts to container size
- **Donut style**: Inner radius creates modern donut chart appearance

## Usage
```tsx
import { PieChart } from './components/visualizations/PieChart';

const data = [
  { name: 'Work Projects', value: 2100, color: '#ffcc00' },
  { name: 'Study Economy', value: 1400, color: '#ff6600' },
  { name: 'Exercise', value: 1000, color: '#ff3300' },
  { name: 'Reading', value: 800, color: '#ff9900' },
];

<PieChart 
  data={data}
  height={320}
  showLegend={true}
/>
```

## Integration
- **Dashboard**: Activity distribution visualization
- **Tag analysis**: Shows time allocation across different activity tags
- **Time periods**: Works with different date range filters