"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { AuthUser } from "@/context/AuthContext";
import { backendAuthApi } from "@/lib/api";
import { useSession } from "next-auth/react";

// 1. Komponen Induk (Handling Auth & Loading)
export default function ProfilePage() {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Memuat data profil...</p>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="min-h-screen bg-gray-50 flex items-center justify-center">
        <p className="text-gray-500">Silakan login terlebih dahulu</p>
      </main>
    );
  }

  // Jika user ada, render konten form profil dan teruskan data user
  return <ProfileContent user={user} />;
}

// 2. Komponen Anak (Isi Profil)
// Catatan: Jika kamu punya tipe TypeScript untuk user, ganti 'any' dengan tipe tersebut.
function ProfileContent({ user }: { user: AuthUser }) {
  const router = useRouter();
  const { data: session } = useSession();
  const [isEditing, setIsEditing] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Inisialisasi state LANGSUNG menggunakan data user (TANPA useEffect)
  const nameParts = user.name ? user.name.split(" ") : [];
  const [formData, setFormData] = useState({
    firstName: nameParts[0] || "",
    lastName: nameParts.slice(1).join(" ") || "",
    email: user.email || "",
  });

  const handleSaveProfile = async () => {
    if (!session?.accessToken) {
      setError("Access token tidak ditemukan");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await backendAuthApi.updateProfile(session.accessToken, formData);
      setIsEditing(false);
      // Refresh page untuk update data user
      router.refresh();
      alert("Profil berhasil diperbarui!");
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "Gagal memperbarui profil";
      setError(errorMessage);
    } finally {
      setIsSaving(false);
    }
  };

  const getUserInitial = () => user.name?.charAt(0).toUpperCase() || "U";
  const getNameDisplay = () => user.name || "Pengguna";
  const getPlanBadge = () => {
    if (user.subscription?.toLowerCase().includes("premium")) {
      return "Premium";
    }
    return "Free Plan";
  };

  return (
    <main className="min-h-screen bg-gray-50 py-10 px-4 sm:px-6">
      <div className="pb-16 md:pb-0 max-w-3xl mx-auto">
        {/* ── Header ── */}
        <div className="mb-6">
          <h2 className="text-xl font-semibold text-gray-800">
            Profil Pengguna
          </h2>
          <p className="text-xs text-gray-500 italic mt-0.5">
            [ Kelola akun dan informasi bisnis Anda ]
          </p>
        </div>

        {/* ── Profile summary card ── */}
        <div className="border border-gray-300 bg-white p-5 mb-5 flex flex-col sm:flex-row gap-4 items-start shadow-sm rounded-md">
          {/* Avatar */}
          <div className="flex flex-col items-center gap-2">
            <div className="w-20 h-20 border-2 border-dashed border-gray-400 bg-blue-100 flex items-center justify-center text-2xl font-bold text-blue-600 rounded-full">
              {getUserInitial()}
            </div>
          </div>
          {/* Info */}
          <div className="flex-1">
            <div className="flex flex-wrap items-center gap-2 mb-1">
              <h3 className="text-lg font-medium text-gray-800">
                {getNameDisplay()}
              </h3>
              <span className="px-2 py-0.5 bg-gray-100 border border-gray-300 text-xs rounded text-gray-600">
                {getPlanBadge()}
              </span>
            </div>
            <p className="text-sm text-gray-500">{user.email}</p>
            {user.subscription && (
              <p className="text-xs text-gray-400 mt-1">
                Paket: {user.subscription}
              </p>
            )}
          </div>
        </div>

        {/* ── Edit profile form ── */}
        <div className="border border-gray-300 bg-white p-5 mb-4 shadow-sm rounded-md">
          <h3 className="font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">
            Edit Informasi Profil
          </h3>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded text-sm text-red-600">
              {error}
            </div>
          )}

          <div className="grid sm:grid-cols-2 gap-3 mb-3">
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 mb-1">Nama Depan</label>
              <input
                type="text"
                value={formData.firstName}
                onChange={(e) =>
                  setFormData({ ...formData, firstName: e.target.value })
                }
                placeholder="Nama depan"
                className="border border-gray-300 p-2 text-sm rounded outline-none focus:border-gray-500 disabled:bg-gray-50 disabled:text-gray-500"
                disabled={!isEditing || isSaving}
              />
            </div>
            <div className="flex flex-col">
              <label className="text-xs text-gray-600 mb-1">
                Nama Belakang
              </label>
              <input
                type="text"
                value={formData.lastName}
                onChange={(e) =>
                  setFormData({ ...formData, lastName: e.target.value })
                }
                placeholder="Nama belakang"
                className="border border-gray-300 p-2 text-sm rounded outline-none focus:border-gray-500 disabled:bg-gray-50 disabled:text-gray-500"
                disabled={!isEditing || isSaving}
              />
            </div>
          </div>
          <div className="flex flex-col mb-3">
            <label className="text-xs text-gray-600 mb-1">Alamat Email</label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) =>
                setFormData({ ...formData, email: e.target.value })
              }
              placeholder="Email"
              className="border border-gray-300 p-2 text-sm rounded outline-none focus:border-gray-500 disabled:bg-gray-50 disabled:text-gray-500"
              disabled={!isEditing || isSaving}
            />
          </div>
          <div className="flex justify-end gap-2">
            {!isEditing ? (
              <button
                onClick={() => setIsEditing(true)}
                className="px-4 py-2 text-sm bg-sky-600 text-white rounded hover:bg-sky-700 transition-colors cursor-pointer"
              >
                Edit Profil
              </button>
            ) : (
              <>
                <button
                  onClick={() => {
                    setIsEditing(false);
                    setError(null);
                  }}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm border border-gray-300 text-gray-700 rounded hover:bg-gray-50 transition-colors disabled:opacity-50"
                >
                  Batal
                </button>
                <button
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 transition-colors disabled:opacity-50"
                >
                  {isSaving ? "Menyimpan..." : "Simpan Perubahan"}
                </button>
              </>
            )}
          </div>
        </div>

        {/* ── Status Langganan ── */}
        <div className="border border-gray-300 bg-white p-5 mb-4 shadow-sm rounded-md">
          <h3 className="font-semibold text-gray-800 mb-4 border-b border-gray-100 pb-2">
            Status Langganan
          </h3>
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <div>
              <div className="flex items-center gap-2 mb-1">
                <p className="text-sm font-medium text-gray-800">
                  {user.subscription || "Free Plan"}
                </p>
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded border border-green-200">
                  Aktif
                </span>
              </div>
              <p className="text-xs text-gray-500">
                {user.subscription
                  ? "Kadaluarsa: [Tanggal]"
                  : "Tidak ada tanggal kadaluarsa"}
              </p>
            </div>
            <button
              onClick={() => router.push("/pricing")}
              className="px-4 py-2 text-sm bg-gray-800 text-white rounded hover:bg-gray-700 transition-colors"
            >
              Upgrade ke Premium →
            </button>
          </div>
        </div>
      </div>
    </main>
  );
}
