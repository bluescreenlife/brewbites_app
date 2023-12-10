from tkinter.ttk import Style
import requests
from bs4 import BeautifulSoup
import datetime
import html
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time

# webdriver setup
def webdriver_init():
    chromedriver = Service("/Users/andrew/Developer/chromedriver")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=chromedriver, options=chrome_options)
    return driver

# date/time variables
current_date_time = datetime.datetime.now()
today = current_date_time.strftime("%A")
today_num = current_date_time.strftime("%d")
if today_num[0] == "0":
    today_num_no_zero = today_num[1]
date_str = current_date_time.strftime("%Y-%m-%d")
date_str_no_zeros = current_date_time.strftime("%Y-%m-") + today_num

# ---------- per-brewery scrape functions ---------- #

# beautifulsoup functions: WORKING

def bauhaus():
    response = requests.get("https://www.bauhausbrewlabs.com/food")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.find("div", class_="sqs-html-content")
    truck = schedule.select(f'p:-soup-contains("{today.upper()}")')[0].get_text().split("-")[1].strip()
    return truck.title()

def fifty_six():
    response = requests.get("https://56brewing.com/events/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.find("div", id=f"tribe-events-calendar-mobile-day-{date_str_no_zeros}")
    truck = schedule.select_one('a:-soup-contains("Food")')
    if truck:
        return truck.get_text().split(":")[1].strip()
    else:
        return "No truck listed for today."

def sociable_ciderwerks(): # resident truck, rarely changes
    response = requests.get("https://sociablecider.com/sociablefoodtruck")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("a", href="/sociablefoodtruck").get_text().strip()
    return element

def lake_monster(): # neighboring vendor, rarely changes
    response = requests.get("https://www.lakemonsterbrewing.com/#intro")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    truck = soup.find_all("p", attrs={'style':'white-space:pre-wrap;'})[2].get_text()
    return truck

def headflyer():
    response = requests.get("https://www.headflyerbrewing.com/food/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    dates = soup.find_all("div", class_="hidden md:block text-4xl fjalla")
    top_date = dates[0].get_text()
    if top_date == today_num:
        truck = soup.find_all("div", class_="font-fjalla pb-2")[0].get_text()
        return truck
    else:
        return "No truck listed for today."
    
# beautifulsoup functions: IN PROGRESS

def bent(): # no current trucks listed, check later
    response = requests.get("https://www.bentbrewstillery.com/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("span", class_="wixui-rich-text__text")
    print(element)

def broken_clock(): # no current trucks listed, check back later
    response = requests.get("https://www.brokenclockbrew.com/events/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find()
    print(element)

def fair_state(): # no current trucks listed, check back later
    response = requests.get("")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find()
    print(element)

# selenium webdriver functions: WORKING

def inbound():
    driver = webdriver_init()
    driver.get("https://inboundbrew.co/inbound-brewco-food-trucks")
    today_element = driver.find_element(By.CLASS_NAME, "today")
    try:
        truck_element = today_element.find_element(By.TAG_NAME, "img")
        truck = truck_element.get_attribute("alt")
        return truck
    except NoSuchElementException:
        return "No truck listed for today."
    finally:
        driver.close()

# selenium webdriver functions: IN PROGRESS

def forgotten_star():
    driver = webdriver_init()
    driver.get("https://www.forgottenstarbrewing.com/food-drink")
    time.sleep(5)
    driver.execute_script("window.scrollTo(0, 2500)")
    time.sleep(30)
    popup_close = driver.find_element(By.ID, "comp-lpjzhokw")
    time.sleep(10)
    popup_close.click()
    time.sleep(10)

    # trucks = WebDriverWait(driver, 30).until(
    #     EC.presence_of_element_located((By.XPATH, "//h3[@class='agenda-item-title mt-0 mb-1 ellipsized bc-agenda-desc-color']"))
    # )
    with open("./html.txt", "w") as file:
        html = driver.page_source
        file.write(html)

    # soup = BeautifulSoup(html, "html.parser")
    # trucks = soup.find_all("h3", class_="agenda-item-title mt-0 mb-1 ellipsized bc-agenda-desc-color")

    # agenda = driver.find_element(By.CLASS_NAME, "agenda modern")
    # events = agenda.find_elements(By.CLASS_NAME, "agenda-item")
    # today = events[0]
    # truck = today.find_element(By.CLASS_NAME, "agenda-item-title mt-0 mb-1 ellipsized bc-agenda-desc-color").text

def insight(): # skipping for now, complicated
    driver = webdriver_init()
    driver.get("https://www.insightbrewing.com/food-trucks-events")
    time.sleep(35)
    expand_button = driver.find_element(By.XPATH, '//*[@id="2023-12-08"]/div/div/div/div/div/div/div/button')
    expand_button.click()


# print food trucks 

print(f"Food trucks around town today:\n"
      f"Bauhaus: {bauhaus()}\n"
      f"56: {fifty_six()}\n"
      f"Sociable: {sociable_ciderwerks()}\n"
      f"Headflyer: {headflyer()}\n"
      f"Lake Monster: {lake_monster()}\n"
      f"Inbound: {inbound()}")