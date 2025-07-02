import React, { useEffect, useState } from "react";
import { Activity, CheckCircle, XCircle } from "lucide-react";

export default function StatusPage() {
  const [status, setStatus] = useState<"loading" | "up" | "down">("loading");

  useEffect(() => {
    fetch("/ping")
      .then((r) => (r.ok ? setStatus("up") : setStatus("down")))
      .catch(() => setStatus("down"));
  }, []);

  const icon =
    status === "loading" ? (
      <Activity className="h-6 w-6 animate-spin" />
    ) : status === "up" ? (
      <CheckCircle className="h-6 w-6 text-green-600" />
    ) : (
      <XCircle className="h-6 w-6 text-red-600" />
    );

  return (
    <div className="space-y-4">
      <h2 className="text-xl font-semibold">Systemstatus</h2>
      <div className="flex items-center gap-3 bg-background border rounded-lg p-4 w-fit">
        {icon}
        <span className="text-lg">
          {status === "loading" && "Kontrollerar..."}
          {status === "up" && "Backend körs"}
          {status === "down" && "Backend otillgänglig"}
        </span>
      </div>
    </div>
  );
}
