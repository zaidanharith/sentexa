"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import {
  HiOutlineHome,
  HiOutlineChartBar,
  HiOutlineChatAlt2,
  HiOutlineDocumentReport,
  HiOutlineClock,
  HiOutlineCog,
  HiOutlineQuestionMarkCircle,
  HiOutlineLogout,
  HiChevronDoubleLeft,
  HiChevronDoubleRight,
  HiOutlineCreditCard,
} from "react-icons/hi";

import { useAuth } from "@/hooks/useAuth";

const navItems = [
  {
    label: "Beranda",
    href: "/dashboard",
    icon: <HiOutlineHome className="w-4 h-4" />,
  },
  {
    label: "Langganan",
    href: "/dashboard/subscription",
    icon: <HiOutlineCreditCard className="w-4 h-4" />,
  },
  {
    label: "Analisis",
    href: "/dashboard/analysis",
    icon: <HiOutlineChartBar className="w-4 h-4" />,
  },
  {
    label: "Ulasan",
    href: "/dashboard/reviews",
    icon: <HiOutlineChatAlt2 className="w-4 h-4" />,
  },
  {
    label: "Laporan",
    href: "/dashboard/reports",
    icon: <HiOutlineDocumentReport className="w-4 h-4" />,
    badge: "Premium",
  },
  {
    label: "Riwayat",
    href: "/dashboard/history",
    icon: <HiOutlineClock className="w-4 h-4" />,
  },
];

const bottomItems = [
  {
    label: "Pengaturan",
    href: "/dashboard/settings",
    icon: <HiOutlineCog className="w-4 h-4" />,
  },
  {
    label: "Bantuan",
    href: "/dashboard/help",
    icon: <HiOutlineQuestionMarkCircle className="w-4 h-4" />,
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const { user, logout } = useAuth();

  const displayName = user?.name?.trim() || "Pengguna";
  const displayPlan = user?.subscription || "Paket Gratis";
  const avatarInitial = displayName.charAt(0).toUpperCase();

  const handleLogout = async () => {
    if (isLoggingOut) {
      return;
    }

    setIsLoggingOut(true);

    try {
      await logout();
      router.push("/");
      router.refresh();
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <>
      <aside
        className={`hidden md:flex flex-col h-screen sticky top-0 border-r border-gray-200 bg-white transition-all duration-300 ${
          collapsed ? "w-16" : "w-60"
        }`}
      >
        <div
          className={`flex items-center h-16 border-b border-gray-100 px-4 ${
            collapsed ? "justify-center" : "justify-between"
          }`}
        >
          {!collapsed && (
            <Link href="/" className="flex items-center gap-2">
              <Image
                src="/logo1.svg"
                alt="Sentexa"
                width={24}
                height={24}
                style={{ height: "auto" }}
              />
              <span className="text-xl font-bold text-sky-500">Sentexa</span>
            </Link>
          )}
          {collapsed && (
            <Link href="/">
              <Image
                src="/logo1.svg"
                alt="Sentexa"
                width={24}
                height={24}
                style={{ height: "auto" }}
              />
            </Link>
          )}
          <button
            onClick={() => setCollapsed((c) => !c)}
            aria-label="Toggle sidebar"
            className={`w-7 h-7 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors cursor-pointer ${
              collapsed ? "hidden" : ""
            }`}
          >
            <HiChevronDoubleLeft className="w-4 h-4" />
          </button>
        </div>

        {collapsed && (
          <button
            onClick={() => setCollapsed(false)}
            aria-label="Expand sidebar"
            className="mt-2 mx-auto w-8 h-8 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors cursor-pointer"
          >
            <HiChevronDoubleRight className="w-4 h-4" />
          </button>
        )}

        <nav className="flex flex-col gap-1 flex-1 overflow-y-auto px-2 py-4">
          {navItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                title={collapsed ? item.label : undefined}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sky-50 text-sky-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <span className={isActive ? "text-sky-500" : "text-gray-400"}>
                  {item.icon}
                </span>
                {!collapsed && (
                  <span className="flex-1 truncate">{item.label}</span>
                )}
                {!collapsed && item.badge && (
                  <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-600 border border-amber-200">
                    {item.badge}
                  </span>
                )}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-gray-100 px-2 py-3 flex flex-col gap-1">
          {bottomItems.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.href}
                href={item.href}
                title={collapsed ? item.label : undefined}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-sky-50 text-sky-600"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                } ${collapsed ? "justify-center" : ""}`}
              >
                <span className={isActive ? "text-sky-500" : "text-gray-400"}>
                  {item.icon}
                </span>
                {!collapsed && <span className="truncate">{item.label}</span>}
              </Link>
            );
          })}

          {!collapsed && (
            <button
              type="button"
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="mt-2 flex items-center gap-3 rounded-lg px-3 py-2.5 hover:bg-gray-100 transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <div className="w-7 h-7 rounded-full bg-sky-100 flex items-center justify-center text-sky-600 text-xs font-bold shrink-0">
                {avatarInitial}
              </div>
              <div className="flex-1 min-w-0 text-left">
                <p className="text-xs font-semibold text-gray-800 truncate">
                  {displayName}
                </p>
                <p className="text-xs text-gray-400 truncate">
                  {displayPlan.charAt(0).toUpperCase() +
                    displayPlan.slice(1).toLowerCase()}
                </p>
              </div>
              <HiOutlineLogout className="w-3.5 h-3.5 text-gray-400 shrink-0" />
            </button>
          )}

          {collapsed && (
            <button
              type="button"
              title="Keluar"
              onClick={handleLogout}
              disabled={isLoggingOut}
              className="mt-1 mx-auto w-8 h-8 flex items-center justify-center rounded-md text-gray-400 hover:bg-gray-100 hover:text-gray-600 transition-colors cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
            >
              <HiOutlineLogout className="w-4 h-4" />
            </button>
          )}
        </div>
      </aside>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 flex items-center justify-around px-2 py-1">
        {navItems.slice(0, 4).map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                isActive ? "text-sky-500" : "text-gray-500 hover:text-gray-800"
              }`}
            >
              <span className={isActive ? "text-sky-500" : "text-gray-400"}>
                {item.icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
        <Link
          href="/dashboard/pengaturan"
          className={`flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
            pathname === "/dashboard/pengaturan"
              ? "text-sky-500"
              : "text-gray-500 hover:text-gray-800"
          }`}
        >
          <span
            className={
              pathname === "/dashboard/pengaturan"
                ? "text-sky-500"
                : "text-gray-400"
            }
          >
            {bottomItems[0].icon}
          </span>
          <span>Pengaturan</span>
        </Link>
      </nav>
    </>
  );
}
