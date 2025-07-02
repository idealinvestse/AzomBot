import { useState, useEffect, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { CheckCircle, XCircle, AlertTriangle, RefreshCw, ServerCrash } from 'lucide-react';
import { cn } from '@/lib/utils';
import { fetchServiceStatus, ServiceStatus, ServiceStatusState } from '@/services/apiService';
import Spinner from '@/components/ui/spinner';

const statusConfig: { 
    [key in ServiceStatusState]: {
        icon: React.ReactElement;
        variant: "default" | "secondary" | "destructive";
        text: string;
    }
} = {
  operational: {
    icon: <CheckCircle className="h-5 w-5 text-green-500" />,
    variant: 'default',
    text: 'I drift',
  },
  degraded: {
    icon: <AlertTriangle className="h-5 w-5 text-yellow-500" />,
    variant: 'secondary',
    text: 'Nedsatt',
  },
  outage: {
    icon: <XCircle className="h-5 w-5 text-red-500" />,
    variant: 'destructive',
    text: 'Avbrott',
  },
};

export default function StatusPage() {
  const [services, setServices] = useState<ServiceStatus[]>([]);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchServiceStatus();
      setServices(data);
      setLastUpdated(new Date());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ett okänt fel inträffade.');
      setServices([]); // Rensa gammal data vid fel
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return (
    <div className="p-4 md:p-6">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <div className="space-y-1.5">
            <CardTitle>Systemstatus</CardTitle>
            {lastUpdated && !error && (
              <CardDescription>
                Senast uppdaterad: {lastUpdated.toLocaleTimeString('sv-SE')}
              </CardDescription>
            )}
          </div>
          <Button variant="outline" size="icon" onClick={fetchData} disabled={isLoading}>
            <RefreshCw className={cn("h-4 w-4", isLoading && "animate-spin")} />
          </Button>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {isLoading ? (
              <div className="flex flex-col items-center justify-center h-48 gap-4">
                <Spinner className="h-8 w-8 text-primary" />
                <p className="text-muted-foreground">Hämtar systemstatus...</p>
              </div>
            ) : error ? (
              <div className="flex flex-col items-center justify-center h-48 gap-4 text-destructive">
                <ServerCrash className="h-8 w-8" />
                <p className="font-semibold">Kunde inte hämta status</p>
                <p className="text-sm text-center">{error}</p>
              </div>
            ) : (
              services.map((service) => {
                const config = statusConfig[service.status];
                return (
                    <div key={service.service} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                        <div className="flex items-center gap-4">
                        {config.icon}
                        <div>
                            <p className="font-semibold">{service.service}</p>
                            <p className="text-sm text-muted-foreground">{service.message}</p>
                        </div>
                        </div>
                        <Badge variant={config.variant} className="capitalize">
                        {config.text}
                        </Badge>
                    </div>
                );
              })
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
