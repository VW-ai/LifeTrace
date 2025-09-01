/**
 * SmartHistory App - Dadaist Activity Tracking Dashboard (Fixed Version)
 */

import { useState, useEffect } from 'react';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { motion } from 'framer-motion';
import { ChaoticButton } from './components/atomic/ChaoticButton';

const GlobalDadaistStyles = createGlobalStyle`
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:wght@400;500;600;700&family=JetBrains+Mono:wght@300;400;500&family=Fredoka+One:wght@400&display=swap');

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  body {
    font-family: 'Inter', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    color: #2C3E50;
    overflow-x: hidden;
  }
`;

const dadaistTheme = {
  colors: {
    primary: '#FF6B6B',
    secondary: '#4ECDC4', 
    accent: '#F9CA24',
    text: '#2C3E50',
    background: '#ECF0F1',
    chaos: ['#FF6B6B', '#4ECDC4', '#6C5CE7', '#F9CA24', '#FD79A8']
  },
  fonts: {
    primary: "'Inter', sans-serif",
    display: "'Playfair Display', serif",
    mono: "'JetBrains Mono', monospace",
    playful: "'Fredoka One', cursive"
  },
  chaos: 0.8
};

const DadaistContainer = styled.div`
  min-height: 100vh;
  padding: 20px;
  position: relative;
`;

const HeroSection = styled.div`
  text-align: center;
  margin: 60px 0;
  position: relative;
`;

const ChaoticTitle = styled(motion.h1)`
  font-family: ${({ theme }) => theme.fonts.display};
  font-size: clamp(2rem, 8vw, 6rem);
  font-weight: 700;
  background: linear-gradient(45deg, #FF6B6B, #4ECDC4, #6C5CE7, #F9CA24);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 20px;
  transform: rotate(-2deg);
`;

const SubTitle = styled(motion.p)`
  font-family: ${({ theme }) => theme.fonts.primary};
  font-size: 1.2rem;
  color: #2C3E50;
  max-width: 600px;
  margin: 0 auto 40px;
  line-height: 1.6;
  transform: rotate(1deg);
`;

const FeatureGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 30px;
  max-width: 1200px;
  margin: 0 auto;
`;

const FeatureCard = styled.div<{ rotation: number }>`
  background: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 20px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  transform: rotate(${({ rotation }) => rotation}deg);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(255, 107, 107, 0.2);
  transition: all 0.3s ease;
  
  &:hover {
    transform: rotate(0deg) translateY(-10px);
    box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  }
`;

const FeatureTitle = styled.h3`
  font-family: ${({ theme }) => theme.fonts.playful};
  font-size: 1.5rem;
  color: #FF6B6B;
  margin-bottom: 15px;
`;

const StatusBar = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: rgba(255, 255, 255, 0.95);
  padding: 15px 25px;
  border-radius: 50px;
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
  border: 2px solid rgba(78, 205, 196, 0.3);
`;

export default function DadaistApp() {
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

  const handleViewDemo = () => {
    console.log('🎭 Demo dashboard coming soon!');
    alert('🎭 Dadaist dashboard coming soon! The chaos is being organized...');
  };

  return (
    <ThemeProvider theme={dadaistTheme}>
      <GlobalDadaistStyles />
      <DadaistContainer>
        <HeroSection>
          <ChaoticTitle
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1 }}
          >
            SmartHistory
          </ChaoticTitle>
          
          <SubTitle
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, delay: 0.3 }}
          >
            🎭 Track your activities through the lens of artistic chaos. 
            Dadaist productivity analytics that make data beautiful.
          </SubTitle>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
            style={{ display: 'flex', gap: '20px', justifyContent: 'center', flexWrap: 'wrap' }}
          >
            <ChaoticButton 
              variant="chaos" 
              size="large" 
              chaos={0.9}
              onClick={handleViewDemo}
            >
              🎨 Enter the Chaos
            </ChaoticButton>
            
            <ChaoticButton 
              variant="harmony" 
              size="large"
              chaos={0.5}
              onClick={handleConnectAPI}
            >
              🔗 Connect to Backend
            </ChaoticButton>
          </motion.div>
        </HeroSection>

        <FeatureGrid>
          <FeatureCard rotation={-2}>
            <div style={{ fontSize: '3rem', marginBottom: '20px' }}>📊</div>
            <FeatureTitle>Dadaist Data Viz</FeatureTitle>
            <p style={{ lineHeight: 1.6, marginBottom: '20px' }}>
              Transform your productivity data into artistic visualizations that challenge 
              conventional chart designs while revealing deep insights.
            </p>
            <ChaoticButton variant="primary" chaos={0.7}>
              Explore Charts
            </ChaoticButton>
          </FeatureCard>

          <FeatureCard rotation={1}>
            <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🎭</div>
            <FeatureTitle>Anti-Traditional UI</FeatureTitle>
            <p style={{ lineHeight: 1.6, marginBottom: '20px' }}>
              Experience an interface that breaks design rules purposefully, creating 
              delightful surprises while maintaining perfect usability.
            </p>
            <ChaoticButton variant="secondary" chaos={0.8}>
              See Interface
            </ChaoticButton>
          </FeatureCard>

          <FeatureCard rotation={-1}>
            <div style={{ fontSize: '3rem', marginBottom: '20px' }}>🚀</div>
            <FeatureTitle>Smart Processing</FeatureTitle>
            <p style={{ lineHeight: 1.6, marginBottom: '20px' }}>
              AI-powered activity analysis with artistic flair. Your Notion and Calendar 
              data becomes a canvas for productivity insights.
            </p>
            <ChaoticButton variant="chaos" chaos={0.9}>
              Start Processing
            </ChaoticButton>
          </FeatureCard>
        </FeatureGrid>

        <StatusBar>
          <span style={{ marginRight: '10px' }}>
            Backend: {apiStatus === 'checking' && '🔄'} 
                    {apiStatus === 'connected' && '✅'} 
                    {apiStatus === 'error' && '❌'}
          </span>
          <span>
            {apiStatus === 'checking' && 'Checking connection...'}
            {apiStatus === 'connected' && 'Connected & Ready'}
            {apiStatus === 'error' && 'Start backend server'}
          </span>
        </StatusBar>
      </DadaistContainer>
    </ThemeProvider>
  );
}