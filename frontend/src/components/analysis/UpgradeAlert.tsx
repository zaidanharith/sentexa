"use client";

import { useRouter } from "next/navigation";
import { FaLock } from "react-icons/fa";

export function UpgradeAlert() {
  const router = useRouter();

  const handleUpgrade = () => {
    router.push("/dashboard/subscription");
  };

  return (
    <div className="rounded-lg bg-linear-to-r from-amber-50 to-orange-50 border border-amber-200 p-4 mb-6">
      <div className="flex items-start gap-3">
        <div className="text-2xl text-amber-600 mt-1">
          <FaLock />
        </div>
        <div className="flex-1">
          <h3 className="font-semibold text-amber-900 mb-1">
            Fitur Upload File Hanya Tersedia di Premium
          </h3>
          <p className="text-sm text-amber-800 mb-3">
            Upgrade ke paket Premium untuk mendapatkan akses ke upload file CSV,
            XLS, atau XLSX dan fitur analisis batch.
          </p>
          <button
            onClick={handleUpgrade}
            className="text-sm font-semibold text-amber-600 hover:text-amber-700 transition-colors cursor-pointer"
          >
            Upgrade Sekarang →
          </button>
        </div>
      </div>
    </div>
  );
}
