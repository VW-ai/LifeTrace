/**
 * Main Dashboard Component
 * Professional activity tracking dashboard with real-time data
 */

import { useState, useEffect } from 'react';
import styled from 'styled-components';
import { Clock, TrendingUp, Activity, Calendar, Sparkles } from 'lucide-react';
import { AreaChart } from '../../visualizations/AreaChart';
import { PieChart } from '../../visualizations/PieChart';
import { MetricCard } from '../../atomic/MetricCard';
import { ProfessionalButton } from '../../atomic/ProfessionalButton';
import { apiClient, type ProcessedActivity, type Tag } from '../../../api/client';
import { professionalTheme } from '../../../styles/professional-theme';

interface DashboardProps {
  className?: string;
}

interface TimeRange {
  label: string;
  value: 'week' | 'month' | 'year';
  days: number;
}

const timeRanges: TimeRange[] = [
  { label: 'Last Week', value: 'week', days: 7 },
  { label: 'Last Month', value: 'month', days: 30 },
  { label: 'Last Year', value: 'year', days: 365 },
];

const DashboardContainer = styled.div`
  min-height: 100vh;
  width: 100vw;
  background: radial-gradient(circle at 20% 80%, rgba(249, 115, 22, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 20%, rgba(255, 204, 0, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 40%, rgba(255, 102, 0, 0.05) 0%, transparent 50%);
  padding: 1rem 2rem 2rem 2rem;
  box-sizing: border-box;
  overflow-x: hidden;
  
  @media (max-width: 768px) {
    padding: 0.5rem 1rem 1rem 1rem;
  }
`;

const DashboardHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  
  @media (max-width: 768px) {
    flex-direction: column;
    gap: 1rem;
    align-items: flex-start;
  }
`;

const HeaderContent = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
`;

const IconContainer = styled.div`
  padding: 0.5rem;
  border-radius: 12px;
  background: linear-gradient(135deg, 
    ${professionalTheme.colors.primary} 0%, 
    ${professionalTheme.colors.secondary} 100%
  );
`;

const Title = styled.h1`
  font-size: ${professionalTheme.typography['4xl']};
  font-weight: ${professionalTheme.typography.bold};
  background: linear-gradient(45deg, 
    ${professionalTheme.colors.primary}, 
    ${professionalTheme.colors.secondary}, 
    ${professionalTheme.colors.accent}
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0;
`;

const Subtitle = styled.p`
  font-size: ${professionalTheme.typography.lg};
  color: ${professionalTheme.colors.textSecondary};
  margin: 0.5rem 0 0 0;
`;

const TimeRangeSelector = styled.div`
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 251, 235, 0.9) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(234, 88, 12, 0.1);
  border-radius: 12px;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
`;

const ChartsGrid = styled.div`
  display: grid;
  gap: 2rem;
  grid-template-columns: repeat(2, 1fr); /* 50% / 50% width distribution */
  margin-bottom: 2rem;
  
  @media (max-width: 1024px) {
    grid-template-columns: 1fr;
  }
`;

const ChartSection = styled.section`
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.9) 0%, rgba(255, 251, 235, 0.9) 100%);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(234, 88, 12, 0.1);
  border-radius: 24px;
  padding: 2rem;
  transition: all 0.3s ease;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 25px rgba(234, 88, 12, 0.15);
  }
`;

const ChartTitle = styled.h2`
  font-size: ${professionalTheme.typography['2xl']};
  font-weight: ${professionalTheme.typography.bold};
  background: linear-gradient(45deg, 
    ${professionalTheme.colors.primary}, 
    ${professionalTheme.colors.secondary}
  );
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin: 0 0 0.5rem 0;
`;

const ChartSubtitle = styled.p`
  color: ${professionalTheme.colors.textSecondary};
  margin: 0 0 1.5rem 0;
`;

const LoadingState = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: ${professionalTheme.colors.textSecondary};
`;

const ErrorState = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  color: ${professionalTheme.colors.accentDanger};
  text-align: center;
`;

export const Dashboard: React.FC<DashboardProps> = ({ className }) => {
  const [selectedTimeRange, setSelectedTimeRange] = useState<TimeRange>(timeRanges[2]);
  const [activities, setActivities] = useState<ProcessedActivity[]>([]);
  const [, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, [selectedTimeRange]);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const endDate = new Date();
      const startDate = new Date();
      startDate.setDate(endDate.getDate() - selectedTimeRange.days);

      const [activitiesRes, tagsRes] = await Promise.all([
        apiClient.getProcessedActivities(
          1000, // limit
          0,    // offset
          undefined, // no tag filter
          startDate.toISOString().split('T')[0],
          endDate.toISOString().split('T')[0]
        ),
        apiClient.getTags()
      ]);

      if (activitiesRes.error) throw new Error(activitiesRes.error);
      if (tagsRes.error) throw new Error(tagsRes.error);

      setActivities(activitiesRes.data?.activities || []);
      setTags(tagsRes.data || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  };

  const prepareChartData = () => {
    // Group activities by date for area chart
    const dateGroups = activities.reduce((acc, activity) => {
      const date = new Date(activity.date).toLocaleDateString();
      if (!acc[date]) acc[date] = {};
      
      activity.tags?.forEach(tag => {
        if (!acc[date][tag]) acc[date][tag] = 0;
        acc[date][tag] += activity.duration_minutes / 60; // Convert to hours
      });
      
      return acc;
    }, {} as Record<string, Record<string, number>>);

    const areaData = Object.entries(dateGroups).map(([date, tagData]) => ({
      date,
      ...tagData
    }));

    // Prepare pie chart data
    const tagTotals = activities.reduce((acc, activity) => {
      activity.tags?.forEach(tag => {
        if (!acc[tag]) acc[tag] = 0;
        acc[tag] += activity.duration_minutes / 60;
      });
      return acc;
    }, {} as Record<string, number>);

    const pieData = Object.entries(tagTotals)
      .sort(([,a], [,b]) => b - a)
      .slice(0, 8) // Top 8 tags
      .map(([tag, hours], index) => ({
        name: tag,
        value: Math.round(hours * 10) / 10,
        color: professionalTheme.colors.dataViz[index % professionalTheme.colors.dataViz.length]
      }));

    // Categories for area chart (top tags)
    const categories = Object.keys(tagTotals)
      .sort((a, b) => tagTotals[b] - tagTotals[a])
      .slice(0, 5)
      .map((tag, index) => ({
        key: tag,
        name: tag,
        color: professionalTheme.colors.dataViz[index]
      }));

    return { areaData, pieData, categories };
  };

  const getMetrics = () => {
    const totalHours = activities.reduce((sum, activity) => sum + activity.duration_minutes, 0) / 60;
    const totalActivities = activities.length;
    const uniqueTags = new Set(activities.flatMap(a => a.tags || [])).size;
    const avgDailyHours = totalHours / selectedTimeRange.days;

    return {
      totalHours: Math.round(totalHours * 10) / 10,
      totalActivities,
      uniqueTags,
      avgDailyHours: Math.round(avgDailyHours * 10) / 10
    };
  };

  if (loading) {
    return (
      <DashboardContainer className={className}>
        <LoadingState>Loading your activity data...</LoadingState>
      </DashboardContainer>
    );
  }

  if (error) {
    return (
      <DashboardContainer className={className}>
        <ErrorState>
          <p>Error loading dashboard: {error}</p>
          <ProfessionalButton onClick={loadData} style={{ marginTop: '1rem' }}>
            Try Again
          </ProfessionalButton>
        </ErrorState>
      </DashboardContainer>
    );
  }

  const { areaData, pieData, categories } = prepareChartData();
  const metrics = getMetrics();

  return (
    <DashboardContainer className={className}>
      <DashboardHeader>
        <div>
          <HeaderContent>
            <IconContainer>
              <Sparkles size={24} color="white" />
            </IconContainer>
            <Title>Time Analytics Dashboard</Title>
          </HeaderContent>
          <Subtitle>AI-powered insights into your creative time allocation</Subtitle>
        </div>
        
        <TimeRangeSelector>
          <Calendar size={20} color={professionalTheme.colors.primary} />
          {timeRanges.map(range => (
            <ProfessionalButton
              key={range.value}
              variant={selectedTimeRange.value === range.value ? 'primary' : 'ghost'}
              size="sm"
              onClick={() => setSelectedTimeRange(range)}
            >
              {range.label}
            </ProfessionalButton>
          ))}
        </TimeRangeSelector>
      </DashboardHeader>

      <MetricsGrid>
        <MetricCard
          title="Total Hours Tracked"
          value={`${metrics.totalHours}h`}
          subtitle="from last period"
          icon={<Clock />}
          trend={{ value: '+12%', isPositive: true }}
        />
        
        <MetricCard
          title="Activities Tracked"
          value={metrics.totalActivities}
          subtitle="Across all categories"
          icon={<Activity />}
        />
        
        <MetricCard
          title="Unique Tags"
          value={metrics.uniqueTags}
          subtitle="Activity categories"
          icon={<TrendingUp />}
        />
        
        <MetricCard
          title="Avg. Daily Hours"
          value={`${metrics.avgDailyHours}h`}
          subtitle="Productive time per day"
          icon={<Clock />}
        />
      </MetricsGrid>

      <ChartsGrid>
        <ChartSection>
          <ChartTitle>Activity Trends Over Time</ChartTitle>
          <ChartSubtitle>Flowing visualization of your time patterns</ChartSubtitle>
          {areaData.length > 0 ? (
            <AreaChart data={areaData} categories={categories} height={"50vh"} />
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: professionalTheme.colors.textSecondary }}>
              No activity data available for the selected period
            </div>
          )}
        </ChartSection>

        <ChartSection>
          <ChartTitle>Activity Composition</ChartTitle>
          <ChartSubtitle>Your time distribution at a glance</ChartSubtitle>
          {pieData.length > 0 ? (
            <PieChart data={pieData} height={"50vh"} />
          ) : (
            <div style={{ padding: '2rem', textAlign: 'center', color: professionalTheme.colors.textSecondary }}>
              No activity data available
            </div>
          )}
        </ChartSection>
      </ChartsGrid>
    </DashboardContainer>
  );
};
