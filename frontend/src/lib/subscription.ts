const SUBSCRIPTION_NAME_BY_CODE: Record<string, string> = {
  free: "Free",
  premium: "Premium",
  weekly: "Premium",
  monthly: "Premium",
  annual: "Premium",
};

export function getSubscriptionName(value?: string | null): string {
  if (!value) {
    return "Free";
  }

  const normalized = value.trim().toLowerCase();
  return SUBSCRIPTION_NAME_BY_CODE[normalized] ?? value;
}

export function isPremiumSubscription(value?: string | null): boolean {
  return getSubscriptionName(value).toLowerCase() === "premium";
}
