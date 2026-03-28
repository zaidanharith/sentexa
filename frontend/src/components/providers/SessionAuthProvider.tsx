"use client";

import { SessionProvider } from "next-auth/react";

import { AuthProvider } from "@/context/AuthContext";
import ToastProvider from "@/components/providers/ToastProvider";

interface SessionAuthProviderProps {
  children: React.ReactNode;
}

export default function SessionAuthProvider({
  children,
}: SessionAuthProviderProps) {
  return (
    <SessionProvider refetchOnWindowFocus={false} refetchWhenOffline={false}>
      <AuthProvider>
        {children}
        <ToastProvider />
      </AuthProvider>
    </SessionProvider>
  );
}
