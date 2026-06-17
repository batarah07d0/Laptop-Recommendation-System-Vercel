export default function About({ onNavigate }) {
  return (
    <div className="max-w-4xl mx-auto py-10 px-4">
      <div className="bg-white rounded-2xl shadow-lg border border-gray-100 p-8 md:p-12">
        <div className="text-center mb-10">
          <h1 className="text-3xl font-extrabold text-gray-900 mb-4">
            Tentang Sistem Rekomendasi
          </h1>
          <div className="w-24 h-1 bg-blue-600 mx-auto rounded-full"></div>
        </div>

        <div className="space-y-6 text-gray-700 leading-relaxed text-lg mb-12">
          <p>
            Sistem Rekomendasi Laptop ini dikembangkan untuk membantu Anda
            menemukan laptop yang paling sesuai berdasarkan kebutuhan spesifik
            dan anggaran yang dimiliki. Seringkali, pengguna awam menghadapi
            kesulitan saat memilih laptop karena keterbatasan pemahaman terhadap
            istilah-istilah teknis perangkat keras (<em>hardware</em>). Sistem
            ini hadir sebagai solusi praktis untuk menjembatani masalah
            tersebut.
          </p>

          <h3 className="text-xl font-bold text-gray-800 mt-8 mb-3">
            Bagaimana Sistem Ini Membantu Anda?
          </h3>
          <p>
            Alih-alih menuntut Anda untuk memahami detail teknis seperti jenis
            prosesor atau kartu grafis secara mendalam, sistem ini bekerja
            dengan menganalisis narasi kebutuhan yang Anda sampaikan. Anda cukup
            menceritakan bagaimana laptop tersebut akan digunakan dalam
            aktivitas sehari-hari.
          </p>
          <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-blue-500 mb-4">
            <p className="text-sm md:text-base italic text-gray-600">
              "Saya butuh laptop untuk kebutuhan kuliah teknik, sering
              menggunakan aplikasi coding, sesekali mengedit video ringan, dan
              baterainya cukup awet untuk dibawa seharian."
            </p>
          </div>

          <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 my-6">
            <h4 className="font-bold text-blue-800 mb-2">
              3 Langkah Mudah Penggunaan:
            </h4>
            <ol className="list-decimal list-inside space-y-2 text-blue-900 text-sm md:text-base">
              <li>
                <strong>Sampaikan Kebutuhan:</strong> Tuliskan deskripsi
                kebutuhan aktivitas Anda pada kolom yang tersedia secara jelas.
              </li>
              <li>
                <strong>Sesuaikan Batasan (Opsional):</strong> Atur filter harga
                maksimal dan preferensi fisik laptop (seperti berat dan ukuran
                layar) jika Anda memiliki kriteria khusus.
              </li>
              <li>
                <strong>Dapatkan Hasil Rekomendasi:</strong> Sistem akan
                memproses data secara instan dan menampilkan daftar laptop yang
                paling relevan dengan profil kebutuhan Anda.
              </li>
            </ol>
          </div>
        </div>

        <hr className="border-gray-200 my-10" />

        <div className="text-center mb-8">
          <h2 className="text-2xl font-extrabold text-gray-900 mb-4">
            Cara Kerja Sistem Pemilihan Laptop
          </h2>
          <div className="w-24 h-1 bg-purple-600 mx-auto rounded-full"></div>
        </div>

        <div className="space-y-4 text-gray-700 leading-relaxed text-lg">
          <p className="mb-6">
            Pencarian rekomendasi pada aplikasi ini tidak dilakukan secara acak.
            Sistem menerapkan pendekatan{" "}
            <strong>
              <em>Content-Based Filtering</em>
            </strong>{" "}
            yang dioptimalkan dengan metode Pemrosesan Bahasa Alami (
            <em>Natural Language Processing</em>), menggunakan algoritma{" "}
            <strong>
              <em>TF-IDF</em>
            </strong>{" "}
            dan{" "}
            <strong>
              <em>Cosine Similarity</em>
            </strong>
            .
          </p>

          <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-xl font-bold text-blue-700 mb-3 flex items-center">
              <svg
                className="w-6 h-6 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 002-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
                ></path>
              </svg>
              1. Pencocokan Isi (<em>Content-Based Filtering</em>)
            </h3>
            <p className="text-sm md:text-base">
              Sistem menganalisis "isi" atau "spesifikasi" dari setiap laptop
              yang ada di dalam <em>database</em>. Sistem akan menyaring dan
              merekomendasikan laptop yang memiliki profil fitur yang paling
              identik dengan kriteria yang Anda minta pada form pencarian.
            </p>
          </div>

          <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-xl font-bold text-purple-700 mb-3 flex items-center">
              <svg
                className="w-6 h-6 mr-2"
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
              2. Pembobotan Kata (TF-IDF)
            </h3>
            <p className="text-sm md:text-base">
              Algoritma <em>Term Frequency-Inverse Document Frequency</em>{" "}
              (TF-IDF) bertugas menganalisis teks yang Anda masukkan,
              mengabaikan kata hubung umum, dan memberikan bobot nilai yang
              tinggi pada kata-kata kunci yang krusial (misalnya "Desain", "
              <em>Coding</em>", atau "<em>Gaming</em>").
            </p>
          </div>

          <div className="bg-gray-50 p-6 rounded-xl border border-gray-200">
            <h3 className="text-xl font-bold text-indigo-700 mb-3 flex items-center">
              <svg
                className="w-6 h-6 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth="2"
                  d="M14 10l-2 1m0 0l-2-1m2 1v2.5M20 7l-2 1m2-1l-2-1m2 1v2.5M14 4l-2-1-2 1M4 7l2-1M4 7l2 1M4 7v2.5M12 21l-2-1m2 1l2-1m-2 1v-2.5M6 18l-2-1v-2.5M18 18l2-1v-2.5"
                ></path>
              </svg>
              3. Penghitungan Kemiripan (<em>Cosine Similarity</em>)
            </h3>
            <p className="text-sm md:text-base">
              Setelah kebutuhan dikonversi menjadi angka bobot, algoritma{" "}
              <em>Cosine Similarity</em>
              mengukur seberapa mirip "Vektor Kebutuhan Anda" dengan "Vektor
              Spesifikasi Laptop". Laptop dengan skor kemiripan tertinggi akan
              diurutkan sebagai rekomendasi utama.
            </p>
          </div>
        </div>

        <div className="text-center mt-10">
          <button
            onClick={() => onNavigate("home")}
            className="inline-block bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 px-8 rounded-lg shadow-md transition-colors"
          >
            Mulai Cari Laptop Anda
          </button>
        </div>
      </div>
    </div>
  );
}
