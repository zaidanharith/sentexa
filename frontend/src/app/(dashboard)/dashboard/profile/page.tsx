"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { AuthUser } from "@/context/AuthContext";
import { backendAuthApi } from "@/lib/api";
import { getSubscriptionName, isPremiumSubscription } from "@/lib/subscription";
import { appToast } from "@/lib/toast";
import { useSession } from "next-auth/react";
import {
  HiOutlineCheckCircle,
  HiOutlinePencilSquare,
  HiOutlineShieldCheck,
} from "react-icons/hi2";
import { GrUpgrade } from "react-icons/gr";

export default function ProfilePage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <main className="min-h-[70vh] bg-linear-to-b from-slate-50 via-white to-sky-50/40 flex items-center justify-center px-4">
        <div className="rounded-2xl border border-gray-200 bg-white/90 px-6 py-4 text-sm text-gray-600 shadow-sm">
          Memuat data profil...
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="min-h-[70vh] bg-linear-to-b from-slate-50 via-white to-sky-50/40 flex items-center justify-center px-4">
        <div className="rounded-2xl border border-gray-200 bg-white/90 px-6 py-4 text-sm text-gray-600 shadow-sm">
          Silakan login terlebih dahulu
        </div>
      </main>
    );
  }

  return <ProfileContent user={user} />;
}

function ProfileContent({ user }: { user: AuthUser }) {
  const router = useRouter();
  const { data: session, update: updateSession } = useSession();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  const nameParts = user.name ? user.name.split(" ") : [];
  const [formData, setFormData] = useState({
    firstName: nameParts[0] || "",
    lastName: nameParts.slice(1).join(" ") || "",
    email: user.email || "",
  });

  const handleSaveProfile = async () => {
    setIsSaving(true);

    try {
      const latestSession = await updateSession();
      const accessToken = latestSession?.accessToken ?? session?.accessToken;

      if (!accessToken) {
        appToast.warning("Sesi login sudah berakhir. Silakan login kembali.");
        return;
      }

      await backendAuthApi.updateProfile(accessToken, formData);
      await updateSession();
      setIsEditing(false);
      router.refresh();
      appToast.success("Profil berhasil diperbarui.");
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Gagal memperbarui profil";
      appToast.error(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  const displayName = user.name || "Pengguna";
  const avatarInitial = displayName.charAt(0).toUpperCase() || "U";
  const hasPremium = isPremiumSubscription(user.subscription);
  const planName = getSubscriptionName(user.subscription);

  return (
    <main className="bg-linear-to-b from-slate-50 via-white to-sky-50/50 py-6 sm:py-10 px-4 sm:px-6">
      <div className="mx-auto max-w-4xl pb-16 md:pb-0 space-y-5">
        <section className="relative overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
          <div className="relative p-6 sm:p-8 flex flex-col sm:flex-row gap-5 sm:items-center sm:justify-between">
            <div className="flex items-center gap-4">
              <div className="h-20 w-20 rounded-2xl bg-sky-100 text-sky-700 text-3xl font-extrabold flex items-center justify-center ring-4 ring-white shadow-sm">
                {avatarInitial}
              </div>
              <div>
                <h2 className="text-2xl font-bold text-slate-900">
                  {displayName}
                </h2>
                <p className="text-sm text-slate-500">{user.email}</p>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              <span
                className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-semibold border ${
                  hasPremium
                    ? "border-amber-200 bg-amber-50 text-amber-700"
                    : "border-slate-200 bg-slate-100 text-slate-600"
                }`}
              >
                <HiOutlineShieldCheck className="h-4 w-4" />
                {planName}
              </span>
              <span className="inline-flex items-center gap-1 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700">
                <HiOutlineCheckCircle className="h-4 w-4" />
                Aktif
              </span>
            </div>
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <div className="mb-5 flex items-center justify-between gap-3 border-b border-slate-100 pb-4">
            <div>
              <h3 className="text-base sm:text-lg font-semibold text-slate-900">
                Edit Informasi Profil
              </h3>
              <p className="mt-0.5 text-xs text-slate-500">
                Ubah nama dan email akun Anda.
              </p>
            </div>
          </div>

          <div className="grid sm:grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col">
              <label className="text-xs font-medium text-slate-600 mb-1.5">
                Nama Depan
              </label>
              <input
                type="text"
                value={formData.firstName}
                onChange={(e) =>
                  setFormData({ ...formData, firstName: e.target.value })
                }
                placeholder="Nama depan"
                className="h-10 rounded-lg border border-slate-300 px-3 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:bg-slate-50 disabled:text-slate-500"
                disabled={!isEditing || isSaving}
              />
            </div>
            <div className="flex flex-col">
              <label className="text-xs font-medium text-slate-600 mb-1.5">
                Nama Belakang
              </label>
              <input
                type="text"
                value={formData.lastName}
                onChange={(e) =>
                  setFormData({ ...formData, lastName: e.target.value })
                }
                placeholder="Nama belakang"
                className="h-10 rounded-lg border border-slate-300 px-3 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:bg-slate-50 disabled:text-slate-500"
                disabled={!isEditing || isSaving}
              />
            </div>
          </div>
          <div className="flex flex-col mb-3">
            <label className="text-xs font-medium text-slate-600 mb-1.5">
              Alamat Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="Email"
              className="h-10 rounded-lg border border-slate-300 px-3 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100 disabled:bg-slate-50 disabled:text-slate-500"
              disabled={!isEditing || isSaving}
            />
          </div>
          <div className="flex flex-wrap justify-end gap-2 pt-1">
            {!isEditing ? (
              <button
                type="button"
                onClick={() => setIsEditing(true)}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-sky-600 text-white rounded-lg hover:bg-sky-700 transition-colors cursor-pointer"
              >
                <HiOutlinePencilSquare className="h-4 w-4" />
                Edit Profil
              </button>
            ) : (
              <>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm border cursor-pointer border-slate-300 text-slate-700 rounded-lg hover:bg-slate-50 transition-colors disabled:opacity-50"
                >
                  Batal
                </button>
                <button
                  type="button"
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="inline-flex items-center gap-2 px-4 py-2 text-sm bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors disabled:opacity-50 cursor-pointer"
                >
                  <HiOutlineCheckCircle className="h-4 w-4" />
                  {isSaving ? "Menyimpan..." : "Simpan Perubahan"}
                </button>
              </>
            )}
          </div>
        </section>

        <section className="rounded-2xl border border-slate-200 bg-white p-5 sm:p-6 shadow-sm">
          <h3 className="text-base sm:text-lg font-semibold text-slate-900 mb-4 border-b border-slate-300 pb-3">
            Status Langganan
          </h3>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="text-sm font-semibold text-slate-800">
                  {planName}
                </p>
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded border border-green-200">
                  Aktif
                </span>
              </div>
              <p className="text-xs text-slate-500">
                {hasPremium
                  ? "Kadaluarsa: [Tanggal]"
                  : "Akun Anda saat ini menggunakan paket gratis"}
              </p>
            </div>
            <button
              type="button"
              onClick={() => router.push("/dashboard/subscription")}
              className="px-4 py-2 text-sm cursor-pointer bg-slate-900 text-white rounded-lg hover:bg-slate-800 transition-colors flex items-center justify-center gap-2"
            >
              <GrUpgrade /> Upgrade ke Premium
            </button>
          </div>
        </section>
      </div>
    </main>
  );
}
