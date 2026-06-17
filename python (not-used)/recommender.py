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

    def _preprocess(self, text: str) -> List[str]:
        text = str(text).lower()
        text = re.sub(r'[^a-z0-9\s]', '', text)
        stopwords = {'dan', 'atau', 'untuk', 'dengan', 'yang', 'di', 'ke', 'dari', 'pada', 'adalah', 'ini', 'itu', 'buat', 'sama', 'juga', 'sih', 'cuma', 'aja', 'nggak', 'gak'}
        return [word for word in text.split() if word not in stopwords]

    def _compute_tf(self, doc: List[str]) -> Dict[str, float]:
        tf = Counter(doc)
        total_words = len(doc)
        return {word: count / total_words for word, count in tf.items()} if total_words > 0 else {}

    def _compute_idf(self) -> Dict[str, float]:
        N = len(self.corpus)
        df = defaultdict(int)
        for doc in self.corpus:
            unique_words = set(doc)
            for word in unique_words:
                df[word] += 1
        return {word: math.log((1 + N) / (1 + count)) + 1 for word, count in df.items()}

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

    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[word] * vec2[word] for word in intersection)
        return dot_product
    

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
    
    def _generate_reason(self, user_input: Dict, laptop: Dict) -> str:
        desc = user_input['description'].lower()
        reasons = []

        # 1. Definisi Aturan
        rules = [
            # Gaming & Rendering: Cek apakah NVIDIA/AMD (bukan sekadar kata 'dedicated')
            (['game', 'gaming', 'render', '3d'], 
             lambda l: l.get('gpu_type') in ['NVIDIA', 'AMD'], 
             "GPU bertenaga tinggi yang sangat mumpuni untuk gaming berat dan rendering 3D."),
             
            # Powerful & Kencang
            (['powerful', 'kencang', 'terbaik', 'high'], 
             lambda l: float(l.get('price', 0)) > 15000000, 
             "Spesifikasi kelas atas untuk performa maksimal tanpa hambatan."),
             
            # Skripsi/Tugas/Kerja (Ganti kondisi berat agar lebih inklusif)
            (['skripsi', 'tugas', 'kuliah', 'kerja', 'office'], 
             lambda l: True, # Selalu masuk untuk kebutuhan umum
             "Performa stabil dan andal untuk mengerjakan dokumen dan tugas harian."),
             
            # Desain/Edit (Layar)
            (['desain', 'edit', 'kreator', 'visual'], 
             lambda l: any(x in str(l.get('panel_type', '')).lower() for x in ['ips', 'oled', 'mini']), 
             "Layar berkualitas tinggi dengan akurasi warna yang sangat baik.")
        ]

        # 2. Pemrosesan Aturan
        for keywords, condition_func, message in rules:
            if any(key in desc for key in keywords):
                if condition_func(laptop):
                    reasons.append(message)

        # 3. Default Reason
        if not reasons:
            brand = laptop.get('brand', 'Laptop ini')
            return f"{brand} adalah pilihan menarik dengan spesifikasi yang solid untuk kebutuhan Anda."
            
        # Mengembalikan alasan yang unik
        return " | ".join(dict.fromkeys(reasons))
    
    def get_recommendations(self, user_input: Dict) -> Dict:
        # 1. Injeksi Kebutuhan User ke dataset (Temporary)
        dummy_user_id = "USER_QUERY_999"
        user_profile = {"id": dummy_user_id, "usage": user_input['description']}
        laptops_temp = self.laptops + [user_profile]
        
        # Re-initialize recommender untuk menghitung TF-IDF dengan input user
        temp_recommender = LaptopRecommender(laptops_temp)
        raw_recommendations = temp_recommender.recommend(dummy_user_id, top_n=len(laptops_temp)-1)

        # 2. Filter Logic (Pembersihan & Penyamaan)
        strict_matches = []
        relaxed_matches = []
        
        # Ambil filter dari user_input (yang dikirim dari Flask)
        max_p = user_input['max_price']
        max_w = user_input['max_weight']
        max_s = user_input['max_screen']
        
        for rec in raw_recommendations:
            laptop = next((l for l in laptops_temp if l.get('id') == rec['id']), None)
            if not laptop or laptop['id'] == dummy_user_id: continue

            passed = True
            
            # Filter Numerik
            if float(laptop.get('price', 0)) > max_p: passed = False
            if float(laptop.get('weight_num', 3.0)) > max_w: passed = False
            if float(laptop.get('screen_size_num', 18.0)) > max_s: passed = False
            
            # Filter String (CPU, RAM, Storage, dll)
            if user_input['cpu'] != 'All' and user_input['cpu'].lower() not in str(laptop.get('cpu', '')).lower(): passed = False
            if user_input['ram'] != 'All' and user_input['ram'].lower().replace(' gb', '') not in str(laptop.get('ram', '')).lower(): passed = False
            if user_input['storage'] != 'All' and user_input['storage'].lower().replace(' gb', '').replace(' tb', '') not in str(laptop.get('storage', '')).lower(): passed = False
            if user_input['os'] != 'All' and user_input['os'].lower() not in str(laptop.get('os', '')).lower(): passed = False
            if user_input['gpu_type'] != 'All' and user_input['gpu_type'].lower() not in str(laptop.get('gpu_type', '')).lower(): passed = False
            if user_input['panel_type'] != 'All' and user_input['panel_type'].lower() not in str(laptop.get('panel_type', '')).lower(): passed = False
            if user_input['screen_quality'] != 'All' and user_input['screen_quality'].lower() not in str(laptop.get('screen_quality', '')).lower(): passed = False

            laptop['similarity_score'] = rec['score']

            if rec['score'] > 0:
                laptop['explanation'] = self._generate_reason(user_input, laptop)
                if passed: strict_matches.append(laptop)
                else: relaxed_matches.append(laptop)

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

def load_laptops(filepath: Path) -> List[Dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

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

if __name__ == "__main__":
    main()