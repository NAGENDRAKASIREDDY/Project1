"""Hyderabad firm scraper (educational sample).

This script demonstrates basic web scraping of listing sites to collect
contact details of architecture and interior design firms.
It outputs the collected information in a PDF.
Use responsibly and check each website's terms of service before scraping.
"""

import argparse
import re
import time
from typing import List

import pandas as pd
import requests
from bs4 import BeautifulSoup
from fpdf import FPDF

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_page(url: str) -> str:
    """Return HTML content of ``url`` or an empty string on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:  # pragma: no cover - network failures
        print(f"Failed to fetch {url}: {exc}")
        return ""


def extract_firm_data(html: str) -> List[dict]:
    """Extract firm information from listing page HTML."""
    soup = BeautifulSoup(html, "html.parser")
    firms = []

    for entry in soup.find_all("div", class_=re.compile("listing|card|result")):
        text = entry.get_text(" ", strip=True)
        name_tag = entry.find(["h1", "h2", "h3"]) or entry.find(
            "a", class_=re.compile("name")
        )
        name = name_tag.get_text(strip=True) if name_tag else ""
        email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone = re.search(r"\+?\d[\d\s-]{8,}\d", text)
        address_tag = entry.find("p", class_=re.compile("addr"))
        desc_tag = entry.find("p", class_=re.compile("desc"))
        website_tag = entry.find("a", href=re.compile("http"))

        firms.append(
            {
                "Name": name,
                "Email": email.group(0) if email else "",
                "Phone": phone.group(0) if phone else "",
                "Address": address_tag.get_text(strip=True) if address_tag else "",
                "Website": website_tag["href"] if website_tag else "",
                "Category": "Architecture / Interior Design",
                "Description": desc_tag.get_text(strip=True) if desc_tag else "",
            }
        )

    return firms


def scrape_site(base_url: str, pages: int) -> List[dict]:
    """Scrape multiple pages of a listing site."""
    collected = []
    for page_num in range(1, pages + 1):
        url = base_url.format(page=page_num)
        html = fetch_page(url)
        if not html:
            break
        page_firms = extract_firm_data(html)
        if not page_firms:
            break
        collected.extend(page_firms)
        time.sleep(1)
    return collected


def save_to_pdf(df: pd.DataFrame, filename: str = "hyderabad_firms.pdf") -> None:
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 10, "Hyderabad Architecture & Interior Design Firms", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)

    for idx, row in df.iterrows():
        pdf.multi_cell(
            0,
            8,
            txt=(
                f"{idx + 1}. {row['Name']}\n"
                f"Address: {row['Address']}\n"
                f"Email: {row['Email']}\n"
                f"Phone: {row['Phone']}\n"
                f"Website: {row['Website']}\n"
                f"Category: {row['Category']}\n"
                f"Description: {row['Description']}"
            ),
        )
        pdf.ln(2)

    pdf.output(filename)


def main() -> None:
    parser = argparse.ArgumentParser(description="Scrape Hyderabad firm listings")
    parser.add_argument(
        "--pages", type=int, default=3, help="number of pages to scrape per site"
    )
    parser.add_argument(
        "--output", default="hyderabad_firms.pdf", help="output PDF filename"
    )
    args = parser.parse_args()

    sites = {
        "JustDial": "https://www.justdial.com/Hyderabad/Architects/page-{page}",
        "Sulekha": "https://www.sulekha.com/interior-designers-decorators/hyderabad?page={page}",
        "Houzz": "https://www.houzz.in/professionals/interior-designers-and-decorators/c/Hyderabadi/p/{page}",
    }

    all_data = []
    for site, url in sites.items():
        print(f"Scraping {site}...")
        all_data.extend(scrape_site(url, args.pages))

    df = pd.DataFrame(all_data).drop_duplicates(subset=["Name", "Phone", "Email"])
    if not df.empty:
        save_to_pdf(df, args.output)
        print(f"Saved {len(df)} records to {args.output}")
    else:
        print("No data scraped.")


if __name__ == "__main__":
    main()
