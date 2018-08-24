from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sqlite3
import sys

def create_table(property_table_name):
    tbl_name = '[{property_table_name} withpeople]'.format(property_table_name=property_table_name)
    with sqlite3.connect('output.db') as conn:
        conn.execute('CREATE TABLE '+ tbl_name +' (property_id int primary key, cash real, source_location text, name text, address_street text, address_city text, address_state text, address_zip text);')
        conn.commit()
    return tbl_name

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

propertyId = sys.argv[1]
# set up the browser
options = Options()
options.set_headless(headless=True)
with webdriver.Firefox(firefox_options=options) as web:
    web.get('http://ctbiglist.com')
    translate_properties(web, [propertyId])
