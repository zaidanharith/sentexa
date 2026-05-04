import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";

export default function ReportsDashboardPage() {
  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle
        title="Laporan"
        subtitle="Kelola laporan analisis Anda"
        isPremiumOnly={true}
      />
    </main>
  );
}
