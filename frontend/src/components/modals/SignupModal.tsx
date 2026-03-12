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
      <div
        className="fixed inset-0 bg-black/60  z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      <div className="fixed inset-0 z-9999 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          {/* Header dengan tombol close */}
          <div className="top-0 bg-white border-b border-gray-200 p-4 relative flex justify-center items-center">
            <div className="flex justify-center">
              <Image src="/logo1.svg" alt="Logo" width={35} height={35} />
            </div>
            <button
              onClick={onClose}
              className="absolute right-4 text-gray-500 hover:text-red-500 text-2xl cursor-pointer"
            >
              ✕
            </button>
          </div>

          <div className="p-6">
            <h2 className="text-2xl font-bold text-gray-800 text-center mb-2">
              Selamat Datang di Sentexa
            </h2>
            <p className="text-sm text-gray-500 italic text-center mb-6">
              Hadir untuk membantu mengembangkan bisnismu
            </p>

            <form className="space-y-4">
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

              {/* Email */}
              <input
                type="email"
                placeholder="contoh@email.com"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              <input
                type="password"
                placeholder="Min. 8 karakter"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              <input
                type="password"
                placeholder="Ulangi kata sandi"
                className="w-full border border-gray-300 rounded px-3 py-2 text-sm focus:outline-none focus:border-sky-500"
              />

              {/* Checkbox */}
              <label className="flex items-start gap-2 text-xs text-gray-600">
                <input type="checkbox" className="mt-0.5 cursor-pointer" />
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
                className="w-full bg-sky-500 text-white font-semibold py-2.5 rounded-lg hover:bg-sky-600 transition-colors cursor-pointer"
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
            <button className="w-full border border-gray-300 text-gray-700 font-semibold py-2 rounded-lg hover:bg-gray-100 transition-colors flex items-center justify-center gap-2 cursor-pointer">
              <Image src="/search.png" alt="G" width={20} height={20} />
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
