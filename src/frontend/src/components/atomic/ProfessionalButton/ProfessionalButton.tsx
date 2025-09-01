/**
 * Professional Button Component
 * Clean, accessible button with consistent styling
 */

import styled from 'styled-components';
import type { ButtonHTMLAttributes } from 'react';

type ButtonVariant = 'primary' | 'secondary' | 'outline' | 'ghost' | 'danger';
type ButtonSize = 'sm' | 'md' | 'lg';

interface ProfessionalButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  loading?: boolean;
}

const getButtonColors = (variant: ButtonVariant) => {
  switch (variant) {
    case 'primary':
      return `
        background-color: #2563EB;
        color: white;
        border: 1px solid #2563EB;
        
        &:hover:not(:disabled) {
          background-color: #1D4ED8;
          border-color: #1D4ED8;
        }
        
        &:active:not(:disabled) {
          background-color: #1E40AF;
          border-color: #1E40AF;
        }
      `;
    case 'secondary':
      return `
        background-color: #64748B;
        color: white;
        border: 1px solid #64748B;
        
        &:hover:not(:disabled) {
          background-color: #475569;
          border-color: #475569;
        }
        
        &:active:not(:disabled) {
          background-color: #334155;
          border-color: #334155;
        }
      `;
    case 'outline':
      return `
        background-color: transparent;
        color: #2563EB;
        border: 1px solid #E2E8F0;
        
        &:hover:not(:disabled) {
          background-color: #F8FAFC;
          border-color: #2563EB;
        }
        
        &:active:not(:disabled) {
          background-color: #F1F5F9;
        }
      `;
    case 'ghost':
      return `
        background-color: transparent;
        color: #64748B;
        border: 1px solid transparent;
        
        &:hover:not(:disabled) {
          background-color: #F8FAFC;
          color: #1E293B;
        }
        
        &:active:not(:disabled) {
          background-color: #F1F5F9;
        }
      `;
    case 'danger':
      return `
        background-color: #EF4444;
        color: white;
        border: 1px solid #EF4444;
        
        &:hover:not(:disabled) {
          background-color: #DC2626;
          border-color: #DC2626;
        }
        
        &:active:not(:disabled) {
          background-color: #B91C1C;
          border-color: #B91C1C;
        }
      `;
    default:
      return '';
  }
};

const getButtonSize = (size: ButtonSize) => {
  switch (size) {
    case 'sm':
      return `
        padding: 0.5rem 0.75rem;
        font-size: 0.875rem;
        line-height: 1.25rem;
      `;
    case 'md':
      return `
        padding: 0.625rem 1rem;
        font-size: 0.875rem;
        line-height: 1.25rem;
      `;
    case 'lg':
      return `
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        line-height: 1.5rem;
      `;
    default:
      return '';
  }
};

const StyledButton = styled.button.withConfig({
  shouldForwardProp: (prop) => !['variant', 'size', 'fullWidth', 'loading'].includes(prop),
})<ProfessionalButtonProps>`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-family: 'Inter', sans-serif;
  font-weight: 500;
  border-radius: 0.375rem;
  transition: all 150ms ease-in-out;
  cursor: pointer;
  outline: none;
  position: relative;
  width: ${({ fullWidth }) => fullWidth ? '100%' : 'auto'};
  
  ${({ variant = 'primary' }) => getButtonColors(variant)}
  ${({ size = 'md' }) => getButtonSize(size)}
  
  &:focus-visible {
    outline: 2px solid #2563EB;
    outline-offset: 2px;
  }
  
  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
  
  ${({ loading }) => loading && `
    color: transparent;
    
    &::after {
      content: '';
      position: absolute;
      width: 1rem;
      height: 1rem;
      border: 2px solid currentColor;
      border-top-color: transparent;
      border-radius: 50%;
      animation: spin 1s linear infinite;
      color: white;
    }
    
    @keyframes spin {
      to {
        transform: rotate(360deg);
      }
    }
  `}
`;

export const ProfessionalButton: React.FC<ProfessionalButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  disabled,
  ...props
}) => {
  return (
    <StyledButton
      variant={variant}
      size={size}
      fullWidth={fullWidth}
      loading={loading}
      disabled={disabled || loading}
      {...props}
    >
      {children}
    </StyledButton>
  );
};