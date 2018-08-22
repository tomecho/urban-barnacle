from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import sys

def visit_site(web):
    web.get('http://ctbiglist.com')
    web.find_element_by_id('PropertyID').send_keys(sys.argv[1])
    web.find_element_by_xpath("//input[@name='Submit']").click()

    search_result_rows = web.find_elements_by_xpath("(//form[@action='UP_Claim.asp']//tbody)[1]/tr[position() > 1]")
    map(
        lambda row: {
            
        }, 
        search_result_rows
    )

options = Options()
options.set_headless(headless=True)
web = webdriver.Firefox(firefox_options=options)
visit_site(web)
web.quit()
