import 'styled-components';

declare module 'styled-components' {
  export interface DefaultTheme {
    colors: {
      primary: string;
      secondary?: string;
      accent?: string;
      text: string;
      background?: string;
      chaos?: string[];
      // Professional theme colors (optional for Dadaist compatibility)
      primaryHover?: string;
      primaryLight?: string;
      secondaryHover?: string;
      secondaryLight?: string;
      accentWarning?: string;
      accentDanger?: string;
      accentInfo?: string;
      textSecondary?: string;
      textMuted?: string;
      backgroundSecondary?: string;
      border?: string;
      borderLight?: string;
      dataViz?: string[];
    };
    fonts: {
      primary: string;
      display?: string;
      mono?: string;
      playful?: string;
    };
    // Optional professional theme properties
    typography?: {
      xs?: string;
      sm?: string;
      base?: string;
      lg?: string;
      xl?: string;
      '2xl'?: string;
      '3xl'?: string;
      '4xl'?: string;
      '5xl'?: string;
      light?: number;
      normal?: number;
      medium?: number;
      semibold?: number;
      bold?: number;
    };
    spacing?: Record<string, string>;
    borderRadius?: Record<string, string>;
    shadows?: Record<string, string>;
    animation?: {
      transition?: Record<string, string>;
      easing?: Record<string, string>;
    };
    breakpoints?: Record<string, string>;
    chaos?: number;
  }
}