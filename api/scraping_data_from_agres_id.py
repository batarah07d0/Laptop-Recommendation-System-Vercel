import json
import os
import re
import time

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# =====================================================
# CONFIG
# =====================================================

INPUT_FILE = "datasets/Link_1.txt"
# INPUT_FILE = "datasets/Link_2.txt"
OUTPUT_FILE = "datasets/laptop_data_agres.xlsx"

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}

# =====================================================
# SESSION + RETRY
# =====================================================

session = requests.Session()

retry = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry)

session.mount("http://", adapter)
session.mount("https://", adapter)

# =====================================================
# HELPER
# =====================================================

def clean_text(text):

    if text is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


def extract_field(text, field):

    pattern = rf"{field}:\s*(.*?)(?=\n[A-Za-z ]+:|$)"

    match = re.search(
        pattern,
        text,
        re.I | re.S
    )

    if match:
        return clean_text(match.group(1))

    return ""


# =====================================================
# CPU TYPE
# =====================================================

def get_cpu_type(cpu):

    cpu = cpu.lower()

    if any(x in cpu for x in [
        "intel",
        "core ultra",
        "core i"
    ]):
        return "Intel"

    if any(x in cpu for x in [
        "ryzen",
        "amd"
    ]):
        return "AMD"

    if "apple" in cpu:
        return "Apple"

    if "snapdragon" in cpu:
        return "Qualcomm"

    return ""


# =====================================================
# GPU TYPE
# =====================================================

def get_gpu_type(gpu):

    gpu = gpu.lower()

    if any(x in gpu for x in [
        "rtx",
        "gtx",
        "geforce",
        "nvidia"
    ]):
        return "NVIDIA"

    if any(x in gpu for x in [
        "radeon",
        "amd"
    ]):
        return "AMD"

    if any(x in gpu for x in [
        "intel arc",
        "iris xe",
        "uhd",
        "intel graphics"
    ]):
        return "Intel"

    if "apple" in gpu:
        return "Apple"

    return ""


# =====================================================
# RAM TYPE
# =====================================================

def get_ram_type(ram):

    ram = ram.upper()

    for item in [
        "LPDDR5X",
        "LPDDR5",
        "LPDDR4X",
        "LPDDR4",
        "DDR5",
        "DDR4"
    ]:

        if item in ram:
            return item

    return ""


# =====================================================
# STORAGE TYPE
# =====================================================

def get_storage_type(storage):

    storage = storage.lower()

    if "ssd" in storage:
        return "SSD"

    if "emmc" in storage:
        return "eMMC"

    if "hdd" in storage:
        return "HDD"

    return ""


# =====================================================
# NUMERIC
# =====================================================

def extract_ram_numeric(text):

    match = re.search(
        r"(\d+)\s*gb",
        text,
        re.I
    )

    if match:
        return int(match.group(1))

    return None


def extract_storage_numeric(text):

    match = re.search(
        r"(\d+)\s*tb",
        text,
        re.I
    )

    if match:
        return int(match.group(1)) * 1024

    match = re.search(
        r"(\d+)\s*gb",
        text,
        re.I
    )

    if match:
        return int(match.group(1))

    return None


def extract_screen_numeric(text):

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        text
    )

    if match:
        return float(match.group(1))

    return None


def extract_weight(text):

    match = re.search(
        r"Weight:\s*(\d+(?:\.\d+)?)\s*kg",
        text,
        re.I
    )

    if match:

        value = float(match.group(1))

        return (
            f"{value} kg",
            value
        )

    return "", None


# =====================================================
# SCRAPER
# =====================================================

def scrape_product(url):

    response = session.get(
        url,
        headers=HEADERS,
        timeout=(10, 30)
    )

    response.raise_for_status()

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    product_json = None

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            data = json.loads(script.string)

            if (
                isinstance(data, dict)
                and data.get("@type") == "Product"
            ):
                product_json = data
                break

        except:
            pass

    if not product_json:
        return None

    spec_text = soup.get_text(
        "\n",
        strip=True
    )

    nama = clean_text(
        product_json.get(
            "name",
            ""
        )
    )

    harga_numeric = int(
        float(
            product_json["offers"]["price"]
        )
    )

    harga_rupiah = (
        f"Rp {harga_numeric:,}"
        .replace(",", ".")
    )

    image_data = product_json.get(
        "image",
        []
    )

    image_url = ""

    if isinstance(image_data, list):

        if image_data:
            image_url = image_data[0]

    elif isinstance(image_data, str):

        image_url = image_data

    brand = extract_field(
        spec_text,
        "Brand"
    )

    if not brand:
        brand = nama.split()[0].upper()

    sku_match = re.search(
        r"SKU:\s*([A-Z0-9\-]+)",
        spec_text
    )

    sku = (
        sku_match.group(1)
        if sku_match
        else ""
    )

    cpu = extract_field(
        spec_text,
        "Processor"
    )

    gpu = extract_field(
        spec_text,
        "Graphics"
    )

    ram = extract_field(
        spec_text,
        "RAM"
    )

    storage = extract_field(
        spec_text,
        "Storage"
    )

    layar = extract_field(
        spec_text,
        "Main Display Size"
    )

    panel = extract_field(
        spec_text,
        "Main Display Type"
    )

    resolusi = extract_field(
        spec_text,
        "Display Resolution"
    )

    os_system = extract_field(
        spec_text,
        "Operating System"
    )

    berat, berat_numeric = (
        extract_weight(spec_text)
    )

    return {

        "Nama": nama,
        "Nama_Display": nama,

        "Brand": brand,

        "Harga_Rupiah": harga_rupiah,
        "Harga_Numeric": harga_numeric,

        "Sistem_Operasi": os_system,

        "GPU": gpu,
        "Tipe_GPU": get_gpu_type(gpu),

        "CPU": cpu,
        "Tipe_CPU": get_cpu_type(cpu),

        "RAM": ram,
        "RAM_Numeric": extract_ram_numeric(ram),
        "Tipe_RAM": get_ram_type(ram),

        "Penyimpanan": storage,
        "Penyimpanan_Numeric": extract_storage_numeric(storage),
        "Tipe_Penyimpanan": get_storage_type(storage),

        "Berat": berat,
        "Berat_Numeric": berat_numeric,

        "Ukuran_Layar": layar,
        "Ukuran_Layar_Numeric": extract_screen_numeric(layar),

        "Tipe_Panel_Layar": panel,
        "Resolusi_Layar": resolusi,

        # FULL RAW DESCRIPTION
        "Deskripsi": spec_text,

        "Product_URL": url,

        "Image_URL": image_url,

        "SKU": sku,

        "Kategori": "Laptop"
    }


# =====================================================
# LOAD EXISTING DATA
# =====================================================

existing_urls = set()

if os.path.exists(OUTPUT_FILE):

    old_df = pd.read_excel(
        OUTPUT_FILE
    )

    if "Product_URL" in old_df.columns:

        existing_urls = set(
            old_df["Product_URL"]
            .astype(str)
            .tolist()
        )

    print(
        f"Dataset lama: {len(existing_urls)} produk"
    )

# =====================================================
# LOAD URLS
# =====================================================

with open(
    INPUT_FILE,
    "r",
    encoding="utf-8"
) as f:

    urls = [
        line.strip()
        for line in f
        if line.strip()
    ]

print(
    f"URL ditemukan: {len(urls)}"
)

# =====================================================
# SCRAPING
# =====================================================

all_rows = []
failed_urls = []

for i, url in enumerate(
    urls,
    start=1
):

    if url in existing_urls:

        print(
            f"[SKIP] {url}"
        )

        continue

    try:

        row = scrape_product(url)

        if row:

            all_rows.append(row)

            print(
                f"[{i}/{len(urls)}] ✓ "
                f"{row['Nama']}"
            )

    except Exception as e:

        failed_urls.append(url)

        print(
            f"[ERROR] {url}"
        )

        print(e)

    time.sleep(1)

# =====================================================
# SAVE FAILED URL
# =====================================================

if failed_urls:

    with open(
        "datasets/failed_urls.txt",
        "w",
        encoding="utf-8"
    ) as f:

        f.write(
            "\n".join(failed_urls)
        )

# =====================================================
# APPEND TO DATASET
# =====================================================

new_df = pd.DataFrame(all_rows)

if os.path.exists(OUTPUT_FILE):

    old_df = pd.read_excel(
        OUTPUT_FILE
    )

    final_df = pd.concat(
        [old_df, new_df],
        ignore_index=True
    )

else:

    final_df = new_df

final_df.drop_duplicates(
    subset=["Product_URL"],
    keep="first",
    inplace=True
)

final_df.to_excel(
    OUTPUT_FILE,
    index=False
)

# =====================================================
# DONE
# =====================================================

print()
print("=" * 60)
print("SCRAPING SELESAI")
print("DATA BARU :", len(new_df))
print("TOTAL DATA:", len(final_df))
print("FAILED    :", len(failed_urls))
print("=" * 60)