// Definierar den förväntade statusen för en enskild tjänst
export type ServiceStatusState = "operational" | "degraded" | "outage";

// Definierar den fullständiga datastrukturen för en tjänst
export interface ServiceStatus {
  service: string;
  status: ServiceStatusState;
  message: string;
}

// Funktion för att hämta status för alla tjänster från backend
export async function fetchServiceStatus(): Promise<ServiceStatus[]> {
  const response = await fetch('/api/v1/status');

  if (!response.ok) {
    // Försöker läsa felmeddelande från backend om det finns
    const errorData = await response.json().catch(() => ({ message: 'Okänt serverfel' }));
    throw new Error(`Nätverksfel: ${response.status} ${response.statusText}. ${errorData.message || ''}`.trim());
  }

  const data: ServiceStatus[] = await response.json();
  return data;
}

// --- Logghantering ---

// Definierar de olika loggnivåerna
export type LogLevel = "INFO" | "WARNING" | "ERROR" | "DEBUG";

// Definierar datastrukturen för en loggpost
export interface LogEntry {
  timestamp: string; // ISO 8601 format
  level: LogLevel;
  message: string;
}

/**
 * Hämtar loggar från backend, med valfri filtrering på nivå.
 * @param level - Valfri loggnivå att filtrera på. Om 'all' eller odefinierad, hämtas alla loggar.
 * @returns En promise som resolverar till en array av LogEntry-objekt.
 */
export async function fetchLogs(level: LogLevel | "all" = "all"): Promise<LogEntry[]> {
  let url = '/api/v1/logs';
  if (level !== 'all') {
    url += `?level=${level}`;
  }

  const response = await fetch(url);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ message: 'Okänt serverfel vid hämtning av loggar' }));
    throw new Error(`Nätverksfel: ${response.status} ${response.statusText}. ${errorData.message || ''}`.trim());
  }

  const data: LogEntry[] = await response.json();
  // Sortera loggarna med den senaste först direkt efter hämtning
  return data.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}

