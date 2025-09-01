/**
 * SmartHistory App - Professional Clean Design
 * Focused on productivity and data visualization
 */

import { useState, useEffect } from 'react';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { professionalTheme } from './styles/professional-theme';
import { ProfessionalButton } from './components/atomic/ProfessionalButton';

const GlobalStyles = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@300;400;500&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: ${professionalTheme.fonts.primary};
    background-color: ${professionalTheme.colors.backgroundSecondary};
    color: ${professionalTheme.colors.text};
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
  }

  button {
    font-family: inherit;
  }
`;

const Container = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
`;

const Header = styled.header`
  background: white;
  border-bottom: 1px solid ${professionalTheme.colors.border};
  padding: 1rem 0;
  box-shadow: ${professionalTheme.shadows.sm};
`;

const HeaderContent = styled.div`
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 2rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
`;

const Logo = styled.h1`
  font-size: ${professionalTheme.typography['2xl']};
  font-weight: ${professionalTheme.typography.bold};
  color: ${professionalTheme.colors.primary};
  margin: 0;
`;

const StatusIndicator = styled.div<{ status: 'checking' | 'connected' | 'error' }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: ${professionalTheme.borderRadius.full};
  font-size: ${professionalTheme.typography.sm};
  font-weight: ${professionalTheme.typography.medium};
  
  ${({ status }) => {
    switch (status) {
      case 'checking':
        return `
          background-color: #FEF3C7;
          color: #92400E;
        `;
      case 'connected':
        return `
          background-color: #D1FAE5;
          color: #065F46;
        `;
      case 'error':
        return `
          background-color: #FEE2E2;
          color: #991B1B;
        `;
    }
  }}
`;

const Main = styled.main`
  max-width: 1200px;
  margin: 0 auto;
  padding: 3rem 2rem;
`;

const HeroSection = styled.section`
  text-align: center;
  margin-bottom: 4rem;
`;

const HeroTitle = styled.h1`
  font-size: ${professionalTheme.typography['5xl']};
  font-weight: ${professionalTheme.typography.bold};
  color: ${professionalTheme.colors.text};
  margin-bottom: 1rem;
  line-height: 1.2;
`;

const HeroSubtitle = styled.p`
  font-size: ${professionalTheme.typography.xl};
  color: ${professionalTheme.colors.textSecondary};
  max-width: 600px;
  margin: 0 auto 2rem;
  line-height: 1.6;
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
  margin-top: 4rem;
`;

const FeatureCard = styled.div`
  background: white;
  padding: 2rem;
  border-radius: ${professionalTheme.borderRadius.xl};
  box-shadow: ${professionalTheme.shadows.md};
  border: 1px solid ${professionalTheme.colors.borderLight};
  transition: all ${professionalTheme.animation.transition.base};
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: ${professionalTheme.shadows.lg};
  }
`;

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 1rem;
`;

const FeatureTitle = styled.h3`
  font-size: ${professionalTheme.typography.xl};
  font-weight: ${professionalTheme.typography.semibold};
  color: ${professionalTheme.colors.text};
  margin-bottom: 1rem;
`;

const FeatureDescription = styled.p`
  color: ${professionalTheme.colors.textSecondary};
  margin-bottom: 1.5rem;
  line-height: 1.6;
`;

export default function ProfessionalApp() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking');

  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        setApiStatus(response.ok ? 'connected' : 'error');
      } catch (error) {
        setApiStatus('error');
      }
    };
    checkAPI();
  }, []);

  const handleConnectAPI = () => {
    window.open('http://localhost:8000/docs', '_blank');
  };

  const handleViewDashboard = () => {
    console.log('🎯 Dashboard coming soon!');
    alert('Dashboard coming soon! Clean, professional analytics await...');
  };

  const getStatusIcon = () => {
    switch (apiStatus) {
      case 'checking': return '🔄';
      case 'connected': return '✅';
      case 'error': return '❌';
    }
  };

  const getStatusText = () => {
    switch (apiStatus) {
      case 'checking': return 'Checking connection...';
      case 'connected': return 'Backend Connected';
      case 'error': return 'Backend Disconnected';
    }
  };

  return (
    <ThemeProvider theme={professionalTheme}>
      <GlobalStyles />
      <Container>
        <Header>
          <HeaderContent>
            <Logo>SmartHistory</Logo>
            <StatusIndicator status={apiStatus}>
              <span>{getStatusIcon()}</span>
              <span>{getStatusText()}</span>
            </StatusIndicator>
          </HeaderContent>
        </Header>

        <Main>
          <HeroSection>
            <HeroTitle>Activity Analytics Dashboard</HeroTitle>
            <HeroSubtitle>
              Track and analyze your productivity with intelligent insights from your Notion and Google Calendar data.
            </HeroSubtitle>
            
            <ButtonGroup>
              <ProfessionalButton 
                variant="primary" 
                size="lg"
                onClick={handleViewDashboard}
              >
                📊 View Dashboard
              </ProfessionalButton>
              
              <ProfessionalButton 
                variant="outline" 
                size="lg"
                onClick={handleConnectAPI}
              >
                🔗 API Documentation
              </ProfessionalButton>
            </ButtonGroup>
          </HeroSection>

          <FeatureGrid>
            <FeatureCard>
              <FeatureIcon>📈</FeatureIcon>
              <FeatureTitle>Data Visualization</FeatureTitle>
              <FeatureDescription>
                Clean, professional charts and graphs that make your productivity data easy to understand and actionable.
              </FeatureDescription>
              <ProfessionalButton variant="secondary" size="sm">
                Explore Charts
              </ProfessionalButton>
            </FeatureCard>

            <FeatureCard>
              <FeatureIcon>🏷️</FeatureIcon>
              <FeatureTitle>Smart Tagging</FeatureTitle>
              <FeatureDescription>
                AI-powered activity categorization that automatically organizes your work patterns and identifies trends.
              </FeatureDescription>
              <ProfessionalButton variant="secondary" size="sm">
                View Tags
              </ProfessionalButton>
            </FeatureCard>

            <FeatureCard>
              <FeatureIcon>⚡</FeatureIcon>
              <FeatureTitle>Real-time Processing</FeatureTitle>
              <FeatureDescription>
                Automated analysis of your Notion and Calendar activities with instant insights and progress tracking.
              </FeatureDescription>
              <ProfessionalButton variant="secondary" size="sm">
                Start Processing
              </ProfessionalButton>
            </FeatureCard>
          </FeatureGrid>
        </Main>
      </Container>
    </ThemeProvider>
  );
}