/**
 * SmartHistory App - Dadaist Activity Tracking Dashboard
 * 
 * Main application component implementing Dadaist design principles while
 * providing full functionality for activity tracking and productivity insights.
 * 
 * Following REGULATION.md principles:
 * - Single responsibility: Main app orchestration
 * - Atomic structure: Composed of smaller, focused components
 * - Co-located documentation: This file serves as app-level documentation
 */

import { useState, useEffect } from 'react';
import styled, { ThemeProvider, createGlobalStyle } from 'styled-components';
import { motion, AnimatePresence } from 'framer-motion';
import { ChaoticButton } from './components/atomic/ChaoticButton';

// Dadaist Global Styles
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

  /* Dadaist scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }
  
  ::-webkit-scrollbar-track {
    background: rgba(255, 107, 107, 0.1);
  }
  
  ::-webkit-scrollbar-thumb {
    background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
    border-radius: 4px;
  }
`;

// Dadaist theme
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

// Styled components with Dadaist principles
const DadaistContainer = styled.div`
  min-height: 100vh;
  padding: 20px;
  position: relative;
  overflow: hidden;
`;

const FloatingBackground = styled(motion.div)`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  pointer-events: none;
  z-index: -1;
`;

const ChaoticShape = styled(motion.div)<{ color: string; size: number }>`
  position: absolute;
  width: ${({ size }) => size}px;
  height: ${({ size }) => size}px;
  background: ${({ color }) => color};
  border-radius: ${() => Math.random() * 50}%;
  opacity: 0.1;
`;

const HeroSection = styled(motion.div)`
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
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
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

const FeatureCard = styled(motion.div)<{ rotation: number }>`
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

const FeatureIcon = styled.div`
  font-size: 3rem;
  margin-bottom: 20px;
`;

const FeatureTitle = styled.h3`
  font-family: ${({ theme }) => theme.fonts.playful};
  font-size: 1.5rem;
  color: #FF6B6B;
  margin-bottom: 15px;
`;

const FeatureDescription = styled.p`
  font-family: ${({ theme }) => theme.fonts.primary};
  line-height: 1.6;
  color: #2C3E50;
  margin-bottom: 20px;
`;

const StatusBar = styled(motion.div)`
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

export default function App() {
  const [apiStatus, setApiStatus] = useState<'checking' | 'connected' | 'error'>('checking');
  const [backgroundShapes, setBackgroundShapes] = useState<Array<{id: number, x: number, y: number, color: string, size: number}>>([]);

  // Generate chaotic background shapes
  useEffect(() => {
    const shapes = Array.from({ length: 15 }, (_, i) => ({
      id: i,
      x: Math.random() * window.innerWidth,
      y: Math.random() * window.innerHeight, 
      color: dadaistTheme.colors.chaos[Math.floor(Math.random() * dadaistTheme.colors.chaos.length)],
      size: 50 + Math.random() * 150
    }));
    setBackgroundShapes(shapes);
  }, []);

  // Check API connection
  useEffect(() => {
    const checkAPI = async () => {
      try {
        const response = await fetch('http://localhost:8000/health');
        if (response.ok) {
          setApiStatus('connected');
        } else {
          setApiStatus('error');
        }
      } catch (error) {
        setApiStatus('error');
      }
    };

    checkAPI();
    const interval = setInterval(checkAPI, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const handleConnectAPI = () => {
    window.open('http://localhost:8000/docs', '_blank');
  };

  const handleViewDemo = () => {
    // TODO: Navigate to demo dashboard
    console.log('🎭 Demo dashboard coming soon!');
  };

  return (
    <ThemeProvider theme={dadaistTheme}>
      <GlobalDadaistStyles />
      <DadaistContainer>
        {/* Chaotic floating background */}
        <FloatingBackground>
          <AnimatePresence>
            {backgroundShapes.map((shape) => (
              <ChaoticShape
                key={shape.id}
                color={shape.color}
                size={shape.size}
                initial={{ 
                  x: shape.x, 
                  y: shape.y, 
                  opacity: 0,
                  rotate: 0 
                }}
                animate={{ 
                  x: shape.x + Math.sin(Date.now() * 0.001) * 50,
                  y: shape.y + Math.cos(Date.now() * 0.001) * 30,
                  opacity: 0.1,
                  rotate: 360
                }}
                transition={{
                  duration: 20 + Math.random() * 10,
                  repeat: Infinity,
                  ease: "linear"
                }}
              />
            ))}
          </AnimatePresence>
        </FloatingBackground>

        {/* Hero Section */}
        <HeroSection>
          <ChaoticTitle
            initial={{ opacity: 0, y: -50, rotate: -10 }}
            animate={{ opacity: 1, y: 0, rotate: -2 }}
            transition={{ duration: 1, type: "spring", stiffness: 100 }}
          >
            SmartHistory
          </ChaoticTitle>
          
          <SubTitle
            initial={{ opacity: 0, y: 30, rotate: 0 }}
            animate={{ opacity: 1, y: 0, rotate: 1 }}
            transition={{ duration: 1, delay: 0.3, type: "spring" }}
          >
            🎭 Track your activities through the lens of artistic chaos. 
            Dadaist productivity analytics that make data beautiful.
          </SubTitle>

          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.6 }}
          >
            <ChaoticButton 
              variant="chaos" 
              size="large" 
              chaos={0.9}
              onClick={handleViewDemo}
              style={{ marginRight: '20px' }}
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

        {/* Features Grid */}
        <FeatureGrid>
          <FeatureCard 
            rotation={-2}
            initial={{ opacity: 0, y: 50, rotate: -2 }}
            animate={{ opacity: 1, y: 0, rotate: -2 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <FeatureIcon>📊</FeatureIcon>
            <FeatureTitle>Dadaist Data Viz</FeatureTitle>
            <FeatureDescription>
              Transform your productivity data into artistic visualizations that challenge 
              conventional chart designs while revealing deep insights.
            </FeatureDescription>
            <ChaoticButton variant="primary" chaos={0.7}>
              Explore Charts
            </ChaoticButton>
          </FeatureCard>

          <FeatureCard 
            rotation={1}
            initial={{ opacity: 0, y: 50, rotate: 1 }}
            animate={{ opacity: 1, y: 0, rotate: 1 }}
            transition={{ duration: 0.8, delay: 1.0 }}
          >
            <FeatureIcon>🎭</FeatureIcon>
            <FeatureTitle>Anti-Traditional UI</FeatureTitle>
            <FeatureDescription>
              Experience an interface that breaks design rules purposefully, creating 
              delightful surprises while maintaining perfect usability.
            </FeatureDescription>
            <ChaoticButton variant="secondary" chaos={0.8}>
              See Interface
            </ChaoticButton>
          </FeatureCard>

          <FeatureCard 
            rotation={-1}
            initial={{ opacity: 0, y: 50, rotate: -1 }}
            animate={{ opacity: 1, y: 0, rotate: -1 }}
            transition={{ duration: 0.8, delay: 1.2 }}
          >
            <FeatureIcon>🚀</FeatureIcon>
            <FeatureTitle>Smart Processing</FeatureTitle>
            <FeatureDescription>
              AI-powered activity analysis with artistic flair. Your Notion and Calendar 
              data becomes a canvas for productivity insights.
            </FeatureDescription>
            <ChaoticButton variant="chaos" chaos={0.9}>
              Start Processing
            </ChaoticButton>
          </FeatureCard>
        </FeatureGrid>

        {/* API Status Bar */}
        <StatusBar
          initial={{ opacity: 0, x: 100 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.8, delay: 1.5 }}
        >
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
