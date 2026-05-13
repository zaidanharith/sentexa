"use client";

import { Fragment, useEffect, useMemo, useState } from "react";
import axios, { AxiosError } from "axios";
import { useSession } from "next-auth/react";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";
import { appToast } from "@/lib/toast";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa6";
import {
  type AnalysisPrediction,
  type AnalysisHistoryItem,
  type AnalysisHistoryResponse,
  type SentimentJobItem,
  resolveBatchTexts,
  resolveBatchPredictions,
  resolveAggregateLabelKey,
  resolveAggregateScore,
  formatScore,
  resolveJobTopLabel,
  resolveJobTopLabelKey,
  resolveJobAverageScore,
} from "@/lib/analysisHistoryHelpers";

type SentimentJobListResponse = {
  items: SentimentJobItem[];
  count: number;
};

type SentimentJobDetailResponse = {
  job: SentimentJobItem;
};

type SentimentJobResultItem = {
  index: number;
  text: string;
  prediction: AnalysisPrediction;
};

type SentimentJobResultsResponse = {
  items: SentimentJobResultItem[];
  count: number;
  total: number;
  offset: number;
  limit: number;
};

type SortKey = "newest" | "oldest" | "score_desc" | "score_asc";

const PAGE_SIZE = 5;

const SENTIMENT_LABEL_MAP: Record<string, string> = {
  positive: "POSITIF",
  negative: "NEGATIF",
  neutral: "NETRAL",
};

const BATCH_TYPES = new Set(["batch"]);
const JOB_TYPES = new Set(["job", "jobs"]);

export default function HistoryDashboardPage() {
  const { data: session, status } = useSession();
  const [items, setItems] = useState<AnalysisHistoryItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [jobItems, setJobItems] = useState<SentimentJobItem[]>([]);
  const [jobsLoading, setJobsLoading] = useState(false);
  const [jobsError, setJobsError] = useState<string | null>(null);
  const [singlePage, setSinglePage] = useState(1);
  const [batchPage, setBatchPage] = useState(1);
  const [jobPage, setJobPage] = useState(1);
  const [singleSort, setSingleSort] = useState<SortKey>("newest");
  const [batchSort, setBatchSort] = useState<SortKey>("newest");
  const [jobSort, setJobSort] = useState<SortKey>("newest");
  const [singleFilter, setSingleFilter] = useState({
    positive: true,
    negative: true,
    neutral: true,
  });
  const [batchFilter, setBatchFilter] = useState({
    positive: true,
    negative: true,
    neutral: true,
  });
  const [jobFilter, setJobFilter] = useState({
    positive: true,
    negative: true,
    neutral: true,
  });
  const [expandedSingleId, setExpandedSingleId] = useState<number | null>(null);
  const [expandedBatchId, setExpandedBatchId] = useState<number | null>(null);
  const [expandedJobId, setExpandedJobId] = useState<string | null>(null);
  const [jobDetails, setJobDetails] = useState<
    Record<string, SentimentJobItem>
  >({});
  const [jobResults, setJobResults] = useState<
    Record<string, SentimentJobResultItem[]>
  >({});
  const [jobLoading, setJobLoading] = useState<Record<string, boolean>>({});

  const apiBaseUrl =
    process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ??
    "http://localhost:8000/api";

  // Fetch analysis history
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
        const response = await axios.get<AnalysisHistoryResponse>(
          `${apiBaseUrl}/analyses`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        );

        if (!isActive) {
          return;
        }

        setItems(response.data.items ?? []);
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
  }, [apiBaseUrl, session?.accessToken, status]);

  useEffect(() => {
    const accessToken = session?.accessToken;
    if (!accessToken || status === "loading") {
      return;
    }

    let isActive = true;
    const fetchJobs = async () => {
      setJobsLoading(true);
      setJobsError(null);
      try {
        const response = await axios.get<SentimentJobListResponse>(
          `${apiBaseUrl}/sentiment/predict/jobs`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        );

        if (!isActive) {
          return;
        }

        setJobItems(response.data.items ?? []);
      } catch (err) {
        if (!isActive) {
          return;
        }

        const apiError = err as AxiosError;
        const message =
          typeof apiError.response?.data === "string"
            ? apiError.response?.data
            : apiError.message || "Gagal memuat data job.";
        setJobsError(message);
        appToast.error("Gagal memuat data job.");
      } finally {
        if (isActive) {
          setJobsLoading(false);
        }
      }
    };

    fetchJobs();
    return () => {
      isActive = false;
    };
  }, [apiBaseUrl, session?.accessToken, status]);

  function formatLabel(value?: string | null) {
    if (!value) {
      return "-";
    }
    const normalized = value.trim().toLowerCase();
    return SENTIMENT_LABEL_MAP[normalized] ?? value.toUpperCase();
  }

  function getLabelColorClasses(label?: string | null): string {
    if (!label) return "bg-slate-100 text-slate-700";
    const normalized = label.trim().toLowerCase();

    if (normalized === "positive") return "bg-green-100 text-green-700";
    if (normalized === "negative") return "bg-red-100 text-red-700";
    if (normalized === "neutral") return "bg-yellow-100 text-yellow-700";

    return "bg-slate-100 text-slate-700";
  }

  function formatTime(value: string) {
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
  }

  function resolveScoreTriple(prediction?: AnalysisPrediction | null) {
    const scores = prediction?.scores ?? {};
    return {
      positive: typeof scores.positive === "number" ? scores.positive : null,
      negative: typeof scores.negative === "number" ? scores.negative : null,
      neutral: typeof scores.neutral === "number" ? scores.neutral : null,
    };
  }

  function shouldIncludeLabel(
    labelKey: string | null | undefined,
    filter: {
      positive: boolean;
      negative: boolean;
      neutral: boolean;
    },
  ) {
    if (!labelKey) {
      return true;
    }
    const normalized = labelKey.toLowerCase();
    if (normalized === "positive" && !filter.positive) {
      return false;
    }
    if (normalized === "negative" && !filter.negative) {
      return false;
    }
    if (normalized === "neutral" && !filter.neutral) {
      return false;
    }
    return true;
  }

  function sortByKey<T>(
    data: T[],
    sortKey: SortKey,
    getDate: (item: T) => string,
    getScore: (item: T) => number,
  ) {
    const sorted = [...data];
    sorted.sort((a, b) => {
      if (sortKey === "newest") {
        return new Date(getDate(b)).getTime() - new Date(getDate(a)).getTime();
      }
      if (sortKey === "oldest") {
        return new Date(getDate(a)).getTime() - new Date(getDate(b)).getTime();
      }
      if (sortKey === "score_desc") {
        return getScore(b) - getScore(a);
      }
      return getScore(a) - getScore(b);
    });
    return sorted;
  }

  async function handleToggleJob(jobId: string) {
    if (expandedJobId === jobId) {
      setExpandedJobId(null);
      return;
    }

    const accessToken = session?.accessToken;
    if (!accessToken) {
      return;
    }

    setExpandedJobId(jobId);
    if (jobDetails[jobId] && jobResults[jobId]) {
      return;
    }

    setJobLoading((prev) => ({ ...prev, [jobId]: true }));
    try {
      const [detailResponse, resultsResponse] = await Promise.all([
        axios.get<SentimentJobDetailResponse>(
          `${apiBaseUrl}/sentiment/predict/jobs/${jobId}`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        ),
        axios.get<SentimentJobResultsResponse>(
          `${apiBaseUrl}/sentiment/predict/jobs/${jobId}/results`,
          {
            headers: {
              Authorization: `Bearer ${accessToken}`,
            },
          },
        ),
      ]);

      setJobDetails((prev) => ({ ...prev, [jobId]: detailResponse.data.job }));
      setJobResults((prev) => ({
        ...prev,
        [jobId]: resultsResponse.data.items ?? [],
      }));
    } catch {
      appToast.error("Gagal memuat detail job.");
    } finally {
      setJobLoading((prev) => ({ ...prev, [jobId]: false }));
    }
  }

  const singleRows = useMemo(() => {
    const filtered = items.filter((item) => {
      if (
        BATCH_TYPES.has(item.source_type) ||
        JOB_TYPES.has(item.source_type)
      ) {
        return false;
      }
      return shouldIncludeLabel(item.result_label, singleFilter);
    });

    const sorted = sortByKey(
      filtered,
      singleSort,
      (item) => item.created_at,
      (item) =>
        typeof item.result_score === "number" ? item.result_score : -1,
    );

    const start = (singlePage - 1) * PAGE_SIZE;
    return sorted.slice(start, start + PAGE_SIZE).map((item, index) => ({
      ...item,
      rowIndex: start + index + 1,
      displayLabel: formatLabel(item.result_label),
      displayScore: formatScore(item.result_score),
    }));
  }, [items, singleFilter, singleSort, singlePage]);

  const singleTotal = useMemo(() => {
    return items.filter((item) => {
      if (
        BATCH_TYPES.has(item.source_type) ||
        JOB_TYPES.has(item.source_type)
      ) {
        return false;
      }
      return shouldIncludeLabel(item.result_label, singleFilter);
    }).length;
  }, [items, singleFilter]);

  const batchRows = useMemo(() => {
    const filtered = items.filter((item) => {
      if (!BATCH_TYPES.has(item.source_type)) {
        return false;
      }
      return shouldIncludeLabel(resolveAggregateLabelKey(item), batchFilter);
    });

    const sorted = sortByKey(
      filtered,
      batchSort,
      (item) => item.created_at,
      (item) => resolveAggregateScore(item),
    );

    const start = (batchPage - 1) * PAGE_SIZE;
    return sorted.slice(start, start + PAGE_SIZE).map((item, index) => {
      const texts = resolveBatchTexts(item);
      const aggregateLabel = resolveAggregateLabelKey(item);
      const aggregateScore = resolveAggregateScore(item);
      return {
        ...item,
        rowIndex: start + index + 1,
        displayText: texts[0] ?? "-",
        textCount: texts.length,
        displayLabel: formatLabel(aggregateLabel),
        aggregateLabel: aggregateLabel,
        displayScore: formatScore(aggregateScore),
      };
    });
  }, [items, batchFilter, batchSort, batchPage]);

  const batchTotal = useMemo(() => {
    return items.filter((item) => {
      if (!BATCH_TYPES.has(item.source_type)) {
        return false;
      }
      return shouldIncludeLabel(resolveAggregateLabelKey(item), batchFilter);
    }).length;
  }, [items, batchFilter]);

  const jobRows = useMemo(() => {
    const filtered = jobItems.filter((job) =>
      shouldIncludeLabel(resolveJobTopLabelKey(job), jobFilter),
    );

    const sorted = sortByKey(
      filtered,
      jobSort,
      (job) => job.created_at,
      (job) => resolveJobAverageScore(job),
    );

    const start = (jobPage - 1) * PAGE_SIZE;
    return sorted.slice(start, start + PAGE_SIZE).map((job, index) => {
      const topLabel = resolveJobTopLabelKey(job);
      return {
        ...job,
        rowIndex: start + index + 1,
        displayLabel: resolveJobTopLabel(job),
        topLabelKey: topLabel,
        displayScore: formatScore(resolveJobAverageScore(job)),
      };
    });
  }, [jobItems, jobFilter, jobSort, jobPage]);

  const jobTotal = useMemo(() => {
    return jobItems.filter((job) =>
      shouldIncludeLabel(resolveJobTopLabelKey(job), jobFilter),
    ).length;
  }, [jobItems, jobFilter]);

  return (
    <main className="w-full mx-auto flex flex-col gap-4">
      <DashboardPageTitle title="Riwayat Analisis" />

      <DashboardPageContent
        title="Riwayat Analisis Single Text"
        subtitle="Riwayat analisis sentimen untuk satu teks"
      >
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="font-semibold text-slate-500">Filter:</span>
            {(["positive", "negative", "neutral"] as const).map((label) => (
              <button
                key={label}
                type="button"
                onClick={() => {
                  setSingleFilter((prev) => ({
                    ...prev,
                    [label]: !prev[label],
                  }));
                  setSinglePage(1);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                  singleFilter[label]
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {formatLabel(label)}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-slate-500">Sort:</span>
            <select
              value={singleSort}
              onChange={(event) => {
                setSingleSort(event.target.value as SortKey);
                setSinglePage(1);
              }}
              className="rounded border border-slate-300 px-2 py-1 text-xs"
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
        ) : singleRows.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Belum ada riwayat analisis single text.
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
                {singleRows.map((item) => {
                  const scores = resolveScoreTriple(
                    typeof item.result_payload === "object"
                      ? (item.result_payload as AnalysisPrediction)
                      : null,
                  );
                  const isExpanded = expandedSingleId === item.id;
                  return (
                    <Fragment key={item.id}>
                      <tr
                        className="cursor-pointer hover:bg-slate-50"
                        onClick={() =>
                          setExpandedSingleId((prev) =>
                            prev === item.id ? null : item.id,
                          )
                        }
                      >
                        <td className="px-4 py-3 text-slate-600">
                          {item.rowIndex}
                        </td>
                        <td className="px-4 py-3 text-slate-900 max-w-xs">
                          <span className="line-clamp-2">
                            {item.input_text ?? "-"}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getLabelColorClasses(item.result_label)}`}
                          >
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
                      {isExpanded && (
                        <tr className="bg-slate-50">
                          <td colSpan={5} className="px-4 py-3">
                            <div className="grid gap-2 text-xs text-slate-600 sm:grid-cols-3">
                              <div>
                                Positive: {formatScore(scores.positive)}
                              </div>
                              <div>
                                Negative: {formatScore(scores.negative)}
                              </div>
                              <div>Neutral: {formatScore(scores.neutral)}</div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {singleTotal > PAGE_SIZE && (
          <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
            <span>
              Halaman {singlePage} dari {Math.ceil(singleTotal / PAGE_SIZE)}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setSinglePage((prev) => Math.max(1, prev - 1))}
                disabled={singlePage === 1}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowLeft />
              </button>
              <button
                type="button"
                onClick={() =>
                  setSinglePage((prev) =>
                    Math.min(Math.ceil(singleTotal / PAGE_SIZE), prev + 1),
                  )
                }
                disabled={singlePage >= Math.ceil(singleTotal / PAGE_SIZE)}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowRight />
              </button>
            </div>
          </div>
        )}
      </DashboardPageContent>

      <DashboardPageContent
        title="Riwayat Analisis Batch"
        subtitle="Riwayat analisis sentimen untuk batch teks"
      >
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="font-semibold text-slate-500">Filter:</span>
            {(["positive", "negative", "neutral"] as const).map((label) => (
              <button
                key={label}
                type="button"
                onClick={() => {
                  setBatchFilter((prev) => ({
                    ...prev,
                    [label]: !prev[label],
                  }));
                  setBatchPage(1);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                  batchFilter[label]
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {formatLabel(label)}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-slate-500">Sort:</span>
            <select
              value={batchSort}
              onChange={(event) => {
                setBatchSort(event.target.value as SortKey);
                setBatchPage(1);
              }}
              className="rounded border border-slate-300 px-2 py-1 text-xs"
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
        ) : batchRows.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Belum ada riwayat analisis batch.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">No</th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Teks (Pertama)
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Label Sentimen Dominan
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Confidence Score Rata-rata
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Jumlah Teks
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Waktu Analisis
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {batchRows.map((item) => {
                  const isExpanded = expandedBatchId === item.id;
                  const texts = resolveBatchTexts(item);
                  const predictions = resolveBatchPredictions(item);
                  return (
                    <Fragment key={item.id}>
                      <tr
                        className="cursor-pointer hover:bg-slate-50"
                        onClick={() =>
                          setExpandedBatchId((prev) =>
                            prev === item.id ? null : item.id,
                          )
                        }
                      >
                        <td className="px-4 py-3 text-slate-600">
                          {item.rowIndex}
                        </td>
                        <td className="px-4 py-3 text-slate-900 max-w-xs">
                          <span className="line-clamp-2">
                            {item.displayText}
                          </span>
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getLabelColorClasses(item.aggregateLabel)}`}
                          >
                            {item.displayLabel}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-700">
                          {item.displayScore}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {item.textCount}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {formatTime(item.created_at)}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-slate-50">
                          <td colSpan={6} className="px-4 py-3">
                            <div className="overflow-x-auto rounded-lg border border-slate-200">
                              <table className="min-w-full text-xs">
                                <thead className="bg-white text-slate-600">
                                  <tr>
                                    <th className="px-3 py-2 text-left font-semibold">
                                      Teks
                                    </th>
                                    <th className="px-3 py-2 text-left font-semibold">
                                      Positive
                                    </th>
                                    <th className="px-3 py-2 text-left font-semibold">
                                      Negative
                                    </th>
                                    <th className="px-3 py-2 text-left font-semibold">
                                      Neutral
                                    </th>
                                  </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-200">
                                  {texts.map((text, index) => {
                                    const scores = resolveScoreTriple(
                                      predictions[index],
                                    );
                                    return (
                                      <tr key={`${item.id}-${index}`}>
                                        <td className="px-3 py-2 text-slate-700 max-w-md">
                                          {text}
                                        </td>
                                        <td className="px-3 py-2 text-slate-600">
                                          {formatScore(scores.positive)}
                                        </td>
                                        <td className="px-3 py-2 text-slate-600">
                                          {formatScore(scores.negative)}
                                        </td>
                                        <td className="px-3 py-2 text-slate-600">
                                          {formatScore(scores.neutral)}
                                        </td>
                                      </tr>
                                    );
                                  })}
                                </tbody>
                              </table>
                            </div>
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {batchTotal > PAGE_SIZE && (
          <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
            <span>
              Halaman {batchPage} dari {Math.ceil(batchTotal / PAGE_SIZE)}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setBatchPage((prev) => Math.max(1, prev - 1))}
                disabled={batchPage === 1}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowLeft />
              </button>
              <button
                type="button"
                onClick={() =>
                  setBatchPage((prev) =>
                    Math.min(Math.ceil(batchTotal / PAGE_SIZE), prev + 1),
                  )
                }
                disabled={batchPage >= Math.ceil(batchTotal / PAGE_SIZE)}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowRight />
              </button>
            </div>
          </div>
        )}
      </DashboardPageContent>

      <DashboardPageContent
        title="Riwayat Sentiment Jobs"
        subtitle="Riwayat job analisis sentimen asinkron"
      >
        <div className="flex flex-wrap items-center justify-between gap-4 mb-4">
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="font-semibold text-slate-500">Filter:</span>
            {(["positive", "negative", "neutral"] as const).map((label) => (
              <button
                key={label}
                type="button"
                onClick={() => {
                  setJobFilter((prev) => ({
                    ...prev,
                    [label]: !prev[label],
                  }));
                  setJobPage(1);
                }}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition ${
                  jobFilter[label]
                    ? "bg-sky-500 text-white"
                    : "bg-slate-100 text-slate-600 hover:bg-slate-200"
                }`}
              >
                {formatLabel(label)}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2 text-xs">
            <span className="font-semibold text-slate-500">Sort:</span>
            <select
              value={jobSort}
              onChange={(event) => {
                setJobSort(event.target.value as SortKey);
                setJobPage(1);
              }}
              className="rounded border border-slate-300 px-2 py-1 text-xs"
            >
              <option value="newest">Terbaru</option>
              <option value="oldest">Terlama</option>
              <option value="score_desc">Skor Tertinggi</option>
              <option value="score_asc">Skor Terendah</option>
            </select>
          </div>
        </div>
        {jobsLoading ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Memuat data job...
          </div>
        ) : jobsError ? (
          <div className="rounded-xl border border-rose-200 bg-rose-50 px-4 py-6 text-sm text-rose-600">
            {jobsError}
          </div>
        ) : jobRows.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-slate-50 px-4 py-6 text-sm text-slate-500">
            Belum ada riwayat sentiment job.
          </div>
        ) : (
          <div className="overflow-x-auto rounded-xl border border-slate-200">
            <table className="min-w-full text-sm">
              <thead className="bg-slate-50 text-slate-600">
                <tr>
                  <th className="px-4 py-3 text-left font-semibold">No</th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Label Sentimen Dominan
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Confidence Score Rata-rata
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">Status</th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Total Teks
                  </th>
                  <th className="px-4 py-3 text-left font-semibold">
                    Waktu Dibuat
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200">
                {jobRows.map((item) => {
                  const isExpanded = expandedJobId === item.job_id;
                  const isLoading = jobLoading[item.job_id];
                  const results = jobResults[item.job_id] ?? [];
                  const detail = jobDetails[item.job_id] ?? item;
                  return (
                    <Fragment key={item.job_id}>
                      <tr
                        className="cursor-pointer hover:bg-slate-50"
                        onClick={() => handleToggleJob(item.job_id)}
                      >
                        <td className="px-4 py-3 text-slate-600">
                          {item.rowIndex}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${getLabelColorClasses(item.topLabelKey)}`}
                          >
                            {item.displayLabel}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-700">
                          {item.displayScore}
                        </td>
                        <td className="px-4 py-3">
                          <span
                            className={`inline-block px-2 py-1 rounded text-xs font-medium ${
                              item.status === "completed"
                                ? "bg-green-100 text-green-700"
                                : item.status === "processing"
                                  ? "bg-blue-100 text-blue-700"
                                  : item.status === "queued"
                                    ? "bg-yellow-100 text-yellow-700"
                                    : "bg-red-100 text-red-700"
                            }`}
                          >
                            {item.status.charAt(0).toUpperCase() +
                              item.status.slice(1)}
                          </span>
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {item.total_texts}
                        </td>
                        <td className="px-4 py-3 text-slate-600">
                          {formatTime(item.created_at)}
                        </td>
                      </tr>
                      {isExpanded && (
                        <tr className="bg-slate-50">
                          <td colSpan={6} className="px-4 py-3">
                            {isLoading ? (
                              <div className="text-xs text-slate-500">
                                Memuat detail job...
                              </div>
                            ) : results.length === 0 ? (
                              <div className="text-xs text-slate-500">
                                Detail job belum tersedia.
                              </div>
                            ) : (
                              <div className="space-y-3">
                                <div className="grid gap-2 text-xs text-slate-600 sm:grid-cols-4">
                                  <div>Status: {detail.status}</div>
                                  <div>Total: {detail.total_texts}</div>
                                  <div>Selesai: {detail.completed_count}</div>
                                  <div>
                                    Update: {formatTime(detail.updated_at)}
                                  </div>
                                </div>
                                <div className="overflow-x-auto rounded-lg border border-slate-200">
                                  <table className="min-w-full text-xs">
                                    <thead className="bg-white text-slate-600">
                                      <tr>
                                        <th className="px-3 py-2 text-left font-semibold">
                                          Teks
                                        </th>
                                        <th className="px-3 py-2 text-left font-semibold">
                                          Positive
                                        </th>
                                        <th className="px-3 py-2 text-left font-semibold">
                                          Negative
                                        </th>
                                        <th className="px-3 py-2 text-left font-semibold">
                                          Neutral
                                        </th>
                                      </tr>
                                    </thead>
                                    <tbody className="divide-y divide-slate-200">
                                      {results.map((result) => {
                                        const scores = resolveScoreTriple(
                                          result.prediction,
                                        );
                                        return (
                                          <tr
                                            key={`${item.job_id}-${result.index}`}
                                          >
                                            <td className="px-3 py-2 text-slate-700 max-w-md">
                                              {result.text}
                                            </td>
                                            <td className="px-3 py-2 text-slate-600">
                                              {formatScore(scores.positive)}
                                            </td>
                                            <td className="px-3 py-2 text-slate-600">
                                              {formatScore(scores.negative)}
                                            </td>
                                            <td className="px-3 py-2 text-slate-600">
                                              {formatScore(scores.neutral)}
                                            </td>
                                          </tr>
                                        );
                                      })}
                                    </tbody>
                                  </table>
                                </div>
                              </div>
                            )}
                          </td>
                        </tr>
                      )}
                    </Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
        {jobTotal > PAGE_SIZE && (
          <div className="mt-3 flex items-center justify-between text-xs text-slate-600">
            <span>
              Halaman {jobPage} dari {Math.ceil(jobTotal / PAGE_SIZE)}
            </span>
            <div className="flex gap-2">
              <button
                type="button"
                onClick={() => setJobPage((prev) => Math.max(1, prev - 1))}
                disabled={jobPage === 1}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowLeft />
              </button>
              <button
                type="button"
                onClick={() =>
                  setJobPage((prev) =>
                    Math.min(Math.ceil(jobTotal / PAGE_SIZE), prev + 1),
                  )
                }
                disabled={jobPage >= Math.ceil(jobTotal / PAGE_SIZE)}
                className="rounded border border-slate-200 px-2 py-1 disabled:opacity-50"
              >
                <FaArrowRight />
              </button>
            </div>
          </div>
        )}
      </DashboardPageContent>
    </main>
  );
}
