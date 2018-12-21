# import libraries
import urllib.request
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import time
import xlsxwriter
from tinydb import TinyDB, Query
from urllib.request import urlopen
from selenium.webdriver.remote.webelement import WebElement
from webium.driver import get_driver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import re
import datetime


number = 0

db = TinyDB("Amazon.json")

def clean (product_description):
    description=[]
    for desc in product_description:
        ProductDescription = desc.text.strip()
        description.append(ProductDescription)
    enter ="\n"
    return enter.join(description)

def clean_pic (imageID):
    image = str(imageID)
    return (image)


# specify the url
urlpage= input("What web page do you want to scrape?")
print(urlpage)
# run firefox webdriver from executable path of your choice
driver = webdriver.Firefox()

def scraping (urlpage, db):
    global number
    # get web page
    driver.get(urlpage)
    # execute script to scroll down the page

    delay = 3 # seconds
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    driver.implicitly_wait(10)
    # sleep for 30s
    time.sleep(10)
    # driver.quit()
    # find elements by xpath
    get_driver()._web_element_cls = WebElement



    # create empty array to store data
    # loop over results
    urlList=[]

    link1 = driver.find_elements_by_xpath("//*[contains(@class, 's-result-item celwidget ' )]")

    print("Number of Link Found: ", len(link1))
    for c in link1:
        link2 = c.find_element_by_xpath(".//*[contains(@class, 's-access-detail-pag')]")
        url = link2.get_attribute("href")
        image1 = c.find_element_by_tag_name('img')
        image = image1.get_attribute('src')
        print(image)
        pair = [url, image]
        urlList.append(pair)
    print("Links Needed to Process: ", len(urlList))
    for url, image in urlList:
        number += 1
        
        print(number, "Processing: ", '. ', '\u001b[34m', url, "......\u001b[0m")
        t1_start = time.perf_counter()
        getUrl = driver.get(url)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        driver.execute_script("window.scrollTo(0, 0);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        driver.execute_script("window.scrollTo(0, 0);")
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
        driver.execute_script("window.scrollTo(0, 0);")
        try:
            WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.ID, "landingImage")))
        except:
            continue
        name = driver.find_element_by_xpath("//*[@id='productTitle'] | //*[@id='mas-title']").text.strip()

        if "Alex" in name:
            print('Alexa detected, skiping this one')
            continue
        print (name)
        try:
            description = driver.find_element_by_id('feature-bullets')
            features = description.find_elements_by_css_selector("span.a-list-item")
            product_description = clean(features)
            print(image)
        except NoSuchElementException:
            print('Not adding this item')
            continue
        try:
            price =float("".join(re.findall("\d+\.\d+", driver.find_element_by_id('priceblock_ourprice').text)))
        except NoSuchElementException:
            price = 0.0
            pass
        try:
            prereview = driver.find_element_by_id('acrCustomerReviewText').text
            review = int("".join(re.findall("\d+", prereview)))
        except NoSuchElementException:
            review = 0
            pass
        try:
            prerating = driver.find_element_by_id('acrPopover').get_attribute('title')
            print(prerating)
            rating = float("".join(re.findall("\d+\.\d+", prerating)))
        except NoSuchElementException:
            rating = 0
            pass
        try:
            details = driver.find_element_by_id('productDetails_detailBullets_sections1')
            more_details = details.find_elements_by_css_selector('td.a-size-base')
            for b in more_details:
                a = b.text
                if "inches" in a:
                    size1 = a
                    print(size1)
                    size = re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", size1)
                    break
                else:
                    size = [0, 0, 0]
            print(size)
            length = float(size[0])
            height = float(size[1])
            depth = float(size[2])
            for d in more_details:
                a = d.text
                print(a)
                if "pounds" in a:
                    weight1 = a
                    weight = float("".join(re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", weight1)))
                    print (weight)
                    break
                elif "ounces" in a:
                    weight1 = a
                    weight = (float("".join(re.findall(r"[+-]? *(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", weight1)))*0.0625)
                    print(weight)
                    break
                else:
                    weight = 0.0
                    print (weight)
                for s in more_details:
                   p = s.text
                   month = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
                   for b in month:
                       if b in p:
                           listed_date = p
                       else:
                           listed_date = "null"
        except NoSuchElementException:
            length = 0
            height = 0
            depth = 0
            weight = 0
            listed_date = "null"
        link = driver.current_url
        created_date = datetime.datetime.now().isoformat()
        rec ={
                "Name": name,
                "Description": product_description,
                "Price": price,
                "Length": length,
                "Height": height,
                "Depth" : depth,
                "Weight": weight,
                "URL": link,
                "Review": review,
                "Rating": rating,
                "Listed_Date": listed_date,
                "Created_Date": created_date,
                "Image" : image
                }

        
        Result = Query()
        s1  = db.search(Result.Name == rec ["Name"])

        if not s1:
            db.insert(rec)
        t1_end = time.perf_counter()
        print('\u001b[31m',t1_end - t1_start, "second used\u001b[0m")
    return driver

page_remaining = True
page = 1
while page_remaining:
    print(page)
    page_remaing = False
    print(urlpage)
    soup = scraping(urlpage, db)
    soup.get(urlpage)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);var lenOfPage=document.body.scrollHeight;return lenOfPage;")
    driver.implicitly_wait(10)
    # sleep for 30s
    time.sleep(10)
    # driver.quit()
    # find elements by xpath
    get_driver()._web_element_cls = WebElement
    try:
        next_link = soup.find_element_by_id('pagnNextLink')
        urlpage = next_link.get_attribute('href')
        print(urlpage)
        if urlpage:
            page_remaining = True
            page +=1
    except NoSuchElementException:
        page_remaining = False
        print("Cannot find the Button")


driver.quit()
