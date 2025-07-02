import React from "react";
import { BarChart2 } from "lucide-react";

export default function StatsPage() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-semibold flex items-center gap-2">
        <BarChart2 className="h-5 w-5" /> Statistik
      </h2>
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
        {[
          { label: "Anrop idag", value: 42 },
          { label: "Fel %", value: "0.5%" },
          { label: "Medellatens", value: "350 ms" },
        ].map((c) => (
          <div
            key={c.label}
            className="bg-background border rounded-lg p-4 text-center space-y-2"
          >
            <div className="text-2xl font-bold">{c.value}</div>
            <div className="text-sm text-muted-foreground">{c.label}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
