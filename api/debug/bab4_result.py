#!/usr/bin/env python3
import csv
import sys
import time
from pathlib import Path
from textwrap import fill

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = (
    SCRIPT_DIR.parent
    if (SCRIPT_DIR.parent / "recommender.py").exists()
    else SCRIPT_DIR
)

# Tambahkan folder api/ ke path Python
sys.path.insert(0, str(BASE_DIR))

from recommender import LaptopRecommender, load_laptops

# =====================================================
# KONFIGURASI SKENARIO BAB IV
# =====================================================

TEST_INPUT = {
    "description": "saya butuh laptop untuk kuliah, mengerjakan skripsi, coding, dan bermain game ringan",

    # Filter numerik
    "max_price": 25000000.0,
    "max_weight": 2.0,
    "max_screen": 14.0,

    # Filter pilihan
    "cpu": "All",
    "ram": "All",
    "storage": "All",
    "os": "All",
    "gpu_type": "All",
    "panel_type": "All",
    "screen_quality": "All",

    # Term yang ingin ditampilkan pada tabel TF-IDF Bab IV
    "debug_terms": ["kuliah", "skripsi", "coding", "game_ringan"]
}


# =====================================================
# HELPER PRINT
# =====================================================

def rupiah(value):
    try:
        return f"Rp {float(value):,.0f}".replace(",", ".")
    except Exception:
        return "Rp 0"



def line(char="=", width=110):
    print(char * width)


def title(text):
    print()
    line("=")
    print(text.center(110))
    line("=")


def subtitle(text):
    print()
    line("-")
    print(text)
    line("-")


def shorten(text, max_len=45):
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def wrap_text(text, width=92, indent=""):
    return fill(str(text), width=width, subsequent_indent=indent)


# =====================================================
# FILTER CHECKER
# Menggunakan aturan langsung dari recommender.py
# =====================================================

def check_filter_status(recommender, user_input, laptop):
    status = recommender.check_filter_status(user_input, laptop)
    return status["passed_all"], status["failed"]


# =====================================================
# RAW RANKING SEBELUM FILTER
# =====================================================

def build_raw_ranking(recommender, laptops, user_input):
    _, raw_recommendations = recommender.rank_query(
        user_input.get("description", "")
    )

    id_to_laptop = {
        laptop.get("id"): laptop
        for laptop in laptops
    }

    raw_rows = []
    for rank, rec in enumerate(raw_recommendations, start=1):
        laptop = id_to_laptop.get(rec["id"])
        if not laptop:
            continue

        passed_all, failed = check_filter_status(
            recommender,
            user_input,
            laptop
        )

        raw_rows.append({
            "rank": rank,
            "id": laptop.get("id", "-"),
            "brand": laptop.get("brand", "-"),
            "name": laptop.get("name", "-"),
            "score": rec.get("score", 0.0),
            "price": laptop.get("price", 0),
            "passed_filter": passed_all,
            "failed_filter": failed
        })

    return raw_rows


# =====================================================
# PRINT SECTION
# =====================================================

def print_input_scenario(user_input):
    title("SKENARIO INPUT PENGGUNA")

    print(f"Query Deskripsi : {user_input['description']}")
    print(f"Harga Maksimal  : {rupiah(user_input['max_price'])}")
    print(f"Berat Maksimal  : {user_input['max_weight']} kg")
    print(f"Layar Maksimal  : {user_input['max_screen']} inci")
    print(f"CPU             : {user_input['cpu']}")
    print(f"RAM             : {user_input['ram']}")
    print(f"Storage         : {user_input['storage']}")
    print(f"OS              : {user_input['os']}")
    print(f"GPU Type        : {user_input['gpu_type']}")
    print(f"Panel Type      : {user_input['panel_type']}")
    print(f"Screen Quality  : {user_input['screen_quality']}")


def print_preprocessing_and_corpus(debug, laptops_count):
    title("4.3.1 HASIL PREPROCESSING DAN REPRESENTASI TEKS")

    print(f"Query Asli              : {debug.get('query_original', '-')}")
    print(f"Token Hasil Preprocessing: {', '.join(debug.get('query_tokens', []))}")

    print()
    print("Representasi Korpus:")
    print(f"- Jumlah dokumen laptop dalam dataset : {laptops_count}")
    print(f"- Jumlah dokumen untuk perhitungan IDF: {debug.get('corpus_size', 0)}")
    print("- Query diproses secara terpisah dan tidak mengubah nilai IDF korpus.")
    print("- Setiap laptop direpresentasikan melalui field usage yang berisi metadata laptop.")


def print_matrix_table(rows, selected_laptops, decimals=6):
    headers = ["Term", "Query"] + [
        laptop.get("id", "-") for laptop in selected_laptops
    ]
    widths = [16, 14] + [14] * len(selected_laptops)

    print(" | ".join(f"{header:<{width}}" for header, width in zip(headers, widths)))
    print("-" * (sum(widths) + 3 * (len(widths) - 1)))

    for row in rows:
        values = [
            row.get("term", "-"),
            f"{row.get('query', 0.0):.{decimals}f}"
        ]
        for laptop in selected_laptops:
            laptop_id = laptop.get("id")
            values.append(f"{row.get(laptop_id, 0.0):.{decimals}f}")
        print(" | ".join(f"{value:<{width}}" for value, width in zip(values, widths)))


def print_weighting_pipeline(debug):
    selected_laptops = debug.get("selected_laptops", [])

    title("RINCIAN TF, IDF, TF-IDF, NORMALISASI, DAN COSINE SIMILARITY")

    print("Dokumen pembanding yang ditampilkan:")
    print("- Query pengguna")
    for laptop in selected_laptops:
        print(f"- {laptop.get('id')} | {laptop.get('brand')} | {laptop.get('name')}")

    subtitle("A. TERM FREQUENCY (TF)")
    print("TF = frekuensi term pada dokumen / jumlah seluruh term pada dokumen")
    print_matrix_table(debug.get("tf_table", []), selected_laptops, decimals=6)

    subtitle("B. DOCUMENT FREQUENCY (DF) DAN INVERSE DOCUMENT FREQUENCY (IDF)")
    print("IDF = ln((1 + N) / (1 + DF)) + 1")
    print(f"Jumlah dokumen pada korpus laptop (N): {debug.get('corpus_size', 0)}")
    print()
    print(f"{'Term':<16} | {'N':<8} | {'DF':<8} | {'IDF':<14}")
    print("-" * 54)
    for row in debug.get("idf_table", []):
        print(
            f"{row.get('term', '-'):<16} | "
            f"{row.get('document_count', 0):<8} | "
            f"{row.get('document_frequency', 0):<8} | "
            f"{row.get('idf', 0.0):<14.6f}"
        )

    subtitle("C. TF-IDF SEBELUM NORMALISASI")
    print("TF-IDF mentah = TF x IDF")
    print_matrix_table(debug.get("tfidf_raw_table", []), selected_laptops, decimals=6)

    subtitle("D. PANJANG VEKTOR DAN PROSES NORMALISASI")
    print("Norm = sqrt(jumlah kuadrat seluruh bobot TF-IDF pada dokumen)")
    print("Bobot ternormalisasi = bobot TF-IDF mentah / norm")
    print()
    print(f"{'Dokumen':<42} | {'ID':<10} | {'Norm Mentah':<14} | {'Norm Setelah':<14}")
    print("-" * 90)
    for row in debug.get("normalization_table", []):
        print(
            f"{shorten(row.get('document', '-'), 42):<42} | "
            f"{row.get('id', '-'):<10} | "
            f"{row.get('raw_vector_norm', 0.0):<14.6f} | "
            f"{row.get('normalized_vector_norm', 0.0):<14.6f}"
        )

    subtitle("E. TF-IDF SETELAH NORMALISASI")
    print_matrix_table(debug.get("tfidf_normalized_table", []), selected_laptops, decimals=6)

    subtitle("F. PERHITUNGAN COSINE SIMILARITY")
    print("Cosine = dot product TF-IDF mentah / (norm query x norm laptop)")
    print("Karena vektor sudah dinormalisasi, cosine juga sama dengan dot product vektor ternormalisasi.")
    print()
    print(
        f"{'ID':<9} | {'Dot Mentah':<13} | {'Norm Query':<12} | "
        f"{'Norm Laptop':<13} | {'Penyebut':<13} | {'Cosine':<11}"
    )
    print("-" * 91)
    for row in debug.get("cosine_detail_table", []):
        print(
            f"{row.get('id', '-'):<9} | "
            f"{row.get('raw_dot_product', 0.0):<13.6f} | "
            f"{row.get('query_norm', 0.0):<12.6f} | "
            f"{row.get('laptop_norm', 0.0):<13.6f} | "
            f"{row.get('denominator', 0.0):<13.6f} | "
            f"{row.get('cosine_from_raw', 0.0):<11.6f}"
        )

    print()
    print("Pemeriksaan konsistensi hasil cosine:")
    print(f"{'ID':<9} | {'Dari TF-IDF Mentah':<20} | {'Dari Vektor Normal':<20} | {'Selisih':<12}")
    print("-" * 72)
    for row in debug.get("cosine_detail_table", []):
        cosine_raw = row.get("cosine_from_raw", 0.0)
        cosine_norm = row.get("cosine_from_normalized", 0.0)
        print(
            f"{row.get('id', '-'):<9} | "
            f"{cosine_raw:<20.8f} | "
            f"{cosine_norm:<20.8f} | "
            f"{abs(cosine_raw - cosine_norm):<12.10f}"
        )


def print_raw_cosine_ranking(raw_rows, top_n=11):
    title("4.3.2 HASIL COSINE SIMILARITY / RANKING AWAL SEBELUM FILTER")

    print(f"{'Rank':<6} | {'ID':<8} | {'Brand':<10} | {'Nama Laptop':<46} | {'Skor':<10} | {'Harga'}")
    print("-" * 110)

    for row in raw_rows[:top_n]:
        print(
            f"{row['rank']:<6} | "
            f"{row['id']:<8} | "
            f"{row['brand']:<10} | "
            f"{shorten(row['name'], 46):<46} | "
            f"{row['score']:<10.4f} | "
            f"{rupiah(row['price'])}"
        )


def print_filter_analysis(raw_rows, hasil):
    title("4.3.3 HASIL PEMERINGKATAN DAN PENERAPAN FILTER")

    print(f"Jumlah hasil strict match : {hasil.get('strict_count', 0)}")
    print(f"Status fallback           : {'Ya' if hasil.get('is_fallback') else 'Tidak'}")
    print(f"Jumlah hasil akhir        : {len(hasil.get('data', []))}")

    print()
    print("Status filter pada 11 ranking awal:")
    print(f"{'Rank':<6} | {'ID':<8} | {'Nama Laptop':<46} | {'Status Filter':<16} | {'Keterangan'}")
    print("-" * 110)

    for row in raw_rows[:11]:
        if row["passed_filter"]:
            status = "Lolos"
            note = "-"
        else:
            status = "Tidak lolos"
            note = ", ".join(row["failed_filter"])

        print(
            f"{row['rank']:<6} | "
            f"{row['id']:<8} | "
            f"{shorten(row['name'], 46):<46} | "
            f"{status:<16} | "
            f"{note}"
        )

    print()
    if hasil.get("is_fallback"):
        print("Interpretasi:")
        print(
            wrap_text(
                "Sistem menggunakan fallback karena jumlah laptop yang lolos seluruh filter "
                "kurang dari enam. Hasil akhir dilengkapi dengan laptop yang masih memenuhi "
                "kriteria harga, tetapi dapat tidak memenuhi salah satu filter lain seperti "
                "berat atau ukuran layar."
            )
        )
    else:
        print("Interpretasi:")
        print(
            wrap_text(
                "Sistem berada pada Strict Mode karena hasil rekomendasi akhir diperoleh dari "
                "laptop yang lolos seluruh filter yang diberikan pengguna."
            )
        )


def print_top6_recommendations(hasil):
    title("4.3.4 HASIL REKOMENDASI TOP-6")

    data = hasil.get("data", [])

    if not data:
        print("Tidak ada rekomendasi yang dihasilkan.")
        return

    print(f"{'Rank':<6} | {'ID':<8} | {'Brand':<10} | {'Nama Laptop':<46} | {'Skor':<10} | {'Harga'}")
    print("-" * 110)

    for idx, laptop in enumerate(data, start=1):
        print(
            f"{idx:<6} | "
            f"{laptop.get('id', '-'):<8} | "
            f"{laptop.get('brand', '-'):<10} | "
            f"{shorten(laptop.get('name', '-'), 46):<46} | "
            f"{laptop.get('similarity_score', 0.0):<10.4f} | "
            f"{rupiah(laptop.get('price', 0))}"
        )

    subtitle("Alasan Rekomendasi Top-6")

    for idx, laptop in enumerate(data, start=1):
        print(f"{idx}. {laptop.get('brand', '-')} - {laptop.get('name', '-')}")
        print(f"   Skor Cosine : {laptop.get('similarity_score', 0.0):.4f}")
        print(f"   Harga : {rupiah(laptop.get('price', 0))}")
        print("   Alasan:")
        print("   " + wrap_text(laptop.get("explanation", "-"), width=96, indent="   "))
        print()


def print_latex_ready_tables(debug, hasil):
    title("OUTPUT RINGKAS UNTUK DIPINDAHKAN KE TABEL / SLIDE")

    selected_laptops = debug.get("selected_laptops", [])
    document_ids = [laptop.get("id", "-") for laptop in selected_laptops]

    print("TABEL PREPROCESSING")
    print(f"Query asli | {debug.get('query_original', '-')}")
    print(f"Token | {', '.join(debug.get('query_tokens', []))}")

    for label, key in [
        ("TABEL TF", "tf_table"),
        ("TABEL TF-IDF SEBELUM NORMALISASI", "tfidf_raw_table"),
        ("TABEL TF-IDF SETELAH NORMALISASI", "tfidf_normalized_table")
    ]:
        print()
        print(label)
        print(" | ".join(["Term", "Query"] + document_ids))
        for row in debug.get(key, []):
            values = [row.get("term", "-"), f"{row.get('query', 0.0):.6f}"]
            values.extend(f"{row.get(doc_id, 0.0):.6f}" for doc_id in document_ids)
            print(" | ".join(values))

    print()
    print("TABEL DF DAN IDF")
    print("Term | N | DF | IDF")
    for row in debug.get("idf_table", []):
        print(
            f"{row.get('term', '-')} | "
            f"{row.get('document_count', 0)} | "
            f"{row.get('document_frequency', 0)} | "
            f"{row.get('idf', 0.0):.6f}"
        )

    print()
    print("TABEL NORMALISASI VEKTOR")
    print("Dokumen | ID | Norm Mentah | Norm Setelah Normalisasi")
    for row in debug.get("normalization_table", []):
        print(
            f"{row.get('document', '-')} | "
            f"{row.get('id', '-')} | "
            f"{row.get('raw_vector_norm', 0.0):.6f} | "
            f"{row.get('normalized_vector_norm', 0.0):.6f}"
        )

    print()
    print("TABEL PERHITUNGAN COSINE SIMILARITY")
    print("ID | Dot Mentah | Norm Query | Norm Laptop | Penyebut | Cosine")
    for row in debug.get("cosine_detail_table", []):
        print(
            f"{row.get('id', '-')} | "
            f"{row.get('raw_dot_product', 0.0):.6f} | "
            f"{row.get('query_norm', 0.0):.6f} | "
            f"{row.get('laptop_norm', 0.0):.6f} | "
            f"{row.get('denominator', 0.0):.6f} | "
            f"{row.get('cosine_from_raw', 0.0):.6f}"
        )

    print()
    print("TABEL TOP-6")
    print("Rank | ID | Brand | Nama Laptop | Skor | Harga")
    for idx, laptop in enumerate(hasil.get("data", []), start=1):
        print(
            f"{idx} | "
            f"{laptop.get('id', '-')} | "
            f"{laptop.get('brand', '-')} | "
            f"{laptop.get('name', '-')} | "
            f"{laptop.get('similarity_score', 0.0):.6f} | "
            f"{rupiah(laptop.get('price', 0))}"
        )


def export_debug_csv(debug, hasil, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    selected_laptops = debug.get("selected_laptops", [])
    document_ids = [laptop.get("id", "-") for laptop in selected_laptops]

    def write_rows(filename, fieldnames, rows):
        path = output_dir / filename
        with path.open("w", newline="", encoding="utf-8-sig") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    matrix_fields = ["term", "query"] + document_ids
    write_rows("01_tf.csv", matrix_fields, debug.get("tf_table", []))
    write_rows(
        "02_idf.csv",
        ["term", "document_count", "document_frequency", "idf"],
        debug.get("idf_table", [])
    )
    write_rows(
        "03_tfidf_sebelum_normalisasi.csv",
        matrix_fields,
        debug.get("tfidf_raw_table", [])
    )
    write_rows(
        "04_norm_vektor.csv",
        ["document", "id", "raw_vector_norm", "normalized_vector_norm"],
        debug.get("normalization_table", [])
    )
    write_rows(
        "05_tfidf_setelah_normalisasi.csv",
        matrix_fields,
        debug.get("tfidf_normalized_table", [])
    )
    write_rows(
        "06_cosine_similarity.csv",
        [
            "id", "brand", "name", "shared_term_count", "shared_terms",
            "raw_dot_product", "query_norm", "laptop_norm",
            "denominator", "cosine_from_raw", "cosine_from_normalized"
        ],
        debug.get("cosine_detail_table", [])
    )

    top6_rows = []
    for rank, laptop in enumerate(hasil.get("data", []), start=1):
        top6_rows.append({
            "rank": rank,
            "id": laptop.get("id", "-"),
            "brand": laptop.get("brand", "-"),
            "name": laptop.get("name", "-"),
            "score": laptop.get("similarity_score", 0.0),
            "price": laptop.get("price", 0)
        })
    write_rows(
        "07_top6.csv",
        ["rank", "id", "brand", "name", "score", "price"],
        top6_rows
    )

    return output_dir


# =====================================================
# MAIN
# =====================================================

def main():
    data_path = BASE_DIR / "laptops.json"
    laptops = load_laptops(data_path)

    if not laptops:
        print("ERROR: laptops.json tidak ditemukan atau kosong.")
        print(f"Path yang dicari: {data_path}")
        print("Pastikan file laptops.json berada di folder api/.")
        return

    recommender = LaptopRecommender(laptops)

    start_time = time.time()
    hasil = recommender.get_recommendations(TEST_INPUT, debug=True)
    duration = (time.time() - start_time) * 1000

    debug = hasil.get("debug", {})
    raw_rows = build_raw_ranking(recommender, laptops, TEST_INPUT)

    title("LAPORAN DEBUG MODEL REKOMENDASI UNTUK BAB IV")
    print(f"Jumlah dataset laptop : {len(laptops)}")
    print(f"Execution time        : {duration:.2f} ms")
    print(f"Mode hasil            : {'Fallback Mode' if hasil.get('is_fallback') else 'Strict Mode'}")
    print(f"Jumlah rekomendasi    : {len(hasil.get('data', []))}")

    print_input_scenario(TEST_INPUT)

    if not debug:
        print("Debug tidak tersedia karena tidak ada term query yang dikenal oleh korpus.")
        return

    print_preprocessing_and_corpus(debug, len(laptops))
    print_weighting_pipeline(debug)
    print_raw_cosine_ranking(raw_rows, top_n=11)
    print_filter_analysis(raw_rows, hasil)
    print_top6_recommendations(hasil)
    print_latex_ready_tables(debug, hasil)

    output_dir = Path(__file__).resolve().parent / "bab4_output"
    export_debug_csv(debug, hasil, output_dir)
    print()
    print(f"File CSV berhasil disimpan di: {output_dir}")


if __name__ == "__main__":
    main()