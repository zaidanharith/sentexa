"use client";

import { useState } from "react";

import { TbCloudUpload } from "react-icons/tb";

interface UploadAreaProps {
  onFileSelected: (file: File) => Promise<void>;
  isLoading: boolean;
}

export function UploadArea({ onFileSelected, isLoading }: UploadAreaProps) {
  const [isDragActive, setIsDragActive] = useState(false);

  const handleDrag = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setIsDragActive(true);
    } else if (e.type === "dragleave") {
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
      className={`relative bg-white rounded-2xl border-2 border-dashed p-8 text-center transition-all duration-200 select-none ${
        isDragActive
          ? "border-sky-500 bg-sky-50 shadow-md"
          : "border-gray-300 hover:border-sky-400"
      } ${isLoading ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
    >
      <div className="flex justify-center mb-4">
        <TbCloudUpload className="w-12 h-12" />
      </div>

      <label htmlFor="file-input" className="cursor-pointer block">
        <p
          className={`text-lg font-semibold mb-1 transition-colors ${
            isDragActive ? "text-sky-600" : "text-gray-900"
          }`}
        >
          {isDragActive
            ? "Letakkan file di sini"
            : "Klik untuk upload atau drag & drop file"}
        </p>
        <p className="text-sm text-gray-500">CSV, XLS, atau XLSX (Max. 10MB)</p>
        <p className="text-md text-gray-500 mt-2">
          Kolom harus memiliki:{" "}
          <span className="font-semibold">ID, Ulasan, Rating</span>
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
