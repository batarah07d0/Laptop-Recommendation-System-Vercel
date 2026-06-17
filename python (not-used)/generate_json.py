import json
import math

import pandas as pd


def generate_json():
    # 1. Pastikan nama file CSV dan path-nya sesuai dengan milik Anda
    # Karena file CSV Anda ada di folder datasets, kita arahkan ke sana
    csv_path = "datasets/laptop_data_agres.csv"
    
    try:
        df = pd.read_csv(csv_path)
        print("KOLOM DI CSV ANDA ADALAH:", df.columns.tolist())
        
    except FileNotFoundError:
        print(f"Error: File CSV tidak ditemukan di {csv_path}")
        return

    laptops_list = []

    for index, row in df.iterrows():
        # Fungsi pembantu untuk mencegah error jika ada data kosong (NaN) di CSV
        def get_val(col_name, default=""):
            if col_name in df.columns:
                val = row[col_name]
                if pd.isna(val):
                    return default
                return val
            return default

        # 2. MAPPING KOLOM (Sudah disesuaikan dengan dataset asli Anda)
        laptop = {
            "id": f"LP{index+1:04d}",
            "name": str(get_val('Nama_Display', get_val('Nama', 'Laptop Tanpa Nama'))),
            "brand": str(get_val('Brand', 'Unknown')),
            "price": float(get_val('Harga_Numeric', 0)),
            
            "cpu": str(get_val('CPU', '')),
            "cpu_type": str(get_val('Tipe_CPU', '')),
            "gpu": str(get_val('GPU', '')),
            "gpu_type": str(get_val('Tipe_GPU', '')), 
            "ram": str(get_val('RAM', '')),
            "storage": str(get_val('Penyimpanan', get_val('Storage', ''))),
            "storage_type": str(get_val('Tipe_Penyimpanan', '')),
            "screen_size": str(get_val('Screen', get_val('Ukuran_Layar', ''))), 
            
            # Numeric values untuk logika Slider
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

    # 3. Simpan hasilnya ke laptops.json (sejajar dengan script recommender.py)
    output_path = "laptops.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(laptops_list, f, indent=4, ensure_ascii=False)

    print(f"Berhasil! {len(laptops_list)} laptop telah di-generate ke {output_path}")

if __name__ == "__main__":
    generate_json()