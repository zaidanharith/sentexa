"use client";

import { useState, useEffect, useRef } from "react";
import { useSession } from "next-auth/react";
import { useAnalysis } from "@/hooks/useAnalysis";
import { useAuth } from "@/hooks/useAuth";
import { parseFile, downloadSampleFile } from "@/lib/file-parser";
import { getFeatureAccess, getSubscriptionTier } from "@/lib/subscription";
import { DataPreview } from "@/components/layout/dashboard/analysis/DataPreview";
import { UploadArea } from "@/components/layout/dashboard/analysis/UploadArea";
import { UpgradeAlert } from "@/components/layout/dashboard/analysis/UpgradeAlert";
import { FaFileDownload } from "react-icons/fa";
import axios, { AxiosError } from "axios";
import { appToast } from "@/lib/toast";
import DashboardPageTitle from "@/components/layout/dashboard/DashboardPageTitle";
import DashboardPageContent from "@/components/layout/dashboard/DashboardPageContent";

interface AnalysisResult {
  text: string;
  label: string;
  score: number;
  scores: {
    negative: number;
    neutral: number;
    positive: number;
  };
}

interface BatchJob {
  job_id: string;
  status: "queued" | "processing" | "completed" | "failed";
  total: number;
  completed: number;
  created_at: string;
  updated_at: string;
  label_counts: {
    positive: number;
    negative: number;
    neutral: number;
  } | null;
  error: string | null;
}

interface BatchResultItem {
  index: number;
  text: string;
  prediction: {
    label: string;
    label_id: number;
    score: number;
    scores: { negative: number; neutral: number; positive: number };
    postprocess: null;
  };
}

function extractTextsFromParsedData(parsedData: {
  rows: Record<string, unknown>[];
}): string[] {
  if (!parsedData.rows || parsedData.rows.length === 0) return [];

  const textKeys = [
    "text",
    "teks",
    "ulasan",
    "review",
    "komentar",
    "comment",
    "content",
    "isi",
  ];
  const firstRow = parsedData.rows[0];
  const key =
    Object.keys(firstRow).find((k) => textKeys.includes(k.toLowerCase())) ??
    Object.keys(firstRow)[0];

  if (!key) return [];
  return parsedData.rows
    .map((row) => String(row[key] ?? ""))
    .filter((t) => t.trim() !== "");
}

export default function AnalysisDashboardPage() {
  const { data: session } = useSession();
  const { user, refreshUser } = useAuth();
  const analysis = useAnalysis();

  const [activeTab, setActiveTab] = useState<"upload" | "text">("upload");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null,
  );
  const resultRef = useRef<HTMLDivElement>(null);

  const [batchJob, setBatchJob] = useState<BatchJob | null>(null);
  const [batchResults, setBatchResults] = useState<BatchResultItem[]>([]);
  const [batchResultsLoading, setBatchResultsLoading] = useState(false);
  const pollingRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    if (analysisResult && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [analysisResult]);

  useEffect(() => {
    return () => {
      if (pollingRef.current) clearInterval(pollingRef.current);
    };
  }, []);

  const subscriptionTier = getSubscriptionTier(user?.subscription_plan);
  const features = getFeatureAccess(user?.subscription_plan);

  const defaultTab = !features.canUploadFile ? "text" : "upload";
  const displayTab = features.canUploadFile ? activeTab : "text";

  function buildUrl(path: string) {
    const base = process.env.NEXT_PUBLIC_API_URL;
    return base ? `${base}${path}` : `/api${path}`;
  }

  function authHeader() {
    return session?.accessToken
      ? { Authorization: `Bearer ${session.accessToken}` }
      : {};
  }

  const fetchBatchResults = async (jobId: string) => {
    setBatchResultsLoading(true);
    try {
      const res = await axios.get(
        buildUrl(`/sentiment/predict/jobs/${jobId}/results`),
        { headers: authHeader() },
      );
      setBatchResults(res.data.items ?? []);
    } catch {
      appToast.error("Gagal memuat hasil analisis batch.");
    } finally {
      setBatchResultsLoading(false);
    }
  };

  const startPolling = (jobId: string) => {
    if (pollingRef.current) clearInterval(pollingRef.current);

    pollingRef.current = setInterval(async () => {
      try {
        const res = await axios.get(
          buildUrl(`/sentiment/predict/jobs/${jobId}`),
          { headers: authHeader() },
        );
        const job: BatchJob = res.data.job;
        setBatchJob(job);

        if (job.status === "completed") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          analysis.setLoading(false);
          fetchBatchResults(jobId);
          // Refresh data user agar kuota analisis di profil langsung terupdate
          void refreshUser();
        } else if (job.status === "failed") {
          clearInterval(pollingRef.current!);
          pollingRef.current = null;
          analysis.setLoading(false);
          appToast.error(
            "Job gagal diproses: " + (job.error ?? "unknown error"),
          );
        }
      } catch {
        if (pollingRef.current) clearInterval(pollingRef.current);
        pollingRef.current = null;
        analysis.setLoading(false);
        appToast.error("Gagal memantau status job.");
      }
    }, 3000);
  };

  const handleReprocess = async (jobId: string) => {
    analysis.setLoading(true);
    setBatchResults([]);

    try {
      const res = await axios.post(
        buildUrl(`/sentiment/predict/jobs/${jobId}/reprocess`),
        { include_scores: true, apply_postprocess: true, include_meta: false },
        { headers: authHeader() },
      );
      setBatchJob(res.data.job);
      appToast.success("Job berhasil di-reprocess.");
      startPolling(jobId);
    } catch {
      appToast.error("Gagal mereprocess job.");
      analysis.setLoading(false);
    }
  };

  const handleFileSelected = async (file: File) => {
    analysis.setLoading(true);
    try {
      const parsed = await parseFile(file);
      analysis.setFile(file);
      analysis.setParsedData(parsed);
      setBatchJob(null);
      setBatchResults([]);
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
        pollingRef.current = null;
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Gagal memproses file";
      appToast.error(errorMessage);
      analysis.setFile(null);
      analysis.setParsedData(null);
    } finally {
      analysis.setLoading(false);
    }
  };

  const handleReset = () => {
    analysis.reset();
    setActiveTab(defaultTab);
    setBatchJob(null);
    setBatchResults([]);
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) fileInput.value = "";
  };

  const handleAnalyze = async () => {
    analysis.setLoading(true);
    let keepLoading = false;

    try {
      if (subscriptionTier === "free" && (user?.analysis_quota ?? 0) <= 0) {
        appToast.error(
          "Kuota analisis sudah habis. Silakan upgrade ke premium untuk kuota lebih banyak.",
        );
        return;
      }

      if (displayTab === "text" && !analysis.state.textInput.trim()) {
        appToast.warning("Masukkan teks untuk dianalisis");
        return;
      }
      if (displayTab === "upload" && !analysis.state.parsedData) {
        appToast.warning("Upload file terlebih dahulu");
        return;
      }

      if (displayTab === "upload") {
        const texts = extractTextsFromParsedData(
          analysis.state.parsedData as { rows: Record<string, unknown>[] },
        );
        if (texts.length === 0) {
          appToast.warning(
            "Tidak ada teks yang dapat diambil dari file. Pastikan file memiliki kolom teks.",
          );
          return;
        }

        const res = await axios.post(
          buildUrl("/sentiment/predict/jobs"),
          {
            texts,
            include_scores: true,
            apply_postprocess: true,
            include_meta: false,
          },
          { headers: authHeader() },
        );

        setBatchJob(res.data.job);
        setBatchResults([]);
        startPolling(res.data.job.job_id);
        keepLoading = true;
        return;
      }

      if (displayTab === "text") {
        try {
          const res = await axios.post(
            buildUrl("/sentiment/predict"),
            { text: analysis.state.textInput },
            { headers: authHeader() },
          );
          setAnalysisResult({
            text: analysis.state.textInput,
            label: res.data.label,
            score: res.data.score,
            scores: res.data.scores,
          });
          analysis.setTextInput("");
          void refreshUser();
        } catch (error) {
          const err = error as AxiosError;
          console.error(
            "Sentiment API error:",
            err.response || err.message || err,
          );
          appToast.error("Gagal menganalisis teks.");
        }
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Terjadi kesalahan";
      appToast.error(errorMessage);
    } finally {
      if (!keepLoading) {
        analysis.setLoading(false);
      }
    }
  };

  function labelColorClass(label: string) {
    if (label === "positive") return "bg-green-100 text-green-700";
    if (label === "negative") return "bg-red-100 text-red-700";
    return "bg-gray-100 text-gray-700";
  }

  function progressPct(job: BatchJob) {
    return job.total > 0 ? Math.round((job.completed / job.total) * 100) : 0;
  }

  return (
    <main className="w-full max-w-4xl mx-auto flex flex-col gap-4">
      <DashboardPageTitle
        title="Analisis Baru"
        subtitle={
          subscriptionTier === "free"
            ? "Masukkan teks untuk dianalisis (Upgrade untuk akses upload file)"
            : "Upload file atau masukkan teks untuk dianalisis"
        }
      />

      <DashboardPageContent>
        {features.canUploadFile && (
          <div className="mb-6 border-b border-gray-300">
            <div className="flex gap-1">
              <button
                onClick={() => {
                  setActiveTab("upload");
                  analysis.setMode("upload");
                }}
                className={`px-4 py-3 font-semibold text-sm border-b-2 transition-colors cursor-pointer ${
                  activeTab === "upload"
                    ? "border-sky-500 text-sky-500"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                Upload File
              </button>
              <button
                onClick={() => {
                  setActiveTab("text");
                  analysis.setMode("text");
                }}
                className={`px-4 py-3 font-semibold text-sm border-b-2 transition-colors cursor-pointer ${
                  activeTab === "text"
                    ? "border-sky-500 text-sky-500"
                    : "border-transparent text-gray-600 hover:text-gray-900"
                }`}
              >
                Input Teks
              </button>
            </div>
          </div>
        )}

        {displayTab === "upload" && features.canUploadFile && (
          <div className="space-y-6">
            <UploadArea
              onFileSelected={handleFileSelected}
              isLoading={analysis.state.loading}
            />

            <button
              onClick={downloadSampleFile}
              className="text-sky-500 hover:text-sky-600 text-md font-medium
                cursor-pointer transition-colors flex items-center gap-2"
            >
              <FaFileDownload className="w-6 h-6" /> Contoh File Input
            </button>

            {analysis.state.parsedData && (
              <div className="space-y-4">
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Preview Data ({analysis.state.parsedData.rowCount} baris)
                  </h3>
                  <p className="text-sm text-gray-600 mb-3">
                    File: {analysis.state.file?.name}
                  </p>
                </div>
                <DataPreview data={analysis.state.parsedData} />
              </div>
            )}

            {/* ── Batch Job Progress Card ──────────────────────────────────── */}
            {/*
             * Rendered after POST /jobs succeeds.
             * Updates live via polling (GET /jobs/{id}).
             * Shows results table after status === "completed"
             *   (data from GET /jobs/{id}/results).
             * Reprocess button triggers POST /jobs/{id}/reprocess.
             */}
            {batchJob && (
              <div className="rounded-xl border border-sky-200 bg-sky-50 p-5 space-y-4">
                {/* Header */}
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-semibold text-gray-900">
                      Status Analisis Batch
                    </h3>
                    <p className="text-xs text-gray-500 mt-0.5">
                      Job ID: {batchJob.job_id}
                    </p>
                  </div>
                  <span
                    className={`px-2.5 py-1 rounded text-xs font-semibold ${
                      batchJob.status === "completed"
                        ? "bg-green-100 text-green-700"
                        : batchJob.status === "failed"
                          ? "bg-red-100 text-red-700"
                          : batchJob.status === "processing"
                            ? "bg-blue-100 text-blue-700"
                            : "bg-yellow-100 text-yellow-700"
                    }`}
                  >
                    {batchJob.status.charAt(0).toUpperCase() +
                      batchJob.status.slice(1)}
                  </span>
                </div>

                {/* Progress bar */}
                <div>
                  <div className="flex justify-between text-xs text-gray-600 mb-1.5">
                    <span>
                      {batchJob.completed} / {batchJob.total} teks diproses
                    </span>
                    <span className="font-semibold">
                      {progressPct(batchJob)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5">
                    <div
                      className={`h-2.5 rounded-full transition-all duration-500 ${
                        batchJob.status === "failed"
                          ? "bg-red-500"
                          : "bg-sky-500"
                      }`}
                      style={{ width: `${progressPct(batchJob)}%` }}
                    />
                  </div>
                </div>

                {/* Label counts (only when completed) */}
                {batchJob.status === "completed" && batchJob.label_counts && (
                  <div className="grid grid-cols-3 gap-3 text-xs">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-green-700">
                        {batchJob.label_counts.positive}
                      </p>
                      <p className="text-green-600 mt-0.5">Positif</p>
                    </div>
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-gray-700">
                        {batchJob.label_counts.neutral}
                      </p>
                      <p className="text-gray-600 mt-0.5">Netral</p>
                    </div>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-3 text-center">
                      <p className="text-xl font-bold text-red-700">
                        {batchJob.label_counts.negative}
                      </p>
                      <p className="text-red-600 mt-0.5">Negatif</p>
                    </div>
                  </div>
                )}

                {/* Error message */}
                {batchJob.status === "failed" && batchJob.error && (
                  <p className="text-xs text-red-600 bg-red-50 border border-red-200 rounded-lg px-3 py-2">
                    Error: {batchJob.error}
                  </p>
                )}

                {/* Results preview table (GET /jobs/{id}/results) */}
                {batchResultsLoading && (
                  <p className="text-xs text-gray-500 animate-pulse">
                    Memuat hasil analisis...
                  </p>
                )}
                {!batchResultsLoading && batchResults.length > 0 && (
                  <div>
                    <p className="text-xs font-semibold text-gray-600 mb-2">
                      Preview Hasil (10 pertama dari {batchResults.length}{" "}
                      total):
                    </p>
                    <div className="overflow-x-auto rounded-lg border border-gray-200">
                      <table className="min-w-full text-xs">
                        <thead className="bg-white text-gray-600">
                          <tr>
                            <th className="px-3 py-2 text-left font-semibold">
                              #
                            </th>
                            <th className="px-3 py-2 text-left font-semibold">
                              Teks
                            </th>
                            <th className="px-3 py-2 text-left font-semibold">
                              Label
                            </th>
                            <th className="px-3 py-2 text-left font-semibold">
                              Score
                            </th>
                          </tr>
                        </thead>
                        <tbody className="divide-y divide-gray-200">
                          {batchResults.slice(0, 10).map((result) => (
                            <tr key={result.index} className="hover:bg-gray-50">
                              <td className="px-3 py-2 text-gray-500">
                                {result.index + 1}
                              </td>
                              <td className="px-3 py-2 text-gray-700 max-w-xs">
                                <span className="line-clamp-2">
                                  {result.text}
                                </span>
                              </td>
                              <td className="px-3 py-2">
                                <span
                                  className={`px-2 py-0.5 rounded-full font-semibold ${labelColorClass(result.prediction.label)}`}
                                >
                                  {result.prediction.label
                                    .charAt(0)
                                    .toUpperCase() +
                                    result.prediction.label.slice(1)}
                                </span>
                              </td>
                              <td className="px-3 py-2 text-gray-600 font-medium">
                                {(result.prediction.score * 100).toFixed(1)}%
                              </td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {batchResults.length > 10 && (
                      <p className="text-xs text-gray-500 mt-1.5">
                        +{batchResults.length - 10} hasil lainnya tersedia di
                        halaman{" "}
                        <span className="text-sky-600 font-medium">
                          Riwayat Analisis
                        </span>
                        .
                      </p>
                    )}
                  </div>
                )}

                {/* Action buttons */}
                <div className="flex items-center gap-3 pt-1">
                  {/* POST /sentiment/predict/jobs/{job_id}/reprocess */}
                  {(batchJob.status === "completed" ||
                    batchJob.status === "failed") && (
                    <button
                      onClick={() => handleReprocess(batchJob.job_id)}
                      disabled={analysis.state.loading}
                      className="px-4 py-1.5 text-xs font-semibold text-sky-600 border border-sky-300
                        rounded-lg hover:bg-sky-100 disabled:opacity-50 disabled:cursor-not-allowed
                        transition-colors"
                    >
                      {analysis.state.loading ? "Memproses..." : "🔄 Reprocess"}
                    </button>
                  )}
                  <button
                    onClick={() => {
                      setBatchJob(null);
                      setBatchResults([]);
                    }}
                    className="px-4 py-1.5 text-xs font-medium text-gray-500 hover:text-gray-700
                      hover:bg-gray-100 rounded-lg transition-colors"
                  >
                    Tutup
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {/* ── Tab: Input Teks ───────────────────────────────────────────────── */}
        {displayTab === "text" && features.canInputText && (
          <div className="space-y-4">
            <div>
              <label className="block text-md font-medium text-gray-900 mb-2">
                Masukkan teks untuk dianalisis
              </label>
              <textarea
                value={analysis.state.textInput}
                onChange={(e) => analysis.setTextInput(e.target.value)}
                placeholder="Produknya bagus, tapi pengirimannya lama..."
                rows={6}
                maxLength={features.maxTextLength || 5000}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none
                  focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
                disabled={analysis.state.loading}
              />
              <p className="text-xs text-gray-500 mt-2">
                {analysis.state.textInput.length} /{" "}
                {features.maxTextLength || 5000} karakter
              </p>
            </div>
          </div>
        )}

        {/* Bottom action row */}
        <div className="mt-3 flex gap-4 justify-end">
          <button
            onClick={handleReset}
            disabled={
              analysis.state.loading ||
              (!analysis.state.file && !analysis.state.textInput)
            }
            className="disabled:text-gray-400 text-gray-900 font-medium rounded-lg
              transition-colors text-sm cursor-pointer"
          >
            Reset Input
          </button>
          <button
            onClick={handleAnalyze}
            disabled={
              analysis.state.loading ||
              (displayTab === "upload" && !analysis.state.parsedData) ||
              (displayTab === "text" && !analysis.state.textInput.trim())
            }
            className="px-6 py-2 bg-sky-500 hover:bg-sky-600 disabled:bg-sky-300
              disabled:cursor-not-allowed text-white font-semibold rounded-lg
              transition-colors cursor-pointer"
          >
            {analysis.state.loading
              ? displayTab === "upload"
                ? "Mengirim job..."
                : "Sedang diproses..."
              : "Mulai Analisis"}
          </button>
        </div>
      </DashboardPageContent>

      {/* Upgrade alert for free users */}
      {subscriptionTier === "free" && (
        <DashboardPageContent>
          <UpgradeAlert />
        </DashboardPageContent>
      )}

      {/* ── Single-text Analysis Result Card ─────────────────────────────────── */}
      {analysisResult && (
        <DashboardPageContent>
          <div
            ref={resultRef}
            className="border-2 border-sky-200 rounded-lg p-6 bg-linear-to-br from-sky-50 to-blue-50"
          >
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              Hasil Analisis
            </h2>

            {/* Input text */}
            <div className="mb-6 pb-4 border-b border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">
                Teks Input:
              </p>
              <p className="text-gray-900 italic bg-white p-3 rounded border border-gray-200">
                &ldquo;{analysisResult.text}&rdquo;
              </p>
            </div>

            {/* Label & main score */}
            <div className="mb-6 pb-4 border-b border-gray-200">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 mb-2">
                    Sentimen:
                  </p>
                  <div className="flex items-center gap-3">
                    <span
                      className={`px-4 py-2 rounded-full font-bold text-white ${
                        analysisResult.label === "positive"
                          ? "bg-green-500"
                          : analysisResult.label === "negative"
                            ? "bg-red-500"
                            : "bg-gray-500"
                      }`}
                    >
                      {analysisResult.label.charAt(0).toUpperCase() +
                        analysisResult.label.slice(1)}
                    </span>
                    <span className="text-2xl font-bold text-sky-600">
                      {(analysisResult.score * 100).toFixed(2)}%
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Score details */}
            <div className="space-y-4">
              <p className="text-sm font-medium text-gray-600 mb-4">
                Detail Skor:
              </p>

              {(
                [
                  { key: "positive", label: "Positif", color: "green" },
                  { key: "neutral", label: "Netral", color: "gray" },
                  { key: "negative", label: "Negatif", color: "red" },
                ] as const
              ).map(({ key, label, color }) => (
                <div key={key}>
                  <div className="flex justify-between items-center mb-2">
                    <span className={`text-sm font-medium text-${color}-700`}>
                      {label}
                    </span>
                    <span className={`text-sm font-semibold text-${color}-600`}>
                      {(analysisResult.scores[key] * 100).toFixed(2)}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`bg-${color}-500 h-2 rounded-full transition-all duration-300`}
                      style={{ width: `${analysisResult.scores[key] * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <button
              onClick={() => setAnalysisResult(null)}
              className="mt-6 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900
                hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Tutup Hasil
            </button>
          </div>
        </DashboardPageContent>
      )}
    </main>
  );
}
