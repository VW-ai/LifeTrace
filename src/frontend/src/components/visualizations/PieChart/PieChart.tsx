/**
 * Professional Pie Chart Component
 * Displays activity composition with artistic styling
 */

import styled from 'styled-components';
import {
  PieChart as RechartsPie,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { professionalTheme } from '../../../styles/professional-theme';

interface PieChartData {
  name: string;
  value: number;
  color: string;
}

interface PieChartProps {
  data: PieChartData[];
  height?: number | string; // allow responsive heights like '40vh'
  showLegend?: boolean;
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

const LegendContainer = styled.div`
  margin-top: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
`;

const LegendItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.2s ease;
  
  &:hover {
    background: rgba(234, 88, 12, 0.05);
  }
`;

const LegendColor = styled.div<{ color: string }>`
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background-color: ${({ color }) => color};
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const LegendLabel = styled.span`
  font-size: 0.875rem;
  font-weight: 500;
  color: ${professionalTheme.colors.text};
`;

const LegendValue = styled.span`
  font-size: 0.875rem;
  font-weight: 700;
  color: ${professionalTheme.colors.primary};
`;

const TooltipContent = ({ active, payload }: any) => {
  if (active && payload && payload.length) {
    const data = payload[0];
    return (
      <CustomTooltip>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
          <div
            style={{
              width: '12px',
              height: '12px',
              borderRadius: '50%',
              backgroundColor: data.payload.color,
            }}
          />
          <span style={{ fontSize: '14px', fontWeight: 600, color: professionalTheme.colors.text }}>
            {data.name}
          </span>
        </div>
        <div style={{ fontSize: '14px', color: professionalTheme.colors.textSecondary }}>
          <strong>{data.value}h</strong>
        </div>
      </CustomTooltip>
    );
  }
  return null;
};

export const PieChart: React.FC<PieChartProps> = ({
  data,
  height = 320,
  showLegend = true,
  className
}) => {
  const totalHours = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <ChartContainer className={className}>
      <div style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <RechartsPie>
            <defs>
              {data.map((entry, index) => (
                <linearGradient
                  key={`pieGradient-${index}`}
                  id={`pieGradient-${index}`}
                  x1="0"
                  y1="0"
                  x2="1"
                  y2="1"
                >
                  <stop offset="0%" stopColor={entry.color} />
                  <stop offset="100%" stopColor={entry.color} stopOpacity={0.7} />
                </linearGradient>
              ))}
            </defs>
            
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={120}
              paddingAngle={4}
              dataKey="value"
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={`url(#pieGradient-${index})`}
                  stroke="white"
                  strokeWidth={2}
                />
              ))}
            </Pie>
            
            <Tooltip content={<TooltipContent />} />
          </RechartsPie>
        </ResponsiveContainer>
      </div>
      
      {showLegend && (
        <LegendContainer>
          {data.map((item, index) => (
            <LegendItem key={index}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <LegendColor color={item.color} />
                <LegendLabel>{item.name}</LegendLabel>
              </div>
              <LegendValue>
                {((item.value / totalHours) * 100).toFixed(1)}%
              </LegendValue>
            </LegendItem>
          ))}
        </LegendContainer>
      )}
    </ChartContainer>
  );
};
