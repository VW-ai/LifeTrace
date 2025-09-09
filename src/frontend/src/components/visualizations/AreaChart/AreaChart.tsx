/**
 * Professional Area Chart Component
 * Displays activity trends over time with artistic gradients
 */

import styled from 'styled-components';
import {
  AreaChart as RechartsArea,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { professionalTheme } from '../../../styles/professional-theme';

interface AreaChartData {
  date: string;
  [key: string]: string | number;
}

interface AreaChartProps {
  data: AreaChartData[];
  categories: Array<{
    key: string;
    name: string;
    color: string;
  }>;
  height?: number | string; // allow responsive heights like '40vh'
  className?: string;
}

const ChartContainer = styled.div`
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(255, 251, 235, 0.95) 100%);
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 8px 32px rgba(234, 88, 12, 0.1);
`;

const CustomTooltip = styled.div`
  background: rgba(255, 255, 255, 0.95);
  border: 1px solid ${professionalTheme.colors.primary};
  border-radius: 12px;
  padding: 12px;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
`;

const TooltipContent = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <CustomTooltip>
        <p style={{ margin: 0, marginBottom: '8px', fontWeight: 600, color: professionalTheme.colors.text }}>
          {label}
        </p>
        {payload.map((entry: any, index: number) => (
          <div key={index} style={{ display: 'flex', alignItems: 'center', gap: '8px', margin: '4px 0' }}>
            <div
              style={{
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: entry.color,
              }}
            />
            <span style={{ fontSize: '14px', color: professionalTheme.colors.textSecondary }}>
              {entry.name}: <strong>{entry.value}h</strong>
            </span>
          </div>
        ))}
      </CustomTooltip>
    );
  }
  return null;
};

export const AreaChart: React.FC<AreaChartProps> = ({
  data,
  categories,
  height = 320,
  className
}) => {
  return (
    <ChartContainer className={className}>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsArea data={data}>
            <defs>
              {categories.map((category, index) => (
                <linearGradient
                  key={`gradient-${index}`}
                  id={`gradient-${category.key}`}
                  x1="0"
                  y1="0"
                  x2="0"
                  y2="1"
                >
                  <stop offset="5%" stopColor={category.color} stopOpacity={0.8} />
                  <stop offset="95%" stopColor={category.color} stopOpacity={0.1} />
                </linearGradient>
              ))}
            </defs>
            
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={professionalTheme.colors.border} 
              opacity={0.3} 
            />
            
            <XAxis 
              dataKey="date" 
              stroke={professionalTheme.colors.textSecondary}
              fontSize={12}
              tick={{ fill: professionalTheme.colors.textSecondary }}
            />
            
            <YAxis 
              stroke={professionalTheme.colors.textSecondary}
              fontSize={12}
              tick={{ fill: professionalTheme.colors.textSecondary }}
            />
            
            <Tooltip content={<TooltipContent />} />
            
            {categories.map((category) => (
              <Area
                key={category.key}
                type="monotone"
                dataKey={category.key}
                stroke={category.color}
                fillOpacity={1}
                fill={`url(#gradient-${category.key})`}
                strokeWidth={3}
                name={category.name}
              />
            ))}
          </RechartsArea>
        </ResponsiveContainer>
      </div>
    </ChartContainer>
  );
};
