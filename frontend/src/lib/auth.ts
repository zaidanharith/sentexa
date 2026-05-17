import type { NextAuthOptions, DefaultSession } from "next-auth";
import type { DefaultJWT } from "next-auth/jwt";
import CredentialsProvider from "next-auth/providers/credentials";
import GoogleProvider from "next-auth/providers/google";
import { backendAuthApi } from "@/lib/api";

declare module "next-auth" {
  interface Session {
    accessToken?: string;
    refreshToken?: string;
    user: DefaultSession["user"] & {
      id: string;
      accessToken?: string;
      refreshToken?: string;
      subscription_plan?: string;
    };
  }

  interface User {
    id: string;
    accessToken?: string;
    refreshToken?: string;
    subscription_plan?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT extends DefaultJWT {
    accessToken?: string;
    refreshToken?: string;
    subscription_plan?: string;
  }
}

export const authOptions: NextAuthOptions = {
  providers: [
    CredentialsProvider({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        if (!credentials?.email || !credentials?.password) {
          throw new Error("Email dan password harus diisi");
        }

        try {
          const response = await backendAuthApi.login({
            email: credentials.email,
            password: credentials.password,
          });

          // Fetch user data
          const userResponse = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"}/auth/me`,
            {
              headers: {
                Authorization: `Bearer ${response.access_token}`,
              },
            }
          );

          if (!userResponse.ok) {
            throw new Error("Failed to fetch user data");
          }

          const userData = await userResponse.json();

          return {
            id: userData.id.toString(),
            name: userData.name,
            email: userData.email,
            accessToken: response.access_token,
            refreshToken: response.refresh_token ?? undefined,
            subscription_plan: userData.subscription_plan || "free",
          };
        } catch {
          throw new Error("Email atau password tidak valid");
        }
      },
    }),

    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],

  callbacks: {
    async signIn({ user, account }) {
      if (account?.provider === "google") {
        try {
          const response = await fetch(
            `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000/api"}/auth/google-callback`,
            {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({
                email: user.email,
                name: user.name,
                googleId: user.id,
                image: user.image,
              }),
            }
          );

          if (!response.ok) {
            return false;
          }

          const data = await response.json();
          user.accessToken = data.access_token;
          user.refreshToken = data.refresh_token;

          return true;
        } catch (error) {
          console.error("Google callback error:", error);
          return false;
        }
      }

      return true;
    },

    async jwt({ token, user }) {
      if (user) {
        token.id = user.id;
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
        token.subscription_plan = user.subscription_plan;
      }
      return token;
    },

    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub || "";
        session.user.accessToken = token.accessToken;
        session.user.refreshToken = token.refreshToken;
        session.user.subscription_plan = token.subscription_plan;
      }
      return session;
    },
  },

  pages: {
    signIn: "/",
  },

  session: {
    strategy: "jwt",
    maxAge: 30 * 60,
  },

  jwt: {
    maxAge: 30 * 60,
  },
};