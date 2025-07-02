import { useState, useEffect, useCallback } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { DollarSign, Zap, Clock, BarChart2, ServerCrash, LucideIcon } from "lucide-react";
import { fetchSystemStats, SystemStats, KpiCardData } from '@/services/apiService';
import Spinner from '@/components/ui/spinner';

const iconMap: Record<KpiCardData['iconName'], LucideIcon> = {
  Zap,
  Clock,
  DollarSign,
};

// Define props for the helper component for type safety
interface KpiCardProps extends KpiCardData {}

// A helper component for rendering KPI cards to keep the main component cleaner
const KpiCard: React.FC<KpiCardProps> = ({ title, value, change, changeType, iconName }) => {
  const Icon = iconMap[iconName] || BarChart2;
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium">{title}</CardTitle>
        <Icon className="h-4 w-4 text-muted-foreground" />
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">{value}</div>
        <p className={`text-xs ${changeType === 'increase' ? 'text-green-600' : 'text-red-600'}`}>
          {change} från förra veckan
        </p>
      </CardContent>
    </Card>
  );
};

export default function StatsPage() {
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await fetchSystemStats();
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Ett okänt fel inträffade.');
      setStats(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-full p-6">
        <Spinner className="h-10 w-10 text-primary" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex flex-col items-center justify-center h-full p-6 text-destructive">
        <ServerCrash className="h-10 w-10 mb-4" />
        <h3 className="text-xl font-semibold">Kunde inte ladda statistik</h3>
        <p>{error}</p>
      </div>
    );
  }

  if (!stats) {
    return <div className="p-6">Ingen statistik att visa.</div>;
  }

  return (
    <div className="p-4 md:p-6 space-y-6">
      <div className="flex items-center gap-3">
        <BarChart2 className="h-6 w-6" />
        <h2 className="text-2xl font-bold">Systemstatistik</h2>
      </div>

      {/* KPI Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        {stats.kpiCards.map((kpi, index) => (
          <KpiCard key={index} {...kpi} />
        ))}
      </div>

      {/* Chart Card */}
      <Card>
        <CardHeader>
          <CardTitle>API-anrop (Senaste 7 dagarna)</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="h-[350px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={stats.dailyRequests}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'hsl(var(--background))',
                    borderColor: 'hsl(var(--border))',
                  }}
                />
                <Legend />
                <Bar dataKey="anrop" fill="hsl(var(--primary))" name="Antal anrop" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
