"use client";

import { useState } from "react";
import Image from "next/image";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenSignUp?: () => void;
}

export default function LoginModal({
  isOpen,
  onClose,
  onOpenSignUp,
}: LoginModalProps) {
  const [rememberMe, setRememberMe] = useState(false);

  if (!isOpen) return null;

  const handleSwitchToSignUp = () => {
    onClose();
    onOpenSignUp?.();
  };

  return (
    <>
      <div
        className="fixed inset-0 bg-black/40 z-9998 transition-opacity duration-300"
        onClick={onClose}
      />

      <div className="fixed inset-0 z-9999 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md border border-gray-200">
          <div className="sticky top-0 bg-white border-b border-gray-200 p-4 flex justify-between items-center">
            <div className="text-center flex-1">
              <Image src="/logo1.svg" alt="Logo" width={30} height={30} />
            </div>
            <button
              onClick={onClose}
              className="text-gray-500 hover:text-gray-700 text-2xl leading-none cursor-pointer"
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Alamat Email
                </label>
                <input
                  type="email"
                  placeholder="contoh@email.com"
                  className="w-full border border-gray-300 rounded px-3 py-2.5 text-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-200 transition"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Kata Sandi
                </label>
                <input
                  type="password"
                  placeholder="••••••••"
                  className="w-full border border-gray-300 rounded px-3 py-2.5 text-sm focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-200 transition"
                />
              </div>

              <div className="flex items-center justify-between text-sm">
                <label className="flex items-center gap-2 text-gray-600 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                    className="w-4 h-4 border border-gray-300 rounded cursor-pointer"
                  />
                  Ingat saya
                </label>
                <a
                  href="#"
                  className="text-sky-500 hover:underline font-medium"
                >
                  Lupa kata sandi?
                </a>
              </div>

              <button
                type="submit"
                className="w-full bg-gray-800 hover:bg-gray-900 text-white font-semibold py-2.5 rounded-lg transition-colors"
              >
                Masuk
              </button>
            </form>

            <p className="text-center text-sm text-gray-600 mt-5">
              Belum punya akun?{" "}
              <button
                onClick={handleSwitchToSignUp}
                className="text-sky-500 font-semibold hover:underline bg-none border-none cursor-pointer"
              >
                Daftar Gratis
              </button>
            </p>
          </div>
        </div>
      </div>
    </>
  );
}
