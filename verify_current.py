from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sys

def visit_site(web, propertyId):
    web.get('http://ctbiglist.com')
    web.find_element_by_id('PropertyID').send_keys(propertyId)
    web.find_element_by_xpath("//input[@name='Submit']").click()

    search_result_rows = web.find_elements_by_xpath("(//form[@action='UP_Claim.asp']//tbody)[1]/tr[position() > 1]")
    result_dict = map(
        lambda row:
        {
            'property_id': propertyId,
            'name': row.find_element_by_xpath('td[3]').text,
            'address_street': row.find_element_by_xpath('td[4]').text,
            'address_city': row.find_element_by_xpath('td[5]').text,
            'address_state': row.find_element_by_xpath('td[6]').text,
            'address_zip': row.find_element_by_xpath('td[7]').text,
        }, 
        search_result_rows
    )

propertyId = sys.argv[1]
# set up the browser
options = Options()
options.set_headless(headless=True)
with webdriver.Firefox(firefox_options=options) as web:
    visit_site(web, propertyId)
