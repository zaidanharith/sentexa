"use client";

import { useState, useRef, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { HiOutlineUser, HiOutlineLogout } from "react-icons/hi";

import { useAuth } from "@/hooks/useAuth";
import { appToast } from "@/lib/toast";

export default function HeaderProfile() {
  const router = useRouter();
  const { user, logout } = useAuth();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const displayName = user?.name?.trim() || "Pengguna";
  const avatarInitial = displayName.charAt(0).toUpperCase();

  const handleLogout = async () => {
    if (isLoggingOut) {
      return;
    }

    setIsLoggingOut(true);
    setShowDropdown(false);

    try {
      await logout();
      router.push("/");
      router.refresh();
      appToast.success("Logout berhasil.");
    } catch {
      appToast.error("Logout gagal. Silakan coba lagi.");
    } finally {
      setIsLoggingOut(false);
    }
  };

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    }

    if (showDropdown) {
      document.addEventListener("mousedown", handleClickOutside);
      return () => {
        document.removeEventListener("mousedown", handleClickOutside);
      };
    }
  }, [showDropdown]);

  return (
    <div className="relative" ref={dropdownRef}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        aria-label="Profil Menu"
        title="Profil"
        className="rounded-full p-1 hover:bg-gray-100 transition-colors focus:outline-none focus:ring-2 focus:ring-sky-500 focus:ring-offset-2 cursor-pointer"
      >
        <div className="w-10 h-10 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 text-md font-bold shrink-0">
          {avatarInitial}
        </div>
      </button>

      {showDropdown && (
        <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-lg shadow-lg z-50">
          <div className="px-4 py-3 border-b border-gray-100">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 font-bold shrink-0">
                {avatarInitial}
              </div>
              <div className="min-w-0">
                <p className="text-sm font-semibold text-gray-900 truncate">
                  {displayName}
                </p>
                <p className="text-xs text-gray-500 truncate">{user?.email}</p>
              </div>
            </div>
          </div>

          <Link
            href="/dashboard/profile"
            onClick={() => setShowDropdown(false)}
            className="flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
          >
            <HiOutlineUser className="w-4 h-4 text-gray-400" />
            <span>Profil Saya</span>
          </Link>

          <button
            onClick={handleLogout}
            disabled={isLoggingOut}
            className="w-full flex items-center gap-3 px-4 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50 disabled:opacity-60 disabled:cursor-not-allowed transition-colors rounded-b-lg"
          >
            <HiOutlineLogout className="w-4 h-4" />
            <span>{isLoggingOut ? "Logging out..." : "Logout"}</span>
          </button>
        </div>
      )}
    </div>
  );
}
