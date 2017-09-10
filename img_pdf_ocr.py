from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
from os import sys

tool = pyocr.get_available_tools()[0]
lang = filter(lambda l: str(l) == 'eng', tool.get_available_languages())[0]

req_image = []

image_pdf = Image(filename=sys.argv[1], resolution=300)
image_jpeg = image_pdf.convert('jpeg')

for img in image_jpeg.sequence:
    img_page = Image(image=img)
    req_image.append(img_page.make_blob('jpeg'))

ignore_str = ['PROPERTY', 'ID','ID CASH']
data = [] # list of tuples (property id, cash value, record source location)

# for each image of page
for img_index in range(0, len(req_image)):
    img = req_image[img_index]
    # lnBx should be a single column on a single page
    lnBxs = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang,
            builder=pyocr.builders.LineBoxBuilder()
            )
    for lnBx_index in range(0,len(lnBxs)):
        lnBx = lnBxs[lnBx_index]
        # for each line box
        property_id = ''
        cash = ''
        import pdb; pdb.set_trace
        source_location = ':'.join([sys.argv[1] + str(img_index+1) + str(lnBx_index+1)])
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

f = open('output_file.csv', 'w')
f.write('property_id,cash,source_location(file:page:line)\n')
for data_pair in data:
    f.write(','.join([data_pair[0].encode('UTF-8'),data_pair[1].encode('UTF-8'), data_pair[2].encode('UTF-8')]))
    f.write('\n')
