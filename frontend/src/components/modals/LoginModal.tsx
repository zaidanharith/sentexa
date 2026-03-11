"use client";

import { useState } from "react";

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onOpenSignUp?: () => void; // Untuk switch ke modal daftar
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
      {/* Overlay - Membuat background redup */}
      <div
        className="fixed inset-0 bg-black bg-opacity-30 z-40 transition-opacity duration-300"
        onClick={onClose}
      />

      {/* Modal */}
      <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div className="bg-white rounded-lg shadow-xl w-full max-w-md border border-gray-200">
          {/* Header */}
          <div className="border-b border-gray-200 p-6 flex justify-between items-start">
            <div>
              <h2 className="text-2xl font-bold text-gray-800 mb-1">
                Selamat Datang di Sentexa
              </h2>
              <p className="text-sm text-gray-500 italic">
                Hadir untuk membantu mengembangkan bisnismu
              </p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl leading-none"
            >
              ✕
            </button>
          </div>

          {/* Form Content */}
          <div className="p-6">
            <form className="space-y-4">
              {/* Email */}
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

              {/* Password */}
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

              {/* Remember & Forgot Password */}
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

              {/* Login Button */}
              <button
                type="submit"
                className="w-full bg-gray-800 hover:bg-gray-900 text-white font-semibold py-2.5 rounded-lg transition-colors"
              >
                Masuk
              </button>
            </form>

            {/* Divider */}
            <div className="flex items-center gap-3 my-5">
              <div className="flex-1 border-t border-gray-300" />
              <span className="text-xs text-gray-400">
                atau masuk dengan email
              </span>
              <div className="flex-1 border-t border-gray-300" />
            </div>

            {/* Google Login */}
            <button className="w-full border border-gray-300 text-gray-700 font-semibold py-2.5 rounded-lg hover:bg-gray-50 transition-colors flex items-center justify-center gap-2">
              <span className="text-lg">G</span>
              Masuk dengan Google
            </button>

            {/* Sign Up Link */}
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
