# Project1

This repository contains examples and datasets for practice purposes.

## Hyderabad Firm Scraper

`hyderabad_firm_scraper.py` shows how to gather contact information for architecture and interior design firms in Hyderabad, Telangana, from listing sites such as JustDial, Sulekha and Houzz. The script uses `requests` and `BeautifulSoup` to parse listings, stores the results in a Pandas DataFrame and exports them to a PDF via `FPDF`.

It demonstrates pagination handling and removes duplicate entries before saving the PDF output.
