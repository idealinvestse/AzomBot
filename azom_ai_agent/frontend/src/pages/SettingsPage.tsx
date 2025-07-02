import React, { useState, useEffect } from "react";
import { Input } from "@/components/ui/Input";
import { Button } from "@/components/ui/Button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { CheckCircle, XCircle, Loader2 } from "lucide-react";

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    pipelineServerUrl: "",
    openWebUiUrl: "",
    apiToken: "",
    maxRetries: "3",
    requestTimeout: "30",
    logLevel: "info",
    enableCaching: true,
    cacheDuration: "60",
    rateLimit: "10",
    targetModel: "azom-se-general",
    enableDynamicKnowledge: true,
    enableScheduledUpdates: true,
    knowledgeCacheTtl: "3600",
    // Groq & backend
    llmBackend: "openwebui",
    groqApiKey: "",
    groqModel: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [saveMessage, setSaveMessage] = useState("");
  const [testStatus, setTestStatus] = useState<"idle" | "testing" | "success" | "error">("idle");
  const [testMessage, setTestMessage] = useState("");
  const [groqModels, setGroqModels] = useState<any[]>([]);

  useEffect(() => {
    // Hämta inställningar från backend
    const baseUrl = window.location.origin;
    fetch(`${baseUrl}/tool/settings`)
      .then((r) => r.json())
      .then((data) => setSettings((prev) => ({ ...prev, ...data })))
      .catch(() => {/* ignore for now */});
  }, []);

  // Hämta Groq-modeller när backend är Groq
  useEffect(() => {
    if (settings.llmBackend !== "groq") return;
    const baseUrl = settings.pipelineServerUrl || window.location.origin;
    fetch(`${baseUrl}/admin/llm/models`, { credentials: "include" })
      .then((r) => r.json())
      .then((data) => setGroqModels(data))
      .catch(() => {/* ignore */});
  }, [settings.llmBackend, settings.pipelineServerUrl]);

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value
    }));
  };

  const handleSelectChange = (name: string, value: string) => {
    setSettings(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSwitchChange = (name: string, checked: boolean) => {
    setSettings(prev => ({
      ...prev,
      [name]: checked
    }));
  };

  const handleSave = () => {
    setIsLoading(true);
    setSaveMessage("");
    const baseUrl = settings.pipelineServerUrl || window.location.origin;
    fetch(`${baseUrl}/tool/settings`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    })
      .then((r) => r.json())
      .then(() => {
        setSaveMessage("Inställningar sparade!");
      })
      .catch(() => {
        setSaveMessage("Fel vid sparande av inställningar");
      })
      .finally(() => {
        setIsLoading(false);
        setTimeout(() => setSaveMessage(""), 3000);
      });
  };

  const handleTestConnection = async () => {
    const baseUrl = settings.pipelineServerUrl || window.location.origin;
    const url = `${baseUrl}/ping`;

    setTestStatus("testing");
    setTestMessage("");
    try {
      // Testa anslutningen till OpenWebUI URL med en timeout på 10 sekunder
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);
      const response = await fetch(url, {
        method: 'GET',
        signal: controller.signal,
        headers: settings.apiToken ? { 'Authorization': `Bearer ${settings.apiToken}` } : {}
      });
      clearTimeout(timeoutId);
      if (response.ok) {
        setTestStatus("success");
        setTestMessage("Anslutning lyckades!");
      } else {
        setTestStatus("error");
        setTestMessage(`Anslutning misslyckades: ${response.status} ${response.statusText}`);
      }
    } catch (error) {
      setTestStatus("error");
      setTestMessage(`Anslutning misslyckades: ${error instanceof Error ? error.message : 'Okänt fel'}`);
    }
    setTimeout(() => {
      setTestStatus("idle");
      setTestMessage("");
    }, 5000);
  };

  return (
    <div className="max-w-2xl space-y-6">
      <h2 className="text-xl font-semibold">Inställningar</h2>
      
      <div className="border rounded-lg p-4 space-y-6">
        <h3 className="text-lg font-medium">Pipeline Server</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="pipelineServerUrl">Pipeline Server URL</Label>
            <Input 
              id="pipelineServerUrl"
              name="pipelineServerUrl"
              value={settings.pipelineServerUrl}
              onChange={handleInputChange}
              placeholder="http://localhost:8008" 
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="targetModel">Modell</Label>
            <Input 
              id="targetModel"
              name="targetModel"
              value={settings.targetModel}
              onChange={handleInputChange}
              placeholder="azom-se-general" 
            />
          </div>
          <div className="space-y-2">
            <Label htmlFor="apiToken">API-token till OpenWebUI</Label>
            <Input
              id="apiToken"
              name="apiToken"
              type="password"
              value={settings.apiToken}
              onChange={handleInputChange}
              placeholder="••••••"
            />
          </div>
          <div className="flex items-center gap-4">
            <Button 
              variant="outline" 
              onClick={handleTestConnection} 
              disabled={testStatus === "testing"}
            >
              {testStatus === "testing" ? (
                <>
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" /> Testar...
                </>
              ) : (
                "Testa anslutning"
              )}
            </Button>
            {testStatus === "success" && (
              <div className="flex items-center text-green-600 text-sm">
                <CheckCircle className="h-4 w-4 mr-1" /> {testMessage}
              </div>
            )}
            {testStatus === "error" && (
              <div className="flex items-center text-red-600 text-sm">
                <XCircle className="h-4 w-4 mr-1" /> {testMessage}
              </div>
            )}
          </div>
        </div>
      </div>
      
      <div className="border rounded-lg p-4 space-y-6">
        <div className="border rounded-lg p-4 space-y-6">
        <h3 className="text-lg font-medium">Groq</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="llmBackend">LLM-backend</Label>
            <Select
              value={settings.llmBackend}
              onValueChange={(value: string) => handleSelectChange("llmBackend", value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Välj backend" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="openwebui">OpenWebUI</SelectItem>
                <SelectItem value="groq">Groq</SelectItem>
              </SelectContent>
            </Select>
          </div>
          {settings.llmBackend === "groq" && (
            <>
              <div className="space-y-2">
                <Label htmlFor="groqApiKey">GROQ API-nyckel</Label>
                <Input
                  id="groqApiKey"
                  name="groqApiKey"
                  type="password"
                  value={settings.groqApiKey}
                  onChange={handleInputChange}
                  placeholder="gsk_..."
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="groqModel">GROQ-modell</Label>
                <Select
                  value={settings.groqModel}
                  onValueChange={(val: string) => handleSelectChange("groqModel", val)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Välj modell" />
                  </SelectTrigger>
                  <SelectContent>
                    {groqModels.length > 0 ? (
                      groqModels.map((m: any) => (
                        <SelectItem key={m.model_id} value={m.model_id}>{m.model_id} – {m.category}</SelectItem>
                      ))
                    ) : (
                      <SelectItem value={settings.groqModel || ""}>{settings.groqModel || "Ingen modell"}</SelectItem>
                    )}
                  </SelectContent>
                </Select>
              </div>
            </>
          )}
        </div>
      </div>

      <h3 className="text-lg font-medium">Förfrågningar</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="maxRetries">Maximalt antal försök</Label>
            <Input 
              id="maxRetries"
              name="maxRetries"
              type="number"
              value={settings.maxRetries}
              onChange={handleInputChange}
              placeholder="3" 
            />
            <p className="text-xs text-muted-foreground">Antal gånger en misslyckad förfrågning ska försöka igen.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="requestTimeout">Timeout (sekunder)</Label>
            <Input 
              id="requestTimeout"
              name="requestTimeout"
              type="number"
              value={settings.requestTimeout}
              onChange={handleInputChange}
              placeholder="30" 
            />
            <p className="text-xs text-muted-foreground">Maximal tid att vänta på serversvar.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="rateLimit">Hastighetsbegränsning (anrop/minut)</Label>
            <Input 
              id="rateLimit"
              name="rateLimit"
              type="number"
              value={settings.rateLimit}
              onChange={handleInputChange}
              placeholder="10" 
            />
            <p className="text-xs text-muted-foreground">Maximalt antal API-anrop per minut för att undvika överbelastning.</p>
          </div>
        </div>
      </div>
      
      <div className="border rounded-lg p-4 space-y-6">
        <h3 className="text-lg font-medium">Loggning & Cache</h3>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="logLevel">Loggnivå</Label>
            <Select 
              value={settings.logLevel} 
              onValueChange={(value: string) => handleSelectChange("logLevel", value)}
            >
              <SelectTrigger>
                <SelectValue placeholder="Välj loggnivå" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="debug">Debug</SelectItem>
                <SelectItem value="info">Info</SelectItem>
                <SelectItem value="warning">Varning</SelectItem>
                <SelectItem value="error">Fel</SelectItem>
              </SelectContent>
            </Select>
            <p className="text-xs text-muted-foreground">Detaljnivå för loggmeddelanden.</p>
          </div>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="enableCaching">Aktivera cache</Label>
              <Switch 
                id="enableCaching"
                checked={settings.enableCaching} 
                onCheckedChange={(checked) => handleSwitchChange("enableCaching", checked === true)} 
              />
            </div>
            <p className="text-xs text-muted-foreground">Spara ofta använda svar för snabbare svarstid.</p>
          </div>
          <div className="space-y-2">
            <Label htmlFor="cacheDuration">Cache-varaktighet (minuter)</Label>
            <Input 
              id="cacheDuration"
              name="cacheDuration"
              type="number"
              value={settings.cacheDuration}
              onChange={handleInputChange}
              disabled={!settings.enableCaching}
              placeholder="60" 
            />
            <p className="text-xs text-muted-foreground">Hur länge cachade svar ska behållas.</p>
          </div>
        </div>
      </div>
      
      <div className="flex items-center gap-4">
        <Button onClick={handleSave} disabled={isLoading}>
          {isLoading ? "Sparar..." : "Spara inställningar"}
        </Button>
        {saveMessage && <span className="text-green-600 text-sm">{saveMessage}</span>}
      </div>
    </div>
  );
}
