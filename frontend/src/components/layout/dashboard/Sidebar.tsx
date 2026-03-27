"use client";

import Image from "next/image";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useState } from "react";
import { MdOutlineSpaceDashboard, MdOutlineAttachMoney } from "react-icons/md";
import {
  HiOutlineChartBar,
  HiOutlineChatAlt2,
  HiOutlineDocumentReport,
  HiOutlineClock,
  HiOutlineUser,
  HiOutlineLogout,
  HiChevronDoubleLeft,
  HiChevronDoubleRight,
} from "react-icons/hi";

import { useAuth } from "@/hooks/useAuth";
import { TfiLayoutWidthDefault } from "react-icons/tfi";

type DashboardNavItem = {
  label: string;
  href: string;
  badge?: string;
};

function getNavIcon(href: string) {
  switch (href) {
    case "/dashboard":
      return <MdOutlineSpaceDashboard className="w-4 h-4" />;
    case "/dashboard/subscription":
      return <MdOutlineAttachMoney className="w-4 h-4" />;
    case "/dashboard/analysis":
      return <HiOutlineChartBar className="w-4 h-4" />;
    case "/dashboard/reviews":
      return <HiOutlineChatAlt2 className="w-4 h-4" />;
    case "/dashboard/reports":
      return <HiOutlineDocumentReport className="w-4 h-4" />;
    case "/dashboard/history":
      return <HiOutlineClock className="w-4 h-4" />;
    default:
      return <TfiLayoutWidthDefault className="w-4 h-4" />;
  }
}

export default function Sidebar({
  navItems,
}: {
  navItems: DashboardNavItem[];
}) {
  const pathname = usePathname();
  const router = useRouter();
  const [collapsed, setCollapsed] = useState(false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const { logout } = useAuth();

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
          className={`h-16 flex items-center border-b border-gray-200 px-4 ${
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
            const icon = getNavIcon(item.href);

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
                  {icon}
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
          <Link
            href="/dashboard/profile"
            title={collapsed ? "Profil" : undefined}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              pathname === "/dashboard/profile"
                ? "bg-sky-50 text-sky-600"
                : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
            } ${collapsed ? "justify-center" : ""}`}
          >
            <span
              className={
                pathname === "/dashboard/profile"
                  ? "text-sky-500"
                  : "text-gray-400"
              }
            >
              <HiOutlineUser className="w-4 h-4" />
            </span>
            {!collapsed && <span className="truncate">Profil</span>}
          </Link>

          <button
            type="button"
            onClick={handleLogout}
            disabled={isLoggingOut}
            title={collapsed ? "Logout" : undefined}
            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors text-red-600 hover:bg-red-50 hover:text-red-700 cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed ${
              collapsed ? "justify-center" : ""
            }`}
          >
            <HiOutlineLogout className="w-4 h-4" />
            {!collapsed && <span className="truncate">Logout</span>}
          </button>
        </div>
      </aside>

      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-300 flex items-center justify-around px-2 py-1">
        {navItems.slice(0, 4).map((item) => {
          const isActive = pathname === item.href;
          const icon = getNavIcon(item.href);

          return (
            <Link
              key={item.href}
              href={item.href}
              className={`flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
                isActive ? "text-sky-500" : "text-gray-500 hover:text-gray-800"
              }`}
            >
              <span className={isActive ? "text-sky-500" : "text-gray-400"}>
                {icon}
              </span>
              <span>{item.label}</span>
            </Link>
          );
        })}
        <Link
          href="/dashboard/profile"
          className={`flex flex-col items-center gap-0.5 px-3 py-2 rounded-lg text-xs font-medium transition-colors ${
            pathname === "/dashboard/profile"
              ? "text-sky-500"
              : "text-gray-500 hover:text-gray-800"
          }`}
        >
          <span
            className={
              pathname === "/dashboard/profile"
                ? "text-sky-500"
                : "text-gray-400"
            }
          >
            <HiOutlineUser className="w-4 h-4" />
          </span>
          <span>Profil</span>
        </Link>
      </nav>
    </>
  );
}
