from inspect import Traceback
import requests
from bs4 import BeautifulSoup
import datetime
import html
from selenium import webdriver
from selenium.webdriver.common.by import By

chrome_options = webdriver.ChromeOptions()
chrome_options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=chrome_options)

current_date_time = datetime.datetime.now()
today = current_date_time.strftime("%A")
today_num = current_date_time.strftime("%d")
if today_num[0] == "0":
    today_num = today_num[1]
date_str = current_date_time.strftime("%Y-%m-%d")

brewery_data = [
    {
    "name": "bauhaus",
    "URL": "https://www.bauhausbrewlabs.com/food",
    "html tag": "p",
    "class rule": "sqsrte-large preFade fadeIn"
    },
    {"name": "headflyer",
     "URL": "https://www.headflyerbrewing.com/food/",
    "html tag": "div",
    "class rule": "font-fjalla pb-2"
    },
    {"name": "forgotten star",
    "URL": "https://www.forgottenstarbrewing.com/food-drink",
    "html tag": "h3",
    "class rule": "agenda-item-title mt-0 mb-1 ellipsized bc-agenda-desc-color"
    },
    {"name": "falling knife",
    "URL": "https://fallingknife.beer/", # no truck schedule on site
    "html tag": None,
    "class rule": None
    },
    {"name": "56",
    "URL": "https://56brewing.com/events/",
    "html tag": None,
    "class rule": None
    },
    {"name": "indeed",
    "URL": "https://www.indeedbrewing.com/",
    "html tag": None,
    "class rule": None
    },
    {"name": "bent brewstillery",
     "URL": "https://www.bentbrewstillery.com/",
    "html tag": None,
    "class rule": None
    },
    {"name": "broken clock",
     "URL": "https://www.brokenclockbrew.com/events/",
    "html tag": None,
    "class rule": None
    },
    {"name": "fair state",
     "URL": "https://fairstate.coop/events/?fwp_event_type=food",
    "html tag": None,
    "class rule": None
    },
    {"name": "sociable ciderwerks",
     "URL": "https://sociablecider.com/sociablefoodtruck",
    "html tag": None,
    "class rule": None
    },
    {"name": "insight",
     "URL": "https://www.insightbrewing.com/food-trucks-events",
    "html tag": None,
    "class rule": None
    }
]

# def make_soup(url):
#     response = requests.get(url)
#     return BeautifulSoup(response.text, "html.parser")

# def get_truck(soup, html_tag, class_rule):
#     try:
#         return soup.find(html_tag, class_=class_rule).get_text()
#     except:
#         return soup.find(html_tag, class_=class_rule)

# for brewery in brewery_data:
#     if brewery["html tag"] and brewery["class rule"]:
#         soup = make_soup(brewery["URL"])
#         truck = get_truck(soup, brewery["html tag"], brewery["class rule"])
#         print(f"{brewery['name'].title()}: {truck}")

# ----------------- fetching rules ----------------- #

def forgotten_star(): # work in progress
    response = requests.get("https://www.forgottenstarbrewing.com/food-drink")
    forgotten_star = response.text
    soup = BeautifulSoup(forgotten_star, "html.parser")
    element = soup.find('h3:contains("Deep Roots")')
    # inner = outer.find("h3", class_="agenda-item-title mt-0 mb-1  bc-agenda-desc-color")
    print(element) 

def bauhaus(): # working
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
    schedule = soup.find("div", class_="tribe-events-calendar-month__day tribe-events-calendar-month__day--current")
    truck = schedule.select_one('a:-soup-contains("Food")').get_text().split(":")[1].strip()
    return truck

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

def sociable_ciderwerks():
    response = requests.get("https://sociablecider.com/sociablefoodtruck")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("a", href="/sociablefoodtruck").get_text().strip()
    return element

def insight():
    response = requests.get("https://www.insightbrewing.com/food-trucks-events")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("div", id={date_str})
    truck = element.find()
    print(element)

def inbound():
    driver.get("https://inboundbrew.co/inbound-brewco-food-trucks")
    today_element = driver.find_element(By.CLASS_NAME, "today")
    truck_element = today_element.find_element(By.TAG_NAME, "img")
    truck = truck_element.get_attribute("alt")
    return truck

print(f"Food trucks around town today:\n"
      f"Bauhaus: {bauhaus()}\n"
      f"56: {fifty_six()}\n"
      f"Sociable: {sociable_ciderwerks()}"
      f"Inbound: {inbound()}")