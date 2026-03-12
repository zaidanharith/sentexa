export default function Hero() {
  return (
    <>
      {/* ══ HERO SECTION ══ */}
      <section className="border-b border-gray-200 py-12 md:py-20 bg-gray-50">
        <div className="mx-auto px-4 grid md:grid-cols-2 gap-8 items-center">
          <div>
            <p color="dark">Khusus Pelaku UMKM</p>
            <h1 className="mt-3 mb-4 text-gray-800">
              Analisis Ribuan Ulasan Pelanggan Secara Otomatis
            </h1>
            <p className="text-sm text-gray-500 italic mb-2 leading-relaxed">
              [ Deskripsi singkat: Sentexa membantu UMKM memahami sentimen
              pelanggan — Positif, Negatif, atau Netral — dari ulasan
              marketplace menggunakan AI berbasis NLP. ]
            </p>

            <div className="flex flex-wrap gap-3 mt-4">
              <p>▶ Mulai Analisis Gratis</p>
              <p>Lihat Demo Dashboard</p>
            </div>
            <p className="text-xs text-gray-400 italic mt-3">
              * Tidak perlu kartu kredit — Gratis hingga 100 ulasan
            </p>
          </div>
        </div>
      </section>

      {/* ══ STATS STRIP ══ */}
      <section className="border-b border-gray-200 py-6 bg-white">
        <div className="max-w-6xl mx-auto px-4 grid grid-cols-3 gap-4 text-center">
          {[
            { val: "10.000+", label: "Ulasan Dianalisis" },
            { val: "95%", label: "Akurasi Model NLP" },
            { val: "500+", label: "UMKM Terbantu" },
          ].map((s, i) => (
            <div key={i} className="border border-gray-300 py-3 px-2">
              <p className="text-xl text-gray-800">{s.val}</p>
              <p className="text-xs text-gray-500 italic mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ══ FEATURES ══ */}
      <section className="py-12 border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4">
          <div className="text-center mb-8">
            <h2 className="text-gray-800">Fitur Utama</h2>
            <p className="text-xs text-gray-400 italic mt-1">
              [ Deskripsi singkat manfaat platform ]
            </p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              {
                icon: "⊕",
                title: "Upload CSV / Excel",
                desc: "Unggah file ulasan langsung dari seller center marketplace",
              },
              {
                icon: "◈",
                title: "Klasifikasi NLP Otomatis",
                desc: "AI berbasis Python mengelompokkan ulasan: Positif, Negatif, Netral",
              },
              {
                icon: "▦",
                title: "Dashboard Visualisasi",
                desc: "Pie chart, line chart, dan word cloud untuk melihat tren kepuasan",
              },
              {
                icon: "⬇",
                title: "Ekspor Laporan",
                desc: "Unduh laporan lengkap dalam format PDF atau CSV (Fitur Premium)",
              },
            ].map((f, i) => (
              <div
                key={i}
                className="border border-gray-300 p-4 bg-white hover:bg-gray-50"
              >
                <div className="w-10 h-10 border border-gray-400 bg-gray-100 flex items-center justify-center text-lg text-gray-600 mb-3">
                  {f.icon}
                </div>
                <h4 className="text-gray-800 mb-1">{f.title}</h4>
                <p className="text-xs text-gray-500 italic leading-relaxed">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ══ HOW IT WORKS ══ */}
      <section className="py-12 border-b border-gray-200 bg-gray-50">
        <div className="max-w-6xl mx-auto px-4">
          <h2 className="text-center text-gray-800 mb-8">Cara Kerja</h2>
          <div className="grid md:grid-cols-3 gap-6">
            {[
              {
                step: "01",
                title: "Unggah Ulasan",
                desc: "Upload file CSV/Excel atau paste teks ulasan secara langsung",
              },
              {
                step: "02",
                title: "AI Memproses",
                desc: "Model NLP menganalisis dan mengklasifikasikan setiap ulasan secara otomatis",
              },
              {
                step: "03",
                title: "Lihat Hasilnya",
                desc: "Dashboard menampilkan visualisasi, kata kunci, dan tabel hasil analisis",
              },
            ].map((s, i) => (
              <div key={i} className="border border-gray-300 bg-white p-5">
                <div className="text-2xl text-gray-300 mb-2">{s.step}</div>
                <h4 className="text-gray-800 mb-2">{s.title}</h4>
                <p className="text-xs text-gray-500 italic leading-relaxed">
                  {s.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>
    </>
  );
}
