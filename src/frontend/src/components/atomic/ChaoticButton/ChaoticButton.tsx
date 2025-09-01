/**
 * ChaoticButton - A Dadaist-inspired button component
 * 
 * Following REGULATION.md atomic principles, this component serves a single purpose:
 * providing interactive buttons with playful, artistic styling that challenges
 * traditional UI expectations while maintaining full accessibility.
 * 
 * Dadaist Features:
 * - Randomized rotation and positioning within bounds
 * - Unexpected color combinations that shift on interaction
 * - Hover animations that "explode" the button slightly
 * - Typography that mixes fonts for visual interest
 */

import React, { useState, useCallback } from 'react';
import { motion } from 'framer-motion';
import { StyledChaoticButton, ButtonContent, ChaoticGlow } from './ChaoticButton.styles';
import type { ChaoticButtonProps } from './types';

export const ChaoticButton: React.FC<ChaoticButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  chaos = 0.8,
  onClick,
  disabled = false,
  loading = false,
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [randomRotation] = useState(() => Math.random() * 4 - 2); // -2 to +2 degrees
  const [randomOffset] = useState(() => ({
    x: Math.random() * 4 - 2, // -2 to +2 pixels
    y: Math.random() * 4 - 2
  }));

  const handleClick = useCallback((event: React.MouseEvent<HTMLButtonElement>) => {
    if (disabled || loading) return;
    
    // Add some chaos to the click event
    const button = event.currentTarget;
    button.style.transform = `scale(0.95) rotate(${randomRotation + (Math.random() * 10 - 5)}deg)`;
    
    setTimeout(() => {
      button.style.transform = `scale(1) rotate(${randomRotation}deg)`;
    }, 150);
    
    onClick?.(event);
  }, [disabled, loading, onClick, randomRotation]);

  const buttonVariants = {
    idle: {
      scale: 1,
      rotate: randomRotation * chaos,
      x: randomOffset.x * chaos,
      y: randomOffset.y * chaos,
    },
    hover: {
      scale: 1.05,
      rotate: (randomRotation + Math.random() * 6 - 3) * chaos,
      x: (randomOffset.x + Math.random() * 4 - 2) * chaos,
      y: (randomOffset.y + Math.random() * 4 - 2) * chaos,
      transition: {
        type: "spring" as const,
        stiffness: 400,
        damping: 17,
      }
    },
    tap: {
      scale: 0.95,
      transition: {
        type: "spring" as const,
        stiffness: 500,
        damping: 30,
      }
    }
  };

  const glowVariants = {
    idle: { opacity: 0 },
    hover: { 
      opacity: 0.6,
      transition: { duration: 0.3 }
    }
  };

  return (
    <motion.div
      variants={buttonVariants}
      initial="idle"
      animate="idle"
      whileHover="hover"
      whileTap="tap"
      style={{ display: 'inline-block' }}
    >
      <StyledChaoticButton
        variant={variant}
        size={size}
        chaos={chaos}
        disabled={disabled}
        loading={loading}
        onClick={handleClick}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        {...props}
      >
        <motion.div
          variants={glowVariants}
          initial="idle"
          animate={isHovered ? "hover" : "idle"}
        >
          <ChaoticGlow variant={variant} />
        </motion.div>
        
        <ButtonContent>
          {loading ? (
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
              style={{ display: 'inline-block' }}
            >
              🎭
            </motion.div>
          ) : (
            children
          )}
        </ButtonContent>
      </StyledChaoticButton>
    </motion.div>
  );
};