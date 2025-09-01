/**
 * ChaoticButton Types
 * 
 * TypeScript interfaces for the ChaoticButton component following
 * REGULATION.md principles of proper type safety and documentation.
 */

export type ChaoticButtonVariant = 'primary' | 'secondary' | 'chaos' | 'harmony' | 'destructive';
export type ChaoticButtonSize = 'small' | 'medium' | 'large' | 'hero';

export interface ChaoticButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  /**
   * Button content - text, icons, or other React elements
   */
  children: React.ReactNode;
  
  /**
   * Visual variant controlling colors and styling approach
   * @default 'primary'
   */
  variant?: ChaoticButtonVariant;
  
  /**
   * Button size affecting padding, font size, and chaos intensity
   * @default 'medium'
   */
  size?: ChaoticButtonSize;
  
  /**
   * Chaos factor controlling randomness intensity
   * 0 = perfectly orderly, 1 = maximum Dadaist chaos
   * @default 0.8
   */
  chaos?: number;
  
  /**
   * Loading state with artistic loading indicator
   * @default false
   */
  loading?: boolean;
  
  /**
   * Disabled state with appropriate visual feedback
   * @default false
   */
  disabled?: boolean;
  
  /**
   * Click handler for button interactions
   */
  onClick?: (event: React.MouseEvent<HTMLButtonElement>) => void;
}

export interface StyledButtonProps {
  variant: ChaoticButtonVariant;
  size: ChaoticButtonSize;
  chaos: number;
  loading: boolean;
  disabled: boolean;
}