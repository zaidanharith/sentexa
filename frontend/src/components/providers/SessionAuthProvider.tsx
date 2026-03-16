"use client";

import { SessionProvider } from "next-auth/react";

import { AuthProvider } from "@/context/AuthContext";

interface SessionAuthProviderProps {
  children: React.ReactNode;
}

export default function SessionAuthProvider({
  children,
}: SessionAuthProviderProps) {
  return (
    <SessionProvider>
      <AuthProvider>{children}</AuthProvider>
    </SessionProvider>
  );
}
