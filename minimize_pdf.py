from PyPDF2 import PdfFileWriter, PdfFileReader
from os import sys

def read_pages():
    with open(sys.argv[1], 'r') as csv_file:
        return set(map(lambda x: int(x.split(',')[-1].split(':')[1]), csv_file.readlines()[1:]))
def extract_pages(pages):
    out_pdf = PdfFileWriter()
    with open(sys.argv[2], 'rb') as pdf_file:
        in_pdf = PdfFileReader(pdf_file)
        for p in pages: out_pdf.addPage(in_pdf.getPage(p-1))
    with open(sys.argv[3], 'wb') as pdf_file:
        out_pdf.write(pdf_file)


if len(sys.argv) != 4:
    print 'python2 minimize_pdf.py {file.csv} {in_file.pdf} {out_file.pdf}'
read_pages()
extract_pages()
