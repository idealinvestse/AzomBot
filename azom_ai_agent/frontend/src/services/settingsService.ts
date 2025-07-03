export interface AppSettings {
  llmBackend: 'openwebui' | 'groq';
  openwebuiUrl: string;
  openwebuiApiToken: string;
  groqApiKey: string;
  targetModel: string;
  pipelineServerUrl: string;
  theme: 'light' | 'dark' | 'system';
}

const SETTINGS_KEY = 'app_settings';

export const defaultSettings: AppSettings = {
  llmBackend: 'openwebui',
  openwebuiUrl: 'http://192.168.50.164:3000',
  openwebuiApiToken: '',
  groqApiKey: '',
  targetModel: 'azom-se-general',
  pipelineServerUrl: 'http://localhost:8001',
  theme: 'system',
};

export function getSettings(): AppSettings {
  try {
    const savedSettings = localStorage.getItem(SETTINGS_KEY);
    if (savedSettings) {
      // Sammanfoga sparade inställningar med standardvärden för att säkerställa att nya fält inkluderas
      return { ...defaultSettings, ...JSON.parse(savedSettings) };
    }
  } catch (error) {
    console.error('Kunde inte läsa inställningar från localStorage:', error);
  }
  return defaultSettings;
}

export function saveSettings(settings: AppSettings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
  } catch (error) {
    console.error('Kunde inte spara inställningar till localStorage:', error);
  }
}
