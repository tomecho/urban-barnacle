# python script.py inputfilename.pdf [all|numPages] outputfilename.pdf

from PyPDF2 import PdfFileWriter, PdfFileReader
from os import sys

with open(sys.argv[1],'rb') as input_stream:
    in_pdf = PdfFileReader(input_stream)
    out_pdf = PdfFileWriter()

    max_page = in_pdf.numPages if sys.argv[2] == 'all' else int(sys.argv[2])

    for i in range(0,max_page):
        page = in_pdf.getPage(i)
        if False:
            # crop header and footer
            page.cropBox.lowerLeft = (page.mediaBox.getLowerLeft_x(), page.mediaBox.getLowerLeft_y()+10) # plus 10 to cut off bottom page numbers
            page.cropBox.upperRight = (page.mediaBox.getUpperRight_x(), page.mediaBox.getUpperRight_y()-35)
        else:
            # crop everything except the property id and cash cols
            page.cropBox.lowerLeft = (page.mediaBox.getLowerLeft_x()+454, page.mediaBox.getLowerLeft_y()+10) # plus 10 to cut off bottom page numbers
            page.cropBox.upperRight = (page.mediaBox.getUpperRight_x()-55, page.mediaBox.getUpperRight_y()-35)

        out_pdf.addPage(page)

    print 'beging write output'
    with open(sys.argv[3], 'wb') as outputStream : out_pdf.write(outputStream)
