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

const API_BASE_URL = 'http://localhost:8000';

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

export async function saveSettingsToBackend(settings: AppSettings): Promise<void> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/v1/settings`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(settings),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred.' }));
      console.error('Failed to save settings to backend:', errorData);
      throw new Error(`Failed to save settings: ${errorData.detail}`);
    }
    console.log('Settings successfully saved to backend.');
  } catch (error) {
    console.error('Error communicating with backend:', error);
    throw error;
  }
}

export function saveSettings(settings: AppSettings): void {
  try {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    saveSettingsToBackend(settings);
  } catch (error) {
    console.error('Kunde inte spara inställningar till localStorage:', error);
  }
}
