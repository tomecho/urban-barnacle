# Urban-Barnacle
It's a simple OCR project with a 4 step process

1. truncate_pdf.py - cuts out any excess in each page of the pdf, producing a minimal pdf
2. img_pdf_ocr.py - visualizes the truncated pdf and inserts findings into db
3. minimize_pdf.py - reads db and builds a pdf of just the relevant findings
4. verify_current.py - reads db and verifies the entry is still current from the online list
