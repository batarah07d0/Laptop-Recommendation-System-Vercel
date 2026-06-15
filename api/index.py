import json
import os
import traceback

from flask import Flask, jsonify, request
from flask_cors import CORS
# Pastikan nama class/fungsi di bawah ini sesuai dengan yang ada di recommender.py Anda
from recommender import LaptopRecommender

app = Flask(__name__)
# Wajib agar React di localhost:5173 diizinkan mengambil data dari localhost:5000
CORS(app) 

base_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(base_dir, 'laptops.json')

# Memuat dataset satu kali saat server dinyalakan (Load into Memory)
# Ini membuat pencarian instan tanpa perlu membaca file berulang kali
print("Memuat dataset laptop...")
try:
    with open(json_path, 'r', encoding='utf-8') as f:
        laptops_data = json.load(f)
    # Inisialisasi
    ai_engine = LaptopRecommender(laptops_data)
    print("Dataset berhasil dimuat. Mesin siap digunakan!")
except Exception as e:
    print(f"Error memuat dataset: {e}")

@app.route('/api/recommend', methods=['POST'])
@app.route('/recommend', methods=['POST'])
def recommend():
    try:
        # 1. Menangkap JSON yang dikirim oleh React (Axios)
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # 2. Mengekstrak 11 parameter filter
        user_input = {
            "description": data.get('description', ''),
            "max_price": float(data.get('max_price', 50000000)),
            "max_weight": float(data.get('max_weight', 3.0)),
            "max_screen": float(data.get('max_screen', 18.0)),
            "cpu": data.get('cpu', 'All'),
            "ram": data.get('ram', 'All'),
            "storage": data.get('storage', 'All'),
            "os": data.get('os', 'All'),
            "gpu_type": data.get('gpu_type', 'All'),
            "panel_type": data.get('panel_type', 'All'),
            "screen_quality": data.get('screen_quality', 'All')
        }

        # 3. Masukkan ke fungsi penghitung TF-IDF dan Cosine Similarity di recommender.py
        # PENTING: Pastikan fungsi get_recommendations milik Anda siap menerima dictionary 'user_input' ini
        hasil = ai_engine.get_recommendations(user_input)
        
        # 4. Kembalikan hasilnya ke React dalam bentuk JSON
        return jsonify(hasil)
        
    except Exception as e:
        error_msg = str(e)
        detailed_error = traceback.format_exc()
        print(f"ERROR: {detailed_error}")
        return jsonify({"error": error_msg, "traceback": detailed_error}), 500