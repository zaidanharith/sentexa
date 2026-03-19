import Image from "next/image";
import Link from "next/link";
import { FaInstagram, FaLinkedinIn, FaXTwitter } from "react-icons/fa6";

const footerLinks = {
  Produk: [
    { label: "Fitur", href: "#fitur" },
    { label: "Cara Kerja", href: "#cara-kerja" },
    { label: "Harga", href: "#harga" },
    { label: "Demo Dashboard", href: "#demo" },
  ],
  Dukungan: [
    { label: "Dokumentasi", href: "#docs" },
    { label: "Panduan Mulai", href: "#guide" },
    { label: "FAQ", href: "#faq" },
    { label: "Hubungi Kami", href: "#kontak" },
  ],
  Perusahaan: [
    { label: "Tentang Sentexa", href: "#tentang" },
    { label: "Blog", href: "#blog" },
    { label: "Karir", href: "#karir" },
    { label: "Kebijakan Privasi", href: "#privasi" },
  ],
};

const socialLinks = [
  {
    label: "Instagram",
    href: "#",
    icon: FaInstagram,
  },
  {
    label: "Twitter / X",
    href: "#",
    icon: FaXTwitter,
  },
  {
    label: "LinkedIn",
    href: "#",
    icon: FaLinkedinIn,
  },
];

export default function Footer() {
  return (
    <footer className="w-full border-t border-gray-200 bg-white">
      <div className="max-w-7xl mx-auto py-12">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-10">
          <div className="lg:col-span-2 flex flex-col gap-4">
            <Link href="/" className="flex items-center gap-2 w-fit">
              <Image
                src="/logo1.svg"
                alt="Logo Sentexa"
                width={28}
                height={28}
              />
              <span className="text-2xl font-bold text-sky-500">Sentexa</span>
            </Link>
            <p className="text-sm text-gray-500 leading-relaxed max-w-xs">
              Platform analisis sentimen berbasis AI untuk UMKM Indonesia.
              Pahami pelangganmu lebih dalam dari setiap ulasan marketplace.
            </p>
            <div className="flex items-center gap-2 mt-1">
              {socialLinks.map((s) => {
                const Icon = s.icon;

                return (
                  <a
                    key={s.label}
                    href={s.href}
                    aria-label={s.label}
                    className="w-8 h-8 flex items-center justify-center rounded-md border border-gray-200 text-gray-500 hover:border-sky-400 hover:text-sky-500 transition-colors"
                  >
                    <Icon className="w-4 h-4" />
                  </a>
                );
              })}
            </div>
            <div className="flex items-center gap-2 mt-1">
              <span className="inline-flex items-center gap-1.5 text-xs font-medium text-sky-600 bg-sky-50 border border-sky-100 rounded-full px-3 py-1">
                <span className="w-1.5 h-1.5 rounded-full bg-sky-400 animate-pulse" />
                Gratis hingga 100 ulasan
              </span>
            </div>
          </div>

          {Object.entries(footerLinks).map(([category, links]) => (
            <div key={category} className="flex flex-col gap-3">
              <h3 className="text-sm font-semibold text-gray-800">
                {category}
              </h3>
              <ul className="flex flex-col gap-2">
                {links.map((link) => (
                  <li key={link.label}>
                    <Link
                      href={link.href}
                      className="text-sm text-gray-500 hover:text-sky-500 transition-colors"
                    >
                      {link.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>

      <div className="border-t border-gray-100">
        <div className="max-w-7xl mx-auto px-5 py-4 flex flex-col sm:flex-row items-center justify-between gap-2">
          <p className="text-xs text-gray-400">
            &copy; {new Date().getFullYear()} Sentexa. Seluruh hak cipta
            dilindungi.
          </p>
          <div className="flex items-center gap-4">
            <Link
              href="#syarat"
              className="text-xs text-gray-400 hover:text-sky-500 transition-colors"
            >
              Syarat &amp; Ketentuan
            </Link>
            <Link
              href="#privasi"
              className="text-xs text-gray-400 hover:text-sky-500 transition-colors"
            >
              Kebijakan Privasi
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
