import re

import pandas as pd

# =========================
# 1. LOAD DATA
# =========================
# Pastikan path ini sesuai dengan lokasi file dataset
df = pd.read_excel('datasets/laptop_data_agres.xlsx')

# =========================
# 2. CLEANING TEXT
# =========================
def clean_text(text):
    text = str(text).lower()

    # Fix desimal (15,6 → 15.6)
    text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)

    # Normalisasi CPU/GPU
    text = re.sub(r'\b(rtx|gtx|rx)\s*([0-9]{3,4})\b', r'\1 \2', text)
    text = re.sub(r'\b(i[3579])[-\s]*([0-9]{4,5}[a-z]{0,2})\b', r'\1 \2', text)

    # Fix konteks kata
    text = re.sub(r'\bcompact\b', 'layar compact', text)
    text = re.sub(r'\bbagus\b', 'layar bagus', text)
    text = re.sub(r'\bcpu ekosistem\b', 'cpu apple ekosistem apple', text)

    # Hapus simbol kecuali titik
    text = re.sub(r'[^\w\s\.]', ' ', text)

    # Normalisasi spasi
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# =========================
# 3. FEATURE ENGINEERING
# =========================
# Harga & berat
df['Harga_Numeric'] = pd.to_numeric(df['Harga_Numeric'], errors='coerce')
df['Berat_Numeric'] = pd.to_numeric(df['Berat_Numeric'], errors='coerce')

# RAM
df['RAM_Numeric'] = pd.to_numeric(
    df['RAM'].str.extract(r'(\d+)', expand=False),
    errors='coerce'
)

# FIX STORAGE (IMPORTANT)
def convert_storage_to_gb(text):
    text = str(text).lower()

    if "tb" in text:
        val = re.search(r'(\d+)', text)
        return int(val.group(1)) * 1024 if val else None

    elif "gb" in text:
        val = re.search(r'(\d+)', text)
        return int(val.group(1)) if val else None

    return None

df['Penyimpanan_Numeric'] = df['Penyimpanan'].apply(convert_storage_to_gb)

# Layar
df['Ukuran_Layar_Numeric'] = pd.to_numeric(df['Ukuran_Layar_Numeric'], errors='coerce')

# =========================
# 4. AUTO TAGGING
# =========================
def generate_tags(row):
    tags = []

    cpu = str(row['CPU']).lower()
    gpu = str(row['GPU']).lower()
    ram = row['RAM_Numeric']
    storage = row['Penyimpanan_Numeric']
    berat = row['Berat_Numeric']
    layar = row['Ukuran_Layar_Numeric']
    panel = str(row['Tipe_Panel_Layar']).lower()
    resolusi = str(row['Resolusi_Layar']).lower()

    # 1. ANALISIS KELAS CPU
    is_cpu_high = False
    is_cpu_mid = False
    if "apple" in cpu or re.search(r"\bm[1-5]\b", cpu):
        tags.extend(["cpu apple", "ekosistem apple"])
        if any(x in cpu for x in ["m4", "m5", "max", "pro"]): is_cpu_high = True
        else: is_cpu_mid = True
    elif "intel" in cpu or "core" in cpu:
        tags.append("cpu intel")
        if any(x in cpu for x in ["i9", "ultra 9", "i7", "ultra 7"]): is_cpu_high = True
        elif any(x in cpu for x in ["i5", "ultra 5"]): is_cpu_mid = True
        else: tags.append("performa dasar")
    elif "amd" in cpu or "ryzen" in cpu:
        tags.append("cpu amd")
        if any(x in cpu for x in ["ryzen 9", "hx", "x3d", "ryzen 7", "ai 7", "ai 9"]): is_cpu_high = True
        elif any(x in cpu for x in ["ryzen 5", "ai 5"]): is_cpu_mid = True
        else: tags.append("performa dasar")
        
    if is_cpu_high: tags.append("performa sangat tinggi")
    elif is_cpu_mid: tags.append("performa menengah")
    if "ai" in cpu or "ultra" in cpu: tags.append("ai ready")

    # 2. ANALISIS KELAS GPU (MAPPING PRESISI BERDASARKAN DATA UNIK)
    is_gpu_dedicated = False
    is_gpu_mid_integrated = False
    
    # A. GPU Dedicated (Gaming Berat) -> RTX series & Apple
    if "rtx" in gpu or "8060s" in gpu or "apple" in gpu:
        is_gpu_dedicated = True
        if any(x in gpu for x in ["5070", "5080", "5090", "4080", "4090"]): 
            tags.append("gpu kelas atas")
        else: 
            tags.append("gpu kelas menengah")
            
    # B. GPU Integrated Modern (Gaming Menengah) -> Arc, Iris Xe, Radeon 600M/800M
    elif "arc" in gpu or "iris" in gpu or any(x in gpu for x in ["680m", "660m", "840m", "860m", "780m", "890m"]):
        is_gpu_mid_integrated = True
        tags.append("grafis menengah modern")
        
    # C. GPU Integrated Dasar (Office) -> UHD, Intel Graphics biasa, Radeon Graphics biasa, Vega 8
    else:
        tags.append("grafis ringan bawaan")

    # 3. ANALISIS RAM & STORAGE
    is_ram_ready = pd.notna(ram) and ram >= 16
    if pd.notna(ram):
        if ram >= 32: tags.append("multitasking ekstrem")
        elif ram >= 16: tags.append("multitasking lancar")
        elif ram >= 8: tags.append("multitasking cukup")
        else: tags.append("penggunaan ringan")

    if pd.notna(storage):
        if storage >= 1024: tags.append("penyimpanan sangat besar")
        elif storage >= 512: tags.append("penyimpanan besar")
        elif storage >= 256: tags.append("penyimpanan cukup")
        else: tags.append("penyimpanan kecil")

    # 4. PENILAIAN KOMBINASI HARDWARE (ANTI-BOTTLENECK UNTUK GAMING & 3D)
    if is_gpu_dedicated:
        if (is_cpu_mid or is_cpu_high) and is_ram_ready:
            tags.append("gaming berat")
            if "gpu kelas atas" in tags: tags.append("gaming extreme")
        else:
            tags.extend(["gaming menengah", "rawan bottleneck"])
    elif is_gpu_mid_integrated:
        if (is_cpu_mid or is_cpu_high) and is_ram_ready:
            tags.append("gaming menengah")
        else:
            tags.append("gaming ringan")
    else:
        tags.append("gaming kasual ringan")

    # 5. BERAT, LAYAR, DAN BATERAI
    if pd.notna(berat):
        if berat <= 1.2: tags.append("ultra ringan")
        elif berat <= 1.5: tags.append("ringan")
        elif berat <= 2: tags.append("sedang")
        else: tags.append("berat")

    if pd.notna(layar):
        if layar >= 16: tags.append("layar besar")
        elif layar >= 14: tags.append("layar sedang")
        else: tags.append("layar compact")

    if "oled" in panel: tags.append("layar oled")
    elif "mini led" in panel: tags.append("layar premium")
    elif "ips" in panel: tags.append("layar bagus")
    elif "tn" in panel: tags.append("layar standar")

    if any(x in resolusi for x in ["4k", "uhd"]): tags.append("resolusi ultra tinggi")
    elif any(x in resolusi for x in ["3k", "2.8k", "3024", "2560"]): tags.append("resolusi tinggi")
    elif any(x in resolusi for x in ["fhd", "1920", "wuxga"]): tags.append("resolusi standar")
    else: tags.append("resolusi rendah")

    if re.search(r'\d+u\b', cpu) or "apple" in cpu or "evo" in cpu or "v" in cpu:
        tags.extend(["baterai awet", "hemat daya", "tahan seharian", "awet buat nongkrong"])
    elif re.search(r'\d+hx?\b', cpu):
        tags.extend(["performa maksimal", "kencang", "butuh charger", "baterai standar"])

    harga = row['Harga_Numeric']
    if pd.notna(harga):
        if harga <= 6500000:
            tags.extend(["murah", "budget", "terjangkau", "entry level", "ramah kantong", "ekonomis", "kere hore"])
        elif harga <= 12000000:
            tags.extend(["menengah", "standar", "harga wajar", "mid range", "value for money"])
        elif harga <= 20000000:
            tags.extend(["premium", "high end", "profesional", "kelas atas", "elegan"])
        else:
            tags.extend(["sultan", "flagship", "mahal", "spek dewa", "pekerjaan berat", "investasi jangka panjang"])

    nama_laptop = str(row['Nama_Display']).lower()
    if any(x in nama_laptop for x in ["touch", "x360", "spin", "flip", "2-in-1", "2in1", "yoga", "duo"]):
        tags.extend(["touchscreen", "layar sentuh", "bisa dilipat", "bisa jadi tablet", "buat nggambar", "stylus", "presentasi interaktif", "fleksibel"])

    # ==========================================
    # USE CASE & KEYWORDS EKSPANSI
    # ==========================================
    if "gaming berat" in tags: tags.append("cocok gaming")
    if "multitasking lancar" in tags: tags.append("cocok kerja")
    if "ringan" in tags or "ultra ringan" in tags: tags.append("mudah dibawa")
    if "grafis ringan bawaan" in tags: tags.append("cocok office")
    if "resolusi tinggi" in tags or "layar oled" in tags: tags.append("cocok multimedia")

    if any(x in tags for x in ["performa dasar", "performa menengah", "grafis ringan bawaan", "penggunaan ringan"]):
        tags.extend(["nugas", "skripsi", "kuliah", "sekolah", "pelajar", "mahasiswa", "browsing", "internet", "zoom", "meeting", "nonton", "film", "youtube", "word", "excel", "presentasi", "ppt"])

    if any(x in tags for x in ["performa tinggi", "performa sangat tinggi", "multitasking lancar", "multitasking ekstrem"]):
        tags.extend(["kantor", "buka banyak tab", "banyak aplikasi", "anti lelet", "anti lemot", "coding", "ngoding", "programming", "programmer", "software", "analis data", "data science", "developer", "lancar jaya"])

    if any(x in tags for x in ["gaming menengah", "grafis menengah modern"]):
        tags.extend(["main game ringan", "valorant", "dota", "genshin impact", "esports", "edit video ringan", "desain grafis", "canva", "photoshop", "corel", "illustrator", "konten kreator"])

    if any(x in tags for x in ["gaming berat", "gaming extreme"]):
        tags.extend(["gamer", "gaming rata kanan", "gta", "cyberpunk", "render 3d", "autocad", "blender", "sketchup", "video editor profesional", "premiere pro", "after effects"])

    if any(x in tags for x in ["ultra ringan", "ringan"]):
        tags.extend(["sering dibawa", "bepergian", "traveling", "mobilitas tinggi", "enteng", "tipis", "dibawa ke kampus", "dibawa nongkrong", "cafe"])

    if "layar oled" in tags or "resolusi tinggi" in tags or "resolusi ultra tinggi" in tags:
        tags.extend(["nonton netflix", "kualitas bioskop", "warna akurat", "manjakan mata", "desainer", "warna tajam"])

    return " ".join(dict.fromkeys(tags))

df['Auto_Tag'] = df.apply(generate_tags, axis=1)

# =========================
# 5. HELPER
# =========================
def format_ram(v):
    return f"ram {int(v)}gb" if pd.notna(v) else ""

def format_storage(v):
    if pd.isna(v): return ""
    if v >= 1024: return f"ssd {int(v/1024)}tb"
    return f"ssd {int(v)}gb"

def format_layar(v):
    return f"layar {float(v):.1f} inch" if pd.notna(v) else ""

def simplify_label(text):
    text = str(text).lower()
    text = re.sub(r'kinerja cepat|boot cepat|loading cepat', 'cepat', text)
    text = re.sub(r'\bterjangkau\b', '', text)
    text = re.sub(r'\bmenengah\b', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def remove_duplicates(text):
    return " ".join(dict.fromkeys(text.split()))

# =========================
# 6. METADATA BUILDER
# =========================
def build_metadata(row):
    parts = []

    parts.extend([
        str(row['Brand']),
        str(row['Nama_Display']),
        str(row['CPU']),
        str(row['GPU'])
    ])

    gpu = str(row['GPU']).lower()
    if "apple" in gpu: parts.append("grafis apple")
    elif any(x in gpu for x in ["uhd", "iris", "intel", "integrated"]): parts.append("grafis terintegrasi")

    parts.append(format_ram(row['RAM_Numeric']))
    parts.append(format_storage(row['Penyimpanan_Numeric']))
    parts.append(format_layar(row['Ukuran_Layar_Numeric']))

    parts.append(row['Auto_Tag'])
    parts.append(simplify_label(row['Label']))

    text = " ".join(parts)
    text = clean_text(text)
    text = remove_duplicates(text)

    return text

df['Metadata'] = df.apply(build_metadata, axis=1)

# =========================
# 7. SAVE
# =========================
df.to_excel("datasets/laptop_data_agres_with_metadata.xlsx", index=False)

print("✅ FINAL: Metadata sudah berhasil diterapkan dan disimpan!")