<!--  -->

# def \_normalize_domain_phrases(self, text: str) -> str:

    #     phrase_patterns = [
    #         # Gaming berat
    #         (r'\b(bermain|main|memainkan)\s+(game|gaming)\s+berat\b', '__GAMING_BERAT__'),
    #         (r'\b(game|gaming)\s+berat\b', '__GAMING_BERAT__'),
    #         (r'\bgaming\s+rata\s+kanan\b', '__GAMING_BERAT__'),

    #         # Gaming ringan / menengah
    #         (r'\b(bermain|main|memainkan)\s+(game|gaming)\s+ringan\b', '__GAMING_RINGAN__'),
    #         (r'\b(game|gaming)\s+ringan\b', '__GAMING_RINGAN__'),
    #         (r'\b(game|gaming)\s+menengah\b', '__GAMING_MENENGAH__'),

    #         # Editing video
    #         (r'\b(edit|editing|mengedit)\s+video\b', '__EDITING_VIDEO__'),

    #         # Render 3D
    #         (r'\b(render|rendering)\s+3d\b', '__RENDER_3D__'),

    #         # Desain grafis
    #         (r'\b(desain|design)\s+grafis\s+berat\b', '__DESAIN_GRAFIS_BERAT__'),
    #         (r'\b(desain|design)\s+grafis\b', '__DESAIN_GRAFIS__'),

    #         # Coding
    #         (r'\b(ngoding|programming|programmer)\b', 'coding programming ngoding'),
    #     ]

    #     for pattern, replacement in phrase_patterns:
    #         text = re.sub(pattern, replacement, text)

    #     phrase_expansions = {
    #         '__GAMING_BERAT__': 'gaming_berat game gaming berat',
    #         '__GAMING_RINGAN__': 'gaming_ringan game gaming ringan',
    #         '__GAMING_MENENGAH__': 'gaming_menengah game gaming menengah',
    #         '__EDITING_VIDEO__': 'editing_video edit editing video',
    #         '__RENDER_3D__': 'render_3d render 3d',
    #         '__DESAIN_GRAFIS_BERAT__': 'desain_grafis_berat desain grafis berat',
    #         '__DESAIN_GRAFIS__': 'desain_grafis desain grafis',
    #     }

    #     for placeholder, expansion in phrase_expansions.items():
    #         text = text.replace(placeholder.lower(), expansion)
    #         text = text.replace(placeholder, expansion)

    #     return text

    # def _preprocess(self, text: str) -> List[str]:
    #     text = str(text).lower()

    #     # Normalisasi frasa domain sebelum tanda baca dibersihkan
    #     text = self._normalize_domain_phrases(text)

    #     # Izinkan underscore agar token seperti gaming_berat tidak hilang
    #     text = re.sub(r'[^a-z0-9_\s]', '', text)

    #     stopwords = {
    #         'dan', 'atau', 'untuk', 'dengan', 'yang', 'di', 'ke', 'dari', 'pada', 'adalah', 'ini', 'itu', 'buat', 'sama', 'juga', 'sih', 'cuma', 'aja', 'nggak', 'gak', 'enggak', 'tidak', 'bukan', 'saya', 'aku', 'kamu', 'dia', 'mereka', 'kita', 'kami', 'halo', 'hai', 'mas', 'mbak', 'bang', 'kak', 'pengen', 'ingin', 'mau', 'beli', 'cari', 'carikan', 'tolong', 'dong', 'lagi', 'pas', 'bisa', 'ada', 'sesuatu', 'kalau', 'kalo', 'biar', 'sudah', 'udah', 'belum', 'sangat', 'paling', 'butuh', 'membutuhkan', 'perlu', 'mengerjakan', 'mengerjain', 'laptop'
    #     }

    #     return [word for word in text.split() if word not in stopwords]

<!-- recommender.py -->

# stopwords = {

        #     'dan', 'atau', 'untuk', 'dengan', 'yang', 'di', 'ke', 'dari', 'pada', 'adalah', 'ini', 'itu',
        #     'buat', 'sama', 'juga', 'sih', 'cuma', 'aja', 'nggak', 'gak', 'enggak', 'tidak', 'bukan',
        #     'saya', 'aku', 'kamu', 'dia', 'mereka', 'kita', 'kami', 'halo', 'hai', 'mas', 'mbak', 'bang', 'kak',
        #     'pengen', 'ingin', 'mau', 'beli', 'cari', 'carikan', 'tolong', 'dong', 'lagi', 'pas', 'bisa',
        #     'ada', 'sesuatu', 'kalau', 'kalo', 'biar', 'sudah', 'udah', 'belum', 'sangat', 'paling'
        # }
