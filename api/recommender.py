#!/usr/bin/env python3
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, List, Tuple


class LaptopRecommender:
    def __init__(self, laptops: List[Dict]):
        self.laptops = laptops
        self.laptop_by_id = {
            laptop.get("id"): laptop
            for laptop in laptops
            if laptop.get("id")
        }
        self.index_by_id = {
            laptop.get("id"): index
            for index, laptop in enumerate(laptops)
            if laptop.get("id")
        }

        self.corpus = [
            self._preprocess(laptop.get('usage', ''))
            for laptop in laptops
        ]

        # Bentuk kamus frasa dari token metadata yang menggunakan underscore.
        # Contoh: baterai_awet -> (baterai, awet) dan
        # acer_aspire_go_14 -> (acer, aspire, go, 14). Kamus ini membuat
        # query mengenali fitur dan nama model tanpa daftar manual terpisah.
        phrase_terms = {
            token
            for document in self.corpus
            for token in document
            if "_" in token
        }
        self.phrase_lookup = {
            tuple(token.split("_")): token
            for token in phrase_terms
        }
        self.max_phrase_words = max(
            (len(words) for words in self.phrase_lookup),
            default=1
        )

        # Matriks antara disimpan agar proses TF, IDF, TF-IDF mentah,
        # normalisasi, dan cosine similarity dapat ditampilkan saat debug.
        # Perubahan ini tidak mengubah hasil rekomendasi utama.
        self.document_frequency: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.tf_matrix: List[Dict[str, float]] = []
        self.tfidf_raw_matrix: List[Dict[str, float]] = []
        self.vector_norms: List[float] = []
        self.tfidf_matrix = self._compute_tfidf()

    @staticmethod
    def _get_stopwords() -> set:
        return {
            'dan', 'atau', 'untuk', 'dengan', 'yang', 'di', 'ke', 'dari',
            'pada', 'adalah', 'ini', 'itu', 'buat', 'saya', 'aku', 'pengen',
            'ingin', 'mau', 'beli', 'cari', 'carikan', 'tolong', 'dong',
            'tidak', 'bukan', 'sangat', 'paling', 'butuh', 'membutuhkan',
            'mengerjakan', 'bermain', 'dipakai', 'digunakan', 'laptop', 'bisa', 'buka'
        }

    # Bersihkan teks input dan normalisasi istilah domain laptop.
    # Fungsi yang sama digunakan untuk metadata laptop dan query pengguna.
    def _preprocess(
        self,
        text: str,
        remove_stopwords: bool = True
    ) -> List[str]:
        text = str(text).lower()

        # Normalisasi frasa domain agar diperlakukan sebagai satu term
        phrase_patterns = [
            (r'\b(?:main\s+)?(?:game|gaming)\s+(?:kasual\s+)?ringan\b', 'game_ringan'),
            (r'\b(?:game|gaming)\s+menengah\b', 'game_menengah'),
            (r'\b(?:game|gaming)\s+(?:berat|extreme|ekstrem)\b', 'game_berat'),
            (r'\bedit(?:ing)?\s+video\s+ringan\b', 'edit_video_ringan'),
            (r'\bdesain\s+grafis\s+ringan\b', 'desain_grafis_ringan'),
            (r'\bgrafis\s+ringan\s+bawaan\b', 'grafis_bawaan'),
            (r'\bpenggunaan\s+ringan\b', 'penggunaan_ringan'),
            (r'\bultra\s+ringan\b', 'bobot_sangat_ringan'),
            (r'\b(?:laptop|notebook|bobot)\s+ringan\b', 'bobot_ringan'),
            (r'\bringan\s+(?:dan\s+)?mudah\s+dibawa\b', 'bobot_ringan'),
        ]

        for pattern, replacement in phrase_patterns:
            text = re.sub(pattern, replacement, text)

        # Kata "ringan" tidak langsung diubah karena konteksnya dapat
        # merujuk pada game, pekerjaan, aplikasi, atau bobot perangkat.

        text = re.sub(r'(\d+),(\d+)', r'\1.\2', text)

        # Normalisasi angka desimal bulat: 14.0 -> 14
        text = re.sub(r'\b(\d+)\.0\b', r'\1', text)

        # Normalisasi GPU: RTX3050 / RTX-3050 -> rtx 3050
        text = re.sub(
            r'\b(rtx|gtx|rx)[-\s]*([0-9]{3,4})\b',
            r'\1 \2',
            text
        )

        # Normalisasi CPU Intel: i5-13420H -> i5 13420h
        text = re.sub(
            r'\b(i[3579])[-\s]*([0-9]{4,5}[a-z]{0,2})\b',
            r'\1 \2',
            text
        )

        # Normalisasi variasi penulisan satuan.
        # Tahap ini hanya menyamakan bentuk teks dan tidak mengubah
        # spesifikasi pada kueri menjadi filter otomatis.
        text = re.sub(
            r'\b(giga|gigabyte|gigabytes|gigabita)\b',
            'gb',
            text
        )
        text = re.sub(
            r'\b(tera|terabyte|terabytes|terabita)\b',
            'tb',
            text
        )
        text = re.sub(r'\b(kilogram|kilo)\b', 'kg', text)
        text = re.sub(r'\binci\b', 'inch', text)

        # Samakan bentuk "16 GB" dan "16GB", serta bentuk satuan lain.
        text = re.sub(
            r'\b(\d+(?:\.\d+)?)\s*(gb|tb|kg|inch)\b',
            r'\1\2',
            text
        )

        # Hapus karakter yang tidak diperlukan, tetapi pertahankan titik
        # karena masih dapat digunakan pada angka desimal seperti 1.5kg.
        text = re.sub(r'[^a-z0-9_\.\s]', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        tokens = [word for word in text.split() if word]

        if remove_stopwords:
            stopwords = self._get_stopwords()
            tokens = [word for word in tokens if word not in stopwords]

        return tokens

    def _merge_known_phrases(self, tokens: List[str]) -> List[str]:
        """Gabungkan urutan kata query yang tersedia sebagai token frasa metadata."""
        if not tokens or not self.phrase_lookup:
            return tokens

        merged: List[str] = []
        index = 0

        while index < len(tokens):
            matched = False
            remaining = len(tokens) - index
            max_size = min(self.max_phrase_words, remaining)

            for size in range(max_size, 1, -1):
                candidate = tuple(tokens[index:index + size])
                phrase_token = self.phrase_lookup.get(candidate)
                if phrase_token:
                    merged.append(phrase_token)
                    index += size
                    matched = True
                    break

            if not matched:
                merged.append(tokens[index])
                index += 1

        return merged

    def _preprocess_query(self, text: str) -> List[str]:
        # Frasa digabungkan sebelum stopword dihapus agar token seperti
        # performa_sangat_tinggi, acer_aspire_go_14, dan dibawa_ke_kampus
        # tetap utuh.
        tokens = self._preprocess(text, remove_stopwords=False)
        tokens = self._merge_known_phrases(tokens)

        stopwords = self._get_stopwords()
        tokens = [token for token in tokens if token not in stopwords]

        # Jika "ringan" menjadi satu-satunya kebutuhan bermakna, konteks
        # yang paling wajar adalah bobot perangkat.
        if tokens == ["ringan"] and "bobot_ringan" in self.idf:
            return ["bobot_ringan"]

        return tokens

    # Hitung Term Frequency (TF) untuk satu dokumen.
    def _compute_tf(self, doc: List[str]) -> Dict[str, float]:
        tf = Counter(doc)
        total_words = len(doc)
        return {
            word: count / total_words for word, count in tf.items()
        } if total_words > 0 else {}

    # Hitung Inverse Document Frequency (IDF) untuk seluruh korpus.
    def _compute_idf(self) -> Dict[str, float]:
        document_count = len(self.corpus)
        df = defaultdict(int)

        for doc in self.corpus:
            # Setiap term hanya dihitung satu kali per dokumen.
            for word in set(doc):
                df[word] += 1

        self.document_frequency = dict(df)
        return {
            word: math.log((1 + document_count) / (1 + count)) + 1
            for word, count in df.items()
        }

    # Bangun TF, TF-IDF mentah, panjang vektor, dan TF-IDF ternormalisasi.
    def _compute_tfidf(self) -> List[Dict[str, float]]:
        self.idf = self._compute_idf()
        self.tf_matrix = []
        self.tfidf_raw_matrix = []
        self.vector_norms = []
        normalized_matrix: List[Dict[str, float]] = []

        for doc in self.corpus:
            tf = self._compute_tf(doc)
            tfidf_raw = {
                word: tf_value * self.idf.get(word, 0.0)
                for word, tf_value in tf.items()
            }

            norm = math.sqrt(sum(value ** 2 for value in tfidf_raw.values()))
            if norm > 0:
                tfidf_normalized = {
                    word: value / norm
                    for word, value in tfidf_raw.items()
                }
            else:
                tfidf_normalized = {}

            self.tf_matrix.append(tf)
            self.tfidf_raw_matrix.append(tfidf_raw)
            self.vector_norms.append(norm)
            normalized_matrix.append(tfidf_normalized)

        return normalized_matrix

    # Bentuk vektor query menggunakan IDF yang sudah dihitung dari korpus laptop.
    # Query tidak dimasukkan ke korpus dan tidak mengubah statistik IDF.
    def _vectorize_query(self, text: str) -> Dict:
        tokens = self._preprocess_query(text)
        tf = self._compute_tf(tokens)

        # Hanya term yang dikenal oleh vocabulary korpus laptop yang dipakai.
        tfidf_raw = {
            word: tf_value * self.idf[word]
            for word, tf_value in tf.items()
            if word in self.idf
        }

        norm = math.sqrt(sum(value ** 2 for value in tfidf_raw.values()))
        if norm > 0:
            tfidf_normalized = {
                word: value / norm
                for word, value in tfidf_raw.items()
            }
        else:
            tfidf_normalized = {}

        return {
            "tokens": tokens,
            "tf": tf,
            "tfidf_raw": tfidf_raw,
            "norm": norm,
            "tfidf_normalized": tfidf_normalized
        }

    # Hitung cosine similarity antar dua vektor TF-IDF.
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        intersection = set(vec1.keys()) & set(vec2.keys())
        dot_product = sum(vec1[word] * vec2[word] for word in intersection)
        return dot_product
    
    # Bentuk ranking query terhadap seluruh laptop dengan IDF korpus tetap.
    # Fungsi ini menjadi satu-satunya sumber ranking awal agar skrip utama,
    # Bab IV, dan analisis skor menggunakan perhitungan yang sama.
    def rank_query(self, text: str) -> Tuple[Dict, List[Dict]]:
        query_info = self._vectorize_query(text)
        query_vector = query_info.get("tfidf_normalized", {})

        if not query_vector:
            return query_info, []

        rankings = []
        for index, laptop_vector in enumerate(self.tfidf_matrix):
            rankings.append({
                "id": self.laptops[index].get("id"),
                "score": self._cosine_similarity(query_vector, laptop_vector)
            })

        rankings.sort(
            key=lambda item: item.get("score", 0.0),
            reverse=True
        )
        return query_info, rankings

    # Ambil rekomendasi laptop dengan skor tertinggi terhadap target query.
    def recommend(self, target_id: str, top_n: int = 5) -> List[Dict]:
        target_idx = next((i for i, laptop in enumerate(self.laptops) if laptop['id'] == target_id), None)

        # Jika target_id tidak ditemukan, kembalikan daftar kosong.
        if target_idx is None:
            return []

        target_vec = self.tfidf_matrix[target_idx]
        scores = []
        
        for i, vec in enumerate(self.tfidf_matrix):
            if i != target_idx:
                score = self._cosine_similarity(target_vec, vec)
                scores.append({'id': self.laptops[i]['id'], 'score': score})
                
        # Urutkan hasil berdasarkan skor tertinggi dan ambil top N
        scores.sort(key=lambda x: x['score'], reverse=True)
        return scores[:top_n]
    
    # Kumpulkan data debug lengkap untuk kebutuhan Bab IV dan CLI.
    def _build_debug_info(
        self,
        user_input: Dict,
        query_info: Dict,
        raw_recommendations: List[Dict],
        final_results: List[Dict],
        top_terms_n: int = 10,
        top_laptops_n: int = 3
    ) -> Dict:
        query_tokens = query_info.get("tokens", [])
        query_tf = query_info.get("tf", {})
        query_tfidf_raw = query_info.get("tfidf_raw", {})
        query_norm = query_info.get("norm", 0.0)
        query_vector_normalized = query_info.get("tfidf_normalized", {})

        custom_terms = user_input.get("debug_terms")
        if custom_terms:
            selected_terms = []
            for term in custom_terms:
                processed = self._preprocess_query(str(term))
                selected_terms.extend(processed if processed else [str(term).lower()])
            selected_terms = list(dict.fromkeys(selected_terms))
        else:
            selected_terms = [
                term
                for term, _ in sorted(
                    query_vector_normalized.items(),
                    key=lambda item: item[1],
                    reverse=True
                )[:top_terms_n]
            ]

        selected_laptops = final_results[:top_laptops_n]

        def build_matrix_table(
            query_vector: Dict[str, float],
            document_matrix: List[Dict[str, float]]
        ) -> List[Dict]:
            rows = []
            for term in selected_terms:
                row = {
                    "term": term,
                    "query": query_vector.get(term, 0.0)
                }
                for laptop in selected_laptops:
                    laptop_id = laptop.get("id")
                    laptop_idx = self.index_by_id.get(laptop_id)
                    vector = document_matrix[laptop_idx] if laptop_idx is not None else {}
                    row[laptop_id] = vector.get(term, 0.0)
                rows.append(row)
            return rows

        tf_table = build_matrix_table(query_tf, self.tf_matrix)
        tfidf_raw_table = build_matrix_table(query_tfidf_raw, self.tfidf_raw_matrix)
        tfidf_normalized_table = build_matrix_table(
            query_vector_normalized,
            self.tfidf_matrix
        )

        idf_table = [
            {
                "term": term,
                "document_count": len(self.corpus),
                "document_frequency": self.document_frequency.get(term, 0),
                "idf": self.idf.get(term, 0.0)
            }
            for term in selected_terms
        ]

        normalization_table = [
            {
                "document": "Query",
                "id": "USER_QUERY",
                "raw_vector_norm": query_norm,
                "normalized_vector_norm": math.sqrt(
                    sum(value ** 2 for value in query_vector_normalized.values())
                )
            }
        ]

        for laptop in selected_laptops:
            laptop_id = laptop.get("id")
            laptop_idx = self.index_by_id.get(laptop_id)
            if laptop_idx is None:
                continue

            normalization_table.append({
                "document": laptop.get("name", "-"),
                "id": laptop_id,
                "raw_vector_norm": self.vector_norms[laptop_idx],
                "normalized_vector_norm": math.sqrt(
                    sum(value ** 2 for value in self.tfidf_matrix[laptop_idx].values())
                )
            })

        cosine_detail_table = []
        for laptop in selected_laptops:
            laptop_id = laptop.get("id")
            laptop_idx = self.index_by_id.get(laptop_id)
            if laptop_idx is None:
                continue

            laptop_raw_vector = self.tfidf_raw_matrix[laptop_idx]
            laptop_norm = self.vector_norms[laptop_idx]
            shared_terms = set(query_tfidf_raw) & set(laptop_raw_vector)

            raw_dot_product = sum(
                query_tfidf_raw[term] * laptop_raw_vector[term]
                for term in shared_terms
            )
            denominator = query_norm * laptop_norm
            cosine_from_raw = (
                raw_dot_product / denominator
                if denominator > 0
                else 0.0
            )
            cosine_from_normalized = self._cosine_similarity(
                query_vector_normalized,
                self.tfidf_matrix[laptop_idx]
            )

            cosine_detail_table.append({
                "id": laptop_id,
                "brand": laptop.get("brand", "-"),
                "name": laptop.get("name", "-"),
                "shared_term_count": len(shared_terms),
                "shared_terms": sorted(shared_terms),
                "raw_dot_product": raw_dot_product,
                "query_norm": query_norm,
                "laptop_norm": laptop_norm,
                "denominator": denominator,
                "cosine_from_raw": cosine_from_raw,
                "cosine_from_normalized": cosine_from_normalized
            })

        similarity_table = []
        for idx, laptop in enumerate(final_results, 1):
            similarity_table.append({
                "rank": idx,
                "id": laptop.get("id", "-"),
                "brand": laptop.get("brand", "-"),
                "name": laptop.get("name", "-"),
                "score": laptop.get("similarity_score", 0.0),
                "price": laptop.get("price", 0.0)
            })

        return {
            "query_original": user_input.get("description", ""),
            "query_tokens": query_tokens,
            "known_query_terms": sorted(query_tfidf_raw.keys()),
            "unknown_query_terms": sorted(
                set(query_tokens) - set(query_tfidf_raw.keys())
            ),
            "corpus_size": len(self.corpus),
            "selected_terms": selected_terms,
            "selected_laptops": [
                {
                    "id": laptop.get("id", "-"),
                    "name": laptop.get("name", "-"),
                    "brand": laptop.get("brand", "-")
                }
                for laptop in selected_laptops
            ],
            "tf_table": tf_table,
            "idf_table": idf_table,
            "tfidf_raw_table": tfidf_raw_table,
            "normalization_table": normalization_table,
            "tfidf_normalized_table": tfidf_normalized_table,
            "tfidf_table": tfidf_normalized_table,
            "cosine_detail_table": cosine_detail_table,
            "similarity_table": similarity_table,
            "raw_highest_score": max(
                (rec.get("score", 0.0) for rec in raw_recommendations),
                default=0.0
            )
        }

    @staticmethod
    def _classify_gpu_type(laptop: Dict) -> str:
        """
        Tentukan tipe GPU sebagai Dedicated, Integrated, atau Unknown.

        Fungsi tetap kompatibel dengan:
        1. JSON baru yang menyimpan gpu_type secara semantik; dan
        2. JSON lama yang menyimpan gpu_type sebagai vendor.
        """
        stored_type = str(laptop.get("gpu_type", "")).strip().lower()

        if stored_type == "dedicated":
            return "Dedicated"
        if stored_type == "integrated":
            return "Integrated"
        if stored_type == "unknown":
            return "Unknown"

        gpu = str(laptop.get("gpu", "") or "").lower().strip()
        if not gpu:
            return "Unknown"

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

    @staticmethod
    def _matches_screen_quality(requested: str, screen_quality: str) -> bool:
        requested_key = str(requested).lower().strip()
        quality = str(screen_quality).lower()
        aliases = {
            "hd": ["1366", "1280", " hd"],
            "fhd": ["fhd", "1920 x 1080", "1920x1080"],
            "wuxga": ["wuxga", "1920 x 1200", "1920x1200"],
            "2.5k": ["2.5k", "wqxga", "2560"],
            "2.8k": ["2.8k", "2880"],
            "3k+": ["3k", "3.2k", "4k", "uhd", "3024", "3200", "3840"],
        }
        return any(alias in quality for alias in aliases.get(requested_key, [requested_key]))

    # Periksa filter dengan aturan yang sama untuk sistem utama dan laporan Bab IV.
    def check_filter_status(self, user_input: Dict, laptop: Dict) -> Dict:
        failed = []
        passed_price = True

        try:
            max_price = float(user_input.get("max_price", 50000000))
            max_weight = float(user_input.get("max_weight", 3.0))
            max_screen = float(user_input.get("max_screen", 18.0))
            price = float(laptop.get("price", 0))
            weight = float(laptop.get("weight_num", 3.0))
            screen = float(laptop.get("screen_size_num", 18.0))
        except (TypeError, ValueError):
            return {
                "passed_all": False,
                "passed_price": False,
                "failed": ["data numerik tidak valid"]
            }

        if price > max_price:
            failed.append("harga")
            passed_price = False
        if weight > max_weight:
            failed.append("berat")
        if screen > max_screen:
            failed.append("ukuran layar")

        if (
            user_input.get("cpu", "All") != "All"
            and str(user_input["cpu"]).lower()
            not in str(laptop.get("cpu", "")).lower()
        ):
            failed.append("cpu")

        if user_input.get("ram", "All") != "All":
            requested_ram = (
                str(user_input["ram"]).lower().replace(" gb", "").strip()
            )
            laptop_ram_match = re.search(r'(\d+)', str(laptop.get("ram", "")))
            laptop_ram = laptop_ram_match.group(1) if laptop_ram_match else ""
            if requested_ram != laptop_ram:
                failed.append("ram")

        if user_input.get("storage", "All") != "All":
            requested_storage = str(user_input["storage"])
            laptop_storage = str(laptop.get("storage", "")).lower()

            if requested_storage == "1000":
                valid_values = ["1 tb", "1000", "1024", "1tb"]
                if not any(value in laptop_storage for value in valid_values):
                    failed.append("storage")
            elif requested_storage == "2000":
                valid_values = ["2 tb", "2000", "2048", "2tb"]
                if not any(value in laptop_storage for value in valid_values):
                    failed.append("storage")
            else:
                requested_value = (
                    requested_storage.lower().replace(" gb", "").strip()
                )
                storage_match = re.search(r'(\d+)', laptop_storage)
                laptop_value = storage_match.group(1) if storage_match else ""
                if requested_value != laptop_value:
                    failed.append("storage")

        for input_key, laptop_key, label in [
            ("os", "os", "os"),
            ("panel_type", "panel_type", "panel type"),
        ]:
            requested = user_input.get(input_key, "All")
            if (
                requested != "All"
                and str(requested).lower()
                not in str(laptop.get(laptop_key, "")).lower()
            ):
                failed.append(label)

        requested_gpu = str(
            user_input.get("gpu_type", "All")
        ).strip()

        if requested_gpu.lower() != "all":
            actual_gpu = self._classify_gpu_type(laptop)

            # Unknown tidak dipaksakan menjadi Integrated atau Dedicated.
            if requested_gpu.lower() != actual_gpu.lower():
                failed.append("gpu type")

        requested_quality = user_input.get("screen_quality", "All")
        if (
            requested_quality != "All"
            and not self._matches_screen_quality(
                requested_quality,
                laptop.get("screen_quality", "")
            )
        ):
            failed.append("screen quality")

        return {
            "passed_all": len(failed) == 0,
            "passed_price": passed_price,
            "failed": failed
        }

    # Fungsi utama untuk menghasilkan rekomendasi berdasarkan input pengguna.
    def get_recommendations(self, user_input: Dict, debug: bool = False) -> Dict:
        # 1. Bentuk vektor dan ranking query dengan IDF korpus yang tetap.
        query_info, raw_recommendations = self.rank_query(
            user_input.get("description", "")
        )

        # Jika tidak ada satu pun term query yang dikenal oleh korpus,
        # sistem tidak memaksakan rekomendasi berdasarkan skor yang tidak bermakna.
        if not raw_recommendations:
            result = {
                "is_fallback": False,
                "strict_count": 0,
                "data": []
            }
            if debug:
                result["debug"] = self._build_debug_info(
                    user_input=user_input,
                    query_info=query_info,
                    raw_recommendations=[],
                    final_results=[]
                )
            return result

        # 2. Filter hasil berdasarkan batasan pengguna.
        strict_matches = []
        relaxed_matches = []

        for rec in raw_recommendations:
            source_laptop = self.laptop_by_id.get(rec.get("id"))
            if not source_laptop:
                continue

            # Salin data agar permintaan API tidak mengubah dataset utama
            # yang disimpan di memori server.
            laptop = dict(source_laptop)

            filter_status = self.check_filter_status(user_input, laptop)
            passed_all = filter_status["passed_all"]
            passed_price = filter_status["passed_price"]

            laptop["similarity_score"] = rec.get("score", 0.0)

            # Hanya item dengan similarity positif yang dapat menjadi rekomendasi.
            if passed_all and rec.get("score", 0.0) > 0:
                strict_matches.append(laptop)
            elif passed_price and rec.get("score", 0.0) > 0:
                relaxed_matches.append(laptop)

        # 3. Ambil Top-6. Jika strict match kurang dari enam,
        # lengkapi dengan kandidat relaxed yang masih berada di bawah anggaran.
        final_results = strict_matches[:6]
        is_fallback = False

        if len(final_results) < 6:
            needed = 6 - len(final_results)
            final_results.extend(relaxed_matches[:needed])
            is_fallback = needed > 0 and len(relaxed_matches) > 0

        result = {
            "is_fallback": is_fallback,
            "strict_count": len(strict_matches),
            "data": final_results
        }

        if debug:
            result["debug"] = self._build_debug_info(
                user_input=user_input,
                query_info=query_info,
                raw_recommendations=raw_recommendations,
                final_results=final_results,
                top_terms_n=10,
                top_laptops_n=3
            )

        return result

# Muat dataset laptop dari file JSON.
def load_laptops(filepath: Path) -> List[Dict]:
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

# Tampilkan hasil debug algoritma di CLI dan Fungsi ini tidak dipakai oleh website/API Flask.
def print_debug_report(hasil: Dict) -> None:
    debug = hasil.get("debug")
    if not debug:
        return

    print("\n" + "="*80)
    print(" " * 24 + "DEBUG ALGORITMA REKOMENDASI")
    print("="*80)

    print(f"[*] Query Asli       : {debug.get('query_original', '')}")
    print(f"[*] Token Query      : {', '.join(debug.get('query_tokens', []))}")
    print(f"[*] Term Ditampilkan : {', '.join(debug.get('selected_terms', []))}")

    selected_laptops = debug.get("selected_laptops", [])
    if selected_laptops:
        print("\n[*] Laptop yang dipakai untuk tabel TF-IDF:")
        for laptop in selected_laptops:
            print(f"    - {laptop.get('id')} | {laptop.get('brand')} | {laptop.get('name')}")

    print("\n" + "-"*80)
    print("TABEL TF-IDF (Term Frequency - Inverse Document Frequency)")
    print("-"*80)

    headers = ["Term", "Query"] + [laptop.get("id", "-") for laptop in selected_laptops]
    print(" | ".join(f"{header:<12}" for header in headers))
    print("-"*80)

    for row in debug.get("tfidf_table", []):
        values = [row.get("term", "-"), f"{row.get('query', 0.0):.4f}"]
        for laptop in selected_laptops:
            laptop_id = laptop.get("id")
            values.append(f"{row.get(laptop_id, 0.0):.4f}")
        print(" | ".join(f"{value:<12}" for value in values))

    print("\n" + "-"*80)
    print("TABEL COSINE SIMILARITY / RANKING TOP-6 LAPTOP")
    print("-"*80)
    print(f"{'Rank':<5} | {'ID':<7} | {'Brand':<10} | {'Nama Laptop':<30} | {'Skor':<8}")
    print("-"*80)

    for item in debug.get("similarity_table", []):
        nama = str(item.get('name', '-'))
        nama = (nama[:28] + '..') if len(nama) > 30 else nama
        print(
            f"{item.get('rank', '-'):<5} | "
            f"{item.get('id', '-'):<7} | "
            f"{item.get('brand', '-'):<10} | "
            f"{nama:<30} | "
            f"{item.get('score', 0.0):.4f}"
        )

# Fungsi utama untuk menguji sistem rekomendasi secara lokal.
def main() -> None:
    # 1. Muat dataset.
    data_path = Path(__file__).parent / "laptops.json"
    laptops = load_laptops(data_path)
    recommender = LaptopRecommender(laptops)

    # 2. Siapkan input uji.
    test_input = {
        "description": "saya butuh laptop untuk kuliah, mengerjakan skripsi, coding, dan bermain game ringan",
        "max_price": 25000000.0, "max_weight": 2.0, "max_screen": 14.0,
        "cpu": "All", "ram": "All", "storage": "All",
        "os": "All", "gpu_type": "All", "panel_type": "All", "screen_quality": "All",
        # Term yang ingin ditampilkan pada tabel TF-IDF untuk debug.
        "debug_terms": ["kuliah", "skripsi", "coding", "game_ringan"]
    }

    # Mulai pengukuran waktu.
    start_time = time.time()
    hasil = recommender.get_recommendations(test_input, debug=True)
    end_time = time.time()

    # Hitung durasi dalam milidetik.
    duration = (end_time - start_time) * 1000

    # 3. Cetak header hasil pengujian.
    print("\n" + "="*80)
    print(" " * 20 + "SISTEM REKOMENDASI LAPTOP - EVALUASI SISTEM")
    print("="*80)

    # 4. Ringkasan teknis hasil uji.
    print(f"[*] Query Deskripsi  : '{test_input['description']}'")
    print(f"[*] Filter Harga     : Rp {test_input['max_price']:,.0f}")
    print(f"[*] Execution Time   : {duration:.2f} ms")
    print(f"[*] Match Status     : {'Fallback Mode (Relaxed)' if hasil['is_fallback'] else 'Strict Mode'}")
    print(f"[*] Data Ditemukan   : {len(hasil['data'])} unit")
    print("-" * 80)

    # 5. Tampilkan tabel hasil rekomendasi.
    if not hasil['data']:
        print("Tidak ada laptop ditemukan.")
    else:
        print(f"{'No':<4} | {'Brand':<10} | {'Nama Laptop':<30} | {'Skor':<8} | {'Harga'}")
        print("-" * 80)
        for idx, laptop in enumerate(hasil['data'], 1):
            nama = (laptop.get('name')[:28] + '..') if len(str(laptop.get('name'))) > 28 else laptop.get('name')
            print(f"{idx:<4} | {laptop.get('brand','-'):<10} | {nama:<30} | {laptop.get('similarity_score',0):.4f} | Rp {float(laptop.get('price',0)):,.0f}")
            
    print("="*80 + "\n")

    # Detail TF-IDF dan cosine similarity hanya tampil saat dijalankan via CLI.
    print_debug_report(hasil)

# Jalankan demo lokal jika file dieksekusi langsung.
if __name__ == "__main__":
    main()