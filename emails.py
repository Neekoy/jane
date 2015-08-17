import csv
import re
import string
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import random

def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def wait(element):
    WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, element))
)

def rand_generator(size):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))

driver = webdriver.Chrome('/home/hristian/chromedriver')

f = open("sports-xtra.csv", 'r')
csv_f = csv.reader(f)
next(csv_f, None)

emails = []

for row in csv_f:
    emails.append(row)

for k, a, m, v in emails:

    split =  re.split(r"@", k)
    email = split[0]
    domain = split[1]

    if v == "":
        v = rand_generator(8)

    driver.get('https://control.gridhost.co.uk/admin_panel/loginas.php')

    driver.find_element_by_name("domain").send_keys(domain)
    driver.find_element_by_name("password").send_keys("taylor12")
    driver.find_element_by_name("submit").click()

    curURL = (driver.current_url)
    custIdExtract = re.split(r"id=", curURL)
    custId = custIdExtract[1]

    driver.get('https://control.gridhost.co.uk/members/mailboxes.php?id=%s' % custId)

    driver.find_element_by_xpath("//strong[.='Create Mailbox']").click()

    driver.find_element_by_name("mailbox").send_keys(email)
    driver.find_element_by_name("new_mailbox_password").send_keys(v)

    driver.find_element_by_xpath("//input[@value='Create New Mailbox']").click()

    if check_exists_by_xpath("//*[contains(text(), 'exists')]") == True:
        print ("The email account {0} was already existent.".format(k))
    else:
        print ("Created *EMail*: {0} *Password*: {1}".format(k, v))

    if m != '':

        driver.find_element_by_xpath("//strong[.='Create Forwarder']").click()

        driver.find_element_by_xpath("//div[@data-tab-pane='3']/form/table/tbody/tr/td[2]/input[@name='mailbox']").send_keys(email)
        driver.find_element_by_name("forward_to").send_keys(m)
        driver.find_element_by_xpath("//div[@data-tab-pane='3']/form/table/tbody/tr[4]/td[2]/input[@type='submit']").click()
        print ("Also created forwarder from {0} to {1}.".format(k, m))

    print ()
    driver.find_element_by_xpath("//strong[.='Logout']").click()

driver.close()
driver.quit()
