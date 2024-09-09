from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
import urllib.request, urllib.parse, urllib.error
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import re
import csv
import pandas as pd
import json
import psycopg2
import psycopg2.extras
import sys
 
#just change these names according to your database details
 
hostname = "localhost"
database = "scraping"
username = "postgres"
pwd = "Datakmkc@42069"
port_id = 5432
 
conn = None
cur = None
 
conn = psycopg2.connect(
    host = hostname,
    dbname = database,
    user = username,
    password = pwd,
    port = port_id)
 
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
 
def create_database():
    cur.execute('DROP TABLE IF EXISTS BeverageLocation')
    cur.execute('DROP TABLE IF EXISTS Location')
    cur.execute('DROP TABLE IF EXISTS Website')
    cur.execute('DROP TABLE IF EXISTS Beverage')
    cur.execute('DROP TABLE IF EXISTS Product')
    cur.execute('DROP TABLE IF EXISTS Brand')
    cur.execute('DROP TABLE IF EXISTS Flavor')
    create_tables_script = '''CREATE TABLE Brand (
                    brand_id SERIAL PRIMARY KEY,
                    brand_name VARCHAR(400) NOT NULL UNIQUE
                );
 
                CREATE TABLE Flavor (
                    flavor_id SERIAL PRIMARY KEY,
                    flavor_name VARCHAR(400) NOT NULL UNIQUE
                );
 
                CREATE TABLE Product (
                    product_id SERIAL PRIMARY KEY,
                    brand_id INT,
                    flavor_id INT,
                    name VARCHAR(400) NOT NULL,
                    FOREIGN KEY (brand_id) REFERENCES Brand(brand_id),
                    FOREIGN KEY (flavor_id) REFERENCES Flavor(flavor_id)
                );
 
                CREATE TABLE Beverage (
                    beverage_id SERIAL PRIMARY KEY,
                    product_id INT,
                    price INT NOT NULL,
                    discount INT,
                    mrp INT NOT NULL,
                    volume TEXT NOT NULL,
                    quantity TEXT NOT NULL,
                    FOREIGN KEY (product_id) REFERENCES Product(product_id)
                );
               
                CREATE TABLE Location (
                    location_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
 
                CREATE TABLE Website (
                    site_id SERIAL PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                );
 
                CREATE TABLE BeverageLocation (
                    beverage_id INT,
                    location_id INT,
                    site_id INT,
                    PRIMARY KEY (beverage_id, location_id, site_id)
                );
                '''
    cur.execute(create_tables_script)
    conn.commit()
 
def get_brand_id(name):
    cur.execute('SELECT brand_id FROM Brand WHERE brand_name = %s', [name])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_brand(name):
    insert_brand = 'INSERT INTO Brand(brand_name) VALUES (%s)'
    cur.execute(insert_brand, [name])
    conn.commit()
 
def get_flavor_id(name):
    cur.execute('SELECT flavor_id FROM Flavor WHERE flavor_name = %s', [name])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_flavor(name):
    insert_flavor = 'INSERT INTO Flavor(flavor_name) VALUES (%s)'
    cur.execute(insert_flavor, [name])
    conn.commit()
 
def get_product_id(brand_id, flavor_id, name):
    cur.execute('SELECT product_id FROM Product WHERE brand_id = %s AND flavor_id = %s AND name = %s', [brand_id, flavor_id, name])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_product(brand_id, flavor_id, name):
    insert_product = 'INSERT INTO Product(brand_id, flavor_id, name) VALUES (%s, %s, %s)'
    cur.execute(insert_product, [brand_id, flavor_id, name])
    conn.commit()
 
def get_beverage_id(product_id, price, discount, mrp, volume, quantity):
    cur.execute('SELECT beverage_id FROM Beverage WHERE product_id = %s AND price = %s AND discount = %s AND mrp = %s AND volume = %s AND quantity = %s', [product_id, price, discount, mrp, volume, quantity])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_beverage(product_id, price, discount, mrp, volume, quantity):
    insert_beverage = 'INSERT INTO Beverage( product_id, price, discount, mrp, volume, quantity) VALUES (%s, %s, %s, %s, %s, %s)'
    cur.execute(insert_beverage, [product_id, price, discount, mrp, volume, quantity])
    conn.commit()
 
def get_location_id(name):
    cur.execute('SELECT location_id FROM Location WHERE name = %s', [name])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_location(name):
    insert_location = 'INSERT INTO Location(name) VALUES (%s)'
    cur.execute(insert_location, [name])
    conn.commit()
 
def get_site_id(site):
    cur.execute('SELECT site_id FROM Website WHERE name = %s', [site])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_website(site):
    insert_site = 'INSERT INTO Website(name) VALUES (%s)'
    cur.execute(insert_site, [site])
    conn.commit()
 
def check_into_beveragelocation(beverage_id, location_id, site_id):
    cur.execute('SELECT location_id FROM BeverageLocation WHERE beverage_id = %s AND location_id = %s AND site_id = %s', [beverage_id, location_id, site_id])
    id = cur.fetchone()
    if id != None:
        return id[0]
    return None
 
def insert_into_beveragelocation(beverage_id, location_id, site_id):
    insert_beveragelocation = 'INSERT INTO BeverageLocation(beverage_id, location_id, site_id) VALUES (%s, %s, %s)'
    cur.execute(insert_beveragelocation, [beverage_id, location_id, site_id])
    conn.commit()
 
create_database()
 
# Define the path to the JSON file
json_file_path = 'C:\Big basket web scraping\End to end project\Backend\script\config.json'
 
# Read the JSON file into a variable config
with open(json_file_path, 'r') as json_file:
    config = json.load(json_file)
 
def write_csv():
    with open('goated.csv', 'w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(row_list)
 
def initialize_driver():
    service = Service(ChromeDriverManager().install())
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument(
    # "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    # chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--ignore-certificate-errors")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--log-level=3")
    #driver = webdriver.Chrome(options=chrome_options)
    driver = webdriver.Chrome(service = service)
    driver.maximize_window()
    return driver
 
def clean(string):
    if string.find('.') != -1:
        string = string[ : string.find('.')]
    string = string.replace(',', '')
    string = string.replace('+', '')
    string = string.replace('\u20B9', '')
    return string
 
def scroll(driver):
    print("scrolling")
    last_height = driver.execute_script("return document.body.scrollHeight")
    if(config["websites"][site]["scrolling"]):
        while True:
            # print("scrolling")
            if(not config["websites"][site]["scrolling_to_bottom"]):
                try:
                    element = driver.find_element(By.CLASS_NAME,config["websites"][site]["scrolling_element"]["class"])
                    driver.execute_script("arguments[0].scrollIntoView(false);", element)
                except:
                    break
            else :
                driver.execute_script("window.scrollTo(0, (document.body.scrollHeight));")
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
    else:
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a')
        for link in links :
            x = link.text
            if x != None:
                if x.strip() == "Next":
                    return (site_url + link.get('href'))
    return None
 
 
def get_class(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    divs = soup.find_all('div')
    dic = {}
    pattern_rupe = r'[a-zA-Z\s]+₹\s?\d{1,3}(?:,\d{3})*(?:\.\d{1,2})?'
    for div in divs:
        x = div.text.lower().strip()
        if re.search(pattern_rupe, x):
            list = div.get_attribute_list('class')
            if len(list) > 0:
                item = list[0]
                if item in dic.keys():
                    dic[item] += 1
                else:
                    dic[item] = 0
            else:
                continue
   
    dic = dict(sorted(dic.items(), key=lambda x:x[1], reverse=True))
    for key in dic.keys():
        if key != None and key[0] != 'a':
            return key
 
def details(driver, location_id, site_id):
    html = driver.page_source
    # print(html)
    soup = BeautifulSoup(html, 'html.parser')
    pattern_rupe = r'₹\s?\d{1,3}(?:,\d{3})*(?:,\d{1,3})?(?:\.\d{1,2})?'
    divs = soup.find_all('div', class_ = get_class(driver))
    for div in divs:
        text = div.text
        temp = ""
        while text.find('(') != -1 and text.find(')') != -1:
            substr = text[text.find('(') : text.find(')') + 1]
            text = text.replace(substr, '')
        prices = re.findall(pattern_rupe, text)
        numbers = []
        for x in prices:
            if len(numbers) == 3:
                break
            if int(clean(x)) not in numbers:
                numbers.append(int(clean(x)))  
        if len(numbers) == 0:
            continue
        mrp, price = 0, 0
        numbers.sort(reverse=True)
        mrp = numbers[0]
        if len(numbers) > 1:
            price = numbers[1]
        else:
            price = mrp
        discount = round(100 - (price * 100)/mrp)
        text = text.replace("SponsoredSponsored You are seeing this ad based on the product’s relevance to your search query.Let us know", '').strip()
        if text.find('  ') != -1:
            text = text[ : text.find('  ')]
        if text.find('OFF') != -1:
            text = text[text.find('OFF') + 3: ]
        regex = r'([a-zA-Z])\d.*'
        if text.find(' mins') != -1:
            text = text[text.find(' mins') + 5 : ]
        text = re.sub(regex, r'\1', text)
        volume_regex = r'\b((\d+(\.\d+)?)\s*([xX]\s*)?\s*\d*\s*(m|M|ml|mL|ML|l|L|litre|liter|Litres|Liters|Litres\.\s*cm))\b'
        quantity_regex = r'\bPack of\s+(\d+)\b'
        volume = 'NA'
        quantity = '1'
        if re.search(volume_regex, text):
            volume = re.search(volume_regex, text).group(0)
        if re.search(quantity_regex, text):
            quantity = re.search(quantity_regex, text).group(0)
        if quantity == '1':
            if volume.find('x') != -1:
                quantity = (volume.split('x'))[0].strip()
            elif volume.find('X') != -1:
                quantity = (volume.split('X'))[0].strip()
        quantity = quantity.replace('Pack of', '').strip()
        if volume != 'NA':
            text = text[ : text.find(volume)]
        title = text.strip()
        if title.find('+') == -1:
            a, b, c, d = len(title), len(title), len(title), len(title)
            if title.find(',') != -1:
                a = title.index(',')
            if title.find('|') != -1:
                b = title.index('|')
            if title.find(' - ') != -1:
                c = title.find(' - ')
            if title.find('..') != -1:
                d = title.find('..')
            title = title[ : min(a, b, c, d)]
 
        brand = "NA"
        flavors = []
        brand_id, flavor_id, product_id = 0, 0, 0
 
        for item in brand_list:
            if text.lower().find(item.lower()) != -1:
                brand = item
                break
       
        if get_brand_id(brand) == None:
            insert_into_brand(brand)
 
        brand_id = get_brand_id(brand)
 
        for item in flavor_list:
            if text.lower().find(item.lower()) != -1:
                flavors.append(item)
       
        if len(flavors) == 0:
            flavors.append("NA")
 
        for flavor in flavors:
            if get_flavor_id(flavor) == None:
                insert_into_flavor(flavor)
 
            flavor_id = get_flavor_id(flavor)
 
            if get_product_id(brand_id, flavor_id, title) == None:
                insert_into_product(brand_id, flavor_id, title)
           
            product_id = get_product_id(brand_id, flavor_id, title)
           
            if get_beverage_id(product_id, price, discount, mrp, volume, quantity) == None:
                insert_into_beverage(product_id, price, discount, mrp, volume, quantity)
 
            beverage_id = get_beverage_id(product_id, price, discount, mrp, volume, quantity)
           
            if( check_into_beveragelocation(beverage_id, location_id, site_id) == None):
                insert_into_beveragelocation(beverage_id, location_id, site_id)
           
            row_list.append([brand, flavor, title, price, discount, mrp, volume, quantity])
 
def count(driver, soup):
    checkboxes = driver.find_elements(By.CSS_SELECTOR, "input[type='checkbox']")
    links = soup.find_all('a')
    return (len(checkboxes) + len(links))
 
def get_categories():
    filters = {}
    while True:
        key = input("Enter Category - ")
        if key == '':
            break
        list = []
        print("Enter Fields - ")
        while True:
            str = input()
            if str == '':
                break
            list.append(str)
        filters[key] = list
    return filters
 
 
 
 
def scroll_into_view(driver, element):
        driver.execute_script("arguments[0].scrollIntoView(false);", element)
        time.sleep(2)
 
 
def manage_category(driver,filters):
   
    actions = ActionChains(driver)  
   
    # filters = { 'brand' : [ 'dabur', 'pepsi'],
    #           }
    for key in filters.keys():
 
        categories = filters[key]
       
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        divs_selenium = driver.find_elements(By.TAG_NAME, 'div')
        divs_bs = soup.find_all('div')
 
       
        if(not config["websites"][site]["category-div-open"]):
            for i in range(len(divs_bs)):
                x = divs_bs[i].text
                if x != None and x.lower().strip() == key:
                    scroll_into_view(driver, divs_selenium[i])
                    actions.move_to_element(divs_selenium[i]).perform()
                    initial = count(driver,soup)
                    time.sleep(3)
                    actions.click(divs_selenium[i]).perform()
                    final = count(driver, soup)
                    if initial > final:
                        actions.click(divs_selenium[i]).perform()
                    break
               
        if(config["websites"][site]["scroll-to-load-page"]):
             driver.execute_script(
"window.scrollTo(0, document.body.scrollHeight);"
)
             time.sleep(3)
 
 
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
 
 
        if(config["websites"][site]["show-more"]=="div"):
            divs_selenium = driver.find_elements(By.TAG_NAME, 'div')
            divs_bs = soup.find_all('div')
            for i in range(len(divs_bs)):
                x = divs_bs[i].text
                if x != None and (x.lower().strip()).find('more') != -1 and len(x.split()) == 2:
                    actions.move_to_element(divs_selenium[i]).perform()
                    time.sleep(3)
                    actions.click(divs_selenium[i]).perform()
                    break
 
 
        else:
            buttons_selenium=driver.find_elements(By.TAG_NAME, 'button')
            buttons_bs=soup.find_all('button')
            for i in range(len(buttons_bs)):
                x = buttons_bs[i].text
                if x != None and (x.lower().strip()).find('show more +') != -1 and len(x.split())==3:
                    try:
                        scroll_into_view(driver, buttons_selenium[i])
                        actions.move_to_element(buttons_selenium[i]).perform()
                        time.sleep(3)
                        actions.click(buttons_selenium[i]).perform()
                    except:
                        pass
 
           
               
        for category in categories:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            divs_selenium = driver.find_elements(By.TAG_NAME, 'div')
            divs_bs = soup.find_all('div')
            spans_selenium = driver.find_elements(By.TAG_NAME, 'span')
            spans_bs = soup.find_all('span')
           
           
            for i in range(len(spans_bs)):
                x = spans_bs[i].text
                if x != None and x.lower().strip() == category:
                    if (config["websites"][site]["category"]=="span"):
                        actions.move_to_element(spans_selenium[i]).perform()
                        time.sleep(3)
                        actions.click(spans_selenium[i]).perform()
                    else:
                        scroll_into_view(driver,spans_selenium[i])
                        actions.move_to_element(spans_selenium[i]).perform()
                        time.sleep(3)
                        input=spans_selenium[i].find_element(By.TAG_NAME,"input")
                        actions.click(input).perform()
                    break
 
 
           
 
            for i in range(len(divs_bs)):
                x = divs_bs[i].text
                if x != None and x.lower().strip() == category:
                    actions.move_to_element(divs_selenium[i]).perform()
                    time.sleep(3)
                    actions.click(divs_selenium[i]).perform()
                    break
           
            # if site=='bigbasket':
            #     time.sleep(3)
            #     open_all_showmore(driver)
            #     time.sleep(2)
 
def pop_up(driver):
    elements = driver.find_elements(By.TAG_NAME, 'input')
    for element in elements:
        aria_label = element.get_attribute('aria-label')
        placeholder = element.get_attribute('placeholder')
        if (aria_label != None and (aria_label.lower().find('pincode') != -1 or aria_label.lower().find('location') != -1 or aria_label.lower().find('street') != -1)) or (placeholder != None and (placeholder.lower().find('pincode') != -1 or placeholder.lower().find('location') != -1 or placeholder.lower().find('street') != -1)):
            return False
    return True
 
def change_location(driver, location):
    actions = ActionChains(driver)  
    divs_old = driver.find_elements(By.TAG_NAME, 'div')
    elements = driver.find_elements(By.TAG_NAME, 'input')
    flag = 0
    for element in elements:
        aria_label = element.get_attribute('aria-label')
        placeholder = element.get_attribute('placeholder')
        if (aria_label != None and (aria_label.lower().find('pincode') != -1 or aria_label.lower().find('location') != -1 or aria_label.lower().find('street') != -1)) or (placeholder != None and (placeholder.lower().find('pincode') != -1 or placeholder.lower().find('location') != -1 or placeholder.lower().find('street') != -1)):
            element.send_keys(location)
            time.sleep(2)
            element.send_keys(" ")
            divs_new = driver.find_elements(By.TAG_NAME, 'div')
            final_divs = [div for div in divs_new if div not in divs_old]
            time.sleep(2)
 
            if len(final_divs) == 0:
                element.send_keys(Keys.ENTER)
                time.sleep(2)
                break
           
            for div in final_divs:
                x = div.text
                if x != None and x.lower().find(location) != -1 and x.lower().find(location) == 0:
                    actions.move_to_element(div).perform()
                    time.sleep(2)
                    actions.click(div).perform()
                    flag = 1
                    break
   
        if flag == 1:
            break
 
def search(prompt, location, filters):
    driver = initialize_driver()
    driver.get(site_url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
 
    if get_location_id(location) == None:
            insert_into_location(location)
       
    location_id = get_location_id(location)
 
    if get_site_id(site) == None:
        insert_into_website(site)
   
    site_id = get_site_id(site)
 
    if pop_up(driver):
        divs_selenium = driver.find_elements(By.TAG_NAME, 'div')
        divs_bs = soup.find_all('div')
        loc_div = ''
        for i in range(len(divs_bs)):
            x = divs_bs[i].text
            if x != None and x.lower().find('location') != -1 and EC.element_to_be_clickable(divs_selenium[i]):
                loc_div = divs_selenium[i]
        if type(loc_div) != str:
            loc_div.click()
            time.sleep(2)
   
    if(config["websites"][site]['Change_location']):
        change_location(driver, location)
    time.sleep(5)
   
    inputs = driver.find_elements(By.TAG_NAME, 'input')
    for input in inputs:
        text = input.get_attribute('placeholder')
        if text.lower().find('search') != -1:
            input.send_keys(prompt)
            time.sleep(2)
            input.send_keys(Keys.ENTER)
            break
    time.sleep(2)
    manage_category(driver, filters)
    while True:
        next_url = scroll(driver)
        print(next_url)
        details(driver, location_id, site_id)
        if next_url != None:
            driver.get(next_url)
            print("going")
        else:
            print("not going")
            break
   
    headers = ["Brand", "Flavor", "Title", "Price", "Discount", "M.R.P.", "Volume", "Quantity"]
    df = pd.DataFrame(row_list, columns=headers)
    df_cleaned = df.dropna()
    final_df = df_cleaned.drop_duplicates()
    final_df = final_df.reset_index()
    final_df.drop(['index'],axis = 1,inplace=True)
    file_name = site + 'output' + location + '.csv'
    final_df.to_csv(file_name, sep='\t', encoding='utf-8', index=False)
    print(final_df)
    driver.quit()
 
site = 'flipkart'
site_url = ""
row_list = []
locations = {"282001" : "agra"}
brand_list = [
    "1600 AD Coffee",
    "18 Herbs",
    "1868 by Tata Tea",
    "24 Mantra Organic",
    "24 Mantra",
    "3 Roses",
    "6rasa",
    "7 Up Nimbooz",
    "7 Up",
    "777",
    "7up",
    "9t9",
    "Aachi",
    "AAGAM",
    "Aanya",
    "Aavin",
    "Again",
    "AGNEE",
    "Aiisiri",
    "AIMIL",
    "Akhya",
    "Alive",
    "Alkalen",
    "All in One",
    "ALLADIN ICE",
    "Alo Frut",
    "ALPHA 8",
    "Amar",
    "Ammae",
    "Amul Pro",
    "Amul",
    "anjali health care",
    "ANNAI",
    "Apis",
    "Apollo Pharmacy",
    "Apollo",
    "Appy Fizz",
    "Appy",
    "Apsara",
    "Aptagrow",
    "Aquafina",
    "AQUATEIN",
    "ARAKU",
    "Arka",
    "Ashvatha",
    "Attagirl",
    "Auric",
    "Aveon",
    "AVT Tea",
    "AVT",
    "Axiom",
    "B Fizz",
    "B Natural",
    "Bab Louie & Co.",
    "Bacardi MIX'R",
    "Baidyanath",
    "Bailley",
    "Bambino",
    "Banarich",
    "Barbican",
    "Baron De Bercy",
    "Barosi",
    "Battler",
    "Bayars",
    "Bazzinga",
    "bb Combo",
    "BB Royal",
    "Bean Good",
    "Bean Song",
    "Beanies",
    "Beyondarie",
    "Bikano",
    "Bindu",
    "Bionova",
    "Bisleri",
    "Blend Art Teas",
    "Blue Barbet",
    "Blue Bird",
    "Blue Tokai",
    "Blv Fine Blend",
    "Boca",
    "Bombay 99",
    "Bombucha",
    "Booch",
    "Booster Water",
    "Boost",
    "Borecha",
    "BORGES",
    "BORN HILL",
    "Bournvita",
    "Bovonto",
    "Brahmins",
    "BREW & BLISS",
    "Brewhouse Tea Brewing Co.",
    "Britvic",
    "Brooke Bond",
    "BRU",
    "BSTAR",
    "BTN Sports",
    "BudLeaf",
    "Budweiser 0.0",
    "By Nature",
    "Cadbury Bournvita",
    "Cadbury",
    "CAFE NILOUFER",
    "Cambridge Tea Party",
    "Carl Jung",
    "Castillo De Salobrena",
    "Catch",
    "Cavins",
    "Celebrations",
    "Centrum",
    "Chaayos",
    "Chaika",
    "CHAIZUP",
    "CHEERS",
    "Chocolate Horlicks",
    "Coca Cola",
    "Coca-Cola",
    "Cocktail Baba",
    "COCO NIRVANAA",
    "COCO ROYAL",
    "Cocojal",
    "Cocomama",
    "Coffee Day",
    "Coffeeza",
    "Cohoma Coffee Company",
    "COLD BLISS",
    "Colombian Brew Coffee",
    "Combo",
    "Complan",
    "Continental Coffee",
    "Continental Malgudi",
    "Continental",
    "Coolberg",
    "Cothas Coffee",
    "Country Bean",
    "Crofters",
    "Dabur",
    "Dadaji",
    "Dad's Hack",
    "DAILEE",
    "Dailyum",
    "Darmona",
    "D'Aromas",
    "Dasani",
    "Dash of RCB",
    "Davidoff",
    "Del Monte",
    "Delight Foods",
    "Desi Cha",
    "Desi Utthana",
    "Dezire",
    "Dhishoom",
    "Diabetics Dezire",
    "Dibha",
    "DILMAH",
    "DOBRA",
    "Dorje",
    "Dr. Cubes",
    "Dras Ice",
    "Drinktales",
    "Druk",
    "Dubai",
    "Dukes",
    "EARTHMADE ORGANIX",
    "Eco Valley",
    "Emoticup",
    "Emperia",
    "Enchanteas",
    "Enerzal",
    "Enfagrow A+",
    "Enfagrow",
    "ENSURE DIABETES CARE",
    "Ensure",
    "Esah Tea",
    "Eva",
    "evocus",
    "Exotic Musings",
    "Fabbox",
    "Fanta",
    "Farm Naturelle",
    "Farmers Family",
    "FEARLESS TEA",
    "Fever Tree",
    "FITLETIC FUEL BETTER",
    "Fitness mantra",
    "Flavour Drum",
    "FLISTAA",
    "Fresca",
    "Fresh Coffee ToDay",
    "Freshey's",
    "Freshgold",
    "FRESHLEAF",
    "Fresho Signature",
    "Fresho",
    "Fre",
    "Frooti",
    "FRUSSH",
    "Fundaaz",
    "Future Organics",
    "Gaia",
    "Gallons",
    "Ganesh",
    "Gatorade",
    "GCC",
    "GIOLLY",
    "Girnar",
    "Glaceau",
    "Glucon-D",
    "Glucovita Bolts",
    "Glucovita",
    "GOANFEST",
    "Golden Tips",
    "GOOD & MOORE",
    "Good Morning",
    "Good Trip",
    "Goodricke",
    "Gopal",
    "GRAMI SUPERFOODS",
    "Granola",
    "GREENBRREW",
    "Groviva",
    "Gtee",
    "Gulab Sweets",
    "Gulabs",
    "Gunsberg",
    "Guruji",
    "Hajoori's",
    "Haldiram's",
    "Hamdard",
    "HAPPY INDIA",
    "HARIMA",
    "Harshaman",
    "HATHIKULI ORGANIC",
    "Hatti Kaapi",
    "Hazbe",
    "Health Basket",
    "HELL ENERGY",
    "Hello Healthy",
    "herbea",
    "Hershey's",
    "Hills & Mist",
    "Himalayan",
    "Himmachal",
    "Hitkary",
    "Hoegaarden 0.0",
    "Honest Tea",
    "Horlicks",
    "Hurricane",
    "ICELINGS",
    "ICY SIPPY",
    "iD",
    "Illy",
    "IncredaBrew",
    "IndiSecrets",
    "Instant Ice",
    "Isvaari",
    "ISVARA",
    "Jai Guruji",
    "Jawai",
    "Jayanthi Coffee",
    "Jeeru",
    "JIMMY'S COCKTAILS",
    "JINTHAAA",
    "Jiva Ayurveda",
    "JIVRAJ SAMAARA",
    "Jivraj9",
    "Jivraj",
    "JOKAI",
    "JOMO FOCUZFUELS",
    "JST SODA",
    "Juicy N Crazy",
    "Junior Horlicks",
    "KAAVERI",
    "Kalimark",
    "KALOUR",
    "KAMAL'S",
    "Kanchana",
    "Kangra Tea House",
    "Kapiva Ayurveda",
    "Kapiva",
    "Karma Kettle",
    "Kashmira",
    "KASTURISHRI",
    "Keya",
    "Kinley",
    "Kissan",
    "KLF Coconad",
    "Konkan Amrut",
    "KORANGANI TEA",
    "Krishi Cress Kombucha",
    "Krishi Cress",
    "KROCC TREATS",
    "Kubal",
    "Kumbakonam Iyer Coffee",
    "Lafiesta",
    "LAIQA",
    "LALA GOLI SODA",
    "LANA",
    "Lavazza",
    "Lazy Cocktails & Co.",
    "Le15",
    "Lehar",
    "Lemor",
    "Leo",
    "LEVISTA",
    "Limca",
    "Lipton Ice Tea",
    "Lipton",
    "LIQUID LIFE",
    "LITT",
    "Local Ferment Co",
    "LQI",
    "Lumiere",
    "Luxmi Tea",
    "Maaza gold",
    "Maaza",
    "Madhur",
    "MAGICSIP COFFEE",
    "Makaibari",
    "Malaki",
    "Malas",
    "Maltova",
    "Maltwin",
    "Mambalam Iyers",
    "Manama",
    "Mangajo",
    "Manna",
    "Mapro",
    "MARQUES DE CADIZ",
    "MARQUES DE FERRO",
    "Marvel Tea",
    "Marvel",
    "Mathieu Teisseire",
    "Maxvida",
    "Melite",
    "Meri Chai",
    "MERIBA",
    "&Me",
    "Mili",
    "Minerva Coffee",
    "Minerva",
    "Minute Maid",
    "Mirakle",
    "Mirchi Bites",
    "Mirinda",
    "Mishrambu",
    "Mlesna",
    "Mojoco",
    "Monin",
    "Monster",
    "Morning Fresh",
    "Morton",
    "Mossant",
    "Mother Organic",
    "Mother's Recipe",
    "Moti's",
    "Mountain Dew",
    "Movenpick",
    "Mr. Fresh Coco",
    "Mr & Mrs",
    "Mr South",
    "Mr.GOLISODA",
    "Mrs Bector'S Cremica",
    "Mrs.Food Rite",
    "MTR",
    "Mysore Coffee",
    "NAARIO",
    "Nameri Tea",
    "Namhya",
    "Namma Aathu Coffee",
    "Nandini",
    "Napa",
    "Narasus",
    "Nargis",
    "Nattfru",
    "Nature Day",
    "Nature's First",
    "Natures",
    "NaturoBell",
    "Nectar Valley",
    "Neer kombucha",
    "Nescafe All in 1",
    "Nescafe Classic",
    "Nescafe Gold",
    "NESCAFE SUNRISE",
    "Nescafe",
    "Nestea",
    "Nestle Lactogrow",
    "Nestlé NANGROW",
    "Nestle",
    "Neuherbs",
    "Nilon's",
    "NOCD",
    "Nonandrai Bholanath",
    "Notlih",
    "Nutramine",
    "Nutrashil",
    "Nutriyash",
    "Nutty Yogi",
    "Ocean Energy",
    "Ocean Spray",
    "Ocean",
    "Octavius",
    "Old Madras Market",
    "Olinda",
    "Omkar",
    "Onlyleaf",
    "Open Secret",
    "Organic India",
    "Organic Tattva",
    "Organic Wellness",
    "Organica",
    "ORSL",
    "Ovaltine",
    "Paper boat Swing",
    "Paper Boat",
    "Paperboat Swing",
    "Patanjali",
    "Patritti",
    "Pediasure",
    "PEER",
    "Pepsi",
    "Perfetto",
    "Phalada Pure & Sure",
    "PICK",
    "POKKA",
    "Pou Chong",
    "PRAN",
    "Predator",
    "Pride Of India",
    "Prime",
    "PRISTINE",
    "Pro360",
    "PROLYTE",
    "Protinex",
    "Provee",
    "Qaadu",
    "Qualinut Gourmet",
    "Qua",
    "Rage Coffee",
    "RASKIK",
    "Rasna",
    "Raw Pressery",
    "Raze",
    "ReActive Organics",
    "Real Activ",
    "Real Gold",
    "REAL TASTE",
    "Real",
    "RED BULL",
    "Red Label",
    "Rider",
    "RISE UP",
    "Riseup",
    "r!neu",
    "Rooh Afza Fusion",
    "Roohafza",
    "Rosewood Cafe",
    "Roshi",
    "Rossvita",
    "RS",
    "Saburi",
    "Saffola FITTIFY Gourmet",
    "SAMS",
    "Sancha",
    "Sanjeevani",
    "Sanjivani",
    "Sante",
    "Sapphire",
    "Satheesh Kaapi",
    "Schweppes",
    "Sepoy & Co",
    "Sericha",
    "Seven Beans",
    "Seven Spring Tea",
    "Shree Guruji",
    "Shree Siddhivinayak",
    "SHREEMATHA'S",
    "SHRINATH AYURVED",
    "Shunya",
    "Sidapur",
    "SimMom",
    "Sippin",
    "Sleepy Owl",
    "Slice",
    "Slurrp Farm",
    "Smoodies",
    "Snacky",
    "So Good",
    "SOCIETY TEA",
    "Society",
    "Sonnets by TATA Coffee",
    "Sorich Organics",
    "Sosyo",
    "Soyvita",
    "Sprig Tea",
    "Sprig",
    "Sprite",
    "Sri Sri Tattva",
    "Stanes",
    "Sting",
    "&Stirred",
    "Storia",
    "SUGANDH",
    "SUMA COFFEE",
    "sumeru",
    "Sunbean",
    "Swa Artisanal Syrups",
    "Swad",
    "Swastiks",
    "SYSTON",
    "T-GO",
    "Taaza",
    "Taj Mahal",
    "Tang",
    "Tata Coffee Grand",
    "Tata Coffee",
    "Tata Fruski",
    "Tata GoFit",
    "Tata Sampann",
    "Tata Soulfull",
    "Tata Tea Agni",
    "Tata Tea Care",
    "Tata Tea Chakra Gold",
    "Tata Tea Gemini",
    "Tata Tea Gold Care",
    "Tata Tea Gold Darjeeling",
    "Tata Tea Gold Saffron",
    "Tata Tea Gold",
    "Tata Tea Kanan Devan",
    "Tata Tea Lal Ghoda",
    "Tata Tea Premium Teaveda",
    "Tata Tea Premium",
    "Tata Tea",
    "Tata",
    "TE-A-ME",
    "Tea Bro",
    "Tea City",
    "Tea Culture Of The World",
    "Tea Leaf & Co.",
    "Tea Sense",
    "Tea Valley",
    "Teabox",
    "TeaFit",
    "Tealia",
    "Teamonk Global",
    "Teamonk",
    "TeaNOURISH",
    "TEAOLOGY",
    "TEAS FROM INDIA",
    "Teddy Roosevelt Coffee",
    "Teddy Roosevelt",
    "Tender Coco",
    "Tendo",
    "Terra Greens",
    "Tetley",
    "TGL Co.",
    "The Betel Leaf Co.",
    "THE HILLCART TALES",
    "The London Essence Co.",
    "The Wise Food Co",
    "THIRD WAVE COFFEE",
    "Thums Up",
    "THUNDERFIZZY",
    "Timios",
    "Tipsy J's",
    "Tipsy Tiger",
    "Trelish",
    "Tropicana",
    "TrueSouth",
    "Tulsi Tea",
    "Tummy Friendly Foods",
    "TummyFriendly Foods",
    "Twinings",
    "Two & A Bud",
    "Typhoo",
    "Tzinga",
    "UJI",
    "Ultx",
    "umami brew",
    "Unifibe",
    "Urban Platter",
    "Urja",
    "V-Nourish",
    "Vaggan Tea",
    "Vahdam",
    "Valentino",
    "Vatan Tea",
    "Vatan",
    "Vidavance",
    "Vidya Ground",
    "Vikram",
    "Vs Mani & Co.",
    "Wagh Bakri",
    "WaghBakri",
    "We Mill",
    "Wild Ideas",
    "Wineberry",
    "Wingreens Farms",
    "Winleaf",
    "Wow! Coco Charge",
    "XPLOR",
    "Y not",
    "Yosvita",
    "Zambaa",
    "Zenzi",
    "Zevic",
    "Zindagi"
]
flavor_list = [
    "Apple",
    "Assorted",
    "Badam",
    "Baja Lime",
    "Black tea",
    "Caffeine",
    "Caramel",
    "Cardamom",
    "Chamomile & mint green tea",
    "Chamomile",
    "Choco mocha",
    "Choco Orange",
    "Chocolate",
    "Coconut",
    "Coffee",
    "Cola",
    "Creamy",
    "Darjeeling tea",
    "Elaichi",
    "Energy Drink",
    "Exotic/Sundae",
    "Fresh Lime",
    "Fruit Flavour",
    "Fruits/Berry",
    "Gauva",
    "Ginger & Cardamom",
    "Ginger & Herbal",
    "Ginger & Lemon",
    "Ginger & Tulsi",
    "Ginger",
    "Grape",
    "Green Apple",
    "Green tea & mint",
    "Green Tea",
    "Guava",
    "Hazelnut",
    "Hibiscus",
    "Jamun",
    "Jasmine",
    "Jeera",
    "Kesar",
    "Kiwi",
    "Kokum",
    "Lemon grass",
    "Lemon",
    "Lime",
    "Litchi & Aloevera",
    "Litchi",
    "Lychee",
    "Mango",
    "Masala ,Ginger & Elaichi",
    "Masala, Tulsi",
    "Masala",
    "Matcha Green tea",
    "Mint",
    "Mixed Fruit",
    "Mixed",
    "Mocha",
    "Mosambi",
    "Nannari",
    "Natural",
    "Orange",
    "Other Juices",
    "Others",
    "Paneer",
    "Peach",
    "Pineapple",
    "Plain",
    "Pomogranate",
    "Regular",
    "Salted Caramel",
    "Soda",
    "Sour Gummy",
    "South Beach",
    "Spiced",
    "Strawberry",
    "Tender coconut",
    "Tulsi",
    "Turmeric",
    "Vanilla",
    "Vegetable Juice",
    "Vegetable",
    "Voodoo",
    "White tea"
]

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <website_name>")
    sys.exit(1)
 
# Read the argument
website_name = sys.argv[1]
site=website_name
 
if site in config['websites']:
    site_url = config['websites'][site]['base_url']
    if (config["websites"][site]['Change_location']):
        if(config["websites"][site]["location-value"]=='pincode'):
                for pincode in config["locations"].keys():
                    search(config["prompt"], pincode, config['filters'])
        else:
                for city in config["locations"].values():
                    search(config["prompt"], city,config['filters'])
 
    else:
        search(config["prompt"],"000000",config['filters'])
   
else:
    print("No such site")
print('ho gya')