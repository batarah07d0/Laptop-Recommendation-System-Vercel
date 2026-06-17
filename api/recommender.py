#!/usr/bin/env python3
import json
import math
import re
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Sequence


class LaptopRecommender:
    def __init__(self, laptops: List[Dict]):
        self.laptops = laptops
        self.corpus = [self._preprocess(laptop.get('usage', '')) for laptop in laptops]
        self.tfidf_matrix = self._compute_tfidf()

    # Fungsi untuk membersihkan dan menormalisasi teks (lowercase, hapus tanda baca, hapus stopwords)
    def _preprocess(self, text: str) -> List[str]:
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        
        stopwords = {
            'dan', 'atau', 'untuk', 'dengan', 'yang', 'di', 'ke', 'dari', 'pada', 'adalah', 'ini', 'itu', 
            'buat', 'sama', 'juga', 'sih', 'cuma', 'aja', 'nggak', 'gak', 'enggak', 'tidak', 'bukan',
            'saya', 'aku', 'kamu', 'dia', 'mereka', 'kita', 'kami', 'halo', 'hai', 'mas', 'mbak', 'bang', 'kak',
            'pengen', 'ingin', 'mau', 'beli', 'cari', 'carikan', 'tolong', 'dong', 'lagi', 'pas', 'bisa',
            'ada', 'sesuatu', 'kalau', 'kalo', 'biar', 'sudah', 'udah', 'belum', 'sangat', 'paling'
        }
        return [word for word in text.split() if word not in stopwords]

    # Fungsi untuk menghitung Term Frequency (TF) dari sebuah dokumen
    def _compute_tf(self, doc: List[str]) -> Dict[str, float]:
        tf = Counter(doc)
        total_words = len(doc)
        return {word: count / total_words for word, count in tf.items()} if total_words > 0 else {}

    # Fungsi untuk menghitung Inverse Document Frequency (IDF) dari seluruh korpus
    def _compute_idf(self) -> Dict[str, float]:
        N = len(self.corpus)
        df = defaultdict(int)
        for doc in self.corpus:
            unique_words = set(doc)
            for word in unique_words:
                df[word] += 1
        return {word: math.log((1 + N) / (1 + count)) + 1 for word, count in df.items()}

    # Fungsi untuk menghitung TF-IDF dari seluruh korpus
    def _compute_tfidf(self) -> List[Dict[str, float]]:
        idf = self._compute_idf()
        tfidf_matrix = []
        for doc in self.corpus:
            tf = self._compute_tf(doc)
            tfidf = {word: tf_val * idf.get(word, 0) for word, tf_val in tf.items()}
            
            norm = math.sqrt(sum(val**2 for val in tfidf.values()))
            if norm > 0:
                tfidf = {word: val / norm for word, val in tfidf.items()}
            tfidf_matrix.append(tfidf)
        return tfidf_matrix

    # Fungsi untuk menghitung Cosine Similarity antara dua vektor TF-IDF
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[word] * vec2[word] for word in intersection)
        return dot_product
    
    # Fungsi untuk merekomendasikan laptop berdasarkan ID target dan jumlah rekomendasi yang diinginkan
    def recommend(self, target_id: str, top_n: int = 5) -> List[Dict]:
        target_idx = next((i for i, laptop in enumerate(self.laptops) if laptop['id'] == target_id), None)
        if target_idx is None:
            raise ValueError(f"Laptop dengan ID {target_id} tidak ditemukan.")

        target_vec = self.tfidf_matrix[target_idx]
        scores = []
        for i, vec in enumerate(self.tfidf_matrix):
            if i != target_idx:
                score = self._cosine_similarity(target_vec, vec)
                scores.append({'id': self.laptops[i]['id'], 'score': score})
                
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_n]
    
    # Fungsi untuk menghasilkan alasan mengapa laptop tertentu cocok dengan kebutuhan pengguna
    def _generate_reason(self, user_input: Dict, laptop: Dict) -> str:
        desc = user_input.get('description', '').lower()
        
        cpu = laptop.get('cpu', 'Prosesor Standar')
        gpu = laptop.get('gpu', 'Grafis Bawaan')
        storage = laptop.get('storage', '256 GB')
        panel = laptop.get('panel_type', 'Layar Standar')
        bobot = laptop.get('weight_kg', 'Standar')
        
        ram_str = str(laptop.get('ram', '8 GB'))
        ram_match = re.search(r'(\d+)', ram_str)
        ram_num = int(ram_match.group(1)) if ram_match else 8
        
        reasons = []

        # 1. Kebutuhan Gaming & 3D Render
        if any(key in desc for key in ['game', 'gaming', 'render', '3d', 'berat']):
            is_heavy_gpu = any(x in gpu.lower() for x in ['rtx', 'gtx', 'rx ', 'apple', '8060s'])
            is_mid_gpu = any(x in gpu.lower() for x in ['arc', '680m', '860m', '840m', '660m', '780m', '890m', 'iris'])
            is_good_cpu = any(x in cpu.lower() for x in ['i5', 'i7', 'i9', 'ultra', 'ryzen 5', 'ryzen 7', 'ryzen 9', 'ai 5', 'ai 7', 'ai 9', 'm2', 'm3', 'm4', 'm5'])
            is_good_ram = ram_num >= 16

            if is_heavy_gpu:
                if is_good_cpu and is_good_ram:
                    reasons.append(f"Spesifikasi tinggi ({cpu}, RAM {ram_num}GB, Grafis {gpu}) membuatnya sangat lancar untuk game berat dan rendering 3D tanpa nge-lag.")
                else:
                    karena = "RAM yang pas-pasan" if not is_good_ram else "prosesor yang kurang maksimal"
                    reasons.append(f"Grafis {gpu} miliknya sudah sangat bagus, namun performanya mungkin sedikit tertahan karena {karena}. Masih cukup oke untuk pemakaian menengah.")
            elif is_mid_gpu and is_good_cpu and is_good_ram:
                reasons.append(f"Meski tanpa kartu grafis khusus, kombinasi {cpu} dan RAM {ram_num}GB sudah sanggup melibas game ringan (e-sports) atau edit video dasar.")
            else:
                reasons.append(f"Perangkat ini dirancang untuk keseharian, bukan untuk game berat. Namun, {cpu} miliknya tetap aman jika sekadar untuk hiburan kasual.")
                
        # 2. Kebutuhan Desain, Editing Visual & UI/UX
        if any(key in desc for key in ['desain', 'edit', 'kreator', 'visual', 'warna', 'video']):
            if any(x in str(panel).lower() for x in ['ips', 'oled', 'mini']):
                reasons.append(f"Layar tipe {panel} memberikan warna yang tajam dan akurat, sangat nyaman untuk desain grafis. Penyimpanan {storage} juga lega untuk file besar.")
            else:
                reasons.append(f"Kapasitas RAM {ram_num}GB membuat aplikasi desain berjalan lancar, dan penyimpanan {storage} cukup untuk menampung banyak aset gambar.")
                
        # 3. Kebutuhan Mobilitas & Travel
        if any(key in desc for key in ['bawa', 'kampus', 'cafe', 'traveling', 'ringan', 'mobile']):
            if float(laptop.get('weight_num', 3.0)) <= 1.5:
                reasons.append(f"Bobotnya sangat ringan (hanya {bobot}), sehingga nyaman dibawa bepergian tanpa bikin pundak pegal.")
            else:
                reasons.append(f"Dengan berat {bobot}, laptop ini masih tergolong wajar dan pas untuk dimasukkan ke dalam tas ransel Anda.")

        # 4. Kebutuhan Produktivitas/Skripsi/Coding
        if any(key in desc for key in ['skripsi', 'tugas', 'kuliah', 'kerja', 'office', 'ngetik', 'coding', 'program', 'kantor']):
            if ram_num >= 16:
                reasons.append(f"RAM besar ({ram_num}GB) membuat Anda leluasa membuka puluhan tab browser, Zoom, dan aplikasi office sekaligus tanpa takut lemot.")
            else:
                reasons.append(f"Spesifikasi {cpu} dan RAM {ram_num}GB sangat pas dan hemat daya untuk kebutuhan ngetik, skripsi, atau sekadar browsing.")

        # 5. Default Reason (Jika tidak ada alasan spesifik yang terdeteksi)
        if not reasons:
            reasons.append(f"Spesifikasi {cpu} dan RAM {ram_num}GB pada laptop ini adalah pilihan yang paling aman dan logis sesuai dengan batasan anggaran Anda.")
            
        return " ".join(dict.fromkeys(reasons))
    
    # Fungsi utama untuk mendapatkan rekomendasi laptop berdasarkan input pengguna
    def get_recommendations(self, user_input: Dict) -> Dict:
        # 1. Injeksi Kebutuhan User ke dataset (Temporary)
        dummy_user_id = "USER_QUERY_999"
        user_profile = {"id": dummy_user_id, "usage": user_input['description']}
        laptops_temp = self.laptops + [user_profile]
        
        # Re-initialize recommender untuk menghitung TF-IDF dengan input user
        temp_recommender = LaptopRecommender(laptops_temp)
        raw_recommendations = temp_recommender.recommend(dummy_user_id, top_n=len(laptops_temp)-1)

        highest_score = max((rec['score'] for rec in raw_recommendations), default=0)
        
        if highest_score < 0.02:
            return {
                "is_fallback": False, 
                "strict_count": 0, 
                "data": []
            }

        # 2. Filter Logic (Pembersihan & Penyamaan)
        strict_matches = []
        relaxed_matches = []
        
        # Ambil filter dari user_input (yang dikirim dari Flask)
        max_p = user_input['max_price']
        max_w = user_input['max_weight']
        max_s = user_input['max_screen']
        
        # Iterasi hasil rekomendasi mentah dan filter berdasarkan kriteria user
        for rec in raw_recommendations:
            laptop = next((l for l in laptops_temp if l.get('id') == rec['id']), None)
            if not laptop or laptop['id'] == dummy_user_id: continue

            # Inisialisasi gembok filter
            passed_all = True
            passed_price = True
            
            # Filter Numerik
            if float(laptop.get('price', 0)) > max_p: 
                passed_all = False
                passed_price = False # Jika gagal di filter harga, otomatis gagal strict match
                
            if float(laptop.get('weight_num', 3.0)) > max_w: passed_all = False
            if float(laptop.get('screen_size_num', 18.0)) > max_s: passed_all = False
            
            # Filter String (CPU, RAM, Storage, dll)
            if user_input['cpu'] != 'All' and user_input['cpu'].lower() not in str(laptop.get('cpu', '')).lower(): passed_all = False
            if user_input['ram'] != 'All' and user_input['ram'].lower().replace(' gb', '') not in str(laptop.get('ram', '')).lower(): passed_all = False
            
            if user_input['storage'] != 'All':
                val_storage = user_input['storage']
                laptop_storage_str = str(laptop.get('storage', '')).lower()
                # Jika user mencari 1 TB (dikirim sebagai "1000" dari React)
                if val_storage == "1000":
                    if "1 tb" not in laptop_storage_str and "1000" not in laptop_storage_str and "1tb" not in laptop_storage_str:
                        passed_all = False
                # Jika user mencari 2 TB (dikirim sebagai "2000" dari React)
                elif val_storage == "2000":
                    if "2 tb" not in laptop_storage_str and "2000" not in laptop_storage_str and "2tb" not in laptop_storage_str:
                        passed_all = False
                # Jika user mencari 128, 256, 512 GB
                else:
                    search_storage = val_storage.lower().replace(' gb', '')
                    if search_storage not in laptop_storage_str:
                        passed_all = False
            
            if user_input['os'] != 'All' and user_input['os'].lower() not in str(laptop.get('os', '')).lower(): passed_all = False
            if user_input['gpu_type'] != 'All' and user_input['gpu_type'].lower() not in str(laptop.get('gpu_type', '')).lower(): passed_all = False
            if user_input['panel_type'] != 'All' and user_input['panel_type'].lower() not in str(laptop.get('panel_type', '')).lower(): passed_all = False
            if user_input['screen_quality'] != 'All' and user_input['screen_quality'].lower() not in str(laptop.get('screen_quality', '')).lower(): passed_all = False

            laptop['similarity_score'] = rec['score']
            laptop['explanation'] = self._generate_reason(user_input, laptop)

            if passed_all and rec['score'] > 0:
                strict_matches.append(laptop)
            elif passed_price:
                relaxed_matches.append(laptop)

        # 3. Fallback Logic (Jika strict_matches kurang dari 6)
        final_results = strict_matches[:6]
        is_fallback = False
        
        if len(final_results) < 6:
            needed = 6 - len(final_results)
            final_results.extend(relaxed_matches[:needed])
            if len(relaxed_matches) > 0: is_fallback = True

        return {
            "is_fallback": is_fallback, 
            "strict_count": len(strict_matches), 
            "data": final_results
        }

# Fungsi untuk memuat dataset laptop dari file JSON
def load_laptops(filepath: Path) -> List[Dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Fungsi utama untuk menguji sistem rekomendasi secara lokal
def main() -> None:
    # 1. Load dataset
    data_path = Path(__file__).parent / "laptops.json"
    laptops = load_laptops(data_path)
    recommender = LaptopRecommender(laptops)

    # 2. Input Testing
    test_input = {
        "description": "laptop untuk skripsi dan edit video",
        "max_price": 25000000.0, "max_weight": 2.0, "max_screen": 14.0,
        "cpu": "All", "ram": "All", "storage": "All", 
        "os": "All", "gpu_type": "All", "panel_type": "All", "screen_quality": "All"
    }

    # MULAI TIMER
    start_time = time.time()
    hasil = recommender.get_recommendations(test_input)
    end_time = time.time()
    
    # HITUNG DURATION (Milidetik)
    duration = (end_time - start_time) * 1000

    # 3. Print Header Profesional
    print("\n" + "="*80)
    print(" " * 20 + "SISTEM REKOMENDASI LAPTOP - EVALUASI SISTEM")
    print("="*80)
    
    # 4. Ringkasan Teknis (Inilah yang dilihat Dosen)
    print(f"[*] Query Deskripsi  : '{test_input['description']}'")
    print(f"[*] Filter Harga     : Rp {test_input['max_price']:,.0f}")
    print(f"[*] Execution Time   : {duration:.2f} ms")
    print(f"[*] Match Status     : {'Fallback Mode (Relaxed)' if hasil['is_fallback'] else 'Strict Mode'}")
    print(f"[*] Data Ditemukan   : {len(hasil['data'])} unit")
    print("-" * 80)
    
    # 5. Tabel Hasil
    if not hasil['data']:
        print("Tidak ada laptop ditemukan.")
    else:
        print(f"{'No':<4} | {'Brand':<10} | {'Nama Laptop':<30} | {'Skor':<8} | {'Harga'}")
        print("-" * 80)
        for idx, laptop in enumerate(hasil['data'], 1):
            nama = (laptop.get('name')[:28] + '..') if len(str(laptop.get('name'))) > 28 else laptop.get('name')
            print(f"{idx:<4} | {laptop.get('brand','-'):<10} | {nama:<30} | {laptop.get('similarity_score',0)*100:.1f}% | Rp {float(laptop.get('price',0)):,.0f}")
            
    print("="*80 + "\n")

# Jika file ini dijalankan secara langsung, panggil fungsi main()
if __name__ == "__main__":
    main()