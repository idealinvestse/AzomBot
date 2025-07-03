import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AppSettings, getSettings, saveSettings } from '@/services/settingsService';

export function SettingsPage() {
  const [settings, setSettings] = useState<AppSettings>(getSettings());
  const [isSaved, setIsSaved] = useState(false);

  useEffect(() => {
    setSettings(getSettings());
  }, []);

  const handleSave = () => {
    saveSettings(settings);
    setIsSaved(true);
    setTimeout(() => setIsSaved(false), 3000);
  };

  const handleChange = (field: keyof AppSettings, value: string) => {
    setSettings((prev) => ({ ...prev, [field]: value }));
  };

  return (
    <div className="flex flex-col gap-8 p-4 md:p-6">
      <h1 className="text-3xl font-bold">Inställningar</h1>

      {/* LLM Backend Settings */}
      <Card>
        <CardHeader>
          <CardTitle>LLM Backend</CardTitle>
          <CardDescription>
            Konfigurera anslutningen till språkmodellen. Välj backend och ange nödvändiga uppgifter.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid w-full max-w-md items-center gap-2">
            <Label htmlFor="llm-backend">Backend</Label>
            <Select
              value={settings.llmBackend}
              onValueChange={(value) => handleChange('llmBackend', value)}
            >
              <SelectTrigger id="llm-backend">
                <SelectValue placeholder="Välj en backend" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openwebui">OpenWebUI (Lokal)</SelectItem>
                <SelectItem value="groq">Groq Cloud (API)</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {settings.llmBackend === 'openwebui' && (
            <>
              <div className="grid w-full max-w-md items-center gap-2">
                <Label htmlFor="openwebui-url">OpenWebUI URL</Label>
                <Input
                  id="openwebui-url"
                  type="text"
                  placeholder="http://localhost:3000"
                  value={settings.openwebuiUrl}
                  onChange={(e) => handleChange('openwebuiUrl', e.target.value)}
                />
              </div>
              <div className="grid w-full max-w-md items-center gap-2">
                <Label htmlFor="openwebui-token">API Token (valfritt)</Label>
                <Input
                  id="openwebui-token"
                  type="password"
                  placeholder="Ange din API-token"
                  value={settings.openwebuiApiToken}
                  onChange={(e) => handleChange('openwebuiApiToken', e.target.value)}
                />
              </div>
            </>
          )}

          {settings.llmBackend === 'groq' && (
            <div className="grid w-full max-w-md items-center gap-2">
              <Label htmlFor="groq-apikey">Groq API Nyckel</Label>
              <Input
                id="groq-apikey"
                type="password"
                placeholder="gsk_..."
                value={settings.groqApiKey}
                onChange={(e) => handleChange('groqApiKey', e.target.value)}
              />
            </div>
          )}
           <div className="grid w-full max-w-md items-center gap-2">
                <Label htmlFor="target-model">Modellnamn</Label>
                <Input
                  id="target-model"
                  type="text"
                  placeholder="azom-se-general"
                  value={settings.targetModel}
                  onChange={(e) => handleChange('targetModel', e.target.value)}
                />
              </div>
        </CardContent>
      </Card>

      {/* Pipeline Server Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Pipeline Server</CardTitle>
          <CardDescription>Ange adressen till servern som hanterar dataindexering och pipelines.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid w-full max-w-md items-center gap-2">
            <Label htmlFor="pipeline-url">Server URL</Label>
            <Input
              id="pipeline-url"
              type="text"
              placeholder="http://localhost:8001"
              value={settings.pipelineServerUrl}
              onChange={(e) => handleChange('pipelineServerUrl', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* General Settings */}
      <Card>
        <CardHeader>
          <CardTitle>Allmänt</CardTitle>
          <CardDescription>Applikationsövergripande inställningar.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid w-full max-w-md items-center gap-2">
            <Label htmlFor="theme-select">Tema</Label>
            <Select
              value={settings.theme}
              onValueChange={(value) => handleChange('theme', value)}
            >
              <SelectTrigger id="theme-select">
                <SelectValue placeholder="Välj ett tema" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="light">Ljust</SelectItem>
                <SelectItem value="dark">Mörkt</SelectItem>
                <SelectItem value="system">System</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end items-center gap-4 mt-4">
        <p className={`text-sm transition-opacity ${isSaved ? 'opacity-100 text-green-600' : 'opacity-0'}`}>
          Inställningarna har sparats!
        </p>
        <Button onClick={handleSave} className="w-32">Spara</Button>
      </div>
    </div>
  );
}
