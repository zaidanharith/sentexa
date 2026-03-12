"use client";

import Image from "next/image";
import Link from "next/link";
import { useState } from "react";
import SignupModal from "@/components/modals/SignupModal";
import LoginModal from "@/components/modals/LoginModal";

const navLinks = [
  { href: "#fitur", label: "Fitur" },
  { href: "#cara-kerja", label: "Cara Kerja" },
  { href: "#harga", label: "Harga" },
];

export default function Navbar() {
  const [menuOpen, setMenuOpen] = useState(false);
  const [daftarOpen, setDaftarOpen] = useState(false);
  const [loginOpen, setLoginOpen] = useState(false);

  return (
    <>
      <nav className="fixed w-full z-50 backdrop-blur-md select-none bg-white/70 border-b border-gray-200">
        <div className="mx-auto max-w-7xl px-5 py-4 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="flex items-center gap-2">
              <Image src="/logo1.svg" alt="Logo" width={30} height={30} />
              <h1 className="text-2xl font-bold text-sky-500">Sentexa</h1>
            </Link>

            <ul className="hidden md:flex items-center gap-4 text-sm font-medium text-gray-700">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className="hover:text-sky-500 transition-colors"
                  >
                    {link.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          <div className="hidden md:flex items-center gap-3 text-md ">
            <button
              onClick={() => setLoginOpen(true)}
              className="border border-gray-300 text-gray-700 px-5 py-2 rounded-lg text-sm font-semibold hover:border-sky-500 hover:text-sky-500 transition-colors cursor-pointer"
            >
              Masuk
            </button>
            <button
              onClick={() => setDaftarOpen(true)}
              className="bg-sky-500 text-white text-sm font-semibold px-5 py-2 rounded-lg hover:bg-sky-600 transition-colors cursor-pointer"
            >
              Daftar
            </button>
          </div>

          <button
            onClick={() => setMenuOpen((prev) => !prev)}
            aria-label="Toggle menu"
            aria-expanded={menuOpen}
            className="md:hidden flex flex-col justify-center items-center w-9 h-9 gap-1.5 rounded-md hover:bg-gray-100 transition-colors cursor-pointer"
          >
            <span
              className={`block h-0.5 w-5 bg-gray-600 rounded transition-all duration-300 ${
                menuOpen ? "translate-y-2 rotate-45" : ""
              }`}
            />
            <span
              className={`block h-0.5 w-5 bg-gray-600 rounded transition-all duration-300 ${
                menuOpen ? "opacity-0" : ""
              }`}
            />
            <span
              className={`block h-0.5 w-5 bg-gray-600 rounded transition-all duration-300 ${
                menuOpen ? "-translate-y-2 -rotate-45" : ""
              }`}
            />
          </button>
        </div>

        <div
          className={`md:hidden overflow-hidden transition-all duration-300 ease-in-out ${
            menuOpen ? "max-h-96 border-t border-gray-100" : "max-h-0"
          }`}
        >
          <div className="px-5 py-4 flex flex-col gap-3 bg-white/95">
            <ul className="flex flex-col gap-1">
              {navLinks.map((link) => (
                <li key={link.href}>
                  <a
                    href={link.href}
                    onClick={() => setMenuOpen(false)}
                    className="block py-2 px-3 rounded-lg text-md font-medium text-gray-700 hover:bg-sky-50 hover:text-sky-500 transition-colors text-center"
                  >
                    {link.label}
                  </a>
                </li>
              ))}
            </ul>
            <div className="flex flex-col gap-2 pt-2 border-t border-gray-100">
              <Link
                href="/login"
                className="block text-center border border-gray-300 text-gray-700 px-5 py-2.5 rounded-lg text-sm font-semibold hover:border-sky-500 hover:text-sky-500 transition-colors"
              >
                Masuk
              </Link>
              <Link
                href="/register"
                className="block text-center bg-sky-500 text-white text-sm font-semibold px-5 py-2.5 rounded-lg hover:bg-sky-600 transition-colors"
              >
                Daftar
              </Link>
            </div>
          </div>
        </div>
      </nav>
      {/* Tambahkan component */}
      <LoginModal
        isOpen={loginOpen}
        onClose={() => setLoginOpen(false)}
        onOpenSignUp={() => setDaftarOpen(true)}
      />
      <SignupModal
        isOpen={daftarOpen}
        onClose={() => setDaftarOpen(false)}
        onOpenLogin={() => setLoginOpen(true)}
      />
    </>
  );
}
