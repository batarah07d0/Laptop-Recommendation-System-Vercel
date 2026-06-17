import { useState } from "react";

export default function Result({ results, onBack }) {
  // State untuk menyimpan pilihan urutan (Sorting)
  const [sortBy, setSortBy] = useState("rekomendasi");
  // State untuk mengontrol buka/tutup custom dropdown
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  // Logika untuk mengurutkan data sebelum ditampilkan
  const sortedData = results.data
    ? [...results.data].sort((a, b) => {
        if (sortBy === "harga") {
          return (a.price || 0) - (b.price || 0); // Urutkan Harga dari Termurah ke Termahal
        }
        // Default: Urutkan berdasarkan Skor Kemiripan (Rekomendasi Tertinggi)
        return (b.similarity_score || 0) - (a.similarity_score || 0);
      })
    : [];

  // Daftar opsi sorting untuk memudahkan rendering custom dropdown
  const sortOptions = [
    { id: "rekomendasi", label: "Urutkan: Rekomendasi Terbaik" },
    { id: "harga", label: "Urutkan: Harga Termurah" },
  ];

  return (
    <div className="max-w-7xl mx-auto py-4 md:py-8 px-4">
      {/* Screenshot Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-4 rounded-r-lg shadow-sm">
        <p className="text-base text-yellow-700 font-bold">
          PERHATIAN: Silakan lakukan Screenshot pada halaman ini!
        </p>
        <p className="text-sm text-yellow-600">
          Sistem tidak menyimpan data ini, hasil rekomendasi akan hilang jika
          Anda menutup atau menyegarkan halaman ini!
        </p>
      </div>

      {/* Fallback Warning */}
      {results.is_fallback && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-4 mb-6 rounded-r-lg shadow-sm">
          <div>
            <p className="text-base text-blue-800 font-bold">
              {results.strict_count === 0
                ? "Mohon Maaf, kami tidak menemukan laptop yang 100% cocok dengan filter Spesifikasi Anda."
                : `Kami hanya menemukan ${results.strict_count} laptop yang cocok dengan filter Spesifikasi Anda.`}
            </p>
            <p className="text-sm text-blue-700 mt-1">
              Sistem otomatis menampilkan <strong>Rekomendasi Terdekat</strong>{" "}
              lainnya yang paling relevan namun tetap di bawah batas anggaran
              Anda.
            </p>
          </div>
        </div>
      )}

      {/* ========================================== */}
      {/* HEADER & FITUR SORTING (CUSTOM DROPDOWN UI)*/}
      {/* ========================================== */}
      <div className="flex flex-col lg:flex-row justify-between items-start lg:items-center mb-6 gap-4 border-b border-gray-200 pb-4">
        <h2 className="text-2xl font-bold text-gray-800">
          Hasil Rekomendasi Laptop
        </h2>

        <div className="flex flex-col sm:flex-row flex-wrap gap-3 w-full lg:w-auto items-center relative">
          {/* Custom Dropdown Sorting */}
          {results.data && results.data.length > 0 && (
            <div className="relative w-full sm:w-auto">
              <button
                type="button"
                onClick={() => setIsDropdownOpen(!isDropdownOpen)}
                className={`w-full sm:w-auto flex items-center justify-between bg-white border ${
                  isDropdownOpen
                    ? "border-blue-500 ring-2 ring-blue-100"
                    : "border-gray-300"
                } text-gray-700 font-semibold py-2.5 px-4 rounded-lg shadow-sm hover:bg-gray-50 focus:outline-none transition-all text-sm cursor-pointer`}
              >
                <div className="flex items-center">
                  <svg
                    className="w-4 h-4 text-blue-600 mr-2"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth="2"
                      d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12"
                    ></path>
                  </svg>
                  {sortOptions.find((opt) => opt.id === sortBy)?.label}
                </div>
                <svg
                  className={`w-4 h-4 text-gray-500 ml-4 transition-transform duration-200 ${
                    isDropdownOpen ? "rotate-180" : ""
                  }`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M19 9l-7 7-7-7"
                  ></path>
                </svg>
              </button>

              {/* Menu Popup Custom */}
              {isDropdownOpen && (
                <div className="absolute z-20 mt-2 w-full sm:w-56 bg-white rounded-lg shadow-xl border border-gray-100 overflow-hidden animate-fade-in-down">
                  <ul className="py-1 text-sm text-gray-700">
                    {sortOptions.map((option) => (
                      <li key={option.id}>
                        <button
                          type="button"
                          onClick={() => {
                            setSortBy(option.id);
                            setIsDropdownOpen(false); // Tutup menu setelah dipilih
                          }}
                          className={`w-full text-left px-4 py-2.5 transition-colors cursor-pointer ${
                            sortBy === option.id
                              ? "bg-blue-50 text-blue-700 font-bold border-l-4 border-blue-500"
                              : "hover:bg-gray-50 hover:text-blue-600 border-l-4 border-transparent"
                          }`}
                        >
                          {option.label}
                        </button>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Tombol Kuesioner & Cari Ulang */}
          <div className="flex gap-3 w-full sm:w-auto">
            <a
              href="https://forms.gle/3R2MH5TBvXJi7YCT9"
              target="_blank"
              rel="noreferrer"
              className="flex-1 sm:flex-none text-center bg-purple-100 hover:bg-purple-200 text-purple-700 font-semibold py-2.5 px-4 rounded-lg transition-colors flex items-center justify-center text-sm shadow-sm"
            >
              <svg
                className="w-4 h-4 mr-1.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                ></path>
              </svg>
              Isi Kuesioner
            </a>
            <button
              onClick={onBack}
              className="flex-1 sm:flex-none text-center bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2.5 px-6 rounded-lg transition-colors text-sm cursor-pointer shadow-sm"
            >
              Cari Ulang
            </button>
          </div>
        </div>
      </div>

      {/* Laptop Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {sortedData && sortedData.length > 0 ? (
          sortedData.map((laptop, index) => (
            <div
              key={index}
              className="bg-white rounded-xl border border-gray-200 shadow-sm flex flex-col hover:shadow-md transition-shadow"
            >
              <div className="h-48 bg-gray-50 p-4 flex justify-center items-center rounded-t-xl border-b border-gray-100">
                <img
                  src={
                    laptop.image_url ||
                    "https://via.placeholder.com/400x300?text=No+Image"
                  }
                  className="max-h-full object-contain mix-blend-multiply"
                  alt={`Gambar Laptop ${laptop.name || "Rekomendasi"}`}
                />
              </div>
              <div className="p-5 flex-1 flex flex-col">
                <div className="flex justify-between items-start mb-3">
                  <span className="text-xs font-bold bg-blue-100 text-blue-800 py-1 px-2.5 rounded-full">
                    {laptop.brand || "Merek Unknown"}
                  </span>
                  <span className="text-xs font-bold bg-green-100 text-green-800 py-1 px-2.5 rounded-full flex items-center">
                    <svg
                      className="w-3 h-3 mr-1"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      ></path>
                    </svg>
                    Cocok: {((laptop.similarity_score || 0) * 100).toFixed(1)}%
                  </span>
                </div>

                <h3 className="text-lg font-bold text-gray-900 mb-1 leading-tight">
                  {laptop.name || "Laptop Tanpa Nama"}
                </h3>

                <p className="text-xl font-black text-orange-600 mb-3">
                  {laptop.price && laptop.price > 0
                    ? `Rp ${Number(laptop.price).toLocaleString("id-ID")}`
                    : "Harga Tidak Tersedia"}
                </p>

                <div className="grid grid-cols-2 gap-y-2 gap-x-4 text-sm text-gray-700 bg-gray-50 p-4 rounded-lg border border-gray-100 flex-1 content-start">
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      CPU (Prosesor)
                    </span>{" "}
                    <span className="font-semibold">{laptop.cpu || "-"}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      GPU (Grafis)
                    </span>{" "}
                    <span className="font-semibold">{laptop.gpu || "-"}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      RAM
                    </span>{" "}
                    <span className="font-semibold">{laptop.ram || "-"}</span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      Penyimpanan
                    </span>{" "}
                    <span className="font-semibold">
                      {laptop.storage || "-"}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      Tipe Penyimpanan
                    </span>{" "}
                    <span className="font-semibold">
                      {laptop.storage_type || "-"}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      Berat
                    </span>{" "}
                    <span className="font-semibold">
                      {laptop.weight_kg || "-"}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      Layar
                    </span>{" "}
                    <span className="font-semibold">
                      {laptop.screen_size || "Ukuran tidak diketahui"}
                    </span>
                  </div>
                  <div>
                    <span className="block text-xs text-gray-400 mb-0.5">
                      Tipe Layar
                    </span>{" "}
                    <span className="font-semibold">
                      {laptop.panel_type || "Tipe tidak diketahui"}
                    </span>
                  </div>
                </div>

                <div className="mt-auto pt-4 flex flex-col gap-3">
                  <div className="p-3 bg-blue-50 border border-blue-100 rounded-lg h-full flex flex-col justify-center">
                    <p className="text-sm font-bold text-blue-800 uppercase tracking-wider mb-1">
                      Mengapa ini cocok?
                    </p>
                    <p className="text-sm text-blue-900 italic">
                      {laptop.explanation}
                    </p>
                  </div>

                  <div>
                    <a
                      href={laptop.product_link || "#"}
                      target="_blank"
                      rel="noreferrer"
                      className="block w-full text-center border-2 border-blue-600 text-blue-600 hover:bg-blue-600 hover:text-white font-bold py-2.5 rounded-lg transition-colors"
                    >
                      Lihat Detail & Beli
                    </a>
                  </div>
                </div>
              </div>
            </div>
          ))
        ) : (
          /* ========================================== */
          /* TAMPILAN JIKA HASIL KOSONG (EMPTY STATE)   */
          /* ========================================== */
          <div className="col-span-1 sm:col-span-2 lg:col-span-3 bg-white rounded-xl border border-gray-200 shadow-sm p-8 text-center mt-4">
            {/* Ikon Netral (Kaca Pembesar Tanda Silang) */}
            <div className="w-24 h-24 bg-gray-50 border border-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
              <svg
                className="w-12 h-12 text-gray-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="1.5"
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM13 10H7"
                ></path>
              </svg>
            </div>

            <h3 className="text-2xl font-bold text-gray-800 mb-3">
              Laptop Tidak Ditemukan
            </h3>
            <p className="text-gray-600 mb-8 max-w-lg mx-auto">
              Sistem kami tidak dapat menemukan laptop yang cocok. Hal ini wajar
              terjadi jika kombinasi filter spesifikasi Anda terlalu ketat.
            </p>

            {/* Kotak Saran & Tips (Warna Biru Informatif) */}
            <div className="bg-blue-50 text-left p-6 md:p-8 rounded-xl border border-blue-100 max-w-2xl mx-auto mb-8 shadow-sm">
              <h4 className="font-bold text-blue-800 mb-4 flex items-center text-lg">
                <svg
                  className="w-6 h-6 mr-2 text-blue-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  ></path>
                </svg>
                💡 Saran Perbaikan Pencarian:
              </h4>
              <ul className="list-none space-y-4 text-blue-900 text-sm md:text-base">
                <li className="flex items-start">
                  <span className="bg-blue-200 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5 shrink-0">
                    1
                  </span>
                  <div>
                    <strong>Naikkan Batas Anggaran (Harga):</strong> Spesifikasi
                    keras yang Anda minta (seperti CPU/GPU gaming) mungkin harga
                    pasarnya melebihi batas <em>slider</em> Anda.
                  </div>
                </li>
                <li className="flex items-start">
                  <span className="bg-blue-200 text-blue-800 rounded-full w-6 h-6 flex items-center justify-center text-xs font-bold mr-3 mt-0.5 shrink-0">
                    2
                  </span>
                  <div>
                    <strong>Perlonggar Filter Lanjutan:</strong> Jika Anda
                    mengunci banyak syarat sekaligus (misal: harus RAM 32GB{" "}
                    <em>dan</em> Layar OLED), cobalah ubah beberapa opsi kembali
                    ke <strong>"Semua Pilihan"</strong>.
                  </div>
                </li>
              </ul>
            </div>

            {/* Tombol Aksi */}
            <button
              onClick={onBack}
              className="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-bold py-3.5 px-8 rounded-lg transition-all cursor-pointer shadow-md hover:shadow-lg hover:-translate-y-0.5"
            >
              <svg
                className="w-5 h-5 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"
                ></path>
              </svg>
              Atur Ulang Filter Spesifikasi
            </button>
          </div>
        )}
      </div>

      {/* Skripsi Banner */}
      {results.data && results.data.length > 0 && (
        <div className="mt-8 bg-linear-to-br from-purple-50 to-indigo-50 border border-purple-100 rounded-2xl p-8 md:p-10 text-center shadow-sm relative overflow-hidden">
          <div className="absolute top-0 right-0 -mt-4 -mr-4 w-24 h-24 bg-purple-200 rounded-full mix-blend-multiply filter blur-xl opacity-50"></div>
          <div className="absolute bottom-0 left-0 -mb-4 -ml-4 w-24 h-24 bg-indigo-200 rounded-full mix-blend-multiply filter blur-xl opacity-50"></div>

          <div className="relative z-10">
            <span className="inline-block py-1 px-3 rounded-full bg-purple-100 text-purple-700 text-xs font-bold mb-4 tracking-wider uppercase">
              Bantu Penelitian Skripsi
            </span>
            <h3 className="text-2xl md:text-3xl font-extrabold text-gray-900 mb-4">
              Bagaimana Pengalaman Anda?
            </h3>
            <p className="text-gray-600 mb-8 max-w-2xl mx-auto md:text-lg">
              Apakah hasil rekomendasi laptop di atas sesuai dengan harapan
              Anda? Mohon luangkan waktu <strong>2-5 menit</strong> untuk
              mengisi kuesioner evaluasi sistem.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <a
                href="https://forms.gle/3R2MH5TBvXJi7YCT9"
                target="_blank"
                rel="noreferrer"
                className="bg-purple-600 hover:bg-purple-700 text-white font-bold py-3.5 px-8 rounded-xl shadow-lg hover:shadow-xl transition-all transform hover:-translate-y-0.5 flex items-center justify-center cursor-pointer"
              >
                <svg
                  className="w-5 h-5 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01"
                  ></path>
                </svg>
                Isi Kuesioner Sekarang
              </a>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
