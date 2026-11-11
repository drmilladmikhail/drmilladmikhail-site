"""Rebuild the existing printable gift from its reviewed HTML source."""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright
from pypdf import PdfReader, PdfWriter

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / "gifts/hodoody-fil-hob-7k2m.pdf"
    temporary = output.with_suffix(".updated.pdf")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page()
        page.goto((ROOT / "tools/gifts/boundaries.html").as_uri())
        page.evaluate("document.fonts.ready")
        page.pdf(path=str(temporary), format="A4", print_background=True,
                 prefer_css_page_size=True)
        browser.close()
    writer = PdfWriter(clone_from=PdfReader(temporary))
    writer.add_metadata({"/Title": "حدودي في الحب — ورقة تمرين",
                         "/Author": "Perplexity Computer"})
    metadata = temporary.with_suffix(".metadata.pdf")
    writer.write(metadata)
    os.replace(metadata, output)
    temporary.unlink()
    print("Updated", output.relative_to(ROOT))


if __name__ == "__main__":
    main()
