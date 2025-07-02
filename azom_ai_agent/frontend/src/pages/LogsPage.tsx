import React, { useEffect, useState } from "react";

interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
}

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);

  useEffect(() => {
    fetch("/logs?limit=100")
      .then((r) => r.json())
      .then((data) => setLogs(data.logs ?? []))
      .catch(() => setLogs([]));
  }, []);

  return (
    <div>
      <h2 className="text-xl font-semibold mb-4">Senaste loggar</h2>
      <div className="border rounded-lg overflow-auto max-h-[70vh]">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-muted text-left">
              <th className="p-2 w-40">Tid</th>
              <th className="p-2 w-24">Nivå</th>
              <th className="p-2">Meddelande</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((l, i) => (
              <tr key={i} className="even:bg-muted/40">
                <td className="p-2 font-mono whitespace-nowrap">{l.timestamp}</td>
                <td className="p-2 uppercase">{l.level}</td>
                <td className="p-2">{l.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
