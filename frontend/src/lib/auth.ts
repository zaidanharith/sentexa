import type { NextAuthOptions } from "next-auth";
import type { JWT } from "next-auth/jwt";
import Credentials from "next-auth/providers/credentials";

import { ApiError, backendAuthApi } from "@/lib/api";

type JwtPayload = {
  exp?: number;
};

function parseJwtPayload(token: string): JwtPayload | null {
  const parts = token.split(".");
  if (parts.length < 2) {
    return null;
  }

  try {
    const normalizedPayload = parts[1].replace(/-/g, "+").replace(/_/g, "/");
    const padding = (4 - (normalizedPayload.length % 4 || 4)) % 4;
    const paddedPayload = `${normalizedPayload}${"=".repeat(padding)}`;
    const json = Buffer.from(paddedPayload, "base64").toString("utf8");
    return JSON.parse(json) as JwtPayload;
  } catch {
    return null;
  }
}

function getAccessTokenExpiryMs(
  accessToken: string | null | undefined,
): number {
  if (!accessToken) {
    return Date.now();
  }

  const payload = parseJwtPayload(accessToken);
  if (typeof payload?.exp === "number") {
    return payload.exp * 1000;
  }

  // Fallback when token payload cannot be parsed.
  return Date.now() + 25 * 60 * 1000;
}

async function refreshAccessToken(token: JWT): Promise<JWT> {
  if (
    typeof token.refreshToken !== "string" ||
    token.refreshToken.length === 0
  ) {
    return {
      ...token,
      accessToken: undefined,
      accessTokenExpires: Date.now(),
      error: "RefreshTokenMissing",
    };
  }

  try {
    const refreshed = await backendAuthApi.refresh(token.refreshToken);
    return {
      ...token,
      accessToken: refreshed.access_token,
      refreshToken: refreshed.refresh_token ?? token.refreshToken,
      accessTokenExpires: getAccessTokenExpiryMs(refreshed.access_token),
      error: undefined,
    };
  } catch {
    return {
      ...token,
      accessToken: undefined,
      accessTokenExpires: Date.now(),
      error: "RefreshAccessTokenError",
    };
  }
}

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
        token.accessTokenExpires = getAccessTokenExpiryMs(user.accessToken);
        token.error = undefined;
        return token;
      }

      const accessTokenExpires =
        typeof token.accessTokenExpires === "number"
          ? token.accessTokenExpires
          : Date.now();

      if (Date.now() < accessTokenExpires - 5000) {
        return token;
      }

      return refreshAccessToken(token);
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
      session.error = typeof token.error === "string" ? token.error : undefined;

      return session;
    },
  },
  pages: {
    signIn: "/",
  },
};
