/**
 * Environment Configuration for SIEM NLP Assistant
 * Handles demo/production mode switching and environment variables
 */

export type EnvironmentMode = 'demo' | 'production' | 'development';
export type SIEMPlatform = 'elasticsearch' | 'wazuh' | 'mock';

interface EnvironmentConfig {
  mode: EnvironmentMode;
  siemPlatform: SIEMPlatform;
  apiBaseUrl: string;
  enableDemoData: boolean;
  enableAnalytics: boolean;
  features: {
    realTimeUpdates: boolean;
    reportGeneration: boolean;
    multiSiemSupport: boolean;
    advancedNLP: boolean;
  };
  ui: {
    showPoweredBy: boolean;
    theme: 'space' | 'cyber' | 'default';
    animations: boolean;
  };
}

// Default configuration
const defaultConfig: EnvironmentConfig = {
  mode: 'development',
  siemPlatform: 'mock',
  apiBaseUrl: 'http://localhost:8000',
  enableDemoData: true,
  enableAnalytics: false,
  features: {
    realTimeUpdates: true,
    reportGeneration: true,
    multiSiemSupport: true,
    advancedNLP: true,
  },
  ui: {
    showPoweredBy: true,
    theme: 'space',
    animations: true,
  },
};

// Environment-specific overrides
const environmentConfigs: Record<string, Partial<EnvironmentConfig>> = {
  production: {
    mode: 'production',
    enableDemoData: false,
    enableAnalytics: true,
    ui: {
      showPoweredBy: false,
      theme: 'space',
      animations: false, // Disable for performance
    },
  },
  demo: {
    mode: 'demo',
    siemPlatform: 'mock',
    enableDemoData: true,
    enableAnalytics: false,
    features: {
      realTimeUpdates: true,
      reportGeneration: true,
      multiSiemSupport: false, // Simplified for demo
      advancedNLP: true,
    },
    ui: {
      showPoweredBy: true,
      theme: 'cyber',
      animations: true,
    },
  },
  development: {
    mode: 'development',
    enableDemoData: true,
    enableAnalytics: false,
  },
};

/**
 * Get environment mode from various sources
 */
function getEnvironmentMode(): EnvironmentMode {
  // 1. Check URL parameters (highest priority)
  const urlParams = new URLSearchParams(window.location.search);
  const urlMode = urlParams.get('mode') as EnvironmentMode;
  if (urlMode && ['demo', 'production', 'development'].includes(urlMode)) {
    return urlMode;
  }

  // 2. Check environment variables
  const envMode = import.meta.env.VITE_APP_MODE as EnvironmentMode;
  if (envMode && ['demo', 'production', 'development'].includes(envMode)) {
    return envMode;
  }

  // 3. Check if running in production build
  if (import.meta.env.PROD) {
    return 'production';
  }

  // 4. Default to development
  return 'development';
}

/**
 * Get SIEM platform from various sources
 */
function getSiemPlatform(): SIEMPlatform {
  // 1. URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const urlSiem = urlParams.get('siem') as SIEMPlatform;
  if (urlSiem && ['elasticsearch', 'wazuh', 'mock'].includes(urlSiem)) {
    return urlSiem;
  }

  // 2. Environment variables
  const envSiem = import.meta.env.VITE_SIEM_PLATFORM as SIEMPlatform;
  if (envSiem && ['elasticsearch', 'wazuh', 'mock'].includes(envSiem)) {
    return envSiem;
  }

  // 3. Local storage (user preference)
  const storedSiem = localStorage.getItem('siem-platform') as SIEMPlatform;
  if (storedSiem && ['elasticsearch', 'wazuh', 'mock'].includes(storedSiem)) {
    return storedSiem;
  }

  // 4. Default based on mode
  const mode = getEnvironmentMode();
  return mode === 'demo' ? 'mock' : 'elasticsearch';
}

/**
 * Get API base URL
 */
function getApiBaseUrl(): string {
  // 1. URL parameters
  const urlParams = new URLSearchParams(window.location.search);
  const urlApi = urlParams.get('api');
  if (urlApi) {
    return urlApi;
  }

  // 2. Environment variables
  const envApi = import.meta.env.VITE_API_BASE;
  if (envApi) {
    return envApi;
  }

  // 3. Default
  return 'http://localhost:8000';
}

/**
 * Build final configuration
 */
function buildConfig(): EnvironmentConfig {
  const mode = getEnvironmentMode();
  const siemPlatform = getSiemPlatform();
  const apiBaseUrl = getApiBaseUrl();

  // Start with default config
  let config = { ...defaultConfig };

  // Apply environment-specific overrides
  if (environmentConfigs[mode]) {
    config = {
      ...config,
      ...environmentConfigs[mode],
      // Merge nested objects properly
      features: {
        ...config.features,
        ...environmentConfigs[mode].features,
      },
      ui: {
        ...config.ui,
        ...environmentConfigs[mode].ui,
      },
    };
  }

  // Apply runtime values
  config.mode = mode;
  config.siemPlatform = siemPlatform;
  config.apiBaseUrl = apiBaseUrl;

  return config;
}

// Create and export the configuration
export const config = buildConfig();

// Export utility functions
export const isDemo = () => config.mode === 'demo';
export const isProduction = () => config.mode === 'production';
export const isDevelopment = () => config.mode === 'development';

export const isMockSiem = () => config.siemPlatform === 'mock';
export const isElasticsearch = () => config.siemPlatform === 'elasticsearch';
export const isWazuh = () => config.siemPlatform === 'wazuh';

/**
 * Update SIEM platform (saves to localStorage)
 */
export function setSiemPlatform(platform: SIEMPlatform) {
  localStorage.setItem('siem-platform', platform);
  // Reload to apply changes
  window.location.reload();
}

/**
 * Get display-friendly labels
 */
export const labels = {
  mode: {
    demo: 'Demo Mode',
    production: 'Production',
    development: 'Development',
  },
  siem: {
    elasticsearch: 'Elasticsearch',
    wazuh: 'Wazuh SIEM',
    mock: 'Mock Data',
  },
};

/**
 * Demo data notice component props
 */
export interface DemoNoticeProps {
  show: boolean;
  onDismiss: () => void;
}

// Debug logging (only in development)
if (isDevelopment()) {
  console.log('[Environment Config]', {
    mode: config.mode,
    siemPlatform: config.siemPlatform,
    apiBaseUrl: config.apiBaseUrl,
    enableDemoData: config.enableDemoData,
  });
}

export default config;
