"use client";

import { useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";

export default function SubscriptionPage() {
  const { user } = useAuth();
  const currentPlan = user?.subscription_plan?.toLowerCase() || "free";
  const [selectedDuration, setSelectedDuration] = useState("monthly");

  const freePlanFeatures = [
    "Analisis teks manual saja (tanpa unggah CSV/Excel)",
    "Maksimal 5 pengiriman teks per hari",
    "Tidak ada akses laporan yang dapat diunduh",
  ];

  const premiumPlanFeatures = [
    "Unggah file ulasan multi-format (CSV/Excel)",
    "Pengiriman teks tanpa batas",
    "Akses laporan yang dapat diunduh (dalam format PDF)",
  ];

  const durationOptions = [
    { code: "weekly", name: "Mingguan", price: 29000, duration: "7 hari" },
    { code: "monthly", name: "Bulanan", price: 99000, duration: "30 hari" },
    { code: "annual", name: "Tahunan", price: 899000, duration: "365 hari" },
  ];

  const selectedDurationData =
    durationOptions.find((d) => d.code === selectedDuration) ||
    durationOptions[1];

  return (
    <main className="w-full max-w-4xl mx-auto flex flex-col gap-6 pb-8">
      <DashboardPageTitle
        title="Langganan"
        subtitle="Kelola plan langganan Anda"
      />

      <DashboardPageContent title="Pilihan Paket Langganan">
        <div className="flex flex-col md:flex-row gap-6">
          <div
            className={`flex-1 rounded-xl border-2 p-8 flex flex-col min-h-125 ${
              currentPlan === "free"
                ? "border-gray-300 bg-gray-50"
                : "border-gray-300 bg-gray-50 opacity-60"
            }`}
          >
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Gratis</h2>
              <p className="text-gray-600 text-sm">Mulai dengan fitur dasar</p>
            </div>

            <div className="mb-6">
              <span className="text-4xl font-bold text-gray-900">IDR 0</span>
              <span className="text-gray-600 text-sm">/bulan</span>
            </div>

            <button
              disabled
              className={`w-full font-semibold py-2.5 px-4 rounded-lg transition mb-8 cursor-not-allowed bg-gray-400 text-white`}
            >
              {currentPlan === "free"
                ? "Plan Anda Saat Ini"
                : "Anda Tidak Dapat Mengubah Plan"}
            </button>

            <div className="space-y-4">
              <p className="text-sm font-semibold text-gray-900 mb-4">
                Fitur yang disertakan:
              </p>
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

          <div
            className={`flex-1 rounded-xl border-2 p-8 flex flex-col relative overflow-hidden min-h-125 border-sky-600 ${
              currentPlan === "premium" ? " bg-sky-50" : ""
            }`}
          >
            {currentPlan !== "premium" && (
              <div className="absolute top-0 right-0 bg-sky-600 text-white px-4 py-1 rounded-bl-lg text-xs font-semibold">
                REKOMENDASI
              </div>
            )}

            <div className="mb-6">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Premium</h2>
              <p className="text-gray-600 text-sm">
                Akses penuh ke semua fitur
              </p>
            </div>

            {currentPlan !== "premium" && (
              <div className="mb-6">
                <p className="text-sm font-semibold text-gray-900 mb-3">
                  Pilih Durasi:
                </p>
                <div className="space-y-2">
                  {durationOptions.map((option) => (
                    <label
                      key={option.code}
                      className="flex items-center gap-3 cursor-pointer"
                    >
                      <input
                        type="radio"
                        name="duration"
                        value={option.code}
                        checked={selectedDuration === option.code}
                        onChange={(e) => setSelectedDuration(e.target.value)}
                        className="w-4 h-4 text-sky-600 bg-gray-100 border-gray-300 focus:ring-sky-500"
                      />
                      <div className="flex-1">
                        <span className="text-sm font-medium text-gray-900">
                          {option.name}
                        </span>
                        <span className="text-xs text-gray-500 ml-2">
                          ({option.duration})
                        </span>
                      </div>
                      <span className="text-sm font-semibold text-sky-600">
                        IDR {option.price.toLocaleString()}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            )}

            <div className="mb-6">
              <span className="text-4xl font-bold text-sky-600">
                IDR{" "}
                {currentPlan === "premium"
                  ? "99.000"
                  : selectedDurationData.price.toLocaleString()}
              </span>
              <span className="text-gray-600 text-sm">
                /
                {currentPlan === "premium"
                  ? "bulan"
                  : selectedDuration === "annual"
                    ? "tahun"
                    : selectedDuration === "monthly"
                      ? "bulan"
                      : "minggu"}
              </span>
            </div>

            <button
              disabled={currentPlan === "premium"}
              className={`w-full font-semibold py-2.5 px-4 rounded-lg transition mb-8 ${
                currentPlan === "premium"
                  ? "bg-sky-600 text-white cursor-not-allowed"
                  : "bg-sky-600 text-white hover:bg-sky-700 cursor-pointer"
              }`}
            >
              {currentPlan === "premium"
                ? "Plan Anda Saat Ini"
                : "Upgrade Sekarang"}
            </button>

            <div className="space-y-4">
              <p className="text-sm font-semibold text-gray-900 mb-4">
                Fitur yang disertakan:
              </p>
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
      </DashboardPageContent>

      <DashboardPageContent title="Metode Pembayaran">
        <p>Detail Pembayaran di sini</p>
      </DashboardPageContent>
    </main>
  );
}
