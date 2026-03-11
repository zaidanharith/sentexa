"use client";

import { useState } from "react";
import Image from "next/image";

interface SignUpModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenLogin?: () => void;
}

export default function SignUpModal({
  isOpen,
  onClose,
  onOpenLogin,
}: SignUpModalProps) {
  if (!isOpen) return null;

  return (
    <>
      {/* Overlay - Membuat background gelap */}
      <div
        className="fixed inset-0 bg-black bg-opacity-15 z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          {/* Header dengan tombol close */}
          <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
            <div className="text-center flex-1">
              <Image src="/logo1.svg" alt="Logo" width={30} height={30} />
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl"
            >
              ✕
            </button>
          </div>

          {/* Form Content */}
          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
              Selamat Datang di Sentexa
            </h2>
            <p className="text-sm text-gray-500 italic text-center mb-6">
              Hadir untuk membantu mengembangkan bisnismu
            </p>

            <form className="space-y-4">
              {/* Nama Depan & Belakang */}
              <div className="grid grid-cols-2 gap-3">
                <input
                  type="text"
                  placeholder="Zaidan"
                  className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
                />
                <input
                  type="text"
                  placeholder="Harith"
                  className="border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
                />
              </div>

              {/* Nama Toko */}
              <input
                type="text"
                placeholder="Toko Saya"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              {/* Email */}
              <input
                type="email"
                placeholder="contoh@email.com"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              {/* Kata Sandi */}
              <input
                type="password"
                placeholder="Min. 8 karakter"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              {/* Konfirmasi Kata Sandi */}
              <input
                type="password"
                placeholder="Ulangi kata sandi"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              {/* Checkbox */}
              <label className="flex items-start gap-2 text-xs text-gray-600">
                <input type="checkbox" className="mt-0.5" />
                <span>
                  Saya menyetujui{" "}
                  <a href="#" className="text-sky-500 hover:underline">
                    Syarat & Ketentuan
                  </a>{" "}
                  dan{" "}
                  <a href="#" className="text-sky-500 hover:underline">
                    Kebijakan Privasi
                  </a>{" "}
                  Sentexa
                </span>
              </label>

              {/* Tombol Submit */}
              <button
                type="submit"
                className="w-full bg-sky-500 text-white font-semibold py-2.5 rounded-lg hover:bg-sky-600 transition-colors"
              >
                Buat Akun Gratis
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-3 my-4">
              <div className="flex-1 border-t border-gray-300" />
              <span className="text-xs text-gray-400">atau</span>
              <div className="flex-1 border-t border-gray-300" />
            </div>

            {/* Google Login */}
            <button className="w-full border border-gray-300 text-gray-700 font-semibold py-2 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
              <span>G</span>
              Daftar dengan Google
            </button>

            {/* Login Link */}
            <p className="text-center text-sm text-gray-600 mt-4">
              Sudah punya akun?{" "}
              <button
                onClick={() => {
                  onClose();
                  onOpenLogin?.();
                }}
                className="text-sky-500 font-semibold hover:underline bg-none border-none cursor-pointer"
              >
                Masuk di sini
              </button>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
