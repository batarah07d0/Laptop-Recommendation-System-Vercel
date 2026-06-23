import argparse
import re
from pathlib import Path

import pandas as pd

FIELD_ORDER = [
    "Brand",
    "Tipe",
    "Color",
    "Operating System",
    "Processor",
    "Graphics",
    "RAM",
    "Storage",
    "Main Display Size",
    "Main Display Type",
    "Display Resolution",
    "Camera",
    "Audio",
    "Battery",
    "Connectivity",
    "Ports",
]

FIELD_ALIASES = {
    "Brand": ["Brand"],
    "Tipe": ["Tipe", "Type", "Model", "Series"],
    "Color": ["Color", "Warna"],
    "Operating System": ["Operating System", "OS"],
    "Processor": ["Processor", "CPU"],
    "Graphics": ["Graphics", "GPU"],
    "RAM": ["RAM"],
    "Storage": ["Storage", "Penyimpanan"],
    "Main Display Size": ["Main Display Size", "Display Size", "Screen Size"],
    "Main Display Type": ["Main Display Type", "Display Type", "Panel", "Screen Type"],
    "Display Resolution": ["Display Resolution", "Resolution", "Resolusi"],
    "Camera": ["Camera", "Kamera"],
    "Audio": ["Audio", "Speaker"],
    "Battery": ["Battery", "Baterai"],
    "Connectivity": ["Connectivity", "Konektivitas"],
    "Ports": ["Ports", "Port"],
}

ALIAS_TO_FIELD = {
    alias.lower(): field_name
    for field_name, aliases in FIELD_ALIASES.items()
    for alias in aliases
}


# =====================================================
# HELPER
# =====================================================

def normalize_whitespace(text):

    return re.sub(
        r"\s+",
        " ",
        str(text)
    ).strip()


# =====================================================
# PARSE DESCRIPTION
# =====================================================

def parse_labeled_fields(text):

    if not text:
        return {}

    pattern = re.compile(
        r"(?i)(Brand|Tipe|Type|Model|Series|Color|Warna|Operating System|OS|Processor|CPU|Graphics|GPU|RAM|Storage|Penyimpanan|Main Display Size|Display Size|Screen Size|Main Display Type|Display Type|Panel|Screen Type|Display Resolution|Resolution|Resolusi|Camera|Kamera|Audio|Speaker|Battery|Baterai|Connectivity|Konektivitas|Ports|Port)\s*:"
    )

    matches = list(pattern.finditer(text))

    if not matches:
        return {}

    fields = {}

    for idx, match in enumerate(matches):

        alias = match.group(1).lower()

        field_name = ALIAS_TO_FIELD.get(alias)

        if not field_name:
            continue

        start = match.end()

        end = (
            matches[idx + 1].start()
            if idx + 1 < len(matches)
            else len(text)
        )

        value = normalize_whitespace(
            text[start:end]
        )

        if value:
            fields[field_name] = value

    return fields


# =====================================================
# FALLBACK
# =====================================================

def fallback_value(row, field_name):

    mapping = {
        "Brand": "Brand",
        "Tipe": "Nama_Display",
        "Operating System": "Sistem_Operasi",
        "Processor": "CPU",
        "Graphics": "GPU",
        "RAM": "RAM",
        "Storage": "Penyimpanan",
        "Main Display Size": "Ukuran_Layar",
        "Main Display Type": "Tipe_Panel_Layar",
        "Display Resolution": "Resolusi_Layar"
    }

    col = mapping.get(field_name)

    if col:
        return row.get(col, "")

    return ""


# =====================================================
# BUILD DESCRIPTION
# =====================================================

def build_description(row):

    source_text = str(
        row.get("Deskripsi", "")
    )

    parsed_fields = parse_labeled_fields(
        source_text
    )

    parts = []

    for field_name in FIELD_ORDER:

        value = parsed_fields.get(
            field_name
        )

        if not value:

            value = fallback_value(
                row,
                field_name
            )

        if value:

            parts.append(
                f"{field_name}: {normalize_whitespace(value)}"
            )

    return " | ".join(parts)


# =====================================================
# TRANSFORM
# =====================================================

def transform_excel(
    input_path,
    output_path
):

    df = pd.read_excel(
        input_path
    )

    if "Deskripsi" not in df.columns:

        raise ValueError(
            "Kolom Deskripsi tidak ditemukan."
        )

    df["Deskripsi"] = df.apply(
        build_description,
        axis=1
    )

    df.to_excel(
        output_path,
        index=False
    )

    print(
        f"Deskripsi berhasil diformat: {output_path}"
    )


# =====================================================
# MAIN
# =====================================================

def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "input",
        nargs="?",
        default="datasets/laptop_data_agres.xlsx"
    )

    parser.add_argument(
        "--output"
    )

    parser.add_argument(
        "--in-place",
        action="store_true"
    )

    args = parser.parse_args()

    input_path = Path(
        args.input
    )

    if args.in_place:

        output_path = input_path

    elif args.output:

        output_path = Path(
            args.output
        )

    else:

        output_path = input_path.with_name(
            f"{input_path.stem}_formatted.xlsx"
        )

    transform_excel(
        input_path,
        output_path
    )


if __name__ == "__main__":
    main()