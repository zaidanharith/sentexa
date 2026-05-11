"use client";

import { useEffect, useMemo, useState } from "react";
import axios, { AxiosError } from "axios";
import { useSession } from "next-auth/react";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";
import { appToast } from "@/lib/toast";
import { FaArrowLeft, FaArrowRight, FaDownload, FaTrash, FaPlus } from "react-icons/fa6";

type Report = {
  id: number;
  title: string;
  description?: string;
  job_id?: string;
  start_date?: string;
  end_date?: string;
  format: string;
  status: string;
  file_path?: string;
  created_at: string;
  updated_at: string;
};

type ReportsResponse = {
  items: Report[];
  count: number;
  offset: number;
  limit: number;
};

const PAGE_SIZE = 10;

export default function ReportsDashboardPage() {
  const { data: session, status } = useSession();
  const [items, setItems] = useState<Report[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [currentPage, setCurrentPage] = useState(1);

  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://localhost:8000/api";

  useEffect(() => {
    const accessToken = session?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    let isActive = true;
    const fetchReports = async () => {
      setLoading(true);
      setError(null);
      try {
        const offset = (currentPage - 1) * PAGE_SIZE;
        const response = await axios.get<ReportsResponse>(
          `${apiBaseUrl}/reports`,
          {
            params: { offset, limit: PAGE_SIZE },
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        );

        if (!isActive) {
          return;
        }

        setItems(response.data.items ?? []);
        setTotalCount(response.data.count ?? 0);
      } catch (err) {
        if (!isActive) {
          return;
        }

        const apiError = err as AxiosError;
        const message =
          typeof apiError.response?.data === "string"
            ? apiError.response?.data
            : apiError.message || "Gagal memuat laporan.";
        setError(message);
        appToast.error("Gagal memuat laporan.");
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    fetchReports();
    return () => {
      isActive = false;
    };
  }, [apiBaseUrl, currentPage, session?.accessToken, status]);

  const filteredItems = useMemo(() => {
    const normalizedSearch = searchTerm.trim().toLowerCase();
    if (!normalizedSearch) {
      return items;
    }

    return items.filter((item) => {
      const title = item.title ?? "";
      const description = item.description ?? "";
      return (
        title.toLowerCase().includes(normalizedSearch) ||
        description.toLowerCase().includes(normalizedSearch)
      );
    });
  }, [items, searchTerm]);

  const formatDate = (value: string) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "-";
    }
    return date.toLocaleDateString("id-ID", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handleDownload = async (report: Report) => {
    if (!report.file_path) {
      appToast.error("File tidak tersedia untuk diunduh.");
      return;
    }
    if (report.format !== "pdf") {
      appToast.error("Laporan hanya tersedia dalam format PDF.");
      return;
    }
    try {
      const response = await axios.get(`${apiBaseUrl}/reports/${report.id}/download`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
        responseType: "blob",
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `${report.title || `report_${report.id}`}.pdf`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      appToast.error("Gagal mengunduh laporan.");
    }
  };

  const handleDelete = async (report: Report) => {
    if (!confirm(`Apakah Anda yakin ingin menghapus laporan "${report.title}"?`)) {
      return;
    }
    try {
      await axios.delete(`${apiBaseUrl}/reports/${report.id}`, {
        headers: {
          Authorization: `Bearer ${session?.accessToken}`,
        },
      });
      setItems((prev) => prev.filter((item) => item.id !== report.id));
      setTotalCount((prev) => prev - 1);
      appToast.success("Laporan berhasil dihapus.");
    } catch (err) {
      appToast.error("Gagal menghapus laporan.");
    }
  };

  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle
        title="Laporan"
        subtitle="Kelola laporan analisis Anda"
        isPremiumOnly={true}
      />

      <DashboardPageContent>
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder="Cari laporan..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <button
              className="flex items-center gap-2 px-4 py-2 bg-sky-500 text-white rounded-md hover:bg-sky-700 transition-colors"
              onClick={() => {
                appToast.info("Fitur buat laporan baru akan segera hadir.");
              }}
            >
              <FaPlus className="w-4 h-4" />
              Buat Laporan Baru
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-sm border-collapse">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-3 px-4 font-semibold">Judul</th>
                  <th className="text-left py-3 px-4 font-semibold">Format</th>
                  <th className="text-left py-3 px-4 font-semibold">Status</th>
                  <th className="text-left py-3 px-4 font-semibold">Dibuat</th>
                  <th className="text-left py-3 px-4 font-semibold">Diperbarui</th>
                  <th className="text-center py-3 px-4 font-semibold">Aksi</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-500">
                      Memuat laporan...
                    </td>
                  </tr>
                ) : error ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-red-500">
                      {error}
                    </td>
                  </tr>
                ) : filteredItems.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="text-center py-8 text-gray-500">
                      {searchTerm ? "Tidak ada laporan yang cocok dengan pencarian." : "Belum ada laporan."}
                    </td>
                  </tr>
                ) : (
                  filteredItems.map((item) => (
                    <tr key={item.id} className="border-b border-gray-100 hover:bg-gray-50">
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{item.title}</div>
                          {item.description && (
                            <div className="text-gray-500 text-xs mt-1">{item.description}</div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 uppercase text-xs font-medium">{item.format}</td>
                      <td className="py-3 px-4">
                        <span
                          className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                            item.status === "completed"
                              ? "bg-green-100 text-green-800"
                              : item.status === "processing"
                              ? "bg-yellow-100 text-yellow-800"
                              : item.status === "failed"
                              ? "bg-red-100 text-red-800"
                              : "bg-gray-100 text-gray-800"
                          }`}
                        >
                          {item.status === "completed"
                            ? "Selesai"
                            : item.status === "processing"
                            ? "Diproses"
                            : item.status === "failed"
                            ? "Gagal"
                            : item.status}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-gray-600">{formatDate(item.created_at)}</td>
                      <td className="py-3 px-4 text-gray-600">{formatDate(item.updated_at)}</td>
                      <td className="py-3 px-4">
                        <div className="flex items-center justify-center gap-2">
                          {item.status === "completed" && item.file_path && (
                            <button
                              onClick={() => handleDownload(item)}
                              className="p-1 text-sky-500 hover:text-sky-700 transition-colors"
                              title="Unduh"
                            >
                              <FaDownload className="w-4 h-4" />
                            </button>
                          )}
                          <button
                            onClick={() => handleDelete(item)}
                            className="p-1 text-red-600 hover:text-red-800 transition-colors"
                            title="Hapus"
                          >
                            <FaTrash className="w-4 h-4" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between">
              <div className="text-sm text-gray-500">
                Menampilkan {Math.min((currentPage - 1) * PAGE_SIZE + 1, totalCount)} -{" "}
                {Math.min(currentPage * PAGE_SIZE, totalCount)} dari {totalCount} laporan
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setCurrentPage((prev) => Math.max(1, prev - 1))}
                  disabled={currentPage === 1}
                  className="p-2 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaArrowLeft className="w-4 h-4" />
                </button>
                <span className="text-sm">
                  Halaman {currentPage} dari {totalPages}
                </span>
                <button
                  onClick={() => setCurrentPage((prev) => Math.min(totalPages, prev + 1))}
                  disabled={currentPage === totalPages}
                  className="p-2 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaArrowRight className="w-4 h-4" />
                </button>
              </div>
            </div>
          )}
        </div>
      </DashboardPageContent>
    </main>
  );
}
