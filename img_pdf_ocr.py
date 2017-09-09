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

ignore_str = ['PROPERTY', 'ID CASH']
final_text = []

# for each image of page
for img in req_image:
    # lnBx should be a single column on a single page
    lnBxs = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang,
            builder=pyocr.builders.LineBoxBuilder()
            )
    for lnBx in lnBxs:
        # for each line box
        # break down into word boxes, we only have two cols
        # so we can try to guess which col the word is from by looking at the position
        # 2125 seems to be just about the bottom left x position for the cash col
        # x >= 2124 is a cash, x < 2125 is a property id

    # suspectCol = filter(lambda col: col == lnBx[0].content,col_names)
    # if suspectCol.size < 1:
        # #couldnt find col
        # next
    # elif suspectCol.size > 1:
        # # too many suspect cols we cant really classify this
        # next
    # # else exactly one which is great
    #for i in range(0, len(lnBx)): final_text.append(lnBx[i].content + '\n')

f = open('output_file', 'w')
for s in final_text:
    f.write(s.encode('UTF-8'))
