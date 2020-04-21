from selenium import webdriver
from sys import argv
from selenium.webdriver.firefox.options import Options
import sqlite3
import datetime
import sys
import time

def choose_table():
    with sqlite3.connect('output.db') as conn:
        cursor = conn.execute("select name from sqlite_master where type = 'table'")
        rows = cursor.fetchall()
    tbl_names = map(lambda x:
        x[0]
    , rows)
    tbl_index = raw_input('select a table to translate (by zero based index):\n' + reduce(lambda x,y: '{}\n{}'.format(x, y) + '\n', tbl_names))
    return tbl_names[int(tbl_index)]

def create_table():
    with sqlite3.connect('output.db') as conn:
        conn.execute('''CREATE TABLE [{}] (property_id int, cash real, source_location text, name text, 
                address_street text, address_city text, address_state text, address_zip text);'''.format(tbl_name))
        conn.commit()

def write_data(result_array):
    if (len(result_array) is not 8):
        print 'cannot write partial data to db ', result_array
    with sqlite3.connect('output.db') as conn:
        conn.execute('INSERT INTO [' + tbl_name + '](property_id, cash, source_location, name, address_street, address_city, address_state, address_zip) VALUES(?,?,?,?,?,?,?,?);', result_array)
        conn.commit()

def read_ocr_table(tbl_name):
    print 'reading from database {}'.format(tbl_name)
    with sqlite3.connect('output.db') as conn:
        cursor = conn.execute("select property_id, cash, better_source_location from [{}] where cast(cash as real) > 1000".format(tbl_name))
        return cursor.fetchall()

def throttle_translation(time_diff, request_count = 1):
    actual_rate = time_diff / request_count # time over count
    # actual rate was less than target rate then sleep
    if (actual_rate < target_rate):
        seconds_to_sleep = ((target_rate / request_count) - actual_rate) * request_count
        # print 'going too fast, sleeping for ', seconds_to_sleep
        if (seconds_to_sleep > 0):
            time.sleep(seconds_to_sleep)

def print_progress_str(action,pct):
    pct = pct * 100 # should start out as 0 - 1 float
    print action + ' ' + str(pct) + '% [' + (u"\u2588"*int(pct)) + (' ' * (100-int(pct))) + ']' + ' ' * 20 +'\r',

def translate_property(web, ocr_property):
    property_id_field = web.find_element_by_id('PropertyID')
    property_id_field.clear()
    property_id_field.send_keys(ocr_property[0])
    web.find_element_by_xpath("//input[@name='Submit']").click()

    search_result_rows = web.find_elements_by_xpath("(//form[@action='UP_Claim.asp']//tbody)[1]/tr[position() > 1]")
    for row in search_result_rows:
        entry = [
            ocr_property[0], # property id
            ocr_property[1], # cash
            ocr_property[2], # source location
            row.find_element_by_xpath('td[3]').text, # name
            row.find_element_by_xpath('td[4]').text, # street 
            row.find_element_by_xpath('td[5]').text, # city
            row.find_element_by_xpath('td[6]').text, # state
            row.find_element_by_xpath('td[7]').text, # zip
        ] 
        write_data(entry)

def translate_properties(web, ocr_properties):
    i = 0
    property_count = len(ocr_properties)
    for ocr_property in ocr_properties:
        i = i + 1
        print_progress_str('translating {} / {}'.format(i, property_count), float(i) / property_count)
        start_time = time.time()
        try:
            translate_property(web, ocr_property)
        except Exception as e:
            # something went wrong
            print 'skipping propertyId ', ocr_property[0], str(e)
            web.get(argv[1])

        end_time = time.time()
        throttle_translation(end_time - start_time, 1)

target_rate = 3 # 3 seconds a request 
ocr_tbl_name = choose_table()
ocr_properties = read_ocr_table(ocr_tbl_name)
tbl_name = '{} properties translated {}'.format(ocr_tbl_name, datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S'))
create_table()

# set up the browser
options = Options()
options.set_headless(headless=True)

with webdriver.Firefox(firefox_options=options) as web:
    web.get(argv[1])
    translate_properties(web, ocr_properties)
