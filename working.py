#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

import argparse
import spur
from pyvirtualdisplay import Display
import time
import subprocess
from pexpect import pxssh
import sys
from time import sleep
import string
import random
import re
import os

domainName = sys.argv[1]
task = sys.argv[2]

############################

parser = argparse.ArgumentParser()
parser.add_argument("-ssh", "--enablessh", help="Enable SSH for the selected domain", action="store_true")
parser.add_argument("-mdb", "--migratedatabase", help="Migrate the database for the selected domain", action="store_true")
args, unknown = parser.parse_known_args()

############################

global error
error = 0

def include(filename):
    if os.path.exists(filename):
            execfile(filename)

def rand_generator(size):
    return ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(size))

def wait(element):
    WebDriverWait(driver, 30).until(
    EC.element_to_be_clickable((By.PARTIAL_LINK_TEXT, element))
)

def check_exists_by_xpath(xpath):
    try:
        driver.find_element_by_xpath(xpath)
    except NoSuchElementException:
        return False
    return True

def endNow():
    driver.close();
    driver.quit();
    display.popen.terminate()
    sys.exit()

def exitWithError(message):
    print ()
    print (colours.red + message + colours.endc)
    print ()
    global error
    error = 1
    endNow()

##############################

class colours:
    yellow = '\033[1;93m'
    red = '\033[1;91m'
    endc = '\033[0m'

##############################

chromedriver = '/home/hristian/chromedriver'
os.environ['webdriver.chrome.driver'] = chromedriver
    
display = Display(visible=0, size=(800, 600))
display.start()
    
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--incognito")
    
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)
driver.get("https://control.gridhost.co.uk/admin_panel/loginas.php")

driver.find_element_by_name("domain").send_keys(domainName)
driver.find_element_by_name("password").send_keys("taylor12")
driver.find_element_by_name("submit").click()

#content = driver.page_source
#print (content)

try:
    driver.find_element_by_id("logo")
except:
    exitWithError("Unable to log in with domain name %s to the Cloud" % domainName)    

#wait("hostsfile.net")
#driver.find_element_by_partial_link_text("hostsfile.net").click()

curURL = (driver.current_url)
custIdExtract = re.split(r"id=", curURL)
custId = custIdExtract[1]

print()

##########################################################################################################

def enableSSH(id):

    driver.get("https://control.gridhost.co.uk/members/ssh.php?id=%s" % custId)

    print(colours.yellow + "Enabling SSH..." + colours.endc)

    if check_exists_by_xpath("//*[contains(text(), 'SSH is currently inactive on this domain.')]") == True:
        driver.find_element_by_name("submitwtf").click()
        print ("SSH has been enabled for the domain.")
        print ("Please allow for 180 seconds for SSH to become active.")
        print ()
        for i in range(180,-1,-1):
            time.sleep(1)
            print("Time remaining: " + str(i), end='\r')
            sys.stdout.flush()
            if i == 0:
                print ("SSH has been activated.")
        sys.stdout.flush()
    else:
        print ("SSH was already enabled for the domain.")

    sshTable = []
    for tr in driver.find_elements_by_xpath('//table[@class="data mB15"]//tr'):
        tds=tr.find_elements_by_tag_name('td')
        if tds:
            sshTable.append([td.text for td in tds])

    global sshUsername
    global sshPassword

    for key, value in sshTable:
        if key == "SSH Username:":
            sshUsername = value
        elif key == "SSH Password:":
            sshPassword = value

    print()
    print(colours.yellow + "SSH Login Credentials:" + colours.endc)
    print("Host: shell.gridhost.co.uk")
    print("Username: {0}".format(sshUsername))
    print("Password: {0}".format(sshPassword))
    print()

    if task == "enableSSH":
        print(colours.yellow + "SSH has been successfully enabled." + colours.endc)
#        shellNew = spur.SshShell(hostname='localhost')
#        shellNew.run("ssh hostsfil@shell.gridhost.co.uk")


##########################################################################################################

def createDB(id):
    print()
    print("Creating database")
    driver.get("https://control.gridhost.co.uk/members/view_mysql_databases.php?id=%s" % id)

    mysqlTable = []
    for tr in driver.find_elements_by_xpath('//table[@id="mysqldb"]//tr'):
        tds=tr.find_elements_by_tag_name('td')
        if tds:
            mysqlTable.append([td.text for td in tds])

    newUser = rand_generator(5)
    newPass = rand_generator(10)

    def checkExists():
        for each in mysqlTable:
            if any(newUser in item for item in each):
                return True
            else:
                return False

    checkExists()

    if checkExists:
        newUser = rand_generator(5)
        checkExists()

    driver.get("https://control.gridhost.co.uk/members/mysql_databases.php?id=%s" % id)

    driver.find_element_by_name("db_name").send_keys(newUser)
    driver.find_element_by_name("db_pass").send_keys(newPass)
    driver.find_element_by_name("submit").click()

    dbTable = []
    for tr in driver.find_elements_by_xpath('//table[@class="data mB15"]//tr'):
        tds=tr.find_elements_by_tag_name('td')
        if tds:
            dbTable.append([td.text for td in tds])

    global dbHost
    global dbName
    global dbUser
    global dbPass

    for key, value in dbTable:
        if key == "Database server/hostname:":
            dbHost = value
        elif key == "Database name:":
            dbName = value
        elif key == "Database username:":
            dbUser = value
        elif key == "Database password:":
            dbPass = value

    print()
    print(colours.yellow + "New database details:" + colours.endc)
    print("Host: {0}".format(dbHost))
    print("Database name: {0}".format(dbName)) 
    print("Username: {0}".format(dbUser))
    print("Password: {0}".format(dbPass))

#########################################################################################################



def locateCreds(custId):    

    print ("Scanning for CMSs...")
    print()

    cmss = {"Wordpress": "wp-config.php", "Magento": "local.xml", "Joomla": "administrator.php"}	
    global s
    s = pxssh.pxssh()
    s.login('shell.gridhost.co.uk', sshUsername, sshPassword)
    cms = 0
    for v in cmss:
        s.sendline("find . -mindepth 2 -maxdepth 2 -name %s" % cmss[v])
        s.prompt()
        out = s.before
        output = (out.decode('utf-8')).split('\n')

        if "wp-config.php" in output[1]:
            print("Wordpress config file found: %s" % output[1])
            global wpconfig
            wpconfig = output[1]
            wpconfig = wpconfig.rstrip()
            cms = "Wordpress"

        if "local.xml" in output[1]:
            print("Magento config file found: %s" % output[1])
            magconfig = output[1]
            magconfig = magconfig.rstrip()
            cms = "Magento"

        if "administrator" in output[1]:
            print("Joomla config file found: %s" % output[1])
            joomconfig = output[1]
            joomconfig = joomconfig.rstrip()
            cms = "Joomla"

    if cms == "Wordpress":
        fields = ("DB_NAME", "DB_USER", "DB_PASSWORD", "DB_HOST")
        for f in fields:
            cmd = 'touch 1234.txt'
            s.sendline(cmd)
            s.prompt()
            cmd = "echo \"cat %s | grep %s | cut -d \\' -f 4\" > 1234.txt" % (wpconfig, f)
            s.sendline(cmd)
            s.prompt()
            s.sendline("sh 1234.txt")
            s.prompt() 
            out = s.before
            output = (out.decode('utf-8')).split('\n')
            if f == "DB_NAME":
                global dbNameOld
                dbNameOld = output[1]
                dbNameOld = dbNameOld.rstrip()
            if f == "DB_USER":
                global dbUserOld
                dbUserOld = output[1]
                dbUserOld = dbUserOld.rstrip()
            if f == "DB_PASSWORD":
                global dbPassOld
                dbPassOld = output[1]
                dbPassOld = dbPassOld.rstrip()
            if f == "DB_HOST":
                global dbHostOld
                dbHostOld = output[1]
                dbHostOld = dbHostOld.rstrip()

    else:
        exitWithError("No CMS was found for the domain")
        return

    print()
    print("Exporting old database...")

    print()
    print(colours.yellow + "Old database details:" + colours.endc)
    print("Host: %s" % dbHostOld)
    print("Database name: %s" % dbNameOld)
    print("Username: %s" % dbUserOld)
    print("Password: %s" % dbPassOld)

    cmd = "echo \"mysqldump -h %s -u %s -p%s %s > sqldumpfile.sql\" > 1234.txt" % (dbHostOld, dbUserOld, dbPassOld, dbNameOld)
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()
    out = s.before
    output = (out.decode('utf-8')).split('\n') 
    noutput = ', '.join(output)
    noutput = noutput.rstrip()
    if "denied" in noutput:
        exitWithError("Login credentials in config file %s are invalid." % wpconfig)

######################################################################################

def importDB(custID):

    print("Importing to new database")

    cmd = "echo \"mysql -h %s -u %s -p%s %s < sqldumpfile.sql\" > 1234.txt" % (dbHost, dbUser, dbPass, dbName) 
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()

 #   s.sendline("cp %s %s.backup" % (wpconfig, wpconfig)
 #   s.prompt()

    cmd = "sed -i \"/DB_HOST/s/'[^']*'/'%s'/2\" %s > 1234.txt" % (dbHost, wpconfig)
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()
    cmd = "sed -i \"/DB_USER/s/'[^']*'/'%s'/2\" %s 1234.txt" % (dbUser, wpconfig)
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()
    cmd = "sed -i \"/DB_NAME/s/'[^']*'/'%s'/2\" %s > 1234.txt" % (dbName, wpconfig)
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()
    cmd = "sed -i \"/DB_PASSWORD/s/'[^']*'/'%s'/2\" %s > 1234.txt" % (dbPass, wpconfig)
    s.sendline(cmd)
    s.prompt()
    s.sendline ("sh 1234.txt")
    s.prompt()

    s.logout()

    print("Database has been successfully migrated to the newest server.")
    print()
    print("Database credentials updated in %s" % wpconfig)

#########################################################################################################

def createSite():
    driver.get("https://control.gridhost.co.uk/members/register_or_host.php")
    driver.find_element_by_name("register_or_host").send_keys("newsub.hostsfile.net")
    driver.find_element_by_xpath("//input[@value='Next']").click()


#########################################################################################################

def progressBar():
    global currentProg
    currentProg = currentProg + steps
    if currentProg < 100:
        writeFile("<script>$('#progress').css('width', '{0}%');</script>".format(currentProg))
    else:
        writeFile("<script>$('#progress').css('width', '100%');</script>")

def initProg(number):
    global steps
    global currentProg
    currentProg = 0
    steps = 100 // number


########################################################################################################

#if task == "enableSSH":
if args.enablessh:
    enableSSH(custId)
    endNow()

#if task == "migrateDB":
if args.migratedatabase:
    enableSSH(custId)
    if error == 0:
        locateCreds(custId)
    if error == 0:
        createDB(custId)
    if error == 0:
        importDB(custId)
    endNow()

#Create site:
    #enableSSH for the old domain #createSite #Assin SSH variables to other ones, enable SSH for new site #LocateCreds() for old site
    #rsync all of the content from old site(including DB dump)
    #CreateDB for new site and import

#########################################################################################################

