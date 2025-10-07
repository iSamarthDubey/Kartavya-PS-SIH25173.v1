import { useState, useEffect } from 'react';

export type Mode = 'demo' | 'development' | 'production';
export type SiemPlatform = 'elasticsearch' | 'wazuh' | 'mock';

interface EnvironmentState {
  mode: Mode;
  siemPlatform: SiemPlatform;
}

export const useEnvironment = () => {
  const [mode, setModeState] = useState<Mode>(() => {
    const stored = localStorage.getItem('app_mode');
    return (stored as Mode) || 'demo';
  });

  const [siemPlatform, setSiemPlatformState] = useState<SiemPlatform>(() => {
    const stored = localStorage.getItem('siem_platform');
    return (stored as SiemPlatform) || 'mock';
  });

  const setMode = (newMode: Mode) => {
    setModeState(newMode);
    localStorage.setItem('app_mode', newMode);
  };

  const setSiemPlatform = (newPlatform: SiemPlatform) => {
    setSiemPlatformState(newPlatform);
    localStorage.setItem('siem_platform', newPlatform);
  };

  useEffect(() => {
    // Sync with localStorage on mount
    const storedMode = localStorage.getItem('app_mode') as Mode;
    const storedPlatform = localStorage.getItem('siem_platform') as SiemPlatform;
    
    if (storedMode && storedMode !== mode) {
      setModeState(storedMode);
    }
    
    if (storedPlatform && storedPlatform !== siemPlatform) {
      setSiemPlatformState(storedPlatform);
    }
  }, []);

  return {
    mode,
    siemPlatform,
    setMode,
    setSiemPlatform,
    isDemo: mode === 'demo',
    isProduction: mode === 'production',
    isDevelopment: mode === 'development'
  };
};
