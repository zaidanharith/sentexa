"use client";

import { useState } from "react";
import { useSession } from "next-auth/react";
import { useAnalysis } from "@/hooks/useAnalysis";
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

export default function AnalysisDashboardPage() {
  const { data: session } = useSession();
  const analysis = useAnalysis();
  const [activeTab, setActiveTab] = useState<"upload" | "text">("upload");
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(
    null,
  );

  const subscriptionTier = getSubscriptionTier(
    session?.user?.subscription_plan,
  );
  const features = getFeatureAccess(session?.user?.subscription_plan);

  const defaultTab = !features.canUploadFile ? "text" : "upload";
  const displayTab = features.canUploadFile ? activeTab : "text";

  const handleFileSelected = async (file: File) => {
    analysis.setLoading(true);

    try {
      const parsed = await parseFile(file);
      analysis.setFile(file);
      analysis.setParsedData(parsed);
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
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) fileInput.value = "";
  };

  const handleAnalyze = async () => {
    analysis.setLoading(true);

    try {
      if (displayTab === "text" && !analysis.state.textInput.trim()) {
        appToast.warning("Masukkan teks untuk dianalisis");
        return;
      }

      if (displayTab === "upload" && !analysis.state.parsedData) {
        appToast.warning("Upload file terlebih dahulu");
        return;
      }

      if (displayTab === "text") {
        try {
          const API_URL = process.env.NEXT_PUBLIC_API_URL;
          const url = API_URL
            ? `${API_URL}/sentiment/predict`
            : "/api/sentiment/predict";
          const res = await axios.post(
            url,
            { text: analysis.state.textInput },
            {
              headers: {
                Authorization: session?.accessToken
                  ? `Bearer ${session.accessToken}`
                  : undefined,
              },
            },
          );
          setAnalysisResult({
            text: analysis.state.textInput,
            label: res.data.label,
            score: res.data.score,
            scores: res.data.scores,
          });
          analysis.setTextInput("");
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
      analysis.setLoading(false);
    }
  };

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
        <div className="mb-6 p-3 bg-sky-50 rounded-lg border border-sky-200 flex items-center justify-between">
          <span className="text-sm font-medium text-gray-700">
            Paket Anda:
            <span className="ml-2 font-semibold text-sky-600">
              {subscriptionTier.charAt(0).toUpperCase() +
                subscriptionTier.slice(1)}
            </span>
          </span>
          {subscriptionTier === "free" && (
            <button className="text-xs font-semibold text-sky-600 hover:text-sky-700 transition-colors">
              Upgrade Sekarang
            </button>
          )}
        </div>

        {/* Tabs - Only show upload tab if premium */}
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

        {/* Tab: Upload File */}
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
          </div>
        )}

        {/* Tab: Input Teks */}
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
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
                disabled={analysis.state.loading}
              />
              <p className="text-xs text-gray-500 mt-2">
                {analysis.state.textInput.length} /{" "}
                {features.maxTextLength || 5000} karakter
              </p>
            </div>
          </div>
        )}

        <div className="mt-3 flex gap-4 justify-end">
          <button
            onClick={handleReset}
            disabled={
              analysis.state.loading ||
              (!analysis.state.file && !analysis.state.textInput)
            }
            className="disabled:text-gray-400 text-gray-900 font-medium rounded-lg transition-colors text-sm cursor-pointer"
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
            className="px-6 py-2 bg-sky-500 hover:bg-sky-600 disabled:bg-sky-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors cursor-pointer"
          >
            {analysis.state.loading ? "Sedang diproses..." : "Mulai Analisis"}
          </button>
        </div>
      </DashboardPageContent>

      {/* Show upgrade alert if free user */}
      {subscriptionTier === "free" && (
        <DashboardPageContent>
          <UpgradeAlert />
        </DashboardPageContent>
      )}

      {/* Analysis Result Card */}
      {analysisResult && (
        <DashboardPageContent>
          <div className="border-2 border-sky-200 rounded-lg p-6 bg-linear-to-br from-sky-50 to-blue-50">
            <h2 className="text-lg font-bold text-gray-900 mb-4">
              Hasil Analisis
            </h2>

            {/* Input Text */}
            <div className="mb-6 pb-4 border-b border-gray-200">
              <p className="text-sm font-medium text-gray-600 mb-2">
                Teks Input:
              </p>
              <p className="text-gray-900 italic bg-white p-3 rounded border border-gray-200">
                &ldquo;{analysisResult.text}&rdquo;
              </p>
            </div>

            {/* Label and Main Score */}
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

            {/* Score Details */}
            <div className="space-y-4">
              <p className="text-sm font-medium text-gray-600 mb-4">
                Detail Skor:
              </p>

              {/* Positive Score */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-green-700">
                    Positif
                  </span>
                  <span className="text-sm font-semibold text-green-600">
                    {(analysisResult.scores.positive * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${analysisResult.scores.positive * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Neutral Score */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-gray-700">
                    Netral
                  </span>
                  <span className="text-sm font-semibold text-gray-600">
                    {(analysisResult.scores.neutral * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-gray-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${analysisResult.scores.neutral * 100}%`,
                    }}
                  ></div>
                </div>
              </div>

              {/* Negative Score */}
              <div>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-sm font-medium text-red-700">
                    Negatif
                  </span>
                  <span className="text-sm font-semibold text-red-600">
                    {(analysisResult.scores.negative * 100).toFixed(2)}%
                  </span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-red-500 h-2 rounded-full transition-all duration-300"
                    style={{
                      width: `${analysisResult.scores.negative * 100}%`,
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* Clear Result Button */}
            <button
              onClick={() => setAnalysisResult(null)}
              className="mt-6 px-4 py-2 text-sm font-medium text-gray-600 hover:text-gray-900 hover:bg-gray-200 rounded-lg transition-colors cursor-pointer"
            >
              Tutup Hasil
            </button>
          </div>
        </DashboardPageContent>
      )}
    </main>
  );
}
