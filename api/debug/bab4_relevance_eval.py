#!/usr/bin/env python3
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


def wrap_text(text, width=100, indent=""):
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


def is_high_cpu(laptop):
    return cpu_contains(laptop, [
        "i7", "i9",
        "ultra 7", "ultra 9",
        "ryzen 7", "ryzen 9",
        "ai 7", "ai 9",
        "m3", "m4", "m5"
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
# SKENARIO PENGUJIAN 4.4
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
            and usage_contains(l, ["kuliah", "office", "tugas_kuliah", "browsing", "penggunaan_ringan", "pelajar", "mahasiswa"])
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
            and usage_contains(l, ["game_berat", "gaming", "gamer", "render_3d", "video_editor_profesional", "editing_video", "premiere_pro", "after_effects"])
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
                or usage_contains(l, ["desain_grafis", "desain_grafis_ringan", "edit_video_ringan", "photoshop", "canva", "konten_kreator", "warna_akurat"])
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
            and usage_contains(l, ["bobot_ringan", "bobot_sangat_ringan", "mudah_dibawa", "mobilitas_tinggi", "dibawa_ke_kampus", "cocok_kerja", "kerja_harian", "meeting", "presentasi"])
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
            and usage_contains(l, ["programming", "coding", "developer", "data_science", "banyak_aplikasi", "multitasking", "multitasking_lancar", "multitasking_ekstrem"])
        )
    }
]


# =====================================================
# EVALUATION
# =====================================================

def build_user_input(scenario):
    user_input = {
        "description": scenario["description"],
        **scenario["filters"]
    }
    return user_input


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


def compute_metrics(recommended_ids, ground_truth_ids, k=6):
    recommended_at_k = recommended_ids[:k]

    recommended_set = set(recommended_at_k)
    ground_truth_set = set(ground_truth_ids)

    true_positive = len(recommended_set & ground_truth_set)

    precision = true_positive / k if k > 0 else 0.0
    recall = true_positive / len(ground_truth_set) if ground_truth_set else 0.0

    if precision + recall == 0:
        f1 = 0.0
    else:
        f1 = 2 * precision * recall / (precision + recall)

    return {
        "tp": true_positive,
        "precision": precision,
        "recall": recall,
        "f1": f1
    }


def evaluate_scenario(recommender, laptops, scenario, k=6):
    user_input = build_user_input(scenario)
    result = recommender.get_recommendations(user_input, debug=False)

    recommendations = result.get("data", [])
    recommended_ids = [laptop.get("id") for laptop in recommendations]

    ground_truth = build_ground_truth(laptops, scenario)
    ground_truth_ids = [laptop.get("id") for laptop in ground_truth]

    metrics = compute_metrics(recommended_ids, ground_truth_ids, k=k)

    return {
        "scenario": scenario,
        "result": result,
        "recommendations": recommendations,
        "recommended_ids": recommended_ids,
        "ground_truth": ground_truth,
        "ground_truth_ids": ground_truth_ids,
        "metrics": metrics
    }


# =====================================================
# PRINT OUTPUT
# =====================================================

def print_scenario_detail(evaluation, k=6):
    scenario = evaluation["scenario"]
    result = evaluation["result"]
    recommendations = evaluation["recommendations"]
    ground_truth_ids = set(evaluation["ground_truth_ids"])
    metrics = evaluation["metrics"]

    title(f"{scenario['id']} - {scenario['name']}")

    print("Kueri Pengguna:")
    print(wrap_text(scenario["description"], width=110))
    print()

    print("Filter:")
    filters = scenario["filters"]
    print(f"- Harga maksimal : {rupiah(filters['max_price'])}")
    print(f"- Berat maksimal : {filters['max_weight']} kg")
    print(f"- Layar maksimal : {filters['max_screen']} inci")
    print(f"- CPU            : {filters['cpu']}")
    print(f"- RAM            : {filters['ram']}")
    print(f"- Storage        : {filters['storage']}")
    print()

    print("Kriteria Ground Truth Berbasis Aturan:")
    print(wrap_text(scenario["criteria_description"], width=110))
    print()

    print(f"Jumlah ground truth berbasis aturan : {len(evaluation['ground_truth'])} laptop")
    print(f"Jumlah hasil strict match   : {result.get('strict_count', 0)} laptop")
    print(f"Status fallback             : {'Ya' if result.get('is_fallback') else 'Tidak'}")
    print()

    print(f"Hasil Rekomendasi Top-{k}:")
    print(f"{'Rank':<6} | {'ID':<8} | {'Brand':<10} | {'Nama Laptop':<48} | {'Skor':<8} | {'Relevan'}")
    print("-" * 120)

    for idx, laptop in enumerate(recommendations[:k], start=1):
        laptop_id = laptop.get("id", "-")
        is_relevant = "Ya" if laptop_id in ground_truth_ids else "Tidak"

        print(
            f"{idx:<6} | "
            f"{laptop_id:<8} | "
            f"{laptop.get('brand', '-'):<10} | "
            f"{shorten(laptop.get('name', '-'), 48):<48} | "
            f"{laptop.get('similarity_score', 0.0):<8.4f} | "
            f"{is_relevant}"
        )

    print()

    print("Perhitungan Metrik:")
    print(f"- Jumlah rekomendasi yang relevan pada Top-{k} : {metrics['tp']}")
    print(f"- Precision@{k} : {metrics['precision']:.4f}")
    print(f"- Recall@{k}    : {metrics['recall']:.4f}")
    print(f"- F1-Score@{k}  : {metrics['f1']:.4f}")

    # print()
    # print("Rumus:")
    # print(f"Precision@{k} = jumlah rekomendasi relevan pada Top-{k} / {k}")
    # print(f"Recall@{k}    = jumlah rekomendasi relevan pada Top-{k} / jumlah ground truth relevan")
    # print(f"F1@{k}        = 2 * Precision@{k} * Recall@{k} / (Precision@{k} + Recall@{k})")


def print_summary_table(evaluations, k=6):
    title(f"RINGKASAN HASIL PRECISION@{k}, RECALL@{k}, DAN F1-SCORE@{k}")

    print(
        f"{'Skenario':<10} | "
        f"{'Ground Truth':<13} | "
        f"{'Relevan Top-6':<14} | "
        f"{'Precision@6':<12} | "
        f"{'Recall@6':<10} | "
        f"{'F1@6':<10} | "
        f"{'Fallback'}"
    )
    print("-" * 120)

    total_precision = 0.0
    total_recall = 0.0
    total_f1 = 0.0

    for evaluation in evaluations:
        scenario = evaluation["scenario"]
        metrics = evaluation["metrics"]
        result = evaluation["result"]

        total_precision += metrics["precision"]
        total_recall += metrics["recall"]
        total_f1 += metrics["f1"]

        print(
            f"{scenario['id']:<10} | "
            f"{len(evaluation['ground_truth']):<13} | "
            f"{metrics['tp']:<14} | "
            f"{metrics['precision']:<12.4f} | "
            f"{metrics['recall']:<10.4f} | "
            f"{metrics['f1']:<10.4f} | "
            f"{'Ya' if result.get('is_fallback') else 'Tidak'}"
        )

    n = len(evaluations)
    avg_precision = total_precision / n if n else 0.0
    avg_recall = total_recall / n if n else 0.0
    avg_f1 = total_f1 / n if n else 0.0

    print("-" * 120)
    print(
        f"{'Rata-rata':<10} | "
        f"{'-':<13} | "
        f"{'-':<14} | "
        f"{avg_precision:<12.4f} | "
        f"{avg_recall:<10.4f} | "
        f"{avg_f1:<10.4f} | "
        f"{'-'}"
    )

    print()
    print("Nilai rata-rata ini merangkum evaluasi terhadap ground truth berbasis aturan pada Bab 4.")


def print_latex_ready(evaluations, k=6):
    title("OUTPUT RINGKAS UNTUK DIPINDAHKAN KE LATEX BAB 4")

    subtitle("Tabel Skenario Pengujian")
    print("ID | Skenario | Kueri | Filter Utama")
    for evaluation in evaluations:
        s = evaluation["scenario"]
        f = s["filters"]
        print(
            f"{s['id']} | "
            f"{s['name']} | "
            f"{s['description']} | "
            f"Harga <= {rupiah(f['max_price'])}, Berat <= {f['max_weight']} kg, Layar <= {f['max_screen']} inci"
        )

    subtitle("Tabel Hasil Top-6 Setiap Skenario")
    print("Skenario | Rank | ID | Brand | Nama Laptop | Skor | Relevan")
    for evaluation in evaluations:
        s = evaluation["scenario"]
        ground_truth_ids = set(evaluation["ground_truth_ids"])

        for idx, laptop in enumerate(evaluation["recommendations"][:k], start=1):
            laptop_id = laptop.get("id", "-")
            is_relevant = "Ya" if laptop_id in ground_truth_ids else "Tidak"
            print(
                f"{s['id']} | "
                f"{idx} | "
                f"{laptop_id} | "
                f"{laptop.get('brand', '-')} | "
                f"{laptop.get('name', '-')} | "
                f"{laptop.get('similarity_score', 0.0):.4f} | "
                f"{is_relevant}"
            )

    subtitle("Tabel Evaluasi Precision@6, Recall@6, dan F1-Score@6")
    print("Skenario | Jumlah Ground Truth | Relevan pada Top-6 | Precision@6 | Recall@6 | F1-Score@6")
    for evaluation in evaluations:
        s = evaluation["scenario"]
        m = evaluation["metrics"]

        print(
            f"{s['id']} | "
            f"{len(evaluation['ground_truth'])} | "
            f"{m['tp']} | "
            f"{m['precision']:.4f} | "
            f"{m['recall']:.4f} | "
            f"{m['f1']:.4f}"
        )


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

    k = 6
    evaluations = []

    title("EVALUASI RELEVANSI REKOMENDASI - BAB 4")
    print(f"Jumlah dataset laptop : {len(laptops)}")
    print(f"Jumlah skenario uji   : {len(SCENARIOS)}")
    print(f"Nilai K               : {k}")

    for scenario in SCENARIOS:
        evaluation = evaluate_scenario(recommender, laptops, scenario, k=k)
        evaluations.append(evaluation)
        print_scenario_detail(evaluation, k=k)

    print_summary_table(evaluations, k=k)
    print_latex_ready(evaluations, k=k)


if __name__ == "__main__":
    main()