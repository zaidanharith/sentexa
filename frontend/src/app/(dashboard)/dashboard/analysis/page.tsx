'use client';

import { useEffect, useState } from 'react';
import { useAuth } from '@/hooks/useAuth';
import { useAnalysis } from '@/hooks/useAnalysis';
import { parseFile, downloadSampleFile } from '@/lib/file-parser';
import { DataPreview } from '@/components/analysis/DataPreview';
import { UploadArea } from '@/components/analysis/UploadArea';

export default function AnalysisDashboardPage() {
  const { user } = useAuth();
  const analysis = useAnalysis();
  const [activeTab, setActiveTab] = useState<'upload' | 'text'>('upload');

  const handleFileSelected = async (file: File) => {
    analysis.setLoading(true);
    analysis.setError(null);

    try {
      const parsed = await parseFile(file);
      analysis.setFile(file);
      analysis.setParsedData(parsed);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Gagal memproses file';
      analysis.setError(errorMessage);
      analysis.setFile(null);
      analysis.setParsedData(null);
    } finally {
      analysis.setLoading(false);
    }
  };

  const handleReset = () => {
    analysis.reset();
    setActiveTab('upload');
    // Reset file input
    const fileInput = document.getElementById('file-input') as HTMLInputElement;
    if (fileInput) fileInput.value = '';
  };

  const handleAnalyze = async () => {
    analysis.setLoading(true);
    analysis.setError(null);

    try {
      if (activeTab === 'text' && !analysis.state.textInput.trim()) {
        throw new Error('Masukkan teks untuk dianalisis');
      }

      if (activeTab === 'upload' && !analysis.state.parsedData) {
        throw new Error('Upload file terlebih dahulu');
      }

      // TODO: Implementasi logic analisis nanti
      console.log('Analisis data:', {
        mode: activeTab,
        data: analysis.state.parsedData,
        text: analysis.state.textInput,
      });
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Terjadi kesalahan';
      analysis.setError(errorMessage);
    } finally {
      analysis.setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto p-6">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Analisis Baru</h1>
        <div className="inline-flex items-center px-4 py-2 bg-blue-50 rounded-lg border border-blue-200">
          <span className="text-sm font-medium text-gray-700">Paket Anda: </span>
          <span className="ml-2 font-semibold text-blue-600">
            {user?.subscription 
  ? user.subscription.charAt(0).toUpperCase() + user.subscription.slice(1).toLowerCase() 
  : 'Memuat...'}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 border-b border-gray-200">
        <div className="flex gap-1">
          <button
            onClick={() => {
              setActiveTab('upload');
              analysis.setMode('upload');
            }}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'upload'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            📤 Upload File
          </button>
          <button
            onClick={() => {
              setActiveTab('text');
              analysis.setMode('text');
            }}
            className={`px-4 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'text'
                ? 'border-blue-600 text-blue-600'
                : 'border-transparent text-gray-600 hover:text-gray-900'
            }`}
          >
            ✍️ Input Teks
          </button>
        </div>
      </div>

      {/* Error Message */}
      {analysis.state.error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm font-medium text-red-800">{analysis.state.error}</p>
        </div>
      )}

      {/* Tab: Upload File */}
      {activeTab === 'upload' && (
        <div className="space-y-6">
          <UploadArea
            onFileSelected={handleFileSelected}
            isLoading={analysis.state.loading}
          />

          {/* Download Sample */}
          <button
            onClick={downloadSampleFile}
            className="text-blue-600 hover:text-blue-700 text-sm font-medium
            cursor-pointer transition-colors"
          >
            📥 Download file contoh
          </button>

          {/* Preview */}
          {analysis.state.parsedData && (
            <div className="space-y-4">
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">
                  📋 Preview Data ({analysis.state.parsedData.rowCount} baris)
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
      {activeTab === 'text' && (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-900 mb-2">
              Masukkan teks untuk dianalisis
            </label>
            <textarea
              value={analysis.state.textInput}
              onChange={(e) => analysis.setTextInput(e.target.value)}
              placeholder="Masukkan teks ulasan atau komentar di sini..."
              rows={6}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              disabled={analysis.state.loading}
            />
          </div>
          <p className="text-xs text-gray-500">
            Teks akan dianalisis menggunakan model NLP untuk mendeteksi sentimen
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="mt-8 flex gap-4 justify-end">
        <button
          onClick={handleReset}
          disabled={analysis.state.loading || (!analysis.state.file && !analysis.state.textInput)}
          className="px-6 py-2 bg-gray-100 hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 text-gray-900 font-medium rounded-lg transition-colors"
        >
          🔄 Reset Form
        </button>
        <button
          onClick={handleAnalyze}
          disabled={
            analysis.state.loading ||
            (activeTab === 'upload' && !analysis.state.parsedData) ||
            (activeTab === 'text' && !analysis.state.textInput.trim())
          }
          className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 disabled:cursor-not-allowed text-white font-medium rounded-lg transition-colors"
        >
          {analysis.state.loading ? '⏳ Sedang diproses...' : '🚀 Mulai Analisis'}
        </button>
      </div>
    </div>
  );
}