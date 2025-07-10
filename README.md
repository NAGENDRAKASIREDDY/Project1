# Project1

This repository contains examples and datasets for practice purposes.

## Hyderabad Firm Scraper

`hyderabad_firm_scraper.py` demonstrates how to collect contact details for
architecture and interior design firms in Hyderabad. The script scrapes listing
pages, stores the results in a Pandas DataFrame and exports them to a PDF using
`FPDF`.

Usage:

```bash
python hyderabad_firm_scraper.py --pages 2 --output firms.pdf
```

The script is intended for educational use. Always check a website's terms of
service before scraping and respect robots.txt guidelines.
