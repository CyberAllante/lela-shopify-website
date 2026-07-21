#!/usr/bin/env python3
"""
Scrape the live inventory from 313carloans.com (a Dealer Car Search site)
and rewrite ../data/inventory.js so the new website shows the real cars.

Usage:
    pip install requests beautifulsoup4
    python3 scrape_inventory.py                  # scrape, keep CDN image URLs
    python3 scrape_inventory.py --download-images  # also save photos locally
    python3 scrape_inventory.py --limit 5        # test run on 5 vehicles

How it works:
  1. Reads /sitemap.xml (Dealer Car Search publishes one) and collects every
     vehicle-detail-page URL (the /vdp/... links). If there is no sitemap it
     falls back to crawling the /newandusedcars listing pages.
  2. Visits each VDP and extracts data, preferring the schema.org JSON-LD
     block Dealer Car Search embeds, then falling back to meta tags and
     visible-text patterns.
  3. Writes ../data/inventory.js in the exact format the site consumes.

Notes:
  - Run this from a normal machine/network (it needs to reach 313carloans.com).
  - Be polite: there is a delay between requests. This is the dealership
    scraping its own data, but there's no reason to hammer the server.
  - Re-run any time the lot changes; commit + push the updated inventory.js
    (or re-upload it to wherever the site is hosted) to publish.
"""

import argparse
import json
import re
import sys
import time
from datetime import date
from pathlib import Path
from urllib.parse import urljoin, urlparse

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    sys.exit("Missing dependencies. Run:  pip install requests beautifulsoup4")

BASE = "https://313carloans.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
}
DELAY_SECONDS = 1.5

REPO_DIR = Path(__file__).resolve().parent.parent
OUTPUT_JS = REPO_DIR / "data" / "inventory.js"
PHOTO_DIR = REPO_DIR / "assets" / "photos"

DEALERSHIP = {
    "name": "Matthew's Stop and Look Auto Sales",
    "legalName": "McQueen Auto, Inc.",
    "phone": "313-891-8000",
    "phoneHref": "tel:+13138918000",
    "address": "8146 E 8 Mile Rd, Detroit, MI 48234",
    "mapsUrl": "https://maps.google.com/?q=8146+E+8+Mile+Rd,+Detroit,+MI+48234",
}

BODY_STYLE_KEYWORDS = {
    "truck": "Truck", "pickup": "Truck",
    "suv": "SUV", "sport utility": "SUV", "crossover": "SUV",
    "van": "Van", "minivan": "Van",
    "coupe": "Coupe", "convertible": "Convertible",
    "hatchback": "Hatchback", "wagon": "Wagon",
    "sedan": "Sedan",
}


def fetch(url):
    """GET a URL with retries and a polite delay."""
    for attempt in range(3):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                time.sleep(DELAY_SECONDS)
                return resp
            print(f"  ! HTTP {resp.status_code} for {url}")
        except requests.RequestException as exc:
            print(f"  ! {exc}")
        time.sleep(2 * (attempt + 1))
    return None


def vdp_urls_from_sitemap():
    resp = fetch(urljoin(BASE, "/sitemap.xml"))
    if not resp:
        return []
    urls = re.findall(r"<loc>\s*(.*?)\s*</loc>", resp.text)
    return sorted({u for u in urls if "/vdp/" in u})


def vdp_urls_from_listing():
    """Fallback: walk /newandusedcars pagination collecting /vdp/ links."""
    found, to_visit, seen_pages = set(), [urljoin(BASE, "/newandusedcars")], set()
    while to_visit:
        page = to_visit.pop(0)
        if page in seen_pages:
            continue
        seen_pages.add(page)
        resp = fetch(page)
        if not resp:
            continue
        soup = BeautifulSoup(resp.text, "html.parser")
        for a in soup.find_all("a", href=True):
            href = urljoin(BASE, a["href"])
            if "/vdp/" in href:
                found.add(href.split("#")[0].split("?")[0])
            # Follow listing pagination links (e.g. ...newandusedcars?page=2)
            elif "newandusedcars" in href and href not in seen_pages and len(seen_pages) < 40:
                to_visit.append(href)
    return sorted(found)


def first_json_ld(soup, wanted_types):
    """Return the first JSON-LD object on the page matching one of wanted_types."""
    for tag in soup.find_all("script", type="application/ld+json"):
        try:
            data = json.loads(tag.string or "")
        except (json.JSONDecodeError, TypeError):
            continue
        items = data if isinstance(data, list) else [data]
        for item in items:
            if isinstance(item, dict) and item.get("@type") in wanted_types:
                return item
    return None


def text_of(soup):
    return re.sub(r"\s+", " ", soup.get_text(" "))


def guess_body_style(*haystacks):
    blob = " ".join(h.lower() for h in haystacks if h)
    for keyword, style in BODY_STYLE_KEYWORDS.items():
        if keyword in blob:
            return style
    return "Sedan"


def parse_vdp(url, html):
    """Extract one vehicle from a VDP. Returns None if it doesn't look like a car."""
    soup = BeautifulSoup(html, "html.parser")
    page_text = text_of(soup)
    ld = first_json_ld(soup, {"Car", "Vehicle", "Product"}) or {}

    # --- Title / year / make / model ---
    title = (
        ld.get("name")
        or (soup.find("meta", property="og:title") or {}).get("content")
        or (soup.title.string if soup.title else "")
        or ""
    ).strip()
    m = re.search(r"\b(19|20)\d{2}\b", title)
    if not m:
        return None
    year = int(m.group(0))
    after_year = title[m.end():].strip()
    parts = after_year.split()
    make = ld.get("brand", {}).get("name") if isinstance(ld.get("brand"), dict) else ld.get("brand")
    make = make or (parts[0] if parts else "")
    model = ld.get("model") or (parts[1] if len(parts) > 1 else "")
    trim = " ".join(parts[2:5]) if len(parts) > 2 else ""
    # Drop marketing tails like "for sale in Detroit MI" from the trim.
    trim = re.split(r"\bfor sale\b|\bin Detroit\b|\|", trim, flags=re.I)[0].strip(" -–")

    # --- Price ---
    price = None
    offers = ld.get("offers") or {}
    if isinstance(offers, dict) and offers.get("price"):
        try:
            price = int(float(str(offers["price"]).replace(",", "")))
        except ValueError:
            pass
    if price is None:
        m = re.search(r"\$\s?([\d,]{4,9})", page_text)
        if m:
            price = int(m.group(1).replace(",", ""))
    if price is None or price < 500:
        price = 0  # shows as "$0" — treat as "Call for price" candidates

    # --- Mileage ---
    mileage = 0
    odo = ld.get("mileageFromOdometer")
    if isinstance(odo, dict) and odo.get("value"):
        mileage = int(float(str(odo["value"]).replace(",", "")))
    if not mileage:
        m = re.search(r"([\d,]{4,8})\s*(?:miles|mi\b)", page_text, re.I)
        if m:
            mileage = int(m.group(1).replace(",", ""))

    # --- VIN / stock ---
    vin = ld.get("vehicleIdentificationNumber") or ""
    if not vin:
        m = re.search(r"\bVIN[:\s#]*([A-HJ-NPR-Z0-9]{17})\b", page_text, re.I)
        vin = m.group(1) if m else ""
    m = re.search(r"\bStock\s*(?:#|No\.?|Number)?[:\s]*([A-Za-z0-9-]{2,12})\b", page_text, re.I)
    stock = m.group(1) if m else ""

    # --- Simple spec fields ---
    def spec(pattern):
        m = re.search(pattern, page_text, re.I)
        return m.group(1).strip() if m else ""

    engine = ld.get("vehicleEngine", {}).get("name", "") if isinstance(ld.get("vehicleEngine"), dict) else ""
    engine = engine or spec(r"Engine[:\s]+([^:|]{3,40}?)(?:\s{2,}|Transmission|Drive|$)")
    transmission = ld.get("vehicleTransmission") or spec(r"Transmission[:\s]+(\w[\w\s/-]{2,25}?)(?:\s{2,}|Drive|Engine|$)") or "Automatic"
    drivetrain = spec(r"\b(AWD|4WD|4X4|FWD|RWD)\b").upper().replace("4X4", "4WD") or "FWD"
    ext_color = ld.get("color") or spec(r"Exterior(?:\s*Color)?[:\s]+([A-Za-z ]{3,25}?)(?:\s{2,}|Interior|$)")
    int_color = spec(r"Interior(?:\s*Color)?[:\s]+([A-Za-z ]{3,25}?)(?:\s{2,}|Engine|$)")

    # --- Images (Dealer Car Search serves from imagescdn.dealercarsearch.com) ---
    images = []
    og = soup.find("meta", property="og:image")
    if og and og.get("content"):
        images.append(og["content"])
    for img in soup.find_all("img", src=True):
        src = urljoin(BASE, img["src"])
        if "dealercarsearch.com/Media" in src and src not in images:
            images.append(src)
    images = images[:20]

    # --- Description ---
    desc_meta = soup.find("meta", attrs={"name": "description"})
    description = ld.get("description") or (desc_meta.get("content", "") if desc_meta else "")
    description = re.sub(r"\s+", " ", description).strip()[:600]

    slug = re.sub(r"[^a-z0-9]+", "-", f"{year}-{make}-{model}-{stock or vin[-6:] or ''}".lower()).strip("-")

    return {
        "id": slug or f"vdp-{abs(hash(url)) % 100000}",
        "sourceUrl": url,
        "year": year,
        "make": make,
        "model": model,
        "trim": trim,
        "price": price,
        "mileage": mileage,
        "bodyStyle": guess_body_style(title, page_text[:2000]),
        "exteriorColor": ext_color or "—",
        "interiorColor": int_color or "—",
        "engine": engine or "—",
        "transmission": transmission,
        "drivetrain": drivetrain,
        "fuel": "Gasoline",
        "vin": vin,
        "stock": stock,
        "description": description,
        "features": [],
        "images": images or ["assets/placeholder-sedan.svg"],
        "featured": False,
        "sold": False,
    }


def download_images(vehicles):
    PHOTO_DIR.mkdir(parents=True, exist_ok=True)
    for v in vehicles:
        local = []
        vdir = PHOTO_DIR / v["id"]
        vdir.mkdir(exist_ok=True)
        for i, src in enumerate(v["images"]):
            if not src.startswith("http"):
                local.append(src)
                continue
            ext = Path(urlparse(src).path).suffix or ".jpg"
            dest = vdir / f"{i:02d}{ext}"
            if not dest.exists():
                resp = fetch(src)
                if not resp:
                    continue
                dest.write_bytes(resp.content)
            local.append(f"assets/photos/{v['id']}/{dest.name}")
        if local:
            v["images"] = local


def write_inventory_js(vehicles):
    # Feature the 6 newest/priciest so the homepage has content.
    for v in sorted(vehicles, key=lambda x: (x["year"], x["price"]), reverse=True)[:6]:
        v["featured"] = True
    payload = {
        "updated": date.today().isoformat(),
        "dealership": DEALERSHIP,
        "vehicles": vehicles,
    }
    OUTPUT_JS.write_text(
        "/** AUTO-GENERATED by scraper/scrape_inventory.py — edit by hand only if "
        "you aren't going to re-run the scraper. */\n"
        "window.INVENTORY = " + json.dumps(payload, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"\nWrote {len(vehicles)} vehicles to {OUTPUT_JS}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=0, help="only scrape the first N vehicles (testing)")
    ap.add_argument("--download-images", action="store_true", help="save photos into assets/photos/")
    args = ap.parse_args()

    print("Collecting vehicle page URLs…")
    urls = vdp_urls_from_sitemap()
    if urls:
        print(f"  sitemap.xml: {len(urls)} vehicle pages")
    else:
        print("  no sitemap — crawling /newandusedcars instead")
        urls = vdp_urls_from_listing()
        print(f"  listing crawl: {len(urls)} vehicle pages")
    if not urls:
        sys.exit("No vehicle pages found. The site structure may have changed — "
                 "open the site in a browser and check where inventory links point.")

    if args.limit:
        urls = urls[: args.limit]

    vehicles, seen = [], set()
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] {url}")
        resp = fetch(url)
        if not resp:
            continue
        v = parse_vdp(url, resp.text)
        if not v:
            print("  ! skipped (couldn't parse a vehicle)")
            continue
        key = v["vin"] or v["id"]
        if key in seen:
            continue
        seen.add(key)
        vehicles.append(v)
        print(f"  ✓ {v['year']} {v['make']} {v['model']} — ${v['price']:,} / {v['mileage']:,} mi / {len(v['images'])} photos")

    if not vehicles:
        sys.exit("Parsed zero vehicles — the page structure may have changed.")

    if args.download_images:
        print("\nDownloading photos…")
        download_images(vehicles)

    write_inventory_js(vehicles)
    print("Done. Open ../index.html to see the site with real inventory.")


if __name__ == "__main__":
    main()
