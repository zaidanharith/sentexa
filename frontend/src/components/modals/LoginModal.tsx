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
        className="fixed inset-0 bg-black/60 z-9998 transition-opacity duration-300"
        onClick={onClose}
      />

      <div className="fixed inset-0 z-9999 flex items-center justify-center p-4">
        <div className="bg-white rounded-xl shadow-xl w-full max-w-md border border-gray-200 overflow-hidden">
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
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1.5">
                  Alamat Email
                </label>
                <input
                  type="email"
                  placeholder="johndoe@email.com"
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
                className="w-full bg-sky-500 text-white font-semibold py-2.5 rounded-lg hover:bg-sky-600 transition-colors cursor-pointer"
              >
                Masuk
              </button>
            </form>

            <div className="flex items-center gap-3 my-5">
              <div className="flex-1 border-t border-gray-300" />
              <span className="text-xs text-gray-400">
                atau masuk dengan email
              </span>
              <div className="flex-1 border-t border-gray-300" />
            </div>

            <button className="w-full border border-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
              <Image src="/google.png" alt="Google" width={20} height={20} />
              Masuk dengan Google
            </button>

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
