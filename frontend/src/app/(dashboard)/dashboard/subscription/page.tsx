"use client";

import { useAuth } from "@/hooks/useAuth";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";

export default function SubscriptionPage() {
  const { user } = useAuth();
  const currentPlan = user?.subscription?.toLowerCase() || "free";

  const freePlanFeatures = [
    "Analisis teks manual saja (tanpa unggah CSV/Excel)",
    "Maksimal 5 pengiriman teks per hari",
    "Tidak ada akses laporan yang dapat diunduh",
  ];

  const premiumPlanFeatures = [
    "Unggah file ulasan multi-format (CSV/Excel)",
    "Pengiriman teks tanpa batas",
    "Akses laporan yang dapat diunduh (PDF/CSV)",
  ];

  return (
    <main className="w-full max-w-4xl mx-auto flex flex-col gap-6 pb-8">
      <DashboardPageTitle
        title="Langganan"
        subtitle="Kelola plan langganan Anda"
      />

      <div className="flex flex-col md:flex-row gap-6">
        <div className={`flex-1 rounded-xl border-2 p-8 flex flex-col ${
          currentPlan === "free"
            ? "border-gray-300 bg-gray-50"
            : "border-gray-300 bg-gray-50 opacity-60"
        }`}>
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Gratis</h2>
            <p className="text-gray-600 text-sm">Mulai dengan fitur dasar</p>
          </div>

          <div className="mb-6">
            <span className="text-4xl font-bold text-gray-900">IDR 0</span>
            <span className="text-gray-600 text-sm">/bulan</span>
          </div>

          <button disabled className={`w-full font-semibold py-2.5 px-4 rounded-lg transition mb-8 cursor-not-allowed bg-gray-400 text-white`}>
            {currentPlan === "free" ? "Plan Anda Saat Ini" : "Anda Tidak Dapat Mengubah Plan"}
          </button>

          <div className="space-y-4">
            <p className="text-sm font-semibold text-gray-900 mb-4">Fitur yang disertakan:</p>
            <ul className="space-y-3">
              {freePlanFeatures.map((feature, idx) => (
                <li key={`free-${idx}`} className="flex items-start gap-3">
                  <span className="text-gray-400 font-bold mt-0.5">✓</span>
                  <span className="text-gray-700 text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Premium Plan Card */}
        <div className={`flex-1 rounded-xl border-2 p-8 flex flex-col relative overflow-hidden ${
          currentPlan === "premium"
            ? "border-sky-600 bg-gradient-to-br from-sky-100 to-white"
            : "border-sky-600 bg-gradient-to-br from-sky-50 to-white"
        }`}>
          {currentPlan !== "premium" && (
            <div className="absolute top-0 right-0 bg-sky-600 text-white px-4 py-1 rounded-bl-lg text-xs font-semibold">
              REKOMENDASI
            </div>
          )}

          <div className="mb-6">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Premium</h2>
            <p className="text-gray-600 text-sm">Akses penuh ke semua fitur</p>
          </div>

          <div className="mb-6">
            <span className="text-4xl font-bold text-sky-600">IDR 99.000</span>
            <span className="text-gray-600 text-sm">/bulan</span>
          </div>

          <button disabled={currentPlan === "premium"} className={`w-full font-semibold py-2.5 px-4 rounded-lg transition mb-8 ${
            currentPlan === "premium"
              ? "bg-sky-600 text-white cursor-not-allowed"
              : "bg-sky-600 text-white hover:bg-sky-700"
          }`}>
            {currentPlan === "premium" ? "✓ Plan Anda Saat Ini" : "Upgrade Sekarang"}
          </button>

          <div className="space-y-4">
            <p className="text-sm font-semibold text-gray-900 mb-4">Fitur yang disertakan:</p>
            <ul className="space-y-3">
              {premiumPlanFeatures.map((feature, idx) => (
                <li key={`premium-${idx}`} className="flex items-start gap-3">
                  <span className="text-sky-600 font-bold mt-0.5">✓</span>
                  <span className="text-gray-700 text-sm">{feature}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>

      {/* FAQ Section */}
      
    </main>
  );
}
