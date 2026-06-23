import json
import math

import pandas as pd


def generate_json():
    csv_path = "datasets/laptop_data_agres(final).csv"
    
    try:
        df = pd.read_csv(csv_path)
        print("KOLOM DI CSV ANDA ADALAH:", df.columns.tolist())
        
    except FileNotFoundError:
        print(f"Error: File CSV tidak ditemukan di {csv_path}")
        return

    laptops_list = []
    seen_laptops = set() # Set untuk melacak data duplikat

    for index, row in df.iterrows():
        # Fungsi pembantu untuk mencegah error jika ada data kosong (NaN) di CSV
        def get_val(col_name, default=""):
            if col_name in df.columns:
                val = row[col_name]
                if pd.isna(val):
                    return default
                return val
            return default

        # Ambil SEMUA variabel kunci spesifikasi untuk mendeteksi duplikat presisi tinggi
        brand = str(get_val('Brand', 'Unknown'))
        name = str(get_val('Nama_Display', get_val('Nama', 'Laptop Tanpa Nama')))
        cpu = str(get_val('CPU', ''))
        gpu = str(get_val('GPU', ''))
        ram = str(get_val('RAM', ''))
        storage = str(get_val('Penyimpanan', get_val('Storage', '')))
        screen = str(get_val('Screen', get_val('Ukuran_Layar', '')))
        price = float(get_val('Harga_Numeric', 0))
        
        # Membuat sidik jari unik (Identifier) yang SANGAT KETAT
        identifier = f"{brand}_{name}_{cpu}_{gpu}_{ram}_{storage}_{screen}_{price}".lower().strip()
        
        # JIKA SELURUH SPESIFIKASI DI ATAS SAMA PERSIS, MAKA ITU DUPLIKAT
        if identifier in seen_laptops:
            print(f"Mengabaikan duplikat identik: {name} (Rp {price:,.0f} | {ram} | {storage})")
            continue
            
        # Jika lolos pengecekan, masukkan ke dalam set pelacakan
        seen_laptops.add(identifier)

        # 2. MAPPING KOLOM
        laptop = {
            "id": f"LP{len(laptops_list)+1:04d}", 
            "name": name,
            "brand": brand,
            "price": price,
            
            "cpu": cpu,
            "cpu_type": str(get_val('Tipe_CPU', '')),
            "gpu": gpu,
            "gpu_type": str(get_val('Tipe_GPU', '')), 
            "ram": ram,
            "storage": storage,
            "storage_type": str(get_val('Tipe_Penyimpanan', '')),
            "screen_size": screen, 
            
            "weight_num": float(get_val('Berat_Numeric', 3.0)), 
            "weight_kg": str(get_val('Berat')), 
            "screen_size_num": float(get_val('Ukuran_Layar_Numeric', 18.0)),
            
            "os": str(get_val('Sistem_Operasi', '')),
            "screen_quality": str(get_val('Resolusi_Layar', get_val('Resolution', ''))),
            "panel_type": str(get_val('Tipe_Panel_Layar', get_val('Panel', ''))),
            "usage": str(get_val('Metadata', '')), 
            "product_link": str(get_val('Product_URL', '#')),
            "image_url": str(get_val('Image_URL', 'https://via.placeholder.com/400x300?text=No+Image'))
        }
        
        laptops_list.append(laptop)

    # 3. Simpan hasilnya ke laptops.json
    output_path = "laptops.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(laptops_list, f, indent=4, ensure_ascii=False)

    print(f"\nBerhasil! {len(laptops_list)} laptop unik telah di-generate ke {output_path}")

if __name__ == "__main__":
    generate_json()