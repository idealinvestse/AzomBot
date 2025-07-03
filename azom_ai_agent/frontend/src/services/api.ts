import { z } from 'zod';

const API_BASE_URL = '/api/v1';

const ChatRequestSchema = z.object({
  user_input: z.string().min(1, 'Input cannot be empty'),
  session_id: z.string().optional(),
});

const ChatResponseSchema = z.object({
  response: z.string(),
  session_id: z.string(),
});

export type ChatRequest = z.infer<typeof ChatRequestSchema>;
export type ChatResponse = z.infer<typeof ChatResponseSchema>;

export async function postChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const validatedRequest = ChatRequestSchema.parse(request);

  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(validatedRequest),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
    throw new Error(errorData.detail || 'Failed to get response from the assistant');
  }

  const data = await response.json();
  return ChatResponseSchema.parse(data);
}

const KpiCardDataSchema = z.object({
  title: z.string(),
  value: z.string(),
  change: z.string(),
  changeType: z.enum(['increase', 'decrease']),
  iconName: z.enum(['Zap', 'Clock', 'DollarSign']),
});

const DailyApiCallSchema = z.object({
  date: z.string(),
  count: z.number(),
});

const SystemStatsSchema = z.object({
  kpiCards: z.array(KpiCardDataSchema),
  apiCalls: z.array(DailyApiCallSchema),
});

export type SystemStats = z.infer<typeof SystemStatsSchema>;
export type KpiCardData = z.infer<typeof KpiCardDataSchema>;

export async function fetchSystemStats(): Promise<SystemStats> {
  const response = await fetch(`${API_BASE_URL}/stats`);

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'An unknown error occurred' }));
    throw new Error(errorData.detail || 'Failed to fetch system stats');
  }

  const data = await response.json();
  return SystemStatsSchema.parse(data);
}
