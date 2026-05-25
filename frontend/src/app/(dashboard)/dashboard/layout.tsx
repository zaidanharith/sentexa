import Breadcrumbs from "@/components/layout/dashboard/Breadcrumbs";
import HeaderProfile from "@/components/layout/dashboard/HeaderProfile";
import Sidebar from "@/components/layout/dashboard/Sidebar";
import DashboardFooter from "@/components/layout/dashboard/DashboardFooter";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const navItems = [
    {
      label: "Dashboard",
      href: "/dashboard",
      isPremiumOnly: false,
    },
    {
      label: "Langganan",
      href: "/dashboard/subscription",
      isPremiumOnly: false,
    },
    {
      label: "Analisis",
      href: "/dashboard/analysis",
      isPremiumOnly: false,
    },
    {
      label: "Riwayat",
      href: "/dashboard/history",
      isPremiumOnly: false,
    },
    {
      label: "Laporan",
      href: "/dashboard/reports",
      isPremiumOnly: true,
    },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar navItems={navItems} />
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-20 h-16 bg-white border-b border-gray-200 px-6 flex items-center justify-between gap-4 mb-6">
          <Breadcrumbs navItems={navItems} />
          <HeaderProfile />
        </header>
        <main className="flex-1 px-6">{children}</main>
        <DashboardFooter />
      </div>
    </div>
  );
}
