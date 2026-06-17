import axios from "axios";
import { useState } from "react";
import InfoTooltip from "../components/InfoTooltip";

export default function Home({ onSearchResults }) {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);

  // 10 Filter States
  const [description, setDescription] = useState("");
  const [maxPrice, setMaxPrice] = useState(25000000);
  const [maxWeight, setMaxWeight] = useState(2.0);
  const [maxScreen, setMaxScreen] = useState(14.0);
  const [cpu, setCpu] = useState("All");
  const [ram, setRam] = useState("All");
  const [storage, setStorage] = useState("All");
  const [os, setOs] = useState("All");
  const [gpuType, setGpuType] = useState("All");
  const [panelType, setPanelType] = useState("All");
  const [screenQuality, setScreenQuality] = useState("All");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError("");

    const data = {
      description,
      max_price: maxPrice,
      max_weight: maxWeight,
      max_screen: maxScreen,
      cpu,
      ram,
      storage,
      os,
      gpu_type: gpuType,
      panel_type: panelType,
      screen_quality: screenQuality,
    };

    try {
      const response = await axios.post("/api/recommend", data);
      onSearchResults(response.data);
    } catch (err) {
      console.error(err);
      setError(
        "Gagal terhubung ke Mesin Pencarian. Server mungkin sedang sibuk atau terjadi gangguan.",
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-6 md:py-10 px-4">
      {/* Banner Header */}
      <div className="text-center mb-8 md:mb-10">
        <h1 className="text-2xl md:text-3xl font-bold text-gray-800 mb-2">
          Cari Laptop Yang Anda Butuhkan!
        </h1>
        <p className="text-sm md:text-base text-gray-600">
          Ceritakan kebutuhan Anda, sistem cerdas kami akan mencarikan laptop
          yang paling sesuai dengan kebutuhan Anda.
        </p>
      </div>

      <div className="bg-white p-5 md:p-8 rounded-xl shadow-lg border border-gray-100">
        <form onSubmit={handleSubmit}>
          {/* Form Deskripsi Cerita User */}
          <div className="mb-2">
            <label className="block text-sm font-semibold text-gray-700 mb-2">
              Ceritakan Kebutuhan Anda (Wajib)
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows="4"
              required
              className="w-full p-3 text-sm md:text-base border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all outline-none"
              placeholder="Contoh: Saya butuh laptop untuk mengerjakan skripsi, sering buka banyak tab browser, bikin desain di Canva, dan kadang main game ringan..."
            />
          </div>

          {/* Slider Batas Harga Maksimal */}
          <div className="mb-3 bg-blue-50 p-5 md:p-6 rounded-lg border border-blue-100">
            <div className="relative">
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm font-semibold text-gray-700 flex items-center">
                  Batas Harga{" "}
                  <InfoTooltip text="Geser untuk mengatur batas anggaran maksimal Anda!" />
                </label>
                <span className="text-blue-600 font-bold text-sm">
                  Rp {maxPrice.toLocaleString("id-ID")}
                </span>
              </div>
              <input
                type="range"
                min="3000000"
                max="50000000"
                step="500000"
                value={maxPrice}
                onChange={(e) => setMaxPrice(Number(e.target.value))}
                className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer"
              />
            </div>
          </div>

          <div className="mb-3 text-center border-t border-b border-gray-100 py-3">
            <button
              type="button"
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="text-xs md:text-sm font-bold text-gray-500 hover:text-blue-600 transition-colors flex items-center justify-center w-full p-2 rounded-lg hover:bg-gray-50 focus:outline-none cursor-pointer"
            >
              <svg
                className={`w-4 h-4 mr-2 transition-transform duration-200 ${showAdvanced ? "rotate-180" : ""}`}
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
              <span>
                {showAdvanced
                  ? "Sembunyikan Filter Spesifikasi Lanjutan"
                  : "Tampilkan Filter Spesifikasi Lanjutan (Jika Memahami Spesifikasi Laptop Dengan Baik)"}
              </span>
            </button>
          </div>

          {showAdvanced && (
            <div className="bg-gray-50 p-5 md:p-6 rounded-lg border border-gray-200 mb-3 space-y-6">
              <div>
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
                  Dimensi & Ukuran Fisik
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {/* Slider Batas Berat */}
                  <div className="relative">
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-gray-700 flex items-center">
                        Batas Berat{" "}
                        <InfoTooltip text="Kurangi angka ini jika Anda ingin sering bepergian sambil membawa laptop! <br> (Sangat ringan < 1.5 Kg)" />
                      </label>
                      <span className="text-blue-600 font-bold text-sm">
                        {maxWeight.toFixed(1)} Kg
                      </span>
                    </div>
                    <input
                      type="range"
                      min="1.0"
                      max="3.0"
                      step="0.1"
                      value={maxWeight}
                      onChange={(e) => setMaxWeight(Number(e.target.value))}
                      className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>

                  {/* Slider Batas Ukuran Layar */}
                  <div className="relative">
                    <div className="flex justify-between items-center mb-2">
                      <label className="text-sm font-semibold text-gray-700 flex items-center">
                        Batas Ukuran Layar{" "}
                        <InfoTooltip text="Ukuran standar adalah 14 Inch. Besarkan jika butuh layar lebar untuk desain, menonton film atau bermain game!" />
                      </label>
                      <span className="text-blue-600 font-bold text-sm">
                        {maxScreen.toFixed(1)} Inch
                      </span>
                    </div>
                    <input
                      type="range"
                      min="11.0"
                      max="18.0"
                      step="0.5"
                      value={maxScreen}
                      onChange={(e) => setMaxScreen(Number(e.target.value))}
                      className="w-full h-2 bg-gray-300 rounded-lg appearance-none cursor-pointer"
                    />
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-3">
                  Spesifikasi Komponen (Hardware)
                </h3>
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                  {/* Dropdown CPU */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Tipe Prosesor (CPU){" "}
                      <InfoTooltip text="Intel dan AMD sama bagusnya. Makin tinggi angkanya (seperti i9 atau Ryzen 9), laptop makin ngebut. Jika bingung, biarkan di Pilihan Semua Prosesor!" />
                    </label>
                    <select
                      value={cpu}
                      onChange={(e) => setCpu(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white outline-none cursor-pointer"
                    >
                      <option value="All">Semua Prosesor</option>
                      <optgroup label="Intel">
                        <option value="Intel Core i3">
                          Intel Core i3 (Ringan)
                        </option>
                        <option value="Intel Core i5">
                          Intel Core i5 (Menengah)
                        </option>
                        <option value="Intel Core i7">
                          Intel Core i7 (Tinggi)
                        </option>
                        <option value="Intel Core i9">
                          Intel Core i9 (Sangat Tinggi)
                        </option>
                        <option value="Intel Core Ultra">
                          Intel Core Ultra (AI/Modern)
                        </option>
                      </optgroup>
                      <optgroup label="AMD">
                        <option value="AMD Ryzen 3">
                          AMD Ryzen 3 (Ringan)
                        </option>
                        <option value="AMD Ryzen 5">
                          AMD Ryzen 5 (Menengah)
                        </option>
                        <option value="AMD Ryzen 7">
                          AMD Ryzen 7 (Tinggi)
                        </option>
                        <option value="AMD Ryzen 9">
                          AMD Ryzen 9 (Sangat Tinggi)
                        </option>
                        <option value="AMD Ryzen AI">
                          AMD Ryzen AI (AI/Modern)
                        </option>
                      </optgroup>
                      <optgroup label="Apple">
                        <option value="Apple M2">Apple M2</option>
                        <option value="Apple M3">Apple M3</option>
                        <option value="Apple M4">Apple M4</option>
                        <option value="Apple M5">Apple M5</option>
                      </optgroup>
                    </select>
                  </div>

                  {/* Dropdown RAM */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Kapasitas RAM{" "}
                      <InfoTooltip text="Makin besar angkanya (seperti 16 GB), makin banyak aplikasi yang bisa Anda buka secara bersamaan tanpa gangguan. Untuk penggunaan ringan, 8 GB sudah cukup. Jika bingung, biarkan di Pilihan Semua Kapasitas!" />
                    </label>
                    <select
                      value={ram}
                      onChange={(e) => setRam(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white outline-none cursor-pointer"
                    >
                      <option value="All">Semua Kapasitas</option>
                      <option value="4 GB">4 GB</option>
                      <option value="8 GB">8 GB</option>
                      <option value="16 GB">16 GB</option>
                      <option value="24 GB">24 GB</option>
                      <option value="32 GB">32 GB</option>
                      <option value="64 GB">64 GB</option>
                    </select>
                  </div>

                  {/* Dropdown Storage */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Penyimpanan (Storage){" "}
                      <InfoTooltip text="256 GB cukup untuk tugas kuliah/kantor. 512 GB cukup untuk tambah beberapa game ringan. Pilih 1 TB atau 2 TB jika ingin bermain game berat dan menyimpan file besar. Jika bingung, biarkan di Pilihan Kapasitas!" />
                    </label>
                    <select
                      value={storage}
                      onChange={(e) => setStorage(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 bg-white outline-none cursor-pointer"
                    >
                      <option value="All">Semua Kapasitas</option>
                      <option value="128 GB">128 GB</option>
                      <option value="256 GB">256 GB</option>
                      <option value="512 GB">512 GB</option>
                      <option value="1000">1 TB</option>
                      <option value="2000">2 TB</option>
                    </select>
                  </div>

                  {/* Dropdown Sistem Operasi */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Sistem Operasi{" "}
                      <InfoTooltip text="Pilih 'Windows' jika terbiasa menggunakan Word/Excel pada umumnya. Sistem Operasi 'macOS' khusus untuk laptop dengan brand Apple. Jika bingung, biarkan di Pilihan Semua Sistem Operasi!" />
                    </label>
                    <select
                      value={os}
                      onChange={(e) => setOs(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg bg-white outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    >
                      <option value="All">Semua OS</option>
                      <option value="Windows">
                        Windows (Paling Umum & Populer)
                      </option>
                      <option value="macOS">macOS (Khusus Laptop Apple)</option>
                    </select>
                  </div>

                  {/* Dropdown GPU Type */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Tipe Kartu Grafis (GPU){" "}
                      <InfoTooltip text="Pilih 'Dedicated' (seperti NVIDIA RTX) jika laptop akan digunakan untuk main game berat atau editing video profesional. Jika bingung, biarkan di Pilihan Semua Tipe GPU!" />
                    </label>
                    <select
                      value={gpuType}
                      onChange={(e) => setGpuType(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg bg-white outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    >
                      <option value="All">Semua Tipe GPU</option>
                      <option value="Integrated">
                        Integrated (Irit Baterai)
                      </option>
                      <option value="Dedicated">
                        Dedicated (Performa Tinggi)
                      </option>
                    </select>
                  </div>

                  {/* Dropdown Panel Type */}
                  <div className="relative">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Tipe Panel Layar{" "}
                      <InfoTooltip text="Tipe Panel Layar OLED memberi warna paling pekat. IPS memberi warna natural dan sudut pandang yang luas (aman untuk mata). Jika bingung, biarkan di Pilihan Semua Tipe Panel Layar!" />
                    </label>
                    <select
                      value={panelType}
                      onChange={(e) => setPanelType(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg bg-white outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    >
                      <option value="All">Semua Tipe Panel Layar</option>
                      <option value="IPS">IPS</option>
                      <option value="OLED">OLED</option>
                      <option value="TN">TN</option>
                      <option value="Mini LED">Mini LED</option>
                    </select>
                  </div>

                  {/* Dropdown Resolusi Layar */}
                  <div className="relative flex-1 sm:col-span-2 md:col-span-3">
                    <label className="flex items-center text-sm font-semibold text-gray-700 mb-2">
                      Resolusi Layar{" "}
                      <InfoTooltip text="Makin tinggi resolusi layar (seperti 2.8K), gambar makin mulus dan tajam, namun bisa membuat baterai menjadi sedikit lebih boros. Jika bingung, biarkan di Pilihan Semua Resolusi Layar!" />
                    </label>
                    <select
                      value={screenQuality}
                      onChange={(e) => setScreenQuality(e.target.value)}
                      className="w-full p-2.5 text-sm border border-gray-300 rounded-lg bg-white outline-none focus:ring-2 focus:ring-blue-500 cursor-pointer"
                    >
                      <option value="All">Semua Resolusi Layar</option>
                      <option value="HD">HD (Kualitas Dasar)</option>
                      <option value="FHD">FHD (Standar Ideal Saat Ini)</option>
                      <option value="WUXGA">
                        WUXGA (Standar Layar Sedikit Lebih Tinggi)
                      </option>
                      <option value="2.5K">
                        WQXGA (Sangat Tajam & Jernih)
                      </option>
                      <option value="2.8K">2.8K (Super Tajam)</option>
                      <option value="3K+">3K+ (Kualitas Premium)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Tampilan Pesan Error */}
          {error && (
            <div className="mt-4 mb-4 bg-red-50 text-red-600 p-4 rounded-lg font-semibold text-center">
              {error}
            </div>
          )}

          {/* Tombol Aksi Submit Akhir */}
          <button
            type="submit"
            disabled={isLoading}
            className={`w-full hover:bg-blue-700 text-white font-bold py-3 md:py-4 px-4 rounded-lg shadow-md transition-colors flex justify-center items-center mt-2 text-sm md:text-base cursor-pointer ${
              isLoading
                ? "bg-blue-600 opacity-75 cursor-not-allowed shadow-none"
                : "bg-blue-600"
            }`}
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                  xmlns="http://www.w3.org/2000/svg"
                  fill="none"
                  viewBox="0 0 24 24"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  ></circle>
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                  ></path>
                </svg>
                Sistem Sedang Mencari Rekomendasi Terbaik...
              </>
            ) : (
              <>
                Cari Rekomendasi Laptop
                <svg
                  className="w-5 h-5 ml-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth="2"
                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                  ></path>
                </svg>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
