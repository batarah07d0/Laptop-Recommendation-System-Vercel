import json
from pathlib import Path

from recommender import LaptopRecommender

# 1. Load dataset
with open("laptops.json", "r", encoding="utf-8") as f:
    laptops = json.load(f)

# 2. Tentukan query yang dipakai di BAB 4
query = "laptop untuk kuliah, coding, dan gaming ringan"

# 3. Tambahkan query sebagai dokumen sementara
dummy_user_id = "USER_QUERY_999"
laptops_temp = laptops + [
    {
        "id": dummy_user_id,
        "usage": query
    }
]

# 4. Hitung TF-IDF menggunakan class LaptopRecommender
recommender = LaptopRecommender(laptops_temp)

# 5. Ambil vektor TF-IDF query
query_vector = recommender.tfidf_matrix[-1]

# 6. Tentukan laptop yang ingin dibandingkan
target_laptop_ids = ["LP0043", "LP0081", "LP0051"]

# 7. Buat mapping ID laptop ke index
id_to_index = {
    laptop["id"]: index
    for index, laptop in enumerate(laptops_temp)
}

# 8. Term yang ingin ditampilkan di BAB 4
terms = ["kuliah", "coding", "gaming", "ringan"]

# 9. Cetak hasil dalam bentuk tabel
print("Term | Query | LP0043 | LP0081 | LP0051")
print("-" * 60)

for term in terms:
    query_weight = query_vector.get(term, 0)

    row = [
        term,
        f"{query_weight:.4f}"
    ]

    for laptop_id in target_laptop_ids:
        idx = id_to_index[laptop_id]
        laptop_vector = recommender.tfidf_matrix[idx]
        weight = laptop_vector.get(term, 0)
        row.append(f"{weight:.4f}")

    print(" | ".join(row))