#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys

import clipboard
import re
import sys
import os
import argparse
import getpass
import subprocess
from pyvirtualdisplay import Display

#pyperclip.copy("lalallalal")

server = sys.argv[1]

password = getpass.getpass()

parser = argparse.ArgumentParser()
parser.add_argument("-ssh", "--enablessh", help="Enable SSH for the selected domain", action="store_true")
parser.add_argument("-mdb", "--migratedatabase", help="Migrate the database for the selected domain", action="store_true")
args, unknown = parser.parse_known_args()

def wait(element):
    WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, element))
)

chromedriver = '/home/hristian/chromedriver'
os.environ['webdriver.chrome.driver'] = chromedriver

display = Display(visible=0, size=(800, 600))
display.start()
    
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
    
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
driver.get("https://netadmin-002.sl5.misp.co.uk/passdb/account/login/?next=/passdb/cred/list/")

driver.find_element_by_id("id_username").send_keys("parhmihaylov")
driver.find_element_by_id("id_password").send_keys(password)

driver.find_element_by_xpath('//form//input[@type="submit"]').click()

driver.find_element_by_xpath('//input[@class="search-query"]').send_keys(server)
driver.find_element_by_xpath('//input[@class="search-query"]').send_keys(Keys.RETURN)

driver.find_element_by_partial_link_text(server).click()

newPass = driver.find_element_by_xpath('//span[@id="password"]').get_attribute('innerHTML')
clipboard.copy(newPass)
newHost = driver.find_element_by_partial_link_text(server).get_attribute('innerHTML')

host = re.sub(r'^https?:\/\/', '', newHost)
host = re.sub(r'/whm', '', host)
host = re.sub(r'/' ,'', host)
host = re.sub(r':2087','', host)

print ()
print ("Now connecting to {0}".format(host))
print ()

subprocess.call(["ssh", "root@{0}".format(host), "-p", "3784"])  

driver.close()
driver.quit()
display.popen.terminate()
sys.exit()
