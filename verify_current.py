from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sqlite3
import sys

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
        conn.execute('''CREATE TABLE {} (property_id int primary key, cash real, source_location text, name text, 
                address_street text, address_city text, address_state text, address_zip text);'''.format(tbl_name))
        conn.commit()

def write_sqlite(result_array):
    with sqlite3.connect('output.db') as conn:
        conn.execute('INSERT INTO ' + tbl_name + ' VALUES(?,?,?,?,?,?,?,?);', result_array)
        conn.commit()

def translate_properties(web, properties):
    for _property in properties:
        web.find_element_by_id('PropertyID').send_keys(propertyId)
        web.find_element_by_xpath("//input[@name='Submit']").click()

        search_result_rows = web.find_elements_by_xpath("(//form[@action='UP_Claim.asp']//tbody)[1]/tr[position() > 1]")
        result_array = map(
            lambda row:
            [
                _property['id'],
                _property['cash'],
                _property['source_location'],
                row.find_element_by_xpath('td[3]').text,
                row.find_element_by_xpath('td[4]').text,
                row.find_element_by_xpath('td[5]').text,
                row.find_element_by_xpath('td[6]').text,
                row.find_element_by_xpath('td[7]').text,
            ], 
            search_result_rows
        )

ocr_tbl_name = choose_table()
tbl_name = '[{} properties]'.format(ocr_tbl_name)
propertyId = sys.argv[1]
# set up the browser
options = Options()
options.set_headless(headless=True)
with webdriver.Firefox(firefox_options=options) as web:
    web.get('http://ctbiglist.com')
    translate_properties(web, [{'id': propertyId, 'cash': 0, 'source_location': ''}])
