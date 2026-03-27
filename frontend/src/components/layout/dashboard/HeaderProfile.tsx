"use client";

import Link from "next/link";

import { useAuth } from "@/hooks/useAuth";

export default function HeaderProfile() {
  const { user } = useAuth();

  const displayName = user?.name?.trim() || "Pengguna";
  const avatarInitial = displayName.charAt(0).toUpperCase();

  return (
    <Link
      href="/dashboard/profile"
      aria-label="Profil"
      title="Profil"
      className="rounded-full p-1 hover:bg-gray-100 transition-colors"
    >
      <div className="w-10 h-10 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 text-md font-bold shrink-0">
        {avatarInitial}
      </div>
    </Link>
  );
}
