/**
 * Professional Theme System for SmartHistory
 * Clean, modern design focused on productivity and data visualization
 */

export const professionalTheme = {
  colors: {
    // Primary Brand Colors
    primary: '#2563EB', // Professional blue
    primaryHover: '#1D4ED8',
    primaryLight: '#DBEAFE',
    
    // Secondary Colors
    secondary: '#64748B', // Neutral gray-blue
    secondaryHover: '#475569',
    secondaryLight: '#F1F5F9',
    
    // Accent Colors for Data Visualization
    accent: '#10B981', // Success green
    accentWarning: '#F59E0B', // Warning amber
    accentDanger: '#EF4444', // Error red
    accentInfo: '#06B6D4', // Info cyan
    
    // Neutral Palette
    text: '#1E293B',
    textSecondary: '#64748B',
    textMuted: '#94A3B8',
    background: '#FFFFFF',
    backgroundSecondary: '#F8FAFC',
    border: '#E2E8F0',
    borderLight: '#F1F5F9',
    
    // Data Visualization Colors (for charts/graphs)
    dataViz: [
      '#2563EB', // Blue
      '#10B981', // Green  
      '#F59E0B', // Amber
      '#EF4444', // Red
      '#8B5CF6', // Purple
      '#06B6D4', // Cyan
      '#F97316', // Orange
      '#EC4899', // Pink
    ]
  },
  
  fonts: {
    primary: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    mono: "'JetBrains Mono', 'Fira Code', 'Monaco', monospace",
    display: "'Inter', sans-serif", // Consistent with primary for professional look
    playful: "'Inter', sans-serif", // For compatibility with legacy themes
  },
  
  typography: {
    // Font sizes using a consistent scale
    xs: '0.75rem',    // 12px
    sm: '0.875rem',   // 14px  
    base: '1rem',     // 16px
    lg: '1.125rem',   // 18px
    xl: '1.25rem',    // 20px
    '2xl': '1.5rem',  // 24px
    '3xl': '1.875rem', // 30px
    '4xl': '2.25rem', // 36px
    '5xl': '3rem',    // 48px
    
    // Font weights
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },
  
  spacing: {
    // Consistent spacing scale (4px base)
    0: '0',
    1: '0.25rem',   // 4px
    2: '0.5rem',    // 8px
    3: '0.75rem',   // 12px
    4: '1rem',      // 16px
    5: '1.25rem',   // 20px
    6: '1.5rem',    // 24px
    8: '2rem',      // 32px
    10: '2.5rem',   // 40px
    12: '3rem',     // 48px
    16: '4rem',     // 64px
    20: '5rem',     // 80px
    24: '6rem',     // 96px
  },
  
  borderRadius: {
    none: '0',
    sm: '0.125rem',   // 2px
    base: '0.25rem',  // 4px
    md: '0.375rem',   // 6px
    lg: '0.5rem',     // 8px
    xl: '0.75rem',    // 12px
    '2xl': '1rem',    // 16px
    full: '9999px',   // Full radius
  },
  
  shadows: {
    xs: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    sm: '0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1)',
    base: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    md: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    lg: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
    xl: '0 25px 50px -12px rgb(0 0 0 / 0.25)',
  },
  
  animation: {
    // Professional, subtle animations
    transition: {
      fast: '150ms ease-in-out',
      base: '200ms ease-in-out', 
      slow: '300ms ease-in-out',
    },
    
    // Easing functions
    easing: {
      default: 'cubic-bezier(0.4, 0, 0.2, 1)',
      in: 'cubic-bezier(0.4, 0, 1, 1)',
      out: 'cubic-bezier(0, 0, 0.2, 1)',
      inOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    }
  },
  
  // Breakpoints for responsive design
  breakpoints: {
    sm: '640px',
    md: '768px', 
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  // Compatibility with legacy Dadaist theme
  chaos: 0 // Professional design has zero chaos
};

// Type definition for TypeScript
export type ProfessionalTheme = typeof professionalTheme;