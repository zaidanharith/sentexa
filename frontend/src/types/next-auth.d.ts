import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    error?: string;
    user: {
      id: string;
      name: string;
      email: string;
      subscription_plan?: string;
      subscription_status?: string;
      subscription_start?: string;
      subscription_end?: string;
      analysis_quota?: number;
    };
  }

  interface User {
    id: string;
    name: string;
    email: string;
    subscription_plan?: string;
    subscription_status?: string;
    subscription_start?: string;
    subscription_end?: string;
    analysis_quota?: number;
    accessToken?: string;
    refreshToken?: string | null;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    subscription_plan?: string;
    subscription_status?: string;
    subscription_start?: string;
    subscription_end?: string;
    analysis_quota?: number;
    accessToken?: string;
    refreshToken?: string | null;
    accessTokenExpires?: number;
    error?: string;
  }
}
