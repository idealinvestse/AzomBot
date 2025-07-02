import React, { useState } from "react";
import { Button } from "@/components/ui/Button";

export default function CustomizePage() {
  const [dark, setDark] = useState(false);

  return (
    <div className="space-y-4 max-w-md">
      <h2 className="text-xl font-semibold">Anpassningar</h2>
      <div className="flex items-center gap-4">
        <span>Mörkt läge</span>
        <Button variant="outline" onClick={() => setDark((d) => !d)}>
          {dark ? "Av" : "På"}
        </Button>
      </div>
      <p className="text-sm text-muted-foreground">
        (Demo – mörkt läge påverkar inte hela UI i denna prototyp.)
      </p>
    </div>
  );
}
