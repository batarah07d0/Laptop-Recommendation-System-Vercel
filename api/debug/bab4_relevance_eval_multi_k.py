#!/usr/bin/env python3
import csv
import re
import sys
from pathlib import Path
from textwrap import fill

# =====================================================
# IMPORT RECOMMENDER DARI FOLDER api/
# =====================================================

SCRIPT_DIR = Path(__file__).resolve().parent
BASE_DIR = (
    SCRIPT_DIR.parent
    if (SCRIPT_DIR.parent / "recommender.py").exists()
    else SCRIPT_DIR
)
sys.path.insert(0, str(BASE_DIR))

from recommender import LaptopRecommender, load_laptops


# =====================================================
# KONFIGURASI PENGUJIAN NILAI K
# =====================================================

# Nilai k yang dibandingkan.
# Website tetap menggunakan k=6 karena file recommender.py tidak diubah.
K_VALUES = [6, 10, 12, 15, 18]

# Kriteria utama pemilihan nilai terbaik:
# 1. Rata-rata F1-Score tertinggi
# 2. Jika sama, rata-rata Precision tertinggi
# 3. Jika masih sama, rata-rata Recall tertinggi
# 4. Jika masih sama, pilih k yang lebih kecil
OUTPUT_DIR = SCRIPT_DIR / "bab4_output_k_6_10_12_15_18"


# =====================================================
# HELPER FORMAT
# =====================================================

def line(char="=", width=125):
    print(char * width)


def title(text):
    print()
    line("=")
    print(text.center(125))
    line("=")


def subtitle(text):
    print()
    line("-")
    print(text)
    line("-")


def rupiah(value):
    try:
        return f"Rp {float(value):,.0f}".replace(",", ".")
    except Exception:
        return "Rp 0"


def shorten(text, max_len=48):
    text = str(text)
    if len(text) <= max_len:
        return text
    return text[:max_len - 3] + "..."


def wrap_text(text, width=105, indent=""):
    return fill(str(text), width=width, subsequent_indent=indent)


def get_text(laptop, field, default=""):
    return str(laptop.get(field, default) or "").lower()


def extract_number(text, default=0.0):
    match = re.search(r"(\d+(?:[.,]\d+)?)", str(text))
    if match:
        return float(match.group(1).replace(",", "."))
    return default


def get_price(laptop):
    try:
        return float(laptop.get("price", 0))
    except Exception:
        return 0.0


def get_weight(laptop):
    if laptop.get("weight_num") not in [None, ""]:
        try:
            return float(laptop.get("weight_num"))
        except Exception:
            pass

    if laptop.get("weight_kg") not in [None, ""]:
        return extract_number(laptop.get("weight_kg"), default=3.0)

    if laptop.get("weight") not in [None, ""]:
        return extract_number(laptop.get("weight"), default=3.0)

    return 3.0


def get_screen(laptop):
    if laptop.get("screen_size_num") not in [None, ""]:
        try:
            return float(laptop.get("screen_size_num"))
        except Exception:
            pass

    if laptop.get("screen_size") not in [None, ""]:
        return extract_number(laptop.get("screen_size"), default=18.0)

    return 18.0


def get_ram_num(laptop):
    ram = laptop.get("ram", "")
    return int(extract_number(ram, default=0))


def get_storage_gb(laptop):
    storage = str(laptop.get("storage", "")).lower()

    match_tb = re.search(r"(\d+)\s*tb", storage)
    if match_tb:
        return int(match_tb.group(1)) * 1024

    match_gb = re.search(r"(\d+)\s*gb", storage)
    if match_gb:
        return int(match_gb.group(1))

    return 0


def usage_tokens(laptop):
    """Ambil token metadata secara utuh agar frasa underscore tidak terpecah."""
    return set(get_text(laptop, "usage").split())


def usage_contains(laptop, keywords):
    tokens = usage_tokens(laptop)
    return any(str(keyword).lower() in tokens for keyword in keywords)


def cpu_contains(laptop, keywords):
    cpu = get_text(laptop, "cpu")
    return any(keyword.lower() in cpu for keyword in keywords)


def gpu_contains(laptop, keywords):
    gpu = get_text(laptop, "gpu")
    return any(keyword.lower() in gpu for keyword in keywords)


def panel_contains(laptop, keywords):
    panel = get_text(laptop, "panel_type")
    quality = get_text(laptop, "screen_quality")
    combined = panel + " " + quality
    return any(keyword.lower() in combined for keyword in keywords)


def is_high_or_mid_cpu(laptop):
    return cpu_contains(laptop, [
        "i5", "i7", "i9",
        "ultra 5", "ultra 7", "ultra 9",
        "ryzen 5", "ryzen 7", "ryzen 9",
        "ai 5", "ai 7", "ai 9",
        "m2", "m3", "m4", "m5"
    ])


def is_dedicated_gpu(laptop):
    gpu = get_text(laptop, "gpu")
    return (
        any(name in gpu for name in ["rtx", "gtx", "geforce", "nvidia", "8060s"])
        or bool(re.search(r"\brx\s*\d+", gpu))
    )


def is_modern_integrated_gpu(laptop):
    return gpu_contains(laptop, [
        "iris", "arc", "680m", "660m", "780m",
        "840m", "860m", "890m"
    ])


def is_good_screen_for_design(laptop):
    return panel_contains(laptop, [
        "oled", "ips", "mini led", "2.8k", "3k", "4k", "wuxga"
    ])


# =====================================================
# SKENARIO PENGUJIAN
# =====================================================

SCENARIOS = [
    {
        "id": "S1",
        "name": "Kuliah, skripsi, coding, dan game ringan",
        "description": "saya butuh laptop untuk kuliah, mengerjakan skripsi, coding, dan bermain game ringan",
        "filters": {
            "max_price": 25000000.0,
            "max_weight": 2.0,
            "max_screen": 14.0,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika memenuhi batas harga maksimal Rp25.000.000, "
            "berat maksimal 2 kg, ukuran layar maksimal 14 inci, RAM minimal 16 GB, "
            "serta memiliki karakteristik penggunaan untuk kuliah/skripsi/coding dan game ringan."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 25000000
            and get_weight(l) <= 2.0
            and get_screen(l) <= 14.0
            and get_ram_num(l) >= 16
            and usage_contains(l, ["kuliah", "skripsi", "coding", "programming", "developer"])
            and usage_contains(l, ["game_ringan", "game_menengah", "grafis_menengah_modern"])
        )
    },
    {
        "id": "S2",
        "name": "Laptop murah untuk kuliah dan office",
        "description": "saya cari laptop murah untuk kuliah, office, browsing, dan mengerjakan tugas",
        "filters": {
            "max_price": 8000000.0,
            "max_weight": 2.0,
            "max_screen": 15.6,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika harga maksimal Rp8.000.000, berat maksimal 2 kg, "
            "RAM minimal 8 GB, penyimpanan minimal 256 GB, dan memiliki karakteristik "
            "penggunaan untuk kuliah, office, tugas, browsing, atau penggunaan ringan."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 8000000
            and get_weight(l) <= 2.0
            and get_ram_num(l) >= 8
            and get_storage_gb(l) >= 256
            and usage_contains(l, [
                "kuliah", "office", "tugas_kuliah", "browsing",
                "penggunaan_ringan", "pelajar", "mahasiswa"
            ])
        )
    },
    {
        "id": "S3",
        "name": "Gaming berat dan rendering",
        "description": "saya butuh laptop untuk gaming berat, render 3d, dan editing video",
        "filters": {
            "max_price": 35000000.0,
            "max_weight": 3.5,
            "max_screen": 18.0,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika harga maksimal Rp35.000.000, RAM minimal 16 GB, "
            "menggunakan CPU kelas menengah/tinggi, memiliki GPU dedicated, dan memiliki "
            "karakteristik penggunaan untuk gaming berat, render 3D, atau editing video."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 35000000
            and get_ram_num(l) >= 16
            and is_high_or_mid_cpu(l)
            and is_dedicated_gpu(l)
            and usage_contains(l, [
                "game_berat", "gaming", "gamer", "render_3d",
                "video_editor_profesional", "editing_video",
                "premiere_pro", "after_effects"
            ])
        )
    },
    {
        "id": "S4",
        "name": "Desain grafis dan konten kreator",
        "description": "saya mencari laptop untuk desain grafis, edit video ringan, canva, photoshop, dan konten kreator",
        "filters": {
            "max_price": 25000000.0,
            "max_weight": 2.2,
            "max_screen": 16.0,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika harga maksimal Rp25.000.000, RAM minimal 16 GB, "
            "memiliki layar yang mendukung kebutuhan visual, serta memiliki karakteristik "
            "untuk desain grafis, edit video ringan, atau konten kreator."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 25000000
            and get_ram_num(l) >= 16
            and is_good_screen_for_design(l)
            and (
                is_modern_integrated_gpu(l)
                or is_dedicated_gpu(l)
                or usage_contains(l, [
                    "desain_grafis", "desain_grafis_ringan",
                    "edit_video_ringan", "photoshop", "canva",
                    "konten_kreator", "warna_akurat"
                ])
            )
        )
    },
    {
        "id": "S5",
        "name": "Mobilitas tinggi untuk kerja dan kampus",
        "description": "saya butuh laptop ringan yang mudah dibawa untuk kerja, kampus, meeting, dan presentasi",
        "filters": {
            "max_price": 22000000.0,
            "max_weight": 1.5,
            "max_screen": 14.0,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika harga maksimal Rp22.000.000, berat maksimal 1,5 kg, "
            "ukuran layar maksimal 14 inci, RAM minimal 16 GB, serta memiliki karakteristik "
            "mudah dibawa untuk kerja, kampus, meeting, atau presentasi."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 22000000
            and get_weight(l) <= 1.5
            and get_screen(l) <= 14.0
            and get_ram_num(l) >= 16
            and usage_contains(l, [
                "bobot_ringan", "bobot_sangat_ringan", "mudah_dibawa",
                "mobilitas_tinggi", "dibawa_ke_kampus", "cocok_kerja",
                "kerja_harian", "meeting", "presentasi"
            ])
        )
    },
    {
        "id": "S6",
        "name": "Programming dan data science",
        "description": "saya butuh laptop untuk programming, coding, data science, membuka banyak aplikasi, dan multitasking",
        "filters": {
            "max_price": 30000000.0,
            "max_weight": 2.5,
            "max_screen": 16.0,
            "cpu": "All",
            "ram": "All",
            "storage": "All",
            "os": "All",
            "gpu_type": "All",
            "panel_type": "All",
            "screen_quality": "All",
        },
        "criteria_description": (
            "Laptop dianggap relevan jika harga maksimal Rp30.000.000, RAM minimal 16 GB, "
            "penyimpanan minimal 512 GB, menggunakan CPU kelas menengah/tinggi, serta "
            "memiliki karakteristik untuk programming, coding, developer, data science, "
            "atau multitasking."
        ),
        "ground_truth_rule": lambda l: (
            get_price(l) <= 30000000
            and get_ram_num(l) >= 16
            and get_storage_gb(l) >= 512
            and is_high_or_mid_cpu(l)
            and usage_contains(l, [
                "programming", "coding", "developer", "data_science",
                "banyak_aplikasi", "multitasking", "multitasking_lancar",
                "multitasking_ekstrem"
            ])
        )
    }
]


# =====================================================
# PEMBENTUKAN INPUT DAN GROUND TRUTH
# =====================================================

def build_user_input(scenario):
    return {
        "description": scenario["description"],
        **scenario["filters"]
    }


def build_ground_truth(laptops, scenario):
    rule = scenario["ground_truth_rule"]
    relevant = []

    for laptop in laptops:
        try:
            if rule(laptop):
                relevant.append(laptop)
        except Exception:
            continue

    return relevant


# =====================================================
# SIMULASI TOP-K UNTUK EVALUASI
# =====================================================

def get_evaluation_recommendations(recommender, user_input, k):
    """
    Membentuk rekomendasi Top-k hanya untuk evaluasi.

    Fungsi ini tidak mengubah recommender.py dan tidak mengubah jumlah
    rekomendasi pada website. Urutan proses dibuat sama dengan sistem:
    1. Ranking cosine seluruh laptop
    2. Strict match
    3. Fallback/relaxed match jika strict kurang dari k
    4. Harga maksimum tetap wajib dipenuhi oleh fallback
    """
    if k <= 0:
        raise ValueError("Nilai k harus lebih besar dari 0.")

    _, raw_recommendations = recommender.rank_query(
        user_input.get("description", "")
    )

    strict_matches = []
    relaxed_matches = []

    for rec in raw_recommendations:
        laptop_id = rec.get("id")
        score = float(rec.get("score", 0.0))

        if score <= 0:
            continue

        source_laptop = recommender.laptop_by_id.get(laptop_id)
        if not source_laptop:
            continue

        laptop = dict(source_laptop)
        filter_status = recommender.check_filter_status(
            user_input,
            laptop
        )

        laptop["similarity_score"] = score

        if filter_status["passed_all"]:
            strict_matches.append(laptop)
        elif filter_status["passed_price"]:
            relaxed_matches.append(laptop)

    final_results = strict_matches[:k]
    selected_relaxed = []

    if len(final_results) < k:
        needed = k - len(final_results)
        selected_relaxed = relaxed_matches[:needed]
        final_results.extend(selected_relaxed)

    return {
        "data": final_results,
        "strict_count": len(strict_matches),
        "relaxed_count": len(selected_relaxed),
        "is_fallback": len(selected_relaxed) > 0
    }


# =====================================================
# METRIK
# =====================================================

def compute_metrics(recommended_ids, ground_truth_ids, k):
    recommended_at_k = recommended_ids[:k]

    recommended_set = set(recommended_at_k)
    ground_truth_set = set(ground_truth_ids)

    true_positive = len(recommended_set & ground_truth_set)

    # Precision@k tetap menggunakan k sebagai penyebut.
    # Jika hasil yang tersedia kurang dari k, posisi kosong dianggap tidak relevan.
    precision = true_positive / k if k > 0 else 0.0
    recall = (
        true_positive / len(ground_truth_set)
        if ground_truth_set
        else 0.0
    )

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "tp": true_positive,
        "returned_count": len(recommended_at_k),
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def evaluate_scenario(recommender, laptops, scenario, k):
    user_input = build_user_input(scenario)

    result = get_evaluation_recommendations(
        recommender=recommender,
        user_input=user_input,
        k=k
    )

    recommendations = result.get("data", [])
    recommended_ids = [
        laptop.get("id")
        for laptop in recommendations
        if laptop.get("id")
    ]

    ground_truth = build_ground_truth(laptops, scenario)
    ground_truth_ids = [
        laptop.get("id")
        for laptop in ground_truth
        if laptop.get("id")
    ]

    metrics = compute_metrics(
        recommended_ids=recommended_ids,
        ground_truth_ids=ground_truth_ids,
        k=k
    )

    return {
        "scenario": scenario,
        "k": k,
        "result": result,
        "recommendations": recommendations,
        "recommended_ids": recommended_ids,
        "ground_truth": ground_truth,
        "ground_truth_ids": ground_truth_ids,
        "metrics": metrics
    }


def evaluate_k(recommender, laptops, scenarios, k):
    evaluations = [
        evaluate_scenario(
            recommender=recommender,
            laptops=laptops,
            scenario=scenario,
            k=k
        )
        for scenario in scenarios
    ]

    count = len(evaluations)
    avg_precision = (
        sum(item["metrics"]["precision"] for item in evaluations) / count
        if count else 0.0
    )
    avg_recall = (
        sum(item["metrics"]["recall"] for item in evaluations) / count
        if count else 0.0
    )
    avg_f1 = (
        sum(item["metrics"]["f1"] for item in evaluations) / count
        if count else 0.0
    )
    avg_returned = (
        sum(item["metrics"]["returned_count"] for item in evaluations) / count
        if count else 0.0
    )
    fallback_count = sum(
        1
        for item in evaluations
        if item["result"].get("is_fallback")
    )

    return {
        "k": k,
        "evaluations": evaluations,
        "avg_precision": avg_precision,
        "avg_recall": avg_recall,
        "avg_f1": avg_f1,
        "avg_returned": avg_returned,
        "fallback_count": fallback_count
    }


# =====================================================
# PEMILIHAN NILAI K TERBAIK
# =====================================================

def select_best_k(comparisons):
    """
    Pilih nilai k dengan F1-Score tertinggi di antara nilai yang diuji.

    Urutan pemilihan:
    1. Rata-rata F1 tertinggi
    2. Rata-rata Precision tertinggi
    3. Rata-rata Recall tertinggi
    4. Nilai k lebih kecil
    """
    if not comparisons:
        return None

    return max(
        comparisons,
        key=lambda row: (
            row["avg_f1"],
            row["avg_precision"],
            row["avg_recall"],
            -row["k"]
        )
    )


# =====================================================
# OUTPUT TERMINAL
# =====================================================

def print_k_comparison(comparisons):
    title("PERBANDINGAN NILAI K")

    print(
        f"{'K':<5} | "
        f"{'Rata-rata Precision':<21} | "
        f"{'Rata-rata Recall':<18} | "
        f"{'Rata-rata F1':<16} | "
        f"{'Rata-rata Hasil':<17} | "
        f"{'Skenario Fallback'}"
    )
    line("-", 125)

    for row in comparisons:
        print(
            f"{row['k']:<5} | "
            f"{row['avg_precision']:<21.4f} | "
            f"{row['avg_recall']:<18.4f} | "
            f"{row['avg_f1']:<16.4f} | "
            f"{row['avg_returned']:<17.2f} | "
            f"{row['fallback_count']}"
        )


def print_scenario_comparison(comparisons):
    title("RINCIAN METRIK SETIAP SKENARIO")

    print(
        f"{'K':<4} | {'Skenario':<9} | {'GT':<5} | {'Hasil':<6} | "
        f"{'TP':<4} | {'Precision':<10} | {'Recall':<10} | "
        f"{'F1':<10} | {'Fallback'}"
    )
    line("-", 105)

    for comparison in comparisons:
        for evaluation in comparison["evaluations"]:
            scenario = evaluation["scenario"]
            metrics = evaluation["metrics"]
            result = evaluation["result"]

            print(
                f"{comparison['k']:<4} | "
                f"{scenario['id']:<9} | "
                f"{len(evaluation['ground_truth']):<5} | "
                f"{metrics['returned_count']:<6} | "
                f"{metrics['tp']:<4} | "
                f"{metrics['precision']:<10.4f} | "
                f"{metrics['recall']:<10.4f} | "
                f"{metrics['f1']:<10.4f} | "
                f"{'Ya' if result.get('is_fallback') else 'Tidak'}"
            )


def print_best_k(best):
    title("NILAI K DENGAN F1-SCORE TERTINGGI PADA PENGUJIAN")

    if not best:
        print("Tidak ada hasil evaluasi.")
        return

    print(f"Nilai k dengan F1-Score tertinggi              : {best['k']}")
    print(f"Rata-rata Precision@{best['k']} : {best['avg_precision']:.4f}")
    print(f"Rata-rata Recall@{best['k']}    : {best['avg_recall']:.4f}")
    print(f"Rata-rata F1-Score@{best['k']}  : {best['avg_f1']:.4f}")
    print(f"Jumlah skenario fallback     : {best['fallback_count']}")
    print()

    print(
        wrap_text(
            f"Nilai k={best['k']} dipilih karena menghasilkan rata-rata "
            "F1-Score tertinggi di antara nilai k yang diuji. Hasil ini hanya "
            "menunjukkan nilai terbaik pada rentang k dan enam skenario dalam "
            "penelitian, bukan nilai optimal secara universal."
        )
    )


def print_best_k_recommendations(best):
    if not best:
        return

    title(f"HASIL REKOMENDASI PADA K TERBAIK ({best['k']})")

    for evaluation in best["evaluations"]:
        scenario = evaluation["scenario"]
        ground_truth_ids = set(evaluation["ground_truth_ids"])

        subtitle(f"{scenario['id']} - {scenario['name']}")
        print(f"Ground truth : {len(evaluation['ground_truth'])} laptop")
        print(
            f"Precision@{best['k']}={evaluation['metrics']['precision']:.4f}, "
            f"Recall@{best['k']}={evaluation['metrics']['recall']:.4f}, "
            f"F1@{best['k']}={evaluation['metrics']['f1']:.4f}"
        )
        print()

        print(
            f"{'Rank':<6} | {'ID':<8} | {'Brand':<10} | "
            f"{'Nama Laptop':<48} | {'Skor':<9} | {'Relevan'}"
        )
        line("-", 110)

        for rank, laptop in enumerate(
            evaluation["recommendations"],
            start=1
        ):
            laptop_id = laptop.get("id", "-")
            relevant = "Ya" if laptop_id in ground_truth_ids else "Tidak"

            print(
                f"{rank:<6} | "
                f"{laptop_id:<8} | "
                f"{laptop.get('brand', '-'):<10} | "
                f"{shorten(laptop.get('name', '-'), 48):<48} | "
                f"{laptop.get('similarity_score', 0.0):<9.4f} | "
                f"{relevant}"
            )


# =====================================================
# EXPORT CSV
# =====================================================

def export_csv(comparisons, best, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)

    summary_path = output_dir / "01_perbandingan_nilai_k.csv"
    with summary_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "k",
                "avg_precision",
                "avg_recall",
                "avg_f1",
                "avg_returned",
                "fallback_count"
            ]
        )
        writer.writeheader()
        for row in comparisons:
            writer.writerow({
                "k": row["k"],
                "avg_precision": row["avg_precision"],
                "avg_recall": row["avg_recall"],
                "avg_f1": row["avg_f1"],
                "avg_returned": row["avg_returned"],
                "fallback_count": row["fallback_count"]
            })

    detail_path = output_dir / "02_rincian_metrik_per_skenario.csv"
    with detail_path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=[
                "k",
                "scenario_id",
                "scenario_name",
                "ground_truth_count",
                "returned_count",
                "true_positive",
                "precision",
                "recall",
                "f1",
                "strict_count",
                "relaxed_count",
                "is_fallback"
            ]
        )
        writer.writeheader()

        for comparison in comparisons:
            for evaluation in comparison["evaluations"]:
                metrics = evaluation["metrics"]
                result = evaluation["result"]
                scenario = evaluation["scenario"]

                writer.writerow({
                    "k": comparison["k"],
                    "scenario_id": scenario["id"],
                    "scenario_name": scenario["name"],
                    "ground_truth_count": len(evaluation["ground_truth"]),
                    "returned_count": metrics["returned_count"],
                    "true_positive": metrics["tp"],
                    "precision": metrics["precision"],
                    "recall": metrics["recall"],
                    "f1": metrics["f1"],
                    "strict_count": result.get("strict_count", 0),
                    "relaxed_count": result.get("relaxed_count", 0),
                    "is_fallback": result.get("is_fallback", False)
                })

    best_path = output_dir / "03_nilai_k_f1_tertinggi.txt"
    if best:
        best_text = (
            f"Nilai k dengan F1-Score tertinggi: {best['k']}\n"
            f"Rata-rata Precision: {best['avg_precision']:.6f}\n"
            f"Rata-rata Recall: {best['avg_recall']:.6f}\n"
            f"Rata-rata F1-Score: {best['avg_f1']:.6f}\n"
            f"Jumlah skenario fallback: {best['fallback_count']}\n\n"
            "Catatan: nilai ini adalah yang terbaik pada rentang k dan "
            "skenario yang diuji, bukan nilai optimal secara universal.\n"
        )
    else:
        best_text = "Tidak ada hasil evaluasi.\n"

    best_path.write_text(best_text, encoding="utf-8")

    return summary_path, detail_path, best_path


# =====================================================
# MAIN
# =====================================================

def main():
    data_path = BASE_DIR / "laptops.json"
    laptops = load_laptops(data_path)

    if not laptops:
        print("ERROR: laptops.json tidak ditemukan atau kosong.")
        print(f"Path yang dicari: {data_path}")
        print("Pastikan file laptops.json berada satu folder dengan recommender.py.")
        return

    recommender = LaptopRecommender(laptops)

    title("EVALUASI PERBANDINGAN NILAI K")
    print(f"Jumlah dataset laptop : {len(laptops)}")
    print(f"Jumlah skenario uji   : {len(SCENARIOS)}")
    print(f"Nilai k yang diuji    : {K_VALUES}")
    print("Recommender utama     : tidak diubah")
    print("Website               : tetap menggunakan k=6")

    comparisons = []

    for k in K_VALUES:
        comparison = evaluate_k(
            recommender=recommender,
            laptops=laptops,
            scenarios=SCENARIOS,
            k=k
        )
        comparisons.append(comparison)

    best = select_best_k(comparisons)

    print_k_comparison(comparisons)
    print_scenario_comparison(comparisons)
    print_best_k(best)
    print_best_k_recommendations(best)

    summary_path, detail_path, best_path = export_csv(
        comparisons=comparisons,
        best=best,
        output_dir=OUTPUT_DIR
    )

    print()
    print("File keluaran:")
    print(f"- {summary_path}")
    print(f"- {detail_path}")
    print(f"- {best_path}")


if __name__ == "__main__":
    main()
