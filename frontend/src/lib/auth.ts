import type { NextAuthOptions } from "next-auth";
import Credentials from "next-auth/providers/credentials";

import { ApiError, backendAuthApi } from "@/lib/api";

export const authOptions: NextAuthOptions = {
  session: {
    strategy: "jwt",
  },
  providers: [
    Credentials({
      name: "Credentials",
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" },
      },
      async authorize(credentials) {
        const email = credentials?.email as string | undefined;
        const password = credentials?.password as string | undefined;

        if (!email || !password) {
          return null;
        }

        try {
          const tokens = await backendAuthApi.login({ email, password });
          const user = await backendAuthApi.me(tokens.access_token);

          return {
            id: String(user.id),
            name: user.name,
            email: user.email,
            subscription: user.subscription,
            accessToken: tokens.access_token,
            refreshToken: tokens.refresh_token ?? null,
          };
        } catch (error) {
          if (error instanceof ApiError && error.status === 401) {
            return null;
          }
          throw error;
        }
      },
    }),
  ],
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.sub = user.id;
        token.name = user.name;
        token.email = user.email;
        token.subscription = user.subscription;
        token.accessToken = user.accessToken;
        token.refreshToken = user.refreshToken;
      }

      return token;
    },
    async session({ session, token }) {
      if (session.user) {
        session.user.id = token.sub ?? "";
        session.user.name = token.name ?? "";
        session.user.email = token.email ?? "";
        session.user.subscription =
          typeof token.subscription === "string"
            ? token.subscription
            : undefined;
      }

      session.accessToken =
        typeof token.accessToken === "string" ? token.accessToken : undefined;
      session.refreshToken =
        typeof token.refreshToken === "string" ? token.refreshToken : undefined;

      return session;
    },
  },
  pages: {
    signIn: "/",
  },
};
