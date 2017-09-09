from PyPDF2 import PdfFileWriter, PdfFileReader
from os import sys
in_pdf = PdfFileReader(open(sys.argv[1],'rb'))
out_pdf = PdfFileWriter()
for i in range(0,int(sys.argv[2])):
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

with open(sys.argv[3], 'wb') as outputStream : out_pdf.write(outputStream)
