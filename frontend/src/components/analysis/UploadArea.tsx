'use client';

import { useState } from 'react';
import { parseFile } from '@/lib/file-parser';

interface UploadAreaProps {
  onFileSelected: (file: File) => Promise<void>;
  isLoading: boolean;
}

export function UploadArea({ onFileSelected, isLoading }: UploadAreaProps) {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setIsDragActive(true);
    } else if (e.type === 'dragleave') {
      setIsDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragActive(false);

    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      const file = files[0];
      onFileSelected(file);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelected(file);
    }
  };

  return (
    <div
      onDragEnter={handleDrag}
      onDragLeave={handleDrag}
      onDragOver={handleDrag}
      onDrop={handleDrop}
      className={`relative bg-white rounded-lg border-2 border-dashed p-8 text-center transition-all duration-200 ${
        isDragActive
          ? 'border-blue-500 bg-blue-50 shadow-md'
          : 'border-gray-300 hover:border-blue-400'
      } ${isLoading ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
    >
      <div className="flex justify-center mb-4">
        <svg
          className={`w-12 h-12 transition-colors ${
            isDragActive ? 'text-blue-500' : 'text-gray-400'
          }`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1.5}
            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3v-9"
          />
        </svg>
      </div>

      <label htmlFor="file-input" className="cursor-pointer block">
        <p className={`text-lg font-semibold mb-1 transition-colors ${
          isDragActive ? 'text-blue-600' : 'text-gray-900'
        }`}>
          {isDragActive
            ? 'Letakkan file di sini'
            : 'Klik untuk upload atau drag & drop file'}
        </p>
        <p className="text-sm text-gray-500">
          CSV, XLS, atau XLSX (Max. 10MB)
        </p>
        <p className="text-xs text-gray-400 mt-2">
          Kolom harus memiliki: <span className="font-semibold">ID, Ulasan, Rating</span>
        </p>
      </label>

      <input
        id="file-input"
        type="file"
        accept=".csv,.xls,.xlsx"
        onChange={handleFileChange}
        disabled={isLoading}
        className="hidden"
      />
    </div>
  );
}