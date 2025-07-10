import requests
from bs4 import BeautifulSoup
import pandas as pd
from fpdf import FPDF
import re
import time

HEADERS = {"User-Agent": "Mozilla/5.0"}


def fetch_page(url):
    """Return HTML content of a page or an empty string on failure."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        print(f"Failed to fetch {url}: {exc}")
        return ""


def extract_firm_data(html):
    """Generic extraction of firm details from listing HTML."""
    soup = BeautifulSoup(html, "html.parser")
    firms = []

    for entry in soup.find_all("div", class_=re.compile("listing|card|result")):
        text = entry.get_text(" ", strip=True)
        name_tag = entry.find(["h1", "h2", "h3"]) or entry.find("a", class_=re.compile("name"))
        name = name_tag.get_text(strip=True) if name_tag else ""
        email = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
        phone = re.search(r"\+?\d[\d\s-]{8,}\d", text)
        address_tag = entry.find("p", class_=re.compile("addr"))
        desc_tag = entry.find("p", class_=re.compile("desc"))
        website_tag = entry.find("a", href=re.compile("http"))

        firms.append({
            "Name": name,
            "Email": email.group(0) if email else "",
            "Phone": phone.group(0) if phone else "",
            "Address": address_tag.get_text(strip=True) if address_tag else "",
            "Website": website_tag["href"] if website_tag else "",
            "Category": "Architecture / Interior Design",
            "Description": desc_tag.get_text(strip=True) if desc_tag else "",
        })

    return firms


def scrape_site(base_url, start_page=1, max_pages=5, page_param="{page}"):
    """Scrape a paginated listing site."""
    collected = []
    for page in range(start_page, start_page + max_pages):
        url = base_url.format(page=page)
        html = fetch_page(url)
        if not html:
            break
        data = extract_firm_data(html)
        if not data:
            break
        collected.extend(data)
        time.sleep(1)
    return collected


def save_to_pdf(df, filename="hyderabad_firms.pdf"):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 10, "Hyderabad Architecture & Interior Design Firms", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", size=10)

    for idx, row in df.iterrows():
        pdf.multi_cell(0, 8, txt=f"""
{idx + 1}. {row['Name']}
Address: {row['Address']}
Email: {row['Email']}
Phone: {row['Phone']}
Website: {row['Website']}
Category: {row['Category']}
Description: {row['Description']}
""")
        pdf.ln(2)

    pdf.output(filename)


if __name__ == "__main__":
    sites = {
        "JustDial": "https://www.justdial.com/Hyderabad/Architects/page-{page}",
        "Sulekha": "https://www.sulekha.com/interior-designers-decorators/hyderabad?page={page}",
        "Houzz": "https://www.houzz.in/professionals/interior-designers-and-decorators/c/Hyderabadi/p/{page}",
    }

    all_data = []
    for site, url in sites.items():
        print(f"Scraping {site}...")
        all_data.extend(scrape_site(url))

    df = pd.DataFrame(all_data).drop_duplicates(subset=["Name", "Phone", "Email"])
    save_to_pdf(df)
