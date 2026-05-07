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

export type SubscriptionTier = 'free' | 'premium';

export interface FeatureAccess {
  canUploadFile: boolean;
  canInputText: boolean;
  maxFilesPerDay?: number;
  maxTextLength?: number;
}

export function getFeatureAccess(subscription: string | undefined): FeatureAccess {
  const tier = (subscription?.toLowerCase() || 'free') as SubscriptionTier;

  const features: Record<SubscriptionTier, FeatureAccess> = {
    free: {
      canUploadFile: false,
      canInputText: true,
      maxTextLength: 500,
    },
    premium: {
      canUploadFile: true,
      canInputText: true,
      maxFilesPerDay: 50,
      maxTextLength: 5000,
    },
  };

  return features[tier] || features.free;
}

export function getSubscriptionTier(subscription: string | undefined): SubscriptionTier {
  return (subscription?.toLowerCase() as SubscriptionTier) || 'free';
}