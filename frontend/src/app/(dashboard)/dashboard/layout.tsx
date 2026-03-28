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
    },
    {
      label: "Langganan",
      href: "/dashboard/subscription",
    },
    {
      label: "Analisis",
      href: "/dashboard/analysis",
    },
    {
      label: "Ulasan",
      href: "/dashboard/reviews",
    },
    {
      label: "Laporan",
      href: "/dashboard/reports",
      badge: "Premium",
    },
    {
      label: "Riwayat",
      href: "/dashboard/history",
    },
  ];

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar navItems={navItems} />
      <div className="flex min-h-screen min-w-0 flex-1 flex-col">
        <header className="h-16 mb-6 border-b border-gray-200 px-6 flex items-center justify-between gap-4">
          <Breadcrumbs navItems={navItems} />
          <HeaderProfile />
        </header>
        <main className="flex-1 px-6">{children}</main>
        <DashboardFooter />
      </div>
    </div>
  );
}
