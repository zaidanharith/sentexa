import { redirect } from "next/navigation";
import { getServerSession } from "next-auth";

import Sidebar from "@/components/layout/dashboard/Sidebar";
import { authOptions } from "@/lib/auth";

export default async function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const session = await getServerSession(authOptions);

  if (!session) {
    redirect("/");
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 min-w-0 p-6 pb-20 md:pb-6">{children}</main>
    </div>
  );
}
