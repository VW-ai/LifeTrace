/**
 * SmartHistory Dashboard App
 * Full-featured dashboard with real backend integration
 */

import { ThemeProvider, createGlobalStyle } from 'styled-components';
import { professionalTheme } from './styles/professional-theme';
import { Dashboard } from './components/dashboard/Dashboard';

const GlobalStyles = createGlobalStyle`

  * {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }

  html, body {
    font-family: ${professionalTheme.fonts.primary};
    background-color: ${professionalTheme.colors.backgroundSecondary};
    color: ${professionalTheme.colors.text};
    line-height: 1.6;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
    width: 100%;
    height: 100%;
    overflow-x: hidden;
  }
  
  #root {
    width: 100%;
    min-height: 100vh;
  }

  button {
    font-family: inherit;
  }

  /* Custom scrollbar */
  ::-webkit-scrollbar {
    width: 8px;
  }

  ::-webkit-scrollbar-track {
    background: ${professionalTheme.colors.borderLight};
  }

  ::-webkit-scrollbar-thumb {
    background: ${professionalTheme.colors.border};
    border-radius: 4px;
  }

  ::-webkit-scrollbar-thumb:hover {
    background: ${professionalTheme.colors.textSecondary};
  }
`;

export default function DashboardApp() {
  return (
    <ThemeProvider theme={professionalTheme}>
      <GlobalStyles />
      <Dashboard />
    </ThemeProvider>
  );
}