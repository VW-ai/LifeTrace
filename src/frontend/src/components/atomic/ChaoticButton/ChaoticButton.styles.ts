/**
 * ChaoticButton Styles
 * 
 * Styled components implementing Dadaist design principles while maintaining
 * accessibility and usability. Features unconventional color combinations,
 * playful typography mixing, and controlled chaos in positioning.
 */

import styled, { css, keyframes } from 'styled-components';
import type { StyledButtonProps } from './types';

// Dadaist color palettes
const dadaistColors = {
  primary: {
    base: '#FF6B6B',
    contrast: '#4ECDC4', 
    accent: '#45B7D1',
    glow: '#FF6B6B'
  },
  secondary: {
    base: '#6C5CE7',
    contrast: '#A0E7E5',
    accent: '#F9CA24', 
    glow: '#6C5CE7'
  },
  chaos: {
    base: 'linear-gradient(45deg, #FF6B6B, #4ECDC4, #F9CA24)',
    contrast: '#2C3E50',
    accent: '#FD79A8',
    glow: '#FF6B6B'
  },
  harmony: {
    base: '#45B7D1',
    contrast: '#2C3E50',
    accent: '#A0E7E5',
    glow: '#45B7D1'
  },
  destructive: {
    base: '#E74C3C',
    contrast: '#ECF0F1',
    accent: '#F39C12',
    glow: '#E74C3C'
  }
};

// Typography mixing for Dadaist effect
const getDadaistFont = (chaos: number) => {
  const fonts = [
    "'Inter', sans-serif",
    "'Playfair Display', serif", 
    "'JetBrains Mono', monospace",
    "'Fredoka One', cursive"
  ];
  
  if (chaos < 0.3) return fonts[0]; // Clean sans-serif for low chaos
  if (chaos < 0.6) return fonts[Math.floor(Math.random() * 2)]; // Mix of clean fonts
  return fonts[Math.floor(Math.random() * fonts.length)]; // Full chaos
};

// Size configurations with Dadaist scaling
const sizes = {
  small: {
    padding: '8px 16px',
    fontSize: '0.875rem',
    minHeight: '32px',
    chaos: 0.5
  },
  medium: {
    padding: '12px 24px', 
    fontSize: '1rem',
    minHeight: '44px',
    chaos: 0.8
  },
  large: {
    padding: '16px 32px',
    fontSize: '1.125rem', 
    minHeight: '56px',
    chaos: 1.0
  },
  hero: {
    padding: '24px 48px',
    fontSize: '1.5rem',
    minHeight: '72px',
    chaos: 1.2
  }
};

// Chaotic pulse animation
const chaoticPulse = keyframes`
  0% { transform: scale(1) rotate(0deg); }
  25% { transform: scale(1.02) rotate(1deg); }
  50% { transform: scale(1.05) rotate(-1deg); } 
  75% { transform: scale(1.02) rotate(0.5deg); }
  100% { transform: scale(1) rotate(0deg); }
`;

// Glitch effect for errors/disabled states
const glitchEffect = keyframes`
  0% { clip-path: inset(40% 0 61% 0); }
  20% { clip-path: inset(92% 0 1% 0); }
  40% { clip-path: inset(43% 0 1% 0); }
  60% { clip-path: inset(25% 0 58% 0); }
  80% { clip-path: inset(54% 0 7% 0); }
  100% { clip-path: inset(58% 0 43% 0); }
`;

export const StyledChaoticButton = styled.button<StyledButtonProps>`
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: ${props => 8 + Math.random() * 8 * props.chaos}px; // Slightly randomized corners
  cursor: pointer;
  font-family: ${props => getDadaistFont(props.chaos)};
  font-weight: 600;
  letter-spacing: ${props => props.chaos * 0.5}px;
  transition: all 0.3s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  overflow: hidden;
  user-select: none;
  outline: none;
  
  /* Size-based styles */
  ${props => css`
    padding: ${sizes[props.size].padding};
    font-size: ${sizes[props.size].fontSize};
    min-height: ${sizes[props.size].minHeight};
  `}
  
  /* Variant-based colors and effects */
  ${props => {
    const colors = dadaistColors[props.variant];
    return css`
      background: ${colors.base};
      color: ${colors.contrast};
      box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
      
      &:hover:not(:disabled) {
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
        transform: translateY(-2px);
      }
      
      &:active:not(:disabled) {
        transform: translateY(0px) scale(0.98);
      }
      
      /* Focus styles for accessibility */
      &:focus-visible {
        outline: 2px solid ${colors.accent};
        outline-offset: 2px;
      }
    `;
  }}
  
  /* Loading state */
  ${props => props.loading && css`
    animation: ${chaoticPulse} 2s ease-in-out infinite;
    cursor: wait;
  `}
  
  /* Disabled state with glitch effect */
  ${props => props.disabled && css`
    opacity: 0.6;
    cursor: not-allowed;
    filter: grayscale(0.7);
    
    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: inherit;
      animation: ${glitchEffect} 1s infinite;
    }
  `}
  
  /* Chaos-based random styling */
  ${props => props.chaos > 0.7 && css`
    &:hover:not(:disabled) {
      animation: ${chaoticPulse} 0.6s ease-in-out;
    }
  `}
`;

export const ButtonContent = styled.span`
  position: relative;
  z-index: 2;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
`;

export const ChaoticGlow = styled.div<{ variant: string }>`
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: ${props => `linear-gradient(45deg, ${dadaistColors[props.variant as keyof typeof dadaistColors]?.glow})`};
  border-radius: inherit;
  opacity: 0;
  z-index: 1;
  filter: blur(8px);
`;