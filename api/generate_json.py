import json
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_XLSX = BASE_DIR / "datasets" / "laptop_data_agres_with_metadata.xlsx"
INPUT_CSV = BASE_DIR / "datasets" / "laptop_data_agres_with_metadata.csv"
OUTPUT_JSON = BASE_DIR / "laptops.json"


def load_dataset() -> pd.DataFrame:
    """Baca hasil pembentukan metadata, bukan dataset mentah."""
    if INPUT_XLSX.exists():
        return pd.read_excel(INPUT_XLSX)

    if INPUT_CSV.exists():
        return pd.read_csv(INPUT_CSV)

    raise FileNotFoundError(
        f"Dataset metadata tidak ditemukan: {INPUT_XLSX} atau {INPUT_CSV}"
    )


def classify_gpu_type(gpu_text: str) -> str:
    """
    Klasifikasikan nama GPU menjadi Dedicated, Integrated, atau Unknown.

    Klasifikasi dilakukan berdasarkan model GPU, bukan hanya vendor,
    karena AMD dan Intel memiliki GPU integrated maupun dedicated.
    """
    gpu = str(gpu_text or "").lower().strip()

    if not gpu:
        return "Unknown"

    # GPU terpisah/dedicated. Pemeriksaan dilakukan lebih dahulu agar
    # Intel Arc seri A/B dan Radeon RX tidak salah dianggap integrated.
    dedicated_patterns = [
        r"\bnvidia\b",
        r"\bgeforce\b",
        r"\brtx[-\s]*\d+",
        r"\bgtx[-\s]*\d+",
        r"\bradeon\s+rx[-\s]*\d+",
        r"\brx[-\s]*\d+",
        r"\bintel\s+arc\s+[ab]\d{3,4}m?\b",
        r"\barc\s+[ab]\d{3,4}m?\b",
    ]
    if any(re.search(pattern, gpu) for pattern in dedicated_patterns):
        return "Dedicated"

    # GPU yang menyatu dengan prosesor/integrated.
    integrated_patterns = [
        r"\bintel\s+uhd\b",
        r"\buhd\s+graphics\b",
        r"\biris\s+xe\b",
        r"\bintel\s+graphics\b",
        r"\bintel\s+arc\s+graphics\b",
        r"\bradeon\s+graphics\b",
        r"\bradeon\s+vega\b",
        r"\bvega\s*\d*\b",
        r"\bradeon\s+\d{3,4}[ms]\b",
        r"\bapple\b",
        r"\badreno\b",
        r"\bintegrated\b",
    ]
    if any(re.search(pattern, gpu) for pattern in integrated_patterns):
        return "Integrated"

    return "Unknown"


def generate_json() -> None:
    try:
        df = load_dataset()
    except FileNotFoundError as exc:
        print(f"Error: {exc}")
        return

    if "Metadata" not in df.columns:
        print("Error: Kolom Metadata tidak ditemukan.")
        return

    empty_metadata = int(df["Metadata"].fillna("").astype(str).str.strip().eq("").sum())
    if empty_metadata > 0:
        print(f"Error: Terdapat {empty_metadata} baris dengan Metadata kosong.")
        return

    laptops_list = []
    seen_laptops = set()

    for _, row in df.iterrows():
        def get_val(column, default=""):
            if column not in df.columns:
                return default
            value = row[column]
            return default if pd.isna(value) else value

        brand = str(get_val("Brand", "Unknown"))
        name = str(get_val("Nama_Display", get_val("Nama", "Laptop Tanpa Nama")))
        cpu = str(get_val("CPU", ""))
        gpu = str(get_val("GPU", ""))
        ram = str(get_val("RAM", ""))
        storage = str(get_val("Penyimpanan", get_val("Storage", "")))
        screen = str(get_val("Ukuran_Layar", get_val("Screen", "")))
        price = float(get_val("Harga_Numeric", 0))

        identifier = (
            f"{brand}_{name}_{cpu}_{gpu}_{ram}_{storage}_{screen}_{price}"
            .lower()
            .strip()
        )

        if identifier in seen_laptops:
            continue
        seen_laptops.add(identifier)

        laptop = {
            "id": f"LP{len(laptops_list) + 1:04d}",
            "name": name,
            "brand": brand,
            "price": price,
            "cpu": cpu,
            "cpu_type": str(get_val("Tipe_CPU", "")),
            "gpu": gpu,
            # Vendor dipisahkan dari kategori fisik GPU.
            "gpu_vendor": str(get_val("Tipe_GPU", "")),
            "gpu_type": classify_gpu_type(gpu),
            "ram": ram,
            "storage": storage,
            "storage_type": str(get_val("Tipe_Penyimpanan", "")),
            "screen_size": screen,
            "weight_num": float(get_val("Berat_Numeric", 3.0)),
            "weight_kg": str(get_val("Berat", "")),
            "screen_size_num": float(get_val("Ukuran_Layar_Numeric", 18.0)),
            "os": str(get_val("Sistem_Operasi", "")),
            "screen_quality": str(
                get_val("Resolusi_Layar", get_val("Resolution", ""))
            ),
            "panel_type": str(
                get_val("Tipe_Panel_Layar", get_val("Panel", ""))
            ),
            "usage": str(get_val("Metadata", "")),
            "product_link": str(get_val("Product_URL", "#")),
            "image_url": str(
                get_val(
                    "Image_URL",
                    "https://via.placeholder.com/400x300?text=No+Image",
                )
            ),
        }
        laptops_list.append(laptop)

    with OUTPUT_JSON.open("w", encoding="utf-8") as file:
        json.dump(laptops_list, file, indent=4, ensure_ascii=False)

    print(f"Berhasil membuat {len(laptops_list)} laptop ke {OUTPUT_JSON}")


if __name__ == "__main__":
    generate_json()
