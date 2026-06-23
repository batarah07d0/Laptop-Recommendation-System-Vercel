import argparse
import asyncio
import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urljoin

import aiohttp
import pandas as pd
from aiohttp import ClientTimeout
from bs4 import BeautifulSoup

LOG = logging.getLogger("extract_og_images")


async def fetch_html(session: aiohttp.ClientSession, url: str, timeout: int = 10) -> Optional[str]:
    try:
        async with session.get(url, timeout=ClientTimeout(total=timeout)) as resp:
            resp.raise_for_status()
            text = await resp.text(errors="ignore")
            return text
    except Exception as e:
        LOG.debug("fetch_html failed for %s: %s", url, e)
        return None


def extract_og_image(html: str, base_url: str, strict: bool = True) -> Optional[str]:
    """Extract image URL. If strict=True, only use og:image/twitter:image. Otherwise try fallbacks."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Priority 1: og:image (most reliable)
    tag = soup.find("meta", property="og:image")
    if tag and tag.get("content"):
        url = tag["content"].strip()
        if url:
            return urljoin(base_url, url)

    # Priority 2: twitter:image
    tag = soup.find("meta", attrs={"name": "twitter:image"})
    if tag and tag.get("content"):
        url = tag["content"].strip()
        if url:
            return urljoin(base_url, url)

    # If strict mode, stop here and don't use fallbacks
    if strict:
        return None

    # Priority 3: link rel=image_src (fallback)
    link = soup.find("link", rel="image_src")
    if link and link.get("href"):
        url = link["href"].strip()
        if url:
            return urljoin(base_url, url)

    # Priority 4: first img src (fallback)
    img = soup.find("img")
    if img and img.get("src"):
        url = img["src"].strip()
        if url:
            return urljoin(base_url, url)

    return None


# Removed validate_image_url function - no longer needed with simplified extraction


async def process_row(session: aiohttp.ClientSession, url: str, semaphore: asyncio.Semaphore, timeout: int, strict: bool = True) -> Optional[str]:
    if not url or str(url).strip() == "":
        return None

    async with semaphore:
        html = await fetch_html(session, url, timeout=timeout)
        if not html:
            return None
        img_url = extract_og_image(html, url, strict=strict)
        return img_url


async def run(input_path: Path, output_path: Path, concurrency: int = 10, timeout: int = 10, overwrite: bool = False, strict: bool = True):
    df = pd.read_csv(input_path)
    if "Product_URL" not in df.columns:
        raise SystemExit("CSV must contain a 'Product_URL' column")

    if "Image_URL" not in df.columns:
        df["Image_URL"] = ""

    urls = []
    indices = []
    for i, row in df.iterrows():
        p = row.get("Product_URL")
        existing = row.get("Image_URL")
        if not overwrite and existing and str(existing).strip():
            continue
        if p and str(p).strip():
            urls.append(str(p).strip())
            indices.append(i)

    LOG.info("Will process %d URLs (concurrency=%d, strict=%s)", len(urls), concurrency, strict)

    timeout_cfg = ClientTimeout(total=timeout)
    connector = aiohttp.TCPConnector(limit_per_host=concurrency)
    sem = asyncio.Semaphore(concurrency)

    async with aiohttp.ClientSession(timeout=timeout_cfg, connector=connector, headers={"User-Agent": "Mozilla/5.0 (compatible; ExtractOG/1.0)"}) as session:
        tasks = [process_row(session, u, sem, timeout, strict=strict) for u in urls]
        results = await asyncio.gather(*tasks, return_exceptions=False)
        
        for idx, img_url in enumerate(results, 1):
            row_index = indices[idx - 1]
            if img_url:
                LOG.info("Found image for row %d: %s", row_index, img_url)
                df.at[row_index, "Image_URL"] = img_url
            else:
                LOG.debug("No image for row %d", row_index)

            # occasional autosave to avoid data loss
            if idx % 50 == 0:
                df.to_csv(output_path, index=False)

    df.to_csv(output_path, index=False)
    LOG.info("Saved results to %s", output_path)


def main():
    parser = argparse.ArgumentParser(description="Extract og:image into Image_URL column")
    parser.add_argument("--input", "-i", default="datasets/laptop_data_agres.csv")
    parser.add_argument("--output", "-o", default="datasets/laptop_data_agres-with-images.csv")
    parser.add_argument("--concurrency", type=int, default=10)
    parser.add_argument("--timeout", type=int, default=10)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--strict", action="store_true", default=True, help="Only use og:image/twitter:image (default: True)")
    parser.add_argument("--no-strict", dest="strict", action="store_false", help="Allow fallback to other image sources")
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()
    if args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    input_path = Path(args.input)
    output_path = Path(args.output)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    asyncio.run(run(input_path, output_path, concurrency=args.concurrency, timeout=args.timeout, overwrite=args.overwrite, strict=args.strict))


if __name__ == "__main__":
    main()
