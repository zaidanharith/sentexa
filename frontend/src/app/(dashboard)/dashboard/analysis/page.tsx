"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";
import { useSession } from "next-auth/react";
import { useAnalysis } from "@/hooks/useAnalysis";
import { parseFile, downloadSampleFile } from "@/lib/file-parser";
import { DataPreview } from "@/components/analysis/DataPreview";
import { UploadArea } from "@/components/analysis/UploadArea";
import { FaFileDownload } from "react-icons/fa";
import axios, { AxiosError } from "axios";

export default function AnalysisDashboardPage() {
  const { user } = useAuth();
  const { data: session } = useSession();
  const analysis = useAnalysis();
  const [activeTab, setActiveTab] = useState<"upload" | "text">("upload");

  const handleFileSelected = async (file: File) => {
    analysis.setLoading(true);
    analysis.setError(null);

    try {
      const parsed = await parseFile(file);
      analysis.setFile(file);
      analysis.setParsedData(parsed);
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Gagal memproses file";
      analysis.setError(errorMessage);
      analysis.setFile(null);
      analysis.setParsedData(null);
    } finally {
      analysis.setLoading(false);
    }
  };

  const handleReset = () => {
    analysis.reset();
    setActiveTab("upload");
    const fileInput = document.getElementById("file-input") as HTMLInputElement;
    if (fileInput) fileInput.value = "";
  };

  const handleAnalyze = async () => {
    analysis.setLoading(true);
    analysis.setError(null);

    try {
      if (activeTab === "text" && !analysis.state.textInput.trim()) {
        throw new Error("Masukkan teks untuk dianalisis");
      }

      if (activeTab === "upload" && !analysis.state.parsedData) {
        throw new Error("Upload file terlebih dahulu");
      }

      // console.log("Analisis data:", {
      //   mode: activeTab,
      //   data: analysis.state.parsedData,
      //   text: analysis.state.textInput,
      // });

      if (activeTab === "text") {
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
          console.log("Sentiment result:", res.data);
        } catch (error) {
          const err = error as AxiosError;
          console.error(
            "Sentiment API error:",
            err.response || err.message || err,
          );
        }
      }
    } catch (err) {
      const errorMessage =
        err instanceof Error ? err.message : "Terjadi kesalahan";
      analysis.setError(errorMessage);
    } finally {
      analysis.setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      <div className="mb-2">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analisis Baru</h1>
      </div>

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

      {analysis.state.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-800">
            {analysis.state.error}
          </p>
        </div>
      )}

      {activeTab === "upload" && (
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

      {activeTab === "text" && (
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
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent resize-none"
              disabled={analysis.state.loading}
            />
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
            (activeTab === "upload" && !analysis.state.parsedData) ||
            (activeTab === "text" && !analysis.state.textInput.trim())
          }
          className="px-6 py-2 bg-sky-500 hover:bg-sky-600 disabled:bg-sky-300 disabled:cursor-not-allowed text-white font-semibold rounded-lg transition-colors cursor-pointer"
        >
          {analysis.state.loading ? "Sedang diproses..." : "Mulai Analisis"}
        </button>
      </div>
    </div>
  );
}
