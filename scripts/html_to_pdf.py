import asyncio
from pyppeteer import launch
import os
import sys

async def html_to_pdf(html_path, pdf_path):
    browser = await launch(args=['--no-sandbox'])
    page = await browser.newPage()
    # Use absolute path for file:// URL
    abs_html_path = os.path.abspath(html_path)
    await page.goto(f'file://{abs_html_path}', {'waitUntil': 'networkidle0'})
    await page.pdf({
        'path': pdf_path,
        'format': 'A4',
        'printBackground': True,
        'margin': {'top': '20px', 'right': '20px', 'bottom': '20px', 'left': '20px'}
    })
    await browser.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 html_to_pdf.py input.html output.pdf")
        sys.exit(1)
    asyncio.run(html_to_pdf(sys.argv[1], sys.argv[2]))
