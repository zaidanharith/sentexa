"use client";

import { useEffect, useMemo, useState } from "react";
import axios, { AxiosError } from "axios";
import { useSession } from "next-auth/react";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";
import { appToast } from "@/lib/toast";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa6";

type AnalysisPrediction = {
  label?: string;
  score?: number | null;
  scores?: Record<string, number> | null;
};

type AnalysisHistoryItem = {
  id: number;
  source_type: string;
  input_text: string | null;
  result_label: string | null;
  result_score: number | null;
  result_payload: AnalysisPrediction[] | Record<string, unknown> | null;
  status: string;
  created_at: string;
};

type AnalysisHistoryResponse = {
  items: AnalysisHistoryItem[];
  count: number;
  offset: number;
  limit: number;
};

type SortKey = "newest" | "oldest" | "score_desc" | "score_asc";

const PAGE_SIZE = 10;

const SENTIMENT_LABEL_MAP: Record<string, string> = {
  positive: "POSITIF",
  negative: "NEGATIF",
  neutral: "NETRAL",
};

export default function HistoryDashboardPage() {
  const { data: session, status } = useSession();
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("newest");
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);

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
    const fetchHistory = async () => {
      setLoading(true);
      setError(null);
      try {
        const offset = (currentPage - 1) * PAGE_SIZE;
        const response = await axios.get<AnalysisHistoryResponse>(
          `${apiBaseUrl}/analyses`,
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
            : apiError.message || "Gagal memuat riwayat analisis.";
        setError(message);
        appToast.error("Gagal memuat riwayat analisis.");
      } finally {
        if (isActive) {
          setLoading(false);
        }
      }
    };

    fetchHistory();
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
      const text = item.input_text ?? "";
      const label = item.result_label ?? "";
      return (
        text.toLowerCase().includes(normalizedSearch) ||
        label.toLowerCase().includes(normalizedSearch)
      );
    });
  }, [items, searchTerm]);

  const sortedItems = useMemo(() => {
    const nextItems = [...filteredItems];
    const scoreForItem = (item: AnalysisHistoryItem) => {
      if (item.source_type === "batch") {
        const predictions = Array.isArray(item.result_payload)
          ? item.result_payload
          : [];
        const firstScore = predictions[0]?.score;
        return typeof firstScore === "number" ? firstScore : -1;
      }
      return typeof item.result_score === "number" ? item.result_score : -1;
    };

    nextItems.sort((a, b) => {
      if (sortKey === "newest") {
        return (
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        );
      }
      if (sortKey === "oldest") {
        return (
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        );
      }
      if (sortKey === "score_desc") {
        return scoreForItem(b) - scoreForItem(a);
      }
      return scoreForItem(a) - scoreForItem(b);
    });

    return nextItems;
  }, [filteredItems, sortKey]);

  const selectedItem = useMemo(
    () => sortedItems.find((item) => item.id === selectedItemId) ?? null,
    [sortedItems, selectedItemId],
  );

  const formatLabel = (value?: string | null) => {
    if (!value) {
      return "-";
    }
    const normalized = value.trim().toLowerCase();
    return SENTIMENT_LABEL_MAP[normalized] ?? value.toUpperCase();
  };

  const formatScore = (value?: number | null) => {
    if (typeof value !== "number" || Number.isNaN(value)) {
      return "-";
    }
    return value.toFixed(4);
  };

  const formatTime = (value: string) => {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) {
      return "-";
    }
    return date.toLocaleString("id-ID", {
      day: "2-digit",
      month: "short",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const resolveBatchTexts = (item: AnalysisHistoryItem) => {
    if (!item.input_text) {
      return [];
    }
    return item.input_text
      .split(/\r?\n/)
      .map((value) => value.trim())
      .filter(Boolean);
  };

  const resolveBatchPredictions = (item: AnalysisHistoryItem) =>
    Array.isArray(item.result_payload) ? item.result_payload : [];

  const tableRows = sortedItems.map((item, index) => {
    const rowIndex = (currentPage - 1) * PAGE_SIZE + index + 1;
    const isBatch = item.source_type === "batch";
    const texts = isBatch ? resolveBatchTexts(item) : [];
    const predictions = isBatch ? resolveBatchPredictions(item) : [];
    const displayText = isBatch ? (texts[0] ?? "-") : (item.input_text ?? "-");
    const displayLabel = isBatch
      ? formatLabel(predictions[0]?.label)
      : formatLabel(item.result_label);
    const displayScore = isBatch
      ? formatScore(predictions[0]?.score ?? null)
      : formatScore(item.result_score);

    return {
      ...item,
      rowIndex,
      displayText,
      displayLabel,
      displayScore,
    };
  });

  const handleSelectItem = (itemId: number) => {
    setSelectedItemId(itemId);
  };

  const handlePageChange = (nextPage: number) => {
    if (nextPage < 1 || nextPage > totalPages) {
      return;
    }
    setCurrentPage(nextPage);
    setSelectedItemId(null);
  };

  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle title="Riwayat Analisis" />
      <DashboardPageContent
        title="Tabel Riwayat"
        subtitle="Klik baris untuk melihat detail analisis"
      >
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3 mb-4">
          <div className="flex flex-col">
            <label className="text-xs font-medium text-slate-600 mb-1">
              Live Search
            </label>
            <input
              type="text"
              value={searchTerm}
              onChange={(event) => setSearchTerm(event.target.value)}
              placeholder="Cari teks atau label..."
              className="h-10 w-full sm:w-64 rounded-lg border border-slate-300 px-3 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            />
          </div>
          <div className="flex flex-col">
            <label className="text-xs font-medium text-slate-600 mb-1">
              Urutkan
            </label>
            <select
              value={sortKey}
              onChange={(event) => setSortKey(event.target.value as SortKey)}
              className="h-10 rounded-lg border border-slate-300 px-3 text-sm outline-none transition focus:border-sky-500 focus:ring-2 focus:ring-sky-100"
            >
              <option value="newest">Terbaru</option>
              <option value="oldest">Terlama</option>
              <option value="score_desc">Skor Tertinggi</option>
              <option value="score_asc">Skor Terendah</option>
            </select>
          </div>
        </div>

        {loading ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Memuat data riwayat...
          </div>
        ) : error ? (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-6 text-sm text-rose-600">
            {error}
          </div>
        ) : tableRows.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Belum ada riwayat analisis untuk ditampilkan.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">No</th>
                  <th className="px-4 py-3 text-left font-semibold">Teks</th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Hasil Sentimen
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Confidence Score
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Waktu Analisis
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {tableRows.map((item) => (
                  <tr
                    key={item.id}
                    onClick={() => handleSelectItem(item.id)}
                    className={`cursor-pointer transition-colors hover:bg-sky-50 ${
                      selectedItemId === item.id ? "bg-sky-50" : "bg-white"
                    }`}
                  >
                    <td className="px-4 py-3 text-slate-600">
                      {item.rowIndex}
                    </td>
                    <td className="px-4 py-3 text-slate-900 max-w-xs">
                      <span className="line-clamp-2">{item.displayText}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                        {item.displayLabel}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-slate-700">
                      {item.displayScore}
                    </td>
                    <td className="px-4 py-3 text-slate-600">
                      {formatTime(item.created_at)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="mt-4 flex flex-wrap items-center justify-between gap-3 text-sm">
          <p className="text-slate-500">
            Menampilkan {tableRows.length} dari {totalCount} riwayat
          </p>
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => handlePageChange(currentPage - 1)}
              disabled={currentPage === 1}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 disabled:text-slate-300 disabled:border-slate-100 hover:bg-slate-50 transition cursor-pointer"
            >
              <FaArrowLeft />
            </button>
            <span className="text-slate-600">
              Halaman {currentPage} dari {totalPages}
            </span>
            <button
              type="button"
              onClick={() => handlePageChange(currentPage + 1)}
              disabled={currentPage === totalPages}
              className="px-3 py-1.5 rounded-lg border border-slate-200 text-slate-600 disabled:text-slate-300 disabled:border-slate-100 hover:bg-slate-50 transition cursor-pointer"
            >
              <FaArrowRight />
            </button>
          </div>
        </div>
      </DashboardPageContent>

      <DashboardPageContent
        title="Detail Analisis"
        subtitle={
          selectedItem
            ? "Detail riwayat yang dipilih"
            : "Pilih salah satu baris untuk melihat detail"
        }
      >
        {!selectedItem ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Belum ada riwayat yang dipilih.
          </div>
        ) : selectedItem.source_type === "batch" ? (
          <div className="space-y-4">
            <div className="text-sm text-slate-600">
              Analisis batch dengan {resolveBatchTexts(selectedItem).length}{" "}
              teks
            </div>
            <div className="overflow-x-auto rounded-xl border border-slate-200">
              <table className="min-w-full text-sm">
                <thead className="bg-slate-50 text-slate-600">
                  <tr>
                    <th className="px-4 py-3 text-left font-semibold">No</th>
                    <th className="px-4 py-3 text-left font-semibold">Teks</th>
                    <th className="px-4 py-3 text-left font-semibold">
                      Hasil Sentimen
                    </th>
                    <th className="px-4 py-3 text-left font-semibold">
                      Confidence Score
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200">
                  {resolveBatchTexts(selectedItem).map((text, index) => {
                    const prediction =
                      resolveBatchPredictions(selectedItem)[index] ?? {};
                    return (
                      <tr key={`${selectedItem.id}-${index}`}>
                        <td className="px-4 py-3 text-slate-600">
                          {index + 1}
                        </td>
                        <td className="px-4 py-3 text-slate-900 max-w-md">
                          {text}
                        </td>
                        <td className="px-4 py-3">
                          <span className="rounded-full bg-slate-100 px-2.5 py-1 text-xs font-semibold text-slate-700">
                            {formatLabel(prediction.label)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-700">
                          {formatScore(prediction.score ?? null)}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ) : (
          <div className="space-y-3 text-sm text-slate-700">
            <div>
              <p className="text-xs font-semibold text-slate-500">Teks</p>
              <p className="mt-1 text-slate-900">
                {selectedItem.input_text ?? "-"}
              </p>
            </div>
            <div className="flex flex-wrap gap-4">
              <div>
                <p className="text-xs font-semibold text-slate-500">Label</p>
                <p className="mt-1 text-slate-900">
                  {formatLabel(selectedItem.result_label)}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500">Skor</p>
                <p className="mt-1 text-slate-900">
                  {formatScore(selectedItem.result_score)}
                </p>
              </div>
              <div>
                <p className="text-xs font-semibold text-slate-500">Waktu</p>
                <p className="mt-1 text-slate-900">
                  {formatTime(selectedItem.created_at)}
                </p>
              </div>
            </div>
          </div>
        )}
      </DashboardPageContent>
    </main>
  );
}
