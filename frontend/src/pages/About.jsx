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
            Sistem Rekomendasi Laptop ini dibangun untuk membantu Anda yang
            merasa kebingungan dengan spesifikasi laptop dan membantu anda untuk
            menemukan laptop yang paling pas dengan kebutuhan dan kantong Anda.
          </p>

          <h3 className="text-xl font-bold text-gray-800 mt-8 mb-3">
            Bagaimana Sistem Ini Membantu Anda?
          </h3>
          <p>
            Bayangkan sistem ini sebagai seorang{" "}
            <strong>Sales Toko Komputer yang Pintar dan Jujur</strong>.
            Alih-alih menyuruh Anda memilih prosesor atau kartu grafis (yang
            mungkin Anda tidak mengerti), Anda cukup menceritakan kebutuhan Anda
            kepada kami.
          </p>
          <p>
            Ketikkan saja:{" "}
            <em>
              <strong>
                "Saya butuh laptop buat kuliah, ngetik skripsi, sesekali nonton
                Netflix, dan tidak terlalu berat kalau dibawa ke kampus."
              </strong>
            </em>
          </p>

          <div className="bg-blue-50 p-6 rounded-xl border border-blue-100 my-6">
            <h4 className="font-bold text-blue-800 mb-2">3 Langkah Mudah:</h4>
            <ol className="list-decimal list-inside space-y-2 text-blue-900">
              <li>
                <strong>Ceritakan</strong> kebutuhan Anda dengan jelas.
              </li>
              <li>
                <strong>Atur batas</strong> harga dan spesifikasi (jika anda
                tidak memahami spesifikasi laptop anda bisa memilih pilihan
                default) yang Anda inginkan.
              </li>
              <li>
                Sistem akan <strong>mencocokkan</strong> kebutuhan Anda dengan
                ratusan laptop yang ada di database kami secara instan.
              </li>
            </ol>
          </div>
        </div>

        <hr className="border-gray-200 my-10" />

        <div className="text-center mb-5">
          <h2 className="text-2xl font-extrabold text-gray-900 mb-4">
            Cara Kerja Kecerdasan Buatan Kami
          </h2>
          <div className="w-24 h-1 bg-purple-600 mx-auto rounded-full"></div>
        </div>

        <div className="space-y-3 text-gray-700 leading-relaxed text-lg">
          <p>
            Mungkin Anda bertanya-tanya,{" "}
            <em>
              <strong>
                "Bagaimana mesin ini bisa tahu laptop mana yang cocok dengan
                kebutuhan saya?"
              </strong>
            </em>{" "}
            <br />
            Rahasia di baliknya adalah metode{" "}
            <strong>Content-Based Filtering</strong> yang digerakkan oleh
            algoritma Pemrosesan Bahasa Alami (NLP) bernama{" "}
            <strong>TF-IDF</strong> dan <strong>Cosine Similarity</strong>.
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
              1. Pencocokan Isi (Content-Based Filtering)
            </h3>
            <p className="mb-4 text-sm md:text-base">
              Sistem kami bekerja menggunakan pendekatan{" "}
              <strong>Content-Based Filtering</strong>. Artinya, mesin akan
              menganalisis "isi" atau "spesifikasi" dari setiap laptop yang ada
              di toko. Jika Anda menyukai atau mencari fitur tertentu (misal:
              memori besar dan anti-lelet), sistem akan menyaring dan
              merekomendasikan laptop yang memiliki "isi" yang identik dengan
              permintaan Anda tersebut.
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
              2. Membaca Makna Kata (TF-IDF)
            </h3>
            <p className="mb-4 text-sm md:text-base">
              Untuk bisa mencocokkan cerita Anda, mesin harus memahami bahasa
              manusia. Di sinilah <strong>TF-IDF</strong> bekerja. Sistem tidak
              sekadar membaca teks, tapi ia menghitung{" "}
              <strong>bobot kepentingan</strong> dari setiap kata yang Anda
              ketik. Kata umum seperti "dan" atau "yang" akan diabaikan.
              Sebaliknya, kata spesifik seperti "Desain", "Skripsi", atau "Game"
              akan diberi nilai (bobot) yang sangat tinggi.
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
              3. Mencari Kemiripan (Cosine Similarity)
            </h3>
            <p className="text-sm md:text-base">
              Setelah cerita Anda dan ratusan spesifikasi laptop diubah menjadi
              "angka bobot", mesin menggunakan rumus matematis{" "}
              <strong>Cosine Similarity</strong>. Rumus ini mengukur seberapa
              mirip "Angka Kebutuhan Anda" dengan "Angka Spesifikasi Laptop".
              Laptop dengan persentase kemiripan tertinggi akan dimunculkan ke
              layar Anda!
            </p>
          </div>
        </div>

        <div className="text-center mt-5">
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
