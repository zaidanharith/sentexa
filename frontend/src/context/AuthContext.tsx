"use client";

import { createContext } from "react";
import { signIn, signOut, useSession } from "next-auth/react";

import { ApiError, backendAuthApi } from "@/lib/api";
import type { LoginPayload, RegisterPayload } from "@/lib/api";

export interface AuthUser {
  id: number;
  name: string;
  email: string;
  subscription?: string;
}

export interface AuthContextValue {
  user: AuthUser | null;
  loading: boolean;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  isAuthenticated: boolean;
}

export const AuthContext = createContext<AuthContextValue | undefined>(
  undefined,
);

interface AuthProviderProps {
  children: React.ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const { data: session, status, update } = useSession();

  const user: AuthUser | null = session?.user
    ? {
        id: Number(session.user.id),
        name: session.user.name,
        email: session.user.email,
        subscription: session.user.subscription,
      }
    : null;

  const loading = status === "loading";

  const refreshUser = async () => {
    await update();
  };

  const login = async (payload: LoginPayload) => {
    const result = await signIn("credentials", {
      email: payload.email,
      password: payload.password,
      redirect: false,
    });

    if (!result || result.error) {
      throw new ApiError("Email atau kata sandi tidak valid.", 401);
    }

    await update();
  };

  const register = async (payload: RegisterPayload) => {
    await backendAuthApi.register(payload);

    const result = await signIn("credentials", {
      email: payload.email,
      password: payload.password,
      redirect: false,
    });

    if (!result || result.error) {
      throw new ApiError(
        "Registrasi berhasil, tetapi login otomatis gagal.",
        401,
      );
    }

    await update();
  };

  const logout = async () => {
    if (session?.accessToken) {
      try {
        await backendAuthApi.logout(session.accessToken);
      } catch {}
    }

    await signOut({ redirect: false });
  };

  const value: AuthContextValue = {
    user,
    loading,
    login,
    register,
    logout,
    refreshUser,
    isAuthenticated: Boolean(user),
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
