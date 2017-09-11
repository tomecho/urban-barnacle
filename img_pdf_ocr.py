from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
from os import sys
import sqlite3
import datetime

# define some vars ill be useing latter
ignore_str = ['PROPERTY', 'ID','ID CASH']
tool = pyocr.get_available_tools()[0]
lang = filter(lambda l: str(l) == 'eng', tool.get_available_languages())[0]
tbl_name = '[' + sys.argv[1] + ' ' + datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S') + ']'

def write_csv(data):
    f = open('output_file.csv', 'w')
    f.write('property_id,cash,source_location(file:page:line)\n')
    for data_pair in data:
        f.write(','.join([data_pair[0].encode('UTF-8'),data_pair[1].encode('UTF-8'), data_pair[2].encode('UTF-8')]))
        f.write('\n')

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

def convert_pdf_to_image():
    print 'Converting PDF to image'
    return Image(filename=sys.argv[1], resolution=300).convert('jpeg')

def print_progress_str(action,pct):
    pct = pct * 100 # should start out as 0 - 1 float
    print(action + ' ' + str(pct) + '% [' + (u"\u2588"*int(pct)) + (' ' * (100-int(pct))) + ']\r'),

def split_pages(image_jpeg):
    req_images = []
    for img_index in range(0,len(image_jpeg.sequence)):
        img = image_jpeg.sequence[img_index]
        print_progress_str('Splitting pages', float(img_index+1)/len(image_jpeg.sequence))
        img_page = Image(image=img)
        req_images.append(img_page.make_blob('jpeg'))
    print '' # finish off with a \n to finish progress bar
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

print 'Begin process %s' % sys.argv[1]
image_jpeg = convert_pdf_to_image()
req_images = split_pages(image_jpeg)
create_table()

# for each image of page
for img_index in range(0, len(req_images)):
    print_progress_str('Processing pages', float(img_index+1)/len(req_images))
    process_page(img_index,req_images)

print '' # finish off progress bar
