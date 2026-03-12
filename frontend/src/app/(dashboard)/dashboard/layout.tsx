import Sidebar from "@/components/layout/dashboard/Sidebar";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 min-w-0 p-6 pb-20 md:pb-6">{children}</main>
    </div>
  );
}
