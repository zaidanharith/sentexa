import "next-auth";
import "next-auth/jwt";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    error?: string;
    user: {
      id: string;
      subscription_plan?: string;
    };
  }

  interface User {
    id: string;
    name?: string;
    email?: string;
    subscription_plan?: string;
    accessToken?: string;
    refreshToken?: string | null;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    id?: string;
    subscription_plan?: string;
    accessToken?: string;
    refreshToken?: string | null;
    accessTokenExpires?: number;
    error?: string;
  }
}
