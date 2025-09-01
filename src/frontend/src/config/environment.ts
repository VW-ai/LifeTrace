/**
 * Environment-based Configuration for Frontend
 * Supports different deployment scenarios with fallback values
 */

interface EnvironmentConfig {
  API_BASE_URL: string;
  ENVIRONMENT: 'development' | 'staging' | 'production';
  DEBUG: boolean;
  ENABLE_ANALYTICS: boolean;
  WEBSOCKET_URL?: string;
  SENTRY_DSN?: string;
  GOOGLE_ANALYTICS_ID?: string;
}

// Environment detection
const getEnvironment = (): 'development' | 'staging' | 'production' => {
  // Check for explicit environment variable
  const viteEnv = import.meta.env?.VITE_ENVIRONMENT as string | undefined;
  if (viteEnv) {
    return viteEnv as any;
  }
  
  // Detect based on hostname (only if window is available)
  if (typeof window !== 'undefined') {
    const hostname = window.location.hostname;
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      return 'development';
    } else if (hostname.includes('staging') || hostname.includes('dev')) {
      return 'staging';
    } else {
      return 'production';
    }
  }
  
  // Fallback for SSR or other environments
  return 'development';
};

// Dynamic API URL detection
const getApiBaseUrl = (): string => {
  // Use environment variable if provided
  const viteApiUrl = import.meta.env?.VITE_API_BASE_URL as string | undefined;
  if (viteApiUrl) {
    return viteApiUrl;
  }
  
  // Dynamic detection based on current hostname (only if window is available)
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol;
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
      // Development: assume backend on port 8000
      return `${protocol}//${hostname}:8000/api/v1`;
    } else {
      // Production: assume API is on same domain with /api prefix
      return `${protocol}//${hostname}/api/v1`;
    }
  }
  
  // Fallback for SSR or other environments
  return 'http://localhost:8000/api/v1';
};

// Environment-specific configurations
const environment = getEnvironment();

const configs: Record<string, EnvironmentConfig> = {
  development: {
    API_BASE_URL: getApiBaseUrl(),
    ENVIRONMENT: 'development',
    DEBUG: true,
    ENABLE_ANALYTICS: false,
    WEBSOCKET_URL: `ws://localhost:8000/ws`,
  },
  
  staging: {
    API_BASE_URL: getApiBaseUrl(),
    ENVIRONMENT: 'staging',
    DEBUG: true,
    ENABLE_ANALYTICS: false,
    WEBSOCKET_URL: typeof window !== 'undefined' ? `wss://${window.location.hostname}/ws` : undefined,
    SENTRY_DSN: import.meta.env?.VITE_SENTRY_DSN as string | undefined,
  },
  
  production: {
    API_BASE_URL: getApiBaseUrl(),
    ENVIRONMENT: 'production',
    DEBUG: false,
    ENABLE_ANALYTICS: true,
    WEBSOCKET_URL: typeof window !== 'undefined' ? `wss://${window.location.hostname}/ws` : undefined,
    SENTRY_DSN: import.meta.env?.VITE_SENTRY_DSN as string | undefined,
    GOOGLE_ANALYTICS_ID: import.meta.env?.VITE_GOOGLE_ANALYTICS_ID as string | undefined,
  },
};

// Export the current environment configuration
export const config = configs[environment];

// Export individual values for convenience
export const {
  API_BASE_URL,
  ENVIRONMENT,
  DEBUG,
  ENABLE_ANALYTICS,
  WEBSOCKET_URL,
  SENTRY_DSN,
  GOOGLE_ANALYTICS_ID,
} = config;

// Development helpers
if (DEBUG) {
  console.log('🔧 SmartHistory Frontend Configuration:', config);
}

export default config;