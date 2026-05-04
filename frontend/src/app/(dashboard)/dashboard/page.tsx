import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";

export default function DashboardPage() {
  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle
        title="Dashboard"
        subtitle="Selamat datang di dashboard Anda"
      />
    </main>
  );
}
