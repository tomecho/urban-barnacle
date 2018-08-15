from selenium import webdriver
from selenium.webdriver.firefox.options import Options

options = Options()
options.set_headless(headless=True)
web = webdriver.Firefox(firefox_options=options)
try:
    visit_google(web)
except(ex):
    print ex.message,

def visit_google(web):
    web.get('http://google.com')

