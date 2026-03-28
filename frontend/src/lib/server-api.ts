import type { SubscriptionPlan } from "@/lib/api";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
  "http://localhost:8000/api";

const SUBSCRIPTION_TIMEOUT_MS = 1500;

function buildApiUrl(path: string) {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  return `${API_BASE_URL}${normalizedPath}`;
}

export async function getSubscriptionPlansForHome(): Promise<
  SubscriptionPlan[]
> {
  try {
    const response = await fetch(buildApiUrl("/subscription/plans"), {
      cache: "force-cache",
      next: { revalidate: 300 },
      signal: AbortSignal.timeout(SUBSCRIPTION_TIMEOUT_MS),
    });

    if (!response.ok) {
      return [];
    }

    const data = (await response.json()) as SubscriptionPlan[];
    return Array.isArray(data) ? data : [];
  } catch {
    return [];
  }
}
