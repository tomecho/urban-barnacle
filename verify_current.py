from selenium import webdriver
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
        conn.execute('''CREATE TABLE [{}] (property_id int primary key, cash real, source_location text, name text, 
                address_street text, address_city text, address_state text, address_zip text);'''.format(tbl_name))
        conn.commit()

def write_data(result_array):
    with sqlite3.connect('output.db') as conn:
        conn.execute('INSERT INTO [' + tbl_name + '] VALUES(?,?,?,?,?,?,?,?);', result_array)
        conn.commit()

def read_ocr_table(tbl_name):
    print 'reading from database'
    with sqlite3.connect('output.db') as conn:
        cursor = conn.execute("select property_id, cash, source_location from [{}] where cast(cash as real) > 10000 order by cash desc".format(tbl_name))
        return cursor.fetchall()
    print 'finished reading from database'

def throttle_translation(time_diff, request_count = 1):
    actual_rate = time_diff / request_count # time over count
    # actual rate was greater than target rate then sleep
    if (actual_rate > target_rate):
        seconds_to_sleep = ((target_rate / request_count) - actual_rate) * request_count
        print 'going too fast, sleeping for ', seconds_to_sleep
        time.sleep(seconds_to_sleep)

def translate_property(web, ocr_property):
    property_id_field = web.find_element_by_id('PropertyID')
    property_id_field.clear()
    property_id_field.send_keys(ocr_property[0])
    web.find_element_by_xpath("//input[@name='Submit']").click()

    search_result_rows = web.find_elements_by_xpath("(//form[@action='UP_Claim.asp']//tbody)[1]/tr[position() > 1]")
    result_array = map(
        lambda row:
        [
            ocr_property[0], # property id
            ocr_property[1], # cash
            ocr_property[2], # source location
            row.find_element_by_xpath('td[3]').text, # name
            row.find_element_by_xpath('td[4]').text, # street 
            row.find_element_by_xpath('td[5]').text, # city
            row.find_element_by_xpath('td[6]').text, # state
            row.find_element_by_xpath('td[7]').text, # zip
        ], 
        search_result_rows
    )
    write_data(result_array)

def translate_properties(web, ocr_properties):
    i = 0
    property_count = len(ocr_properties)
    for ocr_property in ocr_properties:
        i = i + 1
        print 'translating {} / {}'.format(i, property_count)
        start_time = time.time()
        try:
            translate_property(web, ocr_property)
        except:
            # something went wrong
            print 'something went wrong reloading page and tryig again'
            import pdb; pdb.set_trace()
            web.get('http://ctbiglist.com')
            translate_property(web, ocr_property)

        end_time = time.time()
        throttle_translation(end_time - start_time, 2)

target_rate = 5 # 5 seconds a request 
ocr_tbl_name = choose_table()
ocr_properties = read_ocr_table(ocr_tbl_name)
tbl_name = '{} properties translated {}'.format(ocr_tbl_name, datetime.datetime.now().strftime('%Y:%m:%d %H:%M:%S'))
create_table()

# set up the browser
options = Options()
options.set_headless(headless=True)

with webdriver.Firefox(firefox_options=options) as web:
    web.get('http://ctbiglist.com')
    translate_properties(web, ocr_properties)
