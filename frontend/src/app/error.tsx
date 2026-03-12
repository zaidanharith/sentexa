"use client";

import { useEffect } from "react";
import Link from "next/link";
import Footer from "@/components/layout/Footer";
import Navbar from "@/components/layout/Navbar";

interface ErrorWithStatus extends Error {
  statusCode?: number;
  status?: number;
  digest?: string;
}

interface ErrorPageProps {
  error: ErrorWithStatus;
  reset: () => void;
}

export default function ErrorPage({ error, reset }: ErrorPageProps) {
  const statusCode = error.statusCode ?? error.status ?? 500;
  const errorName = error.name ?? "Error";
  const errorMessage =
    error.message ?? "Terjadi kesalahan yang tidak terduga. Silakan coba lagi.";

  useEffect(() => {
    console.error(error);
  }, [error]);

  return (
    <>
      <Navbar />
      <div className="py-24 flex flex-col items-center justify-center bg-white px-6">
        <div className="w-full max-w-lg text-center space-y-6">
          <div className="inline-flex items-center justify-center w-24 h-24 rounded-full bg-sky-50 border-2 border-sky-100 mx-auto">
            <span className="text-3xl font-extrabold text-sky-500">
              {statusCode}
            </span>
          </div>

          <h1 className="text-2xl font-bold text-gray-900">{errorName}</h1>

          <div className="w-12 h-1 rounded-full bg-sky-400 mx-auto" />

          <div className="bg-gray-50 border border-gray-200 rounded-xl px-6 py-4 text-left">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-1">
              Detail
            </p>
            <p className="text-sm text-gray-700 leading-relaxed wrap-break-word">
              {errorMessage}
            </p>
            {error.digest && (
              <p className="text-xs text-gray-400 mt-2 font-mono">
                Digest: {error.digest}
              </p>
            )}
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <button
              onClick={reset}
              className="w-full sm:w-auto bg-sky-500 text-white text-sm font-semibold px-6 py-2.5 rounded-lg hover:bg-sky-600 transition-colors cursor-pointer"
            >
              Coba Lagi
            </button>
            <Link
              href="/"
              className="w-full sm:w-auto border border-gray-300 text-gray-700 text-sm font-semibold px-6 py-2.5 rounded-lg hover:border-sky-500 hover:text-sky-500 transition-colors text-center"
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
