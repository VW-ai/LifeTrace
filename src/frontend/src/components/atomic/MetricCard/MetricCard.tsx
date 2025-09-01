/**
 * Professional Metric Card Component
 * Displays key metrics with artistic gradient borders
 */

import styled from 'styled-components';
import type { ReactNode } from 'react';
import { professionalTheme } from '../../../styles/professional-theme';

interface MetricCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon?: ReactNode;
  trend?: {
    value: string;
    isPositive: boolean;
  };
  className?: string;
}

const CardContainer = styled.div`
  background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);
  border-radius: 1rem;
  padding: 1.5rem;
  position: relative;
  transition: all 0.3s ease;
  
  /* Gradient border effect */
  &::before {
    content: '';
    position: absolute;
    inset: 0;
    padding: 2px;
    background: linear-gradient(135deg, #ea580c, #f97316, #ffcc00);
    border-radius: inherit;
    mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
    mask-composite: xor;
    -webkit-mask-composite: xor;
  }
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(234, 88, 12, 0.15);
    
    .pulse-effect {
      animation: pulse 2s ease-in-out infinite;
    }
  }
  
  @keyframes pulse {
    0%, 100% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
  }
`;

const CardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.5rem;
`;

const Title = styled.h3`
  font-size: ${professionalTheme.typography.sm};
  font-weight: ${professionalTheme.typography.medium};
  color: ${professionalTheme.colors.textSecondary};
  margin: 0;
`;

const IconContainer = styled.div`
  padding: 0.5rem;
  border-radius: 8px;
  background: linear-gradient(135deg, 
    rgba(234, 88, 12, 0.2) 0%, 
    rgba(249, 115, 22, 0.2) 100%
  );
  
  svg {
    width: 1rem;
    height: 1rem;
    color: ${professionalTheme.colors.primary};
  }
`;

const ValueContainer = styled.div`
  margin-bottom: 0.25rem;
`;

const Value = styled.div`
  font-size: ${professionalTheme.typography['3xl']};
  font-weight: ${professionalTheme.typography.bold};
  background: linear-gradient(45deg, 
    ${professionalTheme.colors.primary}, 
    ${professionalTheme.colors.secondary}
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
`;

const Subtitle = styled.p`
  font-size: ${professionalTheme.typography.xs};
  color: ${professionalTheme.colors.textSecondary};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.25rem;
`;

const TrendIcon = styled.span<{ isPositive: boolean }>`
  color: ${({ isPositive }) => isPositive ? '#10B981' : '#EF4444'};
  font-weight: bold;
`;

export const MetricCard: React.FC<MetricCardProps> = ({
  title,
  value,
  subtitle,
  icon,
  trend,
  className
}) => {
  return (
    <CardContainer className={className}>
      <CardHeader>
        <Title>{title}</Title>
        {icon && (
          <IconContainer className="pulse-effect">
            {icon}
          </IconContainer>
        )}
      </CardHeader>
      
      <ValueContainer>
        <Value>{value}</Value>
      </ValueContainer>
      
      {(subtitle || trend) && (
        <Subtitle>
          {trend && (
            <TrendIcon isPositive={trend.isPositive}>
              {trend.isPositive ? '↗' : '↘'} {trend.value}
            </TrendIcon>
          )}
          {subtitle && <span>{subtitle}</span>}
        </Subtitle>
      )}
    </CardContainer>
  );
};