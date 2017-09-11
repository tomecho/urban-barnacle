from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
from os import sys
import os
import sqlite3
import datetime
from PyPDF2 import PdfFileWriter, PdfFileReader

# define some vars ill be useing latter
ignore_str = ['PROPERTY', 'ID','ID CASH']
tool = pyocr.get_available_tools()[0]
lang = filter(lambda l: str(l) == 'eng', tool.get_available_languages())[0]
tbl_name = '[' + sys.argv[1] + ' ' + datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S') + ']'
tmp_pdf_filename = '.work.pdf' # represents a workable part of the pdf
page_chunk_size = 80 # number of pages to work at once

def create_table():
    conn = sqlite3.connect('output.db')
    conn.execute('CREATE TABLE '+ tbl_name +' (property_id int, cash real, source_location text);')
    conn.execute('CREATE INDEX `index_cash_' + tbl_name + '` ON ' + tbl_name + ' (cash);')
    conn.commit()
    conn.close()

def write_sqlite(data):
    conn = sqlite3.connect('output.db')
    for part in data:
        conn.execute('INSERT INTO ' + tbl_name + ' VALUES(?,?,?);', map(lambda s: s.encode('UTF-8'),part))
    conn.commit()
    conn.close()

def convert_pdf_to_image(fn):
    #print 'Converting PDF to image'
    return Image(filename=fn, resolution=300).convert('jpeg')

def print_progress_str(action,pct):
    pct = pct * 100 # should start out as 0 - 1 float
    print action + ' ' + str(pct) + '% [' + (u"\u2588"*int(pct)) + (' ' * (100-int(pct))) + ']' + ' ' * 20 +'\r',

def split_pages(image_jpeg):
    req_images = []
    for img_index in range(0,len(image_jpeg.sequence)):
        img = image_jpeg.sequence[img_index]
        #print_progress_str('Splitting pages', float(img_index+1)/len(image_jpeg.sequence))
        img_page = Image(image=img)
        req_images.append(img_page.make_blob('jpeg'))
    return req_images

def process_page(img_index, req_images):
    img = req_images[img_index]
    # single row/line of that page
    lnBxs = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang,
            builder=pyocr.builders.LineBoxBuilder()
            )

    data = [] # list of tuples (property id, cash value, record source location)
    for lnBx_index in range(0,len(lnBxs)):
        lnBx = lnBxs[lnBx_index]
        # for each line box in page
        property_id = ''
        cash = ''
        source_location = ':'.join([sys.argv[1], str(img_index+1), str(lnBx_index+1)])
        for Bx in lnBx.word_boxes:
            if Bx.content in ignore_str: break # next line this is a header
            # break down into word boxes, we only have two cols
            # so we can try to guess which col the word is from by looking at the position
            # 2125 seems to be just about the bottom left x position for the cash col
            # x >= 2100 is a cash, x < 2100 is a property id
            if Bx.position[0][0] >= 2100: # position lower left x
                cash += Bx.content
            else: # x < 2100
                property_id += Bx.content
        if property_id and cash: # only add line if we have something
            data.append((property_id,cash,source_location)) # append final find to data
    # at the end of a page we write to db that way data doesnt get too big
    write_sqlite(data)

# start and end are zero indexed inclusive page range
def chunk_pdf(in_pdf, start_page, end_page): # gets 100 pages out of the pdf and writes it to temp pdf
    out_pdf = PdfFileWriter()
    for i in range(start_page,end_page+1):
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

    with open(tmp_pdf_filename, 'wb') as outputStream : out_pdf.write(outputStream) # overwrites every time

print 'Begin process %s' % sys.argv[1]
create_table() # start out by creating the table

# this can get awfully resource heavy, we need to get one a few pages at a time from the doc
with open(sys.argv[1],'rb') as _file:
    in_pdf = PdfFileReader(_file)
    start_index = 0 # start chunk page index
    end_index = 0 # end chunk
    while end_index+1 < in_pdf.numPages:
        print_progress_str('Status', (end_index/(in_pdf.numPages-1.0))) # -1.0 forces float math and offset for index at 0
        end_index = start_index + page_chunk_size if start_index + page_chunk_size < in_pdf.numPages else in_pdf.numPages-1
        chunk_pdf(in_pdf, start_index, end_index) # writes to temp_pdf_filename
        start_index = end_index+1 # page after last page we included

        image_jpeg = convert_pdf_to_image(tmp_pdf_filename)
        req_images = split_pages(image_jpeg)

        # for each image of page
        for img_index in range(0, len(req_images)):
            #print_progress_str('Processing pages', float(img_index+1)/len(req_images))
            process_page(img_index,req_images)
print_progress_str('Status', 1.0) # show that it finished
print '' # finish off progress bar

os.remove(tmp_pdf_filename) # remove temp pdf
