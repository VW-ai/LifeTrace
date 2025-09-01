# MetricCard Component

## Purpose
Professional metric card component for displaying key statistics with artistic gradient borders and hover animations.

## Features
- **Gradient borders**: CSS-only gradient border effect using mask technique
- **Hover animations**: Subtle lift effect with pulse animation for icons
- **Trend indicators**: Optional trend arrows with color coding
- **Icon support**: Flexible icon placement with artistic background
- **Responsive text**: Gradient text for values, consistent typography

## Usage
```tsx
import { MetricCard } from './components/atomic/MetricCard';
import { Clock, TrendingUp } from 'lucide-react';

<MetricCard
  title="Total Hours Tracked"
  value="5,300h"
  subtitle="from last period"
  icon={<Clock />}
  trend={{
    value: "+12%",
    isPositive: true
  }}
/>
```

## Styling Features
- **Artistic gradients**: Orange theme consistent with template design
- **Glass morphism**: Subtle transparency and backdrop blur effects
- **Micro-animations**: Smooth transitions and pulse effects on hover
- **Professional typography**: Hierarchical text sizing and colors

## Integration
- **Dashboard**: Key metrics display (total hours, activities, categories)
- **Statistics**: Any numerical data that needs prominent display
- **Status indicators**: System health, processing status, etc.