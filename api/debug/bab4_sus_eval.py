#!/usr/bin/env python3
import csv
import re
import statistics
from collections import Counter, defaultdict
from pathlib import Path
from textwrap import fill

# =====================================================
# KONFIGURASI FILE
# =====================================================
# Letakkan file ini satu folder dengan file CSV hasil Google Form,
# atau ubah path CSV_PATH sesuai lokasi file Anda.
CSV_PATH = Path(__file__).resolve().parent / "Kuesioner Evaluasi Usability Sistem Rekomendasi Laptop (Jawaban) - Form Responses 1.csv"

# Jika file dijalankan dari folder berbeda, Anda bisa pakai path absolut/relatif, contoh:
# CSV_PATH = Path("../datasets/Kuesioner Evaluasi Usability Sistem Rekomendasi Laptop (Jawaban) - Form Responses 1.csv")

# =====================================================
# HELPER FORMAT
# =====================================================

def line(char="=", width=120):
    print(char * width)


def title(text):
    print()
    line("=")
    print(text.center(120))
    line("=")


def subtitle(text):
    print()
    line("-")
    print(text)
    line("-")


def pct(part, total):
    return (part / total * 100) if total else 0.0


def mean(values):
    return statistics.mean(values) if values else 0.0


def median(values):
    return statistics.median(values) if values else 0.0


def safe_int(value, default=0):
    try:
        return int(str(value).strip())
    except Exception:
        return default


def wrap(text, width=100):
    return fill(str(text), width=width)


def normalize_category(text):
    text = str(text).strip()
    if text.startswith("Sangat tidak paham"):
        return "Sangat tidak paham"
    if text.startswith("Kurang paham"):
        return "Kurang paham"
    if text.startswith("Cukup paham"):
        return "Cukup paham"
    if text.startswith("Sangat paham"):
        return "Sangat paham"
    return text or "Tidak diketahui"


def sus_level(score):
    # Kategori interpretasi sederhana. Sesuaikan dengan rujukan SUS yang digunakan di Bab 2.
    if score >= 80.3:
        return "Sangat baik"
    if score >= 68:
        return "Baik"
    if score >= 50:
        return "Cukup"
    return "Rendah"


def clean_comment(text):
    text = str(text).strip()
    if not text:
        return ""
    if text.lower() in {"-", ".", "tidak ada", "belum ada", "ga ada", "gak ada", "none", "no"}:
        return ""
    return re.sub(r"\s+", " ", text)


def classify_comment(text):
    t = text.lower()
    themes = []

    if any(k in t for k in ["filter", "slider", "cpu", "gpu", "ram", "spesifikasi", "spec", "textfield", "autocomplete"]):
        themes.append("Filter/spesifikasi perlu diperjelas")

    if any(k in t for k in ["akurat", "rekomendasi", "sesuai", "meleset", "tuning", "kebutuhan", "tidak ada laptop"]):
        themes.append("Akurasi/relevansi rekomendasi")

    if any(k in t for k in ["ui", "ux", "tampilan", "antarmuka", "simple", "gampang", "mudah", "interaktif"]):
        themes.append("Antarmuka dan kemudahan penggunaan")

    if any(k in t for k in ["riwayat", "history", "favorite", "wishlist", "sorting", "sort", "brand"]):
        themes.append("Fitur tambahan hasil rekomendasi")

    if any(k in t for k in ["beli", "error", "loading", "gerai", "lokasi", "toko"]):
        themes.append("Detail pembelian/tautan/gerai")

    if any(k in t for k in ["second", "mac", "pilihan", "terbatas", "alternatif", "review", "youtube", "yutub"]):
        themes.append("Perluasan informasi/produk")

    if not themes:
        themes.append("Komentar umum/dukungan")

    return themes


# =====================================================
# LOAD DATA
# =====================================================

def load_csv(path):
    if not path.exists():
        raise FileNotFoundError(f"File CSV tidak ditemukan: {path.resolve()}")

    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        raise ValueError("File CSV kosong atau tidak memiliki data responden.")

    headers = list(rows[0].keys())

    # Struktur berdasarkan Google Form yang digunakan:
    # 0 timestamp, 1 nama, 2 kategori pemahaman,
    # 3-12 pertanyaan SUS, 13-14 pertanyaan tambahan, 15 kritik/saran.
    columns = {
        "timestamp": headers[0],
        "name": headers[1],
        "category": headers[2],
        "sus": headers[3:13],
        "extra_relevance": headers[13],
        "extra_filter": headers[14],
        "comment": headers[15],
    }
    return rows, columns


# =====================================================
# SUS CALCULATION
# =====================================================

def calculate_sus(row, sus_cols):
    scores = [safe_int(row[col]) for col in sus_cols]

    odd_contrib = []
    even_contrib = []
    item_contrib = []

    for i, score in enumerate(scores, start=1):
        if i % 2 == 1:
            contribution = score - 1
            odd_contrib.append(contribution)
        else:
            contribution = 5 - score
            even_contrib.append(contribution)

        item_contrib.append(contribution)

    total_contrib = sum(item_contrib)
    sus_score = total_contrib * 2.5

    return {
        "raw_scores": scores,
        "item_contrib": item_contrib,
        "odd_sum": sum(odd_contrib),
        "even_sum": sum(even_contrib),
        "total_contrib": total_contrib,
        "sus_score": sus_score,
        "level": sus_level(sus_score),
    }


def build_records(rows, columns):
    records = []

    for idx, row in enumerate(rows, start=1):
        sus = calculate_sus(row, columns["sus"])
        category = normalize_category(row[columns["category"]])
        comment = clean_comment(row[columns["comment"]])

        records.append({
            "respondent_id": f"R{idx:02d}",
            "name": row[columns["name"]].strip(),
            "category": category,
            "sus": sus,
            "extra_relevance": safe_int(row[columns["extra_relevance"]]),
            "extra_filter": safe_int(row[columns["extra_filter"]]),
            "comment": comment,
            "comment_themes": classify_comment(comment) if comment else [],
        })

    return records


# =====================================================
# PRINT SECTIONS FOR BAB 4
# =====================================================

def print_profile(records):
    title("4.6.1 PROFIL RESPONDEN")

    total = len(records)
    counter = Counter(r["category"] for r in records)
    order = ["Sangat tidak paham", "Kurang paham", "Cukup paham", "Sangat paham"]

    print(f"Jumlah responden: {total}")
    print()
    print(f"{'Kategori Pemahaman':<25} | {'Jumlah':<8} | {'Persentase'}")
    line("-", 70)
    for category in order:
        count = counter.get(category, 0)
        print(f"{category:<25} | {count:<8} | {pct(count, total):.2f}%")


def print_sus_all(records):
    title("4.6.2 HASIL SKOR SUS SELURUH RESPONDEN")

    scores = [r["sus"]["sus_score"] for r in records]

    print(f"Jumlah responden : {len(records)}")
    print(f"Rata-rata SUS    : {mean(scores):.2f}")
    print(f"Median SUS       : {median(scores):.2f}")
    print(f"Skor terendah    : {min(scores):.2f}")
    print(f"Skor tertinggi   : {max(scores):.2f}")
    print()

    print(f"{'Responden':<10} | {'Kategori':<22} | {'Skor SUS':<8} | {'Interpretasi'}")
    line("-", 80)
    for r in records:
        print(
            f"{r['respondent_id']:<10} | "
            f"{r['category']:<22} | "
            f"{r['sus']['sus_score']:<8.2f} | "
            f"{r['sus']['level']}"
        )


def print_sus_by_category(records):
    title("4.6.3 PERBANDINGAN SKOR SUS BERDASARKAN KATEGORI RESPONDEN")

    grouped = defaultdict(list)
    for r in records:
        grouped[r["category"]].append(r["sus"]["sus_score"])

    order = ["Sangat tidak paham", "Kurang paham", "Cukup paham", "Sangat paham"]
    print(f"{'Kategori':<25} | {'Jumlah':<8} | {'Rata-rata':<10} | {'Min':<8} | {'Max'}")
    line("-", 85)

    for category in order:
        scores = grouped.get(category, [])
        if not scores:
            continue
        print(
            f"{category:<25} | "
            f"{len(scores):<8} | "
            f"{mean(scores):<10.2f} | "
            f"{min(scores):<8.2f} | "
            f"{max(scores):.2f}"
        )


def print_item_analysis(records, sus_cols):
    title("4.6.4 ANALISIS ITEM SUS")

    # Raw mean dan contribution mean per item
    print(f"{'Item':<6} | {'Jenis':<10} | {'Rata-rata Jawaban':<18} | {'Rata-rata Kontribusi'}")
    line("-", 85)

    for i, col in enumerate(sus_cols, start=1):
        raw_scores = [r["sus"]["raw_scores"][i - 1] for r in records]
        contrib_scores = [r["sus"]["item_contrib"][i - 1] for r in records]
        item_type = "Positif" if i % 2 == 1 else "Negatif"
        print(
            f"P{i:<5} | "
            f"{item_type:<10} | "
            f"{mean(raw_scores):<18.2f} | "
            f"{mean(contrib_scores):.2f}"
        )

    print()
    print("Catatan perhitungan:")
    print("- Item positif: kontribusi = skor jawaban - 1")
    print("- Item negatif: kontribusi = 5 - skor jawaban")
    print("- Skor SUS = total kontribusi x 2,5")


def print_extra_questions(records):
    title("4.6.5 ANALISIS PERTANYAAN TAMBAHAN")

    relevance_values = [r["extra_relevance"] for r in records if r["extra_relevance"] > 0]
    filter_values = [r["extra_filter"] for r in records if r["extra_filter"] > 0]

    print("Pertanyaan tambahan 1: Relevansi hasil rekomendasi terhadap teks kebutuhan pengguna")
    print(f"Rata-rata skor: {mean(relevance_values):.2f}")
    print("Distribusi jawaban:")
    counter = Counter(relevance_values)
    for score in range(1, 6):
        print(f"- Skor {score}: {counter.get(score, 0)} responden ({pct(counter.get(score, 0), len(records)):.2f}%)")

    print()
    print("Pertanyaan tambahan 2: Keberhasilan filter dropdown/spesifikasi")
    print(f"Rata-rata skor: {mean(filter_values):.2f}")
    print("Distribusi jawaban:")
    counter = Counter(filter_values)
    for score in range(1, 6):
        print(f"- Skor {score}: {counter.get(score, 0)} responden ({pct(counter.get(score, 0), len(records)):.2f}%)")


def print_comments(records):
    title("4.6.6 KRITIK DAN SARAN RESPONDEN")

    comments = [r for r in records if r["comment"]]
    print(f"Jumlah komentar/saran yang dapat dianalisis: {len(comments)}")
    print()

    theme_counter = Counter()
    for r in comments:
        for theme in r["comment_themes"]:
            theme_counter[theme] += 1

    print("Ringkasan tema kritik dan saran:")
    print(f"{'Tema':<45} | {'Jumlah'}")
    line("-", 70)
    for theme, count in theme_counter.most_common():
        print(f"{theme:<45} | {count}")

    print()
    print("Cuplikan komentar responden (tanpa nama):")
    for r in comments[:10]:
        print(f"- {r['respondent_id']}: {wrap(r['comment'], width=100)}")


def print_latex_ready(records):
    title("OUTPUT RINGKAS UNTUK DIPINDAHKAN KE LATEX BAB 4")

    total = len(records)
    scores = [r["sus"]["sus_score"] for r in records]

    subtitle("Tabel Profil Responden")
    print("Kategori | Jumlah | Persentase")
    counter = Counter(r["category"] for r in records)
    for category in ["Sangat tidak paham", "Kurang paham", "Cukup paham", "Sangat paham"]:
        count = counter.get(category, 0)
        print(f"{category} | {count} | {pct(count, total):.2f}%")

    subtitle("Tabel Ringkasan Skor SUS")
    print("Jumlah Responden | Rata-rata | Median | Minimum | Maksimum")
    print(f"{total} | {mean(scores):.2f} | {median(scores):.2f} | {min(scores):.2f} | {max(scores):.2f}")

    subtitle("Tabel Perbandingan SUS Berdasarkan Kategori")
    print("Kategori | Jumlah | Rata-rata SUS | Minimum | Maksimum")
    grouped = defaultdict(list)
    for r in records:
        grouped[r["category"]].append(r["sus"]["sus_score"])
    for category in ["Sangat tidak paham", "Kurang paham", "Cukup paham", "Sangat paham"]:
        scores_cat = grouped.get(category, [])
        if scores_cat:
            print(f"{category} | {len(scores_cat)} | {mean(scores_cat):.2f} | {min(scores_cat):.2f} | {max(scores_cat):.2f}")

    subtitle("Tabel Pertanyaan Tambahan")
    relevance_values = [r["extra_relevance"] for r in records if r["extra_relevance"] > 0]
    filter_values = [r["extra_filter"] for r in records if r["extra_filter"] > 0]
    print("Aspek | Rata-rata Skor")
    print(f"Relevansi hasil rekomendasi | {mean(relevance_values):.2f}")
    print(f"Keberhasilan filter | {mean(filter_values):.2f}")

    subtitle("Tabel Tema Kritik dan Saran")
    theme_counter = Counter()
    for r in records:
        for theme in r["comment_themes"]:
            theme_counter[theme] += 1
    print("Tema | Jumlah")
    for theme, count in theme_counter.most_common():
        print(f"{theme} | {count}")


# =====================================================
# MAIN
# =====================================================

def main():
    rows, columns = load_csv(CSV_PATH)
    records = build_records(rows, columns)

    title("EVALUASI USABILITY - SYSTEM USABILITY SCALE (SUS)")
    print(f"File CSV          : {CSV_PATH}")
    print(f"Jumlah responden  : {len(records)}")
    print("Jumlah item SUS   : 10")
    print("Skala jawaban     : 1 sampai 5")

    print_profile(records)
    print_sus_all(records)
    print_sus_by_category(records)
    print_item_analysis(records, columns["sus"])
    print_extra_questions(records)
    print_comments(records)
    print_latex_ready(records)


if __name__ == "__main__":
    main()
