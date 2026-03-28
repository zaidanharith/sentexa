import {
  FiUpload,
  FiBarChart2,
  FiDownload,
  FiArrowRight,
} from "react-icons/fi";
import { MdAutoAwesome } from "react-icons/md";
import { HiSparkles } from "react-icons/hi2";
import Link from "next/link";
import { Suspense } from "react";
import { getSubscriptionPlansForHome } from "@/lib/server-api";
import type { SubscriptionPlan } from "@/lib/api";

function formatIdr(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value);
}

export default async function Home() {
  return (
    <>
      <section className="border-b border-gray-200 bg-white w-full pb-16">
        <div className="relative mx-auto grid md:grid-cols-2 gap-12 items-center max-w-7xl">
          <div>
            <span className="inline-flex items-center gap-1.5 bg-sky-50 border border-sky-200 text-sky-600 text-xs font-semibold px-3 py-1 rounded-full mb-5">
              <HiSparkles className="text-sky-400" />
              Khusus Pelaku UMKM
            </span>

            <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 leading-tight tracking-tight mb-5">
              Analisis Ribuan{" "}
              <span className="text-sky-500">Ulasan Pelanggan</span> Secara
              Otomatis
            </h1>

            <p className="text-base text-gray-500 leading-relaxed mb-8 max-w-lg">
              Sentexa membantu UMKM memahami sentimen pelanggan —{" "}
              <span className="font-semibold text-green-600">Positif</span>,{" "}
              <span className="font-semibold text-red-500">Negatif</span>, atau{" "}
              <span className="font-semibold text-yellow-500">Netral</span> —
              dari ulasan marketplace menggunakan AI berbasis NLP, secara cepat
              dan akurat.
            </p>

            <div className="flex flex-wrap items-center gap-3">
              <Link
                href="/dashboard"
                className="inline-flex items-center gap-2 bg-sky-500 hover:bg-sky-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors shadow-md shadow-sky-100 cursor-pointer"
              >
                <FiArrowRight className="text-sm" />
                Mulai Analisis Sekarang
              </Link>
            </div>
            <p className="text-xs text-gray-400 mt-4">
              ✓ Tidak perlu kartu kredit &nbsp;·&nbsp; Gratis hingga 100 ulasan
            </p>
          </div>

          <div className="hidden md:block select-none">
            <div className="rounded-2xl border border-gray-200 bg-gray-50 shadow-xl overflow-hidden">
              <div className="flex items-center gap-1.5 px-4 py-3 border-b border-gray-200 bg-white">
                <span className="w-3 h-3 rounded-full bg-red-400" />
                <span className="w-3 h-3 rounded-full bg-yellow-400" />
                <span className="w-3 h-3 rounded-full bg-green-400" />
                <span className="ml-3 text-xs text-gray-400 font-mono">
                  /dashboard
                </span>
              </div>
              <div className="p-5 space-y-4">
                <div className="flex gap-3">
                  {[
                    {
                      label: "Positif",
                      pct: "72%",
                      color: "bg-green-100 text-green-700",
                    },
                    {
                      label: "Negatif",
                      pct: "15%",
                      color: "bg-red-100 text-red-600",
                    },
                    {
                      label: "Netral",
                      pct: "13%",
                      color: "bg-yellow-100 text-yellow-600",
                    },
                  ].map((c) => (
                    <div
                      key={c.label}
                      className={`flex-1 rounded-lg p-3 ${c.color}`}
                    >
                      <p className="text-lg font-bold">{c.pct}</p>
                      <p className="text-xs font-medium">{c.label}</p>
                    </div>
                  ))}
                </div>
                {[
                  {
                    label: "Pengiriman cepat",
                    w: "w-4/5",
                    color: "bg-sky-400",
                  },
                  { label: "Produk sesuai", w: "w-3/5", color: "bg-sky-300" },
                  { label: "Kemasan rusak", w: "w-2/5", color: "bg-red-300" },
                  {
                    label: "Seller responsif",
                    w: "w-1/2",
                    color: "bg-green-300",
                  },
                ].map((r) => (
                  <div key={r.label} className="space-y-1">
                    <p className="text-xs text-gray-500">{r.label}</p>
                    <div className="h-2 w-full bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className={`h-full rounded-full ${r.w} ${r.color}`}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-b border-gray-200 py-8 bg-white w-full">
        <div className="mx-auto w-fit px-6 grid grid-cols-3 gap-4 text-center flex-wrap">
          {[
            {
              val: "10.000+",
              label: "Ulasan Dianalisis",
              accent: "text-sky-500",
            },
            {
              val: "95%",
              label: "Akurasi Model NLP",
              accent: "text-green-500",
            },
            { val: "500+", label: "UMKM Terbantu", accent: "text-purple-500" },
          ].map((s, i) => (
            <div key={i} className="py-4 px-2">
              <p className={`text-3xl font-extrabold ${s.accent}`}>{s.val}</p>
              <p className="text-xs text-gray-500 mt-1 font-medium">
                {s.label}
              </p>
            </div>
          ))}
        </div>
      </section>

      <section
        id="feature"
        className="py-16 border-b border-gray-200 bg-gray-50 w-full"
      >
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-10">
            <span className="inline-block bg-sky-50 border border-sky-200 text-sky-600 text-xs font-semibold px-3 py-1 rounded-full mb-3">
              Fitur Unggulan
            </span>
            <h2 className="text-3xl font-bold text-gray-900">
              Semua yang Kamu Butuhkan
            </h2>
            <p className="text-sm text-gray-500 mt-2 max-w-md mx-auto">
              Dari unggah data hingga ekspor laporan — semua tersedia dalam satu
              platform.
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-5">
            {[
              {
                icon: FiUpload,
                title: "Upload CSV / Excel",
                desc: "Unggah file ulasan langsung dari seller center marketplace dengan mudah.",
                accent: "bg-sky-50 text-sky-500",
              },
              {
                icon: MdAutoAwesome,
                title: "Klasifikasi NLP Otomatis",
                desc: "AI berbasis Python mengelompokkan ulasan: Positif, Negatif, Netral secara real-time.",
                accent: "bg-purple-50 text-purple-500",
              },
              {
                icon: FiBarChart2,
                title: "Dashboard Visualisasi",
                desc: "Pie chart, line chart, dan word cloud untuk melihat tren kepuasan pelanggan.",
                accent: "bg-green-50 text-green-500",
              },
              {
                icon: FiDownload,
                title: "Ekspor Laporan",
                desc: "Unduh laporan lengkap dalam format PDF atau CSV. Tersedia di paket Premium.",
                accent: "bg-orange-50 text-orange-500",
              },
            ].map((f, i) => {
              const Icon = f.icon;
              return (
                <div
                  key={i}
                  className="group border border-gray-200 rounded-xl p-5 bg-white hover:shadow-md hover:-translate-y-0.5 transition-all duration-200"
                >
                  <div
                    className={`w-11 h-11 rounded-lg flex items-center justify-center text-xl mb-4 ${f.accent}`}
                  >
                    <Icon />
                  </div>
                  <h4 className="text-gray-800 font-semibold mb-1.5">
                    {f.title}
                  </h4>
                  <p className="text-xs text-gray-500 leading-relaxed">
                    {f.desc}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      <section
        id="how-it-works"
        className="py-16 border-b border-gray-200 bg-white w-full"
      >
        <div className="mx-auto max-w-7xl">
          <div className="text-center mb-10">
            <span className="inline-block bg-sky-50 border border-sky-200 text-sky-600 text-xs font-semibold px-3 py-1 rounded-full mb-3">
              Cara Kerja
            </span>
            <h2 className="text-3xl font-bold text-gray-900">
              Mulai dalam 3 Langkah Mudah
            </h2>
          </div>
          <div className="grid md:grid-cols-3 gap-6 relative">
            <div className="hidden md:block absolute top-10 left-1/6 right-1/6 h-px bg-gray-200 z-0" />
            {[
              {
                step: "01",
                title: "Unggah Ulasan",
                desc: "Upload file CSV/Excel atau paste teks ulasan secara langsung ke platform.",
                color: "bg-sky-500 text-white",
              },
              {
                step: "02",
                title: "AI Memproses",
                desc: "Model NLP menganalisis dan mengklasifikasikan setiap ulasan secara otomatis.",
                color: "bg-purple-500 text-white",
              },
              {
                step: "03",
                title: "Lihat Hasilnya",
                desc: "Dashboard menampilkan visualisasi, kata kunci, dan tabel hasil analisis.",
                color: "bg-green-500 text-white",
              },
            ].map((s, i) => (
              <div
                key={i}
                className="relative border border-gray-200 rounded-xl p-6 bg-white shadow-sm hover:shadow-md transition-shadow"
              >
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold mb-4 ${s.color}`}
                >
                  {s.step}
                </div>
                <h4 className="text-gray-800 font-semibold mb-2">{s.title}</h4>
                <p className="text-sm text-gray-500 leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <Suspense fallback={<PricingSectionFallback />}>
        <PricingSection />
      </Suspense>
    </>
  );
}

async function PricingSection() {
  const plans = await getSubscriptionPlansForHome();

  return (
    <section
      id="pricing"
      className="py-16 border-b border-gray-200 bg-gray-50 w-full"
    >
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-10">
          <span className="inline-block bg-sky-50 border border-sky-200 text-sky-600 text-xs font-semibold px-3 py-1 rounded-full mb-3">
            Harga Langganan
          </span>
          <h2 className="text-3xl font-bold text-gray-900">
            Pilih Paket Sesuai Kebutuhan Bisnis
          </h2>
          <p className="text-sm text-gray-500 mt-2 max-w-xl mx-auto">
            Data paket dan harga di bawah ini diambil langsung dari API
            subscription Sentexa.
          </p>
        </div>

        {plans.length === 0 ? (
          <div className="rounded-xl border border-amber-200 bg-amber-50 px-5 py-4 text-sm text-amber-800">
            Paket langganan belum dapat dimuat saat ini. Silakan coba beberapa
            saat lagi.
          </div>
        ) : (
          <SubscriptionCards plans={plans} />
        )}

        <div className="mt-10 text-center">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 bg-sky-500 hover:bg-sky-600 text-white font-semibold px-6 py-3 rounded-lg transition-colors shadow-md shadow-sky-100"
          >
            Cek Langganan
            <FiArrowRight className="text-sm" />
          </Link>
        </div>
      </div>
    </section>
  );
}

function SubscriptionCards({ plans }: { plans: SubscriptionPlan[] }) {
  return (
    <div className="grid md:grid-cols-2 gap-6">
      {plans.map((plan) => {
        const minPrice =
          plan.duration_options.length > 0
            ? Math.min(...plan.duration_options.map((d) => d.price))
            : null;

        return (
          <div
            key={plan.code}
            className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm"
          >
            <div className="flex items-start justify-between gap-3 mb-5">
              <div>
                <h3 className="text-2xl font-bold text-gray-900">
                  {plan.name}
                </h3>
                <p className="text-sm text-gray-500 mt-1">
                  Kuota analisis:{" "}
                  {plan.quota >= 999999 ? "Unlimited" : plan.quota}
                </p>
              </div>
              <span className="inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-semibold text-sky-700 capitalize">
                {plan.name}
              </span>
            </div>

            <div className="mb-5">
              {minPrice === null ? (
                <p className="text-lg font-semibold text-gray-800">Gratis</p>
              ) : (
                <p className="text-lg font-semibold text-gray-800">
                  Mulai dari {formatIdr(minPrice)}
                </p>
              )}
            </div>

            <ul className="space-y-2 mb-6">
              {plan.features.map((feature) => (
                <li key={feature} className="text-sm text-gray-600">
                  • {feature}
                </li>
              ))}
            </ul>

            {plan.duration_options.length > 0 && (
              <div className="space-y-2 border-t border-gray-100 pt-4">
                {plan.duration_options.map((duration) => (
                  <div
                    key={duration.code}
                    className="flex items-center justify-between text-sm"
                  >
                    <span className="text-gray-600">{duration.name}</span>
                    <span className="font-semibold text-gray-900">
                      {formatIdr(duration.price)}
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}

function PricingSectionFallback() {
  return (
    <section
      id="pricing"
      className="py-16 border-b border-gray-200 bg-gray-50 w-full"
    >
      <div className="mx-auto max-w-7xl">
        <div className="text-center mb-10">
          <span className="inline-block bg-sky-50 border border-sky-200 text-sky-600 text-xs font-semibold px-3 py-1 rounded-full mb-3">
            Harga Langganan
          </span>
          <h2 className="text-3xl font-bold text-gray-900">
            Pilih Paket Sesuai Kebutuhan Bisnis
          </h2>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {[0, 1].map((idx) => (
            <div
              key={idx}
              className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm animate-pulse"
            >
              <div className="h-6 w-1/2 rounded bg-gray-200 mb-4" />
              <div className="h-4 w-2/3 rounded bg-gray-100 mb-6" />
              <div className="space-y-2">
                <div className="h-3 rounded bg-gray-100" />
                <div className="h-3 rounded bg-gray-100" />
                <div className="h-3 w-4/5 rounded bg-gray-100" />
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
