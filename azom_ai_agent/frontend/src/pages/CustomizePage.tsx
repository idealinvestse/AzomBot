import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { Slider } from "@/components/ui/slider";
import { Label } from "@/components/ui/label";
import { Settings } from "lucide-react";

const DEFAULT_PROMPT = `Du är Azom, en AI-assistent specialiserad på att svara på frågor om produkter från Azom.se. Svara alltid på svenska. Var kortfattad, hjälpsam och vänlig. Använd endast information från den kunskapsbas som tillhandahålls.`;

export default function CustomizePage() {
  const [systemPrompt, setSystemPrompt] = useState(DEFAULT_PROMPT);
  const [temperature, setTemperature] = useState([0.5]);
  const [maxTokens, setMaxTokens] = useState([256]);

  const handleSave = () => {
    // I en riktig applikation skulle detta skickas till backend.
    console.log("Sparar inställningar:", { systemPrompt, temperature: temperature[0], maxTokens: maxTokens[0] });
    alert("Inställningarna har sparats (simulerat)!");
  };

  return (
    <div className="p-4 md:p-6 space-y-6">
        <div className="flex items-center gap-3">
            <Settings className="h-6 w-6" />
            <h2 className="text-2xl font-bold">Anpassa AI-agenten</h2>
        </div>

      <Card>
        <CardHeader>
          <CardTitle>System-prompt</CardTitle>
          <CardDescription>Detta är den grundläggande instruktionen som styr AI-agentens personlighet och beteende.</CardDescription>
        </CardHeader>
        <CardContent>
          <Textarea
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            rows={8}
            className="font-mono text-sm"
          />
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Modell-parametrar</CardTitle>
          <CardDescription>Justera hur kreativ och långrandig modellen ska vara.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <div className="flex justify-between">
                <Label htmlFor="temperature">Temperatur</Label>
                <span className="text-sm text-muted-foreground">{temperature[0].toFixed(2)}</span>
            </div>
            <Slider
              id="temperature"
              min={0}
              max={1}
              step={0.05}
              value={temperature}
              onValueChange={setTemperature}
            />
            <p className="text-xs text-muted-foreground">Lägre värden ger mer förutsägbara svar, högre ger mer kreativa svar.</p>
          </div>
          <div className="space-y-2">
            <div className="flex justify-between">
                <Label htmlFor="max-tokens">Maximal svarslängd (tokens)</Label>
                <span className="text-sm text-muted-foreground">{maxTokens[0]}</span>
            </div>
            <Slider
              id="max-tokens"
              min={64}
              max={1024}
              step={8}
              value={maxTokens}
              onValueChange={setMaxTokens}
            />
            <p className="text-xs text-muted-foreground">Bestämmer den maximala längden på svaren från AI-agenten.</p>
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-end">
        <Button onClick={handleSave}>Spara ändringar</Button>
      </div>
    </div>
  );
}
