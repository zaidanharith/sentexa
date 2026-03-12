"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";

export default function NotFoundPage() {
  const pathname = usePathname();
  return (
    <>
      <Navbar />
      <div className="py-24 flex flex-col items-center justify-center bg-white px-6">
        <div className="w-full max-w-lg text-center space-y-6">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-sky-50 border-2 border-sky-100 mx-auto">
            <span className="text-3xl font-extrabold text-sky-500">404</span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900">
            Halaman Tidak Ditemukan
          </h1>

          <div className="w-12 h-1 rounded-full bg-sky-400 mx-auto" />

          <div className="bg-gray-50 border border-gray-200 rounded-xl px-6 py-4">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">
              Detail
            </p>
            <p className="text-sm text-gray-700 leading-relaxed">
              Halaman yang kamu cari tidak ada atau telah dipindahkan. Periksa
              kembali URL yang kamu masukkan.
            </p>
            {pathname && (
              <p className="text-xs text-gray-400 mt-2 font-mono">
                Path: {pathname}
              </p>
            )}
          </div>

          <div className="flex items-center justify-center pt-2">
            <Link
              href="/"
              className="bg-sky-500 text-white text-sm font-semibold px-6 py-2.5 rounded-lg hover:bg-sky-600 transition-colors"
            >
              Kembali ke Beranda
            </Link>
          </div>
        </div>
      </div>
      <Footer />
    </>
  );
}
