import { useEffect, useState, useCallback } from "react";
import { RefreshCw, FileText, Loader2, ServerCrash } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge, BadgeProps } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { cn } from "@/lib/utils";
import { fetchLogs, LogEntry, LogLevel } from "@/services/apiService";

export default function LogsPage() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [levelFilter, setLevelFilter] = useState<LogLevel | "all">("all");

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const fetchedLogs = await fetchLogs(levelFilter);
      setLogs(fetchedLogs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ett okänt fel inträffade vid hämtning av loggar.');
      setLogs([]);
    } finally {
      setIsLoading(false);
    }
  }, [levelFilter]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const getBadgeVariant = (level: LogLevel): BadgeProps["variant"] => {
    switch (level) {
      case "ERROR": return "destructive";
      case "WARNING": return "secondary";
      case "INFO": return "default";
      case "DEBUG": return "outline";
      default: return "default";
    }
  };

  return (
    <div className="p-4 md:p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="flex items-center gap-3">
            <FileText className="h-6 w-6" />
            <CardTitle>Systemloggar</CardTitle>
          </div>
          <div className="flex items-center gap-2">
            <Select value={levelFilter} onValueChange={(value) => setLevelFilter(value as LogLevel | 'all')}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filtrera på nivå" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">Alla nivåer</SelectItem>
                <SelectItem value="INFO">Info</SelectItem>
                <SelectItem value="WARNING">Varning</SelectItem>
                <SelectItem value="ERROR">Fel</SelectItem>
                <SelectItem value="DEBUG">Debug</SelectItem>
              </SelectContent>
            </Select>
            <Button variant="outline" onClick={fetchData} disabled={isLoading}>
              <RefreshCw className={cn("h-4 w-4 mr-2", isLoading && "animate-spin")} />
              Uppdatera
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          <div className="border rounded-lg relative min-h-[400px]">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-[200px]">Tidsstämpel</TableHead>
                  <TableHead className="w-[120px]">Nivå</TableHead>
                  <TableHead>Meddelande</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  <TableRow>
                    <TableCell colSpan={3} className="h-24 text-center">
                      <div className="flex justify-center items-center">
                        <Loader2 className="h-8 w-8 animate-spin text-primary" />
                      </div>
                    </TableCell>
                  </TableRow>
                ) : error ? (
                  <TableRow>
                    <TableCell colSpan={3} className="h-24 text-center text-destructive">
                       <div className="flex flex-col items-center justify-center gap-2">
                         <ServerCrash className="h-8 w-8" />
                         <p className="font-semibold">Kunde inte hämta loggar</p>
                         <p className="text-sm">{error}</p>
                       </div>
                    </TableCell>
                  </TableRow>
                ) : logs.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={3} className="text-center h-24">
                      Inga loggar att visa för den valda nivån.
                    </TableCell>
                  </TableRow>
                ) : (
                  logs.map((log, index) => (
                    <TableRow key={index}>
                      <TableCell className="font-mono text-xs">{new Date(log.timestamp).toLocaleString('sv-SE')}</TableCell>
                      <TableCell>
                        <Badge variant={getBadgeVariant(log.level)}>{log.level}</Badge>
                      </TableCell>
                      <TableCell className="font-mono text-xs">{log.message}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
