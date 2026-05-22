"use client";

import { useEffect, useMemo, useState, useCallback } from "react";
import axios, { AxiosError } from "axios";
import { useSession } from "next-auth/react";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";
import { appToast } from "@/lib/toast";
import { isPremiumSubscription } from "@/lib/subscription";
import { UpgradeAlert } from "@/components/layout/dashboard/analysis/UpgradeAlert";
import {
  FaArrowLeft,
  FaArrowRight,
  FaDownload,
  FaTrash,
  FaPlus,
  FaPen,
} from "react-icons/fa6";

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

  // States for Create Report Modal
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: "",
    description: "",
    format: "pdf",
    sourceType: "date_range",
    startDate: "",
    endDate: "",
    jobId: "",
  });
  const [jobs, setJobs] = useState<any[]>([]);
  const [loadingJobs, setLoadingJobs] = useState(false);
  const [submittingCreate, setSubmittingCreate] = useState(false);

  // States for Edit Report Modal
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [selectedReport, setSelectedReport] = useState<Report | null>(null);
  const [editForm, setEditForm] = useState({
    title: "",
    description: "",
  });
  const [submittingEdit, setSubmittingEdit] = useState(false);

  // State for Delete Confirmation Modal
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [reportToDelete, setReportToDelete] = useState<Report | null>(null);

  const isPremium = isPremiumSubscription(session?.user?.subscription_plan);
  const totalPages = Math.max(1, Math.ceil(totalCount / PAGE_SIZE));

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://localhost:8000/api";

  const fetchReports = useCallback(async (showLoading = true) => {
    const accessToken = session?.user?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    const isPremium = isPremiumSubscription(session?.user?.subscription_plan);
    if (!isPremium) {
      setError("Fitur Laporan hanya tersedia untuk pengguna Premium.");
      return;
    }

    if (showLoading) setLoading(true);
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

      setItems(response.data.items ?? []);
      setTotalCount(response.data.count ?? 0);
    } catch (err) {
      const apiError = err as AxiosError;
      const message =
        typeof apiError.response?.data === "string"
          ? apiError.response?.data
          : apiError.message || "Gagal memuat laporan.";
      setError(message);
      appToast.error("Gagal memuat laporan.");
    } finally {
      if (showLoading) setLoading(false);
    }
  }, [apiBaseUrl, currentPage, session?.user?.accessToken, session?.user?.subscription_plan, status]);

  useEffect(() => {
    fetchReports(true);
  }, [fetchReports]);

  // Polling for processing/draft reports
  useEffect(() => {
    const hasPendingReports = items.some(
      (item) => item.status === "processing" || item.status === "draft"
    );

    if (!hasPendingReports) return;

    const interval = setInterval(() => {
      fetchReports(false);
    }, 5000);

    return () => clearInterval(interval);
  }, [items, fetchReports]);

  const fetchJobs = async () => {
    const accessToken = session?.user?.accessToken;
    if (!accessToken) return;
    setLoadingJobs(true);
    try {
      const response = await axios.get(`${apiBaseUrl}/sentiment/predict/jobs`, {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      const completedJobs = (response.data.items ?? []).filter(
        (job: any) => job.status === "completed"
      );
      setJobs(completedJobs);
    } catch {
      appToast.error("Gagal memuat daftar job analisis sentimen.");
    } finally {
      setLoadingJobs(false);
    }
  };

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
      const response = await axios.get(
        `${apiBaseUrl}/reports/${report.id}/download`,
        {
          headers: {
            Authorization: `Bearer ${session?.user?.accessToken}`,
          },
          responseType: "blob",
        },
      );
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute(
        "download",
        `${report.title || `report_${report.id}`}.pdf`,
      );
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch {
      appToast.error("Gagal mengunduh laporan.");
    }
  };

  const handleDelete = (report: Report) => {
  // Open custom confirmation modal
  setReportToDelete(report);
  setIsDeleteModalOpen(true);
};

  // Perform actual deletion after user confirms in modal
  const confirmDelete = async () => {
  if (!reportToDelete) return;
  console.log('Confirm delete called for report id:', reportToDelete.id);
  try {
    await axios.delete(`${apiBaseUrl}/reports/${reportToDelete.id}`, {
      headers: { Authorization: `Bearer ${session?.user?.accessToken}` },
    });
    setItems((prev) => prev.filter((item) => item.id !== reportToDelete.id));
    setTotalCount((prev) => prev - 1);
    appToast.success("Laporan berhasil dihapus.");
  } catch (error) {
    console.error('Delete error:', error);
    appToast.error("Gagal menghapus laporan.");
  } finally {
    setIsDeleteModalOpen(false);
    setReportToDelete(null);
  }
};

  const handleEditClick = (report: Report) => {
    setSelectedReport(report);
    setEditForm({
      title: report.title,
      description: report.description ?? "",
    });
    setIsEditModalOpen(true);
  };

  const handleEditSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedReport) return;
    if (!editForm.title.trim()) {
      appToast.error("Judul laporan tidak boleh kosong.");
      return;
    }
    setSubmittingEdit(true);
    try {
      const response = await axios.patch(
        `${apiBaseUrl}/reports/${selectedReport.id}`,
        {
          title: editForm.title.trim(),
          description: editForm.description.trim() || null,
        },
        {
          headers: {
            Authorization: `Bearer ${session?.user?.accessToken}`,
          },
        }
      );
      
      setItems((prev) =>
        prev.map((item) =>
          item.id === selectedReport.id ? response.data.report : item
        )
      );
      
      appToast.success("Laporan berhasil diperbarui.");
      setIsEditModalOpen(false);
    } catch {
      appToast.error("Gagal memperbarui laporan.");
    } finally {
      setSubmittingEdit(false);
    }
  };

  const handleCreateSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!createForm.title.trim()) {
      appToast.error("Judul laporan tidak boleh kosong.");
      return;
    }
    
    const payload: any = {
      title: createForm.title.trim(),
      description: createForm.description.trim() || null,
      format: createForm.format,
    };
    
    if (createForm.sourceType === "job") {
      if (!createForm.jobId) {
        appToast.error("Silakan pilih Job ID analisis sentimen.");
        return;
      }
      payload.job_id = createForm.jobId;
    } else {
      if (!createForm.startDate && !createForm.endDate) {
        appToast.error("Silakan tentukan setidaknya tanggal mulai atau tanggal selesai.");
        return;
      }
      if (createForm.startDate) {
        payload.start_date = new Date(createForm.startDate).toISOString();
      }
      if (createForm.endDate) {
        payload.end_date = new Date(createForm.endDate).toISOString();
      }
    }
    
    setSubmittingCreate(true);
    try {
      await axios.post(
        `${apiBaseUrl}/reports/generate`,
        payload,
        {
          headers: {
            Authorization: `Bearer ${session?.user?.accessToken}`,
          },
        }
      );
      
      fetchReports(true);
      appToast.success("Pembuatan laporan berhasil dimulai.");
      setIsCreateModalOpen(false);
      setCreateForm({
        title: "",
        description: "",
        format: "pdf",
        sourceType: "date_range",
        startDate: "",
        endDate: "",
        jobId: "",
      });
    } catch (err: any) {
      const message = err.response?.data?.detail || "Gagal membuat laporan baru.";
      appToast.error(message);
    } finally {
      setSubmittingCreate(false);
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
        {!isPremium && <UpgradeAlert />}
        <div className="flex flex-col gap-4">
          <div className="flex items-center justify-between">
            <div className="flex-1 max-w-md">
              <input
                type="text"
                placeholder="Cari laporan..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!isPremium}
              />
            </div>
            <button
              className="flex items-center gap-2 px-4 py-2 bg-sky-500 text-white rounded-md hover:bg-sky-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={!isPremium}
              onClick={() => {
                if (isPremium) {
                  setIsCreateModalOpen(true);
                }
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
                  <th className="text-left py-3 px-4 font-semibold">
                    Diperbarui
                  </th>
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
                      {searchTerm
                        ? "Tidak ada laporan yang cocok dengan pencarian."
                        : "Belum ada laporan."}
                    </td>
                  </tr>
                ) : (
                  filteredItems.map((item) => (
                    <tr
                      key={item.id}
                      className="border-b border-gray-100 hover:bg-gray-50"
                    >
                      <td className="py-3 px-4">
                        <div>
                          <div className="font-medium">{item.title}</div>
                          {item.description && (
                            <div className="text-gray-500 text-xs mt-1">
                              {item.description}
                            </div>
                          )}
                        </div>
                      </td>
                      <td className="py-3 px-4 uppercase text-xs font-medium">
                        {item.format}
                      </td>
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
                      <td className="py-3 px-4 text-gray-600">
                        {formatDate(item.created_at)}
                      </td>
                      <td className="py-3 px-4 text-gray-600">
                        {formatDate(item.updated_at)}
                      </td>
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
                            onClick={() => handleEditClick(item)}
                            className="p-1 text-yellow-600 hover:text-yellow-800 transition-colors"
                            title="Edit"
                          >
                            <FaPen className="w-4 h-4" />
                          </button>
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
                Menampilkan{" "}
                {Math.min((currentPage - 1) * PAGE_SIZE + 1, totalCount)} -{" "}
                {Math.min(currentPage * PAGE_SIZE, totalCount)} dari{" "}
                {totalCount} laporan
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() =>
                    setCurrentPage((prev) => Math.max(1, prev - 1))
                  }
                  disabled={currentPage === 1}
                  className="p-2 rounded-md border border-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <FaArrowLeft className="w-4 h-4" />
                </button>
                <span className="text-sm">
                  Halaman {currentPage} dari {totalPages}
                </span>
                <button
                  onClick={() =>
                    setCurrentPage((prev) => Math.min(totalPages, prev + 1))
                  }
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

      {/* Create Report Modal */}
      {isCreateModalOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setIsCreateModalOpen(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-lg border border-slate-100 overflow-hidden flex flex-col max-h-[90vh] animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-slate-50 border-b border-slate-100 px-6 py-4 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-slate-800">
                  Buat Laporan Baru
                </h3>
                <p className="text-xs text-slate-500">
                  Konfigurasikan kriteria data untuk laporan analisis Anda
                </p>
              </div>
              <button
                onClick={() => setIsCreateModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-lg transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleCreateSubmit} className="flex flex-col overflow-y-auto p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">
                  Judul Laporan <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  placeholder="Contoh: Analisis Sentimen Q2 2026"
                  value={createForm.title}
                  onChange={(e) =>
                    setCreateForm((prev) => ({ ...prev, title: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm text-slate-800"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">
                  Deskripsi
                </label>
                <textarea
                  placeholder="Tambahkan catatan tambahan mengenai laporan ini..."
                  value={createForm.description}
                  onChange={(e) =>
                    setCreateForm((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  rows={2}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm text-slate-800"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">
                    Format Laporan
                  </label>
                  <select
                    value={createForm.format}
                    onChange={(e) =>
                      setCreateForm((prev) => ({ ...prev, format: e.target.value }))
                    }
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm bg-white text-slate-800"
                  >
                    <option value="pdf">PDF</option>
                    <option value="csv">CSV</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-semibold text-slate-700 mb-1">
                    Sumber Data
                  </label>
                  <select
                    value={createForm.sourceType}
                    onChange={(e) => {
                      const type = e.target.value;
                      setCreateForm((prev) => ({ ...prev, sourceType: type }));
                      if (type === "job" && jobs.length === 0) {
                        fetchJobs();
                      }
                    }}
                    className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm bg-white text-slate-800"
                  >
                    <option value="date_range">Rentang Tanggal</option>
                    <option value="job">Sentiment Job ID</option>
                  </select>
                </div>
              </div>

              {createForm.sourceType === "date_range" ? (
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
                  <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Rentang Waktu Analisis
                  </h4>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">
                        Tanggal Mulai
                      </label>
                      <input
                        type="datetime-local"
                        value={createForm.startDate}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            startDate: e.target.value,
                          }))
                        }
                        className="w-full px-3 py-1.5 border border-slate-200 rounded-md focus:outline-none text-xs text-slate-800"
                      />
                    </div>
                    <div>
                      <label className="block text-xs font-medium text-slate-500 mb-1">
                        Tanggal Selesai
                      </label>
                      <input
                        type="datetime-local"
                        value={createForm.endDate}
                        onChange={(e) =>
                          setCreateForm((prev) => ({
                            ...prev,
                            endDate: e.target.value,
                          }))
                        }
                        className="w-full px-3 py-1.5 border border-slate-200 rounded-md focus:outline-none text-xs text-slate-800"
                      />
                    </div>
                  </div>
                  <p className="text-[10px] text-slate-400">
                    Laporan akan mencakup semua data analisis sentimen Anda dalam periode yang dipilih.
                  </p>
                </div>
              ) : (
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-3">
                  <h4 className="text-xs font-bold text-slate-600 uppercase tracking-wider">
                    Pilih Job Analisis
                  </h4>
                  <div>
                    <label className="block text-xs font-medium text-slate-500 mb-1">
                      Job ID Analisis Batch <span className="text-red-500">*</span>
                    </label>
                    {loadingJobs ? (
                      <div className="text-xs text-slate-500 py-2">
                        Memuat daftar job...
                      </div>
                    ) : jobs.length === 0 ? (
                      <div className="text-xs text-amber-600 py-2">
                        Tidak ditemukan job analisis yang selesai. Pastikan Anda sudah menjalankan analisis batch terlebih dahulu.
                      </div>
                    ) : (
                      <select
                        value={createForm.jobId}
                        onChange={(e) =>
                          setCreateForm((prev) => ({ ...prev, jobId: e.target.value }))
                        }
                        className="w-full px-3 py-2 border border-slate-200 rounded-md focus:outline-none text-xs bg-white text-slate-800 animate-in fade-in duration-200"
                        required
                      >
                        <option value="">-- Pilih Job Sentimen --</option>
                        {jobs.map((job) => (
                          <option key={job.job_id} value={job.job_id}>
                            ID: {job.job_id.substring(0, 8)}... ({formatDate(job.created_at)}) - {job.total} Data
                          </option>
                        ))}
                      </select>
                    )}
                  </div>
                </div>
              )}

              {/* Modal Footer */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsCreateModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 text-sm font-medium transition-colors cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={
                    submittingCreate ||
                    (createForm.sourceType === "job" && !createForm.jobId) ||
                    (createForm.sourceType === "date_range" &&
                      !createForm.startDate &&
                      !createForm.endDate)
                  }
                  className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submittingCreate ? "Membuat..." : "Generate Laporan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Report Modal */}
      {isEditModalOpen && selectedReport && (
        <div
          className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4 animate-in fade-in duration-200"
          onClick={() => setIsEditModalOpen(false)}
        >
          <div
            className="bg-white rounded-2xl shadow-2xl w-full max-w-md border border-slate-100 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="bg-slate-50 border-b border-slate-100 px-6 py-4 flex justify-between items-center">
              <div>
                <h3 className="text-lg font-bold text-slate-800">
                  Ubah Detail Laporan
                </h3>
                <p className="text-xs text-slate-500">
                  Perbarui judul atau deskripsi dari laporan ini
                </p>
              </div>
              <button
                onClick={() => setIsEditModalOpen(false)}
                className="text-slate-400 hover:text-slate-600 text-lg transition-colors cursor-pointer"
              >
                ✕
              </button>
            </div>

            {/* Modal Body */}
            <form onSubmit={handleEditSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">
                  Judul Laporan <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  required
                  value={editForm.title}
                  onChange={(e) =>
                    setEditForm((prev) => ({ ...prev, title: e.target.value }))
                  }
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm text-slate-800"
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-slate-700 mb-1">
                  Deskripsi
                </label>
                <textarea
                  value={editForm.description}
                  onChange={(e) =>
                    setEditForm((prev) => ({
                      ...prev,
                      description: e.target.value,
                    }))
                  }
                  rows={3}
                  className="w-full px-3 py-2 border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500/20 focus:border-sky-500 transition text-sm text-slate-800"
                />
              </div>

              {/* Modal Footer */}
              <div className="pt-4 border-t border-slate-100 flex items-center justify-end gap-2">
                <button
                  type="button"
                  onClick={() => setIsEditModalOpen(false)}
                  className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50 text-sm font-medium transition-colors cursor-pointer"
                >
                  Batal
                </button>
                <button
                  type="submit"
                  disabled={submittingEdit || !editForm.title.trim()}
                  className="px-4 py-2 bg-sky-500 hover:bg-sky-600 text-white rounded-lg text-sm font-medium transition-colors flex items-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submittingEdit ? "Menyimpan..." : "Simpan Perubahan"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
      {/* Delete Confirmation Modal */}
      {isDeleteModalOpen && reportToDelete && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-xs flex items-center justify-center p-4"
          onClick={() => {
            setIsDeleteModalOpen(false);
            setReportToDelete(null);
          }}>
          <div className="bg-white rounded-2xl shadow-2xl w-full max-w-sm border border-slate-100 overflow-hidden flex flex-col animate-in fade-in zoom-in-95 duration-200"
            onClick={e => e.stopPropagation()}>
            <div className="bg-slate-50 border-b border-slate-100 px-6 py-4 flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-800">Konfirmasi Hapus</h3>
              <button onClick={() => {
                setIsDeleteModalOpen(false);
                setReportToDelete(null);
              }} className="text-slate-400 hover:text-slate-600 text-lg transition-colors cursor-pointer">✕</button>
            </div>
            <div className="p-6">
              <p className="mb-4">Apakah Anda yakin ingin menghapus laporan “{reportToDelete.title}”?</p>
              <div className="flex justify-end gap-2">
                <button onClick={() => {
                  setIsDeleteModalOpen(false);
                  setReportToDelete(null);
                }} className="px-4 py-2 border border-slate-200 text-slate-600 rounded-lg hover:bg-slate-50">Batal</button>
                <button onClick={confirmDelete} className="px-4 py-2 bg-red-500 hover:bg-red-600 text-white rounded-lg">
                  Hapus
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
