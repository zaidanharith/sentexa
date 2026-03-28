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
      subscription?: string;
    };
  }

  interface User {
    id: string;
    name: string;
    email: string;
    subscription?: string;
    accessToken?: string;
    refreshToken?: string | null;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    subscription?: string;
    accessToken?: string;
    refreshToken?: string | null;
    accessTokenExpires?: number;
    error?: string;
  }
}
