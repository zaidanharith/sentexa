import Image from "next/image";
import Link from "next/link";

export default function Home() {
  return (
    <div className="bg-white text-slate-600 px-48 h-full w-full">
      <nav className="flex items-center justify-between px-8 py-4 w-full">
        <div className="flex items-center gap-4">
          {/* Logo */}
          <div className="flex items-center gap-2">
            <Image src="/logo1.png" alt="Logo" width={100} height={100} />
            <span className="text-2xl font-bold text-blue-600">Sentexa</span>
          </div>

          {/* Menu Links */}
          <ul className="flex items-center space-x-8">
            <li>
              <a href="#fitur" className="hover:text-blue-500 transition">
                Fitur
              </a>
            </li>
            <li>
              <Link
                href="#cara-kerja"
                className="hover:text-blue-500 transition"
              >
                Cara kerja
              </Link>
            </li>
            <li>
              <a href="#harga" className="hover:text-blue-500 transition">
                Harga
              </a>
            </li>
          </ul>
        </div>

        {/* Auth Buttons */}
        <div className="flex items-center gap-4">
          <a
            href="/login"
            className="text-[#1E2939] border-[#6A7282] border px-6 py-2 rounded-lg font-semibold hover:text-blue-700"
          >
            Masuk
          </a>
          <a
            href="/register"
            className="bg-[#1E2939] text-white font-semibold px-6 py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Daftar Gratis
          </a>
        </div>
      </nav>
    </div>
  );
}
