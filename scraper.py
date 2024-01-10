'''Retrieves local brewery food trucks operating today in the Twin Cities, MN.
Publishes data to a hosted json bin.'''
import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import json

# webdriver setup

def webdriver_init():
    # service = Service("/Users/andrew/Developer/chromedriver")
    service = Service(ChromeDriverManager().install())
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

# date-time varialbes for classes

class DateData:
    def __init__(self):
        self.now = datetime.datetime.now()
        self.weekday_str = self.now.strftime("%A")
        self.today_num = self.now.strftime("%d")
        self.today_num_no_zero = None
        if self.today_num[0] == "0":
            self.today_num_no_zero = self.today_num[1]
        self.date_str = self.now.strftime("%Y-%m-%d")
        self.date_str_no_zeros = self.now.strftime("%Y-%m-") + self.today_num
        self.month_year = self.now.strftime("%m-%Y")
        self.month_day = self.now.strftime("%B %-d")
        self.year_month_day = self.now.strftime("%Y-%m-%d")

# -------------------- per-brewery scrape functions -------------------- #

# beautifulsoup:

def bauhaus():
    calendar = DateData()
    weekday_str = calendar.weekday_str

    response = requests.get("https://www.bauhausbrewlabs.com/food")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.find("div", class_="sqs-html-content")
    truck = schedule.select(
        f'p:-soup-contains("{weekday_str.upper()}")')[0].get_text().split("-")[1].strip()
    return truck.title()


def elm_creek():
    calendar = DateData()
    today_num = calendar.today_num
    if calendar.today_num_no_zero:
        today_num = calendar.today_num_no_zero

    response = requests.get("https://www.elmcreekbrewing.com/events")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    event_strings = []

    event_list = soup.find("div", class_="eventlist eventlist--upcoming")
    date_elements = event_list.find_all(
        "div", class_="eventlist-datetag-startdate eventlist-datetag-startdate--day")[:5]

    matching_date_elements = [
        element for element in date_elements if element.get_text() == today_num]

    for element in matching_date_elements:
        container = element.parent.parent.parent.parent
        event = container.find("a", class_="eventlist-title-link").get_text()
        event_strings.append(event)

    if event_strings:
        non_trucks = ["Kegs & Eggs", "Board Games + Adult Coloring Night", "Board Games + Adult Coloring Night ", "Trivia Mafia",
                      "Trivia Mafia ", "Meat Raffle", "Essential Oils Roller Making", "SEEK Sunday"]
        event_strings = [
            string for string in event_strings if string not in non_trucks]
        for string in event_strings:
            if "Live Music" in string:
                event_strings.remove(string)

    if event_strings:
        return event_strings[0]
    else:
        return "No food truck listed for today."


def fifty_six():
    response = requests.get("https://56brewing.com/events/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    today_element = soup.find(
        "div", "tribe-events-calendar-month__day tribe-events-calendar-month__day--current")

    try:
        food_element = today_element.find(
            'a', attrs={'title': lambda value: value and 'Food' in value})
        truck = food_element.get_text().split(":")[1].strip()
        return truck
    except ValueError:
        return "No food truck listed for today."


def sociable_ciderwerks():  # resident truck, rarely changes
    response = requests.get("https://sociablecider.com/sociablefoodtruck")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("a", href="/sociablefoodtruck").get_text().strip()
    return element


def lake_monster():  # neighboring vendor, rarely changes
    response = requests.get("https://www.lakemonsterbrewing.com/#intro")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    truck = soup.find_all(
        "p", attrs={'style': 'white-space:pre-wrap;'})[2].get_text().strip()
    return truck


def headflyer():
    calendar = DateData()
    today_num = calendar.today_num

    response = requests.get("https://www.headflyerbrewing.com/food/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    dates = soup.find_all("div", class_="hidden md:block text-4xl fjalla")
    try:
        top_date = dates[0].get_text()
        if top_date == today_num:
            truck = soup.find_all(
                "div", class_="font-fjalla pb-2")[0].get_text()
            return truck
        else:
            return "No food truck listed for today."
    except IndexError:
        return "No food truck listed for today."


def blackstack():
    calendar = DateData()
    today_num = calendar.today_num
    today_num_no_zero = calendar.today_num_no_zero

    response = requests.get("https://www.blackstackbrewing.com/events")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    if today_num_no_zero:
        date_element = soup.find(
            "div", attrs={'data-hook': f'calendar-day-{today_num_no_zero}'})
    else:
        date_element = soup.find(
            "div", attrs={'data-hook': f'calendar-day-{today_num}'})

    if date_element:
        truck = date_element.find(
            "div", attrs={'data-hook': 'cell-event-title'}).get_text()
        return truck
    else:
        return "No food truck listed for today."


# beautifulsoup: not in use

def bent():  # no current trucks listed, check later
    response = requests.get("https://www.bentbrewstillery.com/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find("span", class_="wixui-rich-text__text")
    print(element)


def broken_clock():  # no current trucks listed, check back later
    response = requests.get("https://www.brokenclockbrew.com/events/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find()
    print(element)


def fair_state():  # no current trucks listed, check back later
    response = requests.get("")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    element = soup.find()
    print(element)


# selenium webdriver:

def bad_weather():
    calendar = DateData()
    month_year = calendar.month_year

    driver = webdriver_init()
    driver.get(
        f"https://badweatherbrewery.com/events?view=calendar&month={month_year}")

    try:
        today_element = driver.find_element(
            By.XPATH, "//td[contains(@class, 'today')]")
        truck_element = today_element.find_element(
            By.XPATH, ".//span[contains(@class, 'item-title') and contains(text(), '(Food Truck)')]")
        truck = truck_element.text.split(")")[1].strip()
        driver.close()
        return truck
    except NoSuchElementException:
        driver.close()
        return "No food truck listed for today."


def inbound():
    driver = webdriver_init()
    driver.get("https://inboundbrew.co/inbound-brewco-food-trucks")
    time.sleep(2)
    try:
        today_element = driver.find_element(
            By.XPATH, "//td[contains(@class, 'today')]")
        truck_element = today_element.find_element(By.TAG_NAME, "img")
        truck = truck_element.get_attribute("alt")
        return truck
    except NoSuchElementException:
        return "No food truck listed for today."
    finally:
        driver.close()


def steeltoe():
    driver = webdriver_init()
    driver.get("https://www.steeltoebrewing.com/")

    time.sleep(2)

    truck = "No food truck listed for today."

    today_element = driver.find_element(
            By.XPATH, "//td[contains(@class, 'today')]")
    
    try:
        truck_element = today_element.find_element(
            By.XPATH, ".//a[contains(@class, 'flyoutitem-link') and contains(text(), 'Food Truck')]")

        truck_text = truck_element.get_attribute(
            "textContent")

        if "TBD" in truck_text:
            truck = "Food Truck TBD"
        else:
            truck = truck_text.split("-")[0].strip()
    except NoSuchElementException:
        try:
            truck_element = today_element.find_element(
                By.XPATH, ".//a[contains(@class, 'flyoutitem-link') and contains(text(), 'Pop-Up')]")
            
            truck = truck_element.get_attribute(
            "textContent")
        except NoSuchElementException:
            pass

    return truck


def alloy():
    calendar = DateData()
    month_year = calendar.month_year

    driver = webdriver_init()
    driver.get(
        f"https://www.alloybrewingcompany.com/taproom?view=calendar&month={month_year}")

    time.sleep(2)

    try:
        today_element = driver.find_element(
            By.XPATH, "//td[contains(@class, 'today')]")
        truck_element = today_element.find_element(
            By.XPATH, ".//a[contains(@class, 'flyoutitem-link') and contains(text(), 'Food Truck')]")
        truck = truck_element.get_attribute(
            "textContent").split(":")[1].strip()
        driver.close()
        return truck
    except NoSuchElementException:
        driver.close()
        return "No food truck listed for today."


def forgotten_star():
    calendar = DateData()
    today_num = calendar.today_num

    driver = webdriver_init()
    driver.get("https://www.forgottenstarbrewing.com/food-drink")
    driver.execute_script("window.scrollTo(0, 2500)")

    time.sleep(5)

    iframe = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//iframe[@class="nKphmK" and @title="Calendar" and @aria-label="Calendar"]')))
    driver.switch_to.frame(iframe)

    top_date = driver.find_element(
        By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div/div[1]/div[1]/div/div[1]/p").text
    if today_num == top_date:
        truck = driver.find_element(
            By.XPATH, "/html/body/div/div[1]/div/div[2]/div/div/div[1]/div[3]/h3").text
        driver.close()
        return truck
    else:
        driver.close()
        return "No food truck listed for today."


def insight():
    calendar = DateData()
    date = calendar.year_month_day

    driver = webdriver_init()
    driver.get("https://www.insightbrewing.com/food-trucks-events")

    time.sleep(5)

    # switch to calendar iframe
    calendar_iframe_rule = (
        By.XPATH, "/html/body/div/div/div[3]/div/main/div/div/div/div[2]/div/div/div/section[1]/div[2]/div/div[4]/iframe")
    calendar_iframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(calendar_iframe_rule))
    driver.switch_to.frame(calendar_iframe)

    # find and click expand button for today's date
    try:
        date_element = driver.find_element(
            By.XPATH, f"//td[contains(@id, '{date}')]")
        button_element = date_element.find_element(By.TAG_NAME, "button")
        button_element.click()
    except NoSuchElementException:
        return "No food truck listed for today."

    # check events within subframe for food trucks, return truck if match
    events_subframe = driver.find_elements(
        By.XPATH, "//div[contains(@class, 'CalendarPopover')]")[2]
    event_elements = events_subframe.find_elements(
        By.XPATH, ".//div[contains(@class, 'EventTitle')]")
    key_phrases = ["Food Truck", "FoodTruck", "food truck",
                   "Philly Express", "Mirasol Mexican Grill", "Brick Oven Pizza Bus"]
    truck = ""
    for element in event_elements:
        for phrase in key_phrases:
            if phrase in element.text:
                truck = element.text
                break

    driver.close()

    if truck:
        return truck
    else:
        return "No food truck listed for today."

# ------------------------------- CORE ------------------------------- #


def scrape():
    print(f"{timestamp()} | Attempting scrape...")

    data = {
        f"56": fifty_six(),
        f"Alloy": alloy(),
        f"Bad Weather": bad_weather(),
        f"Bauhaus": bauhaus(),
        f"BlackStack": blackstack(),
        f"Elm Creek": elm_creek(),
        f"Forgotten Star": forgotten_star(),
        f"Headflyer": headflyer(),
        f"Inbound": inbound(),
        f"Insight": insight(),
        f"Lake Monster": lake_monster(),
        f"Sociable Ciderwerks": sociable_ciderwerks(),
        f"Steel Toe": steeltoe()
    }

    json_data = json.dumps(data)
    print(f"{timestamp()} | Scrape successful.")
    return json_data


def publish(data):
    print(f"{timestamp()} | Attempting publish...")

    json_bin = "https://api.jsonbin.io/v3/b/659b6e0a1f5677401f18ffe1"

    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': '$2a$10$iTnNq06UFXSRHIYKj1EoCuNZEjdkvpZLt9rWEJva7c08HOEdwVDJq'
    }
    response = requests.put(json_bin, data=data, headers=headers)

    if response.status_code == 200:
        print(f"{timestamp()} | Publish successful.")
    else:
        print(f"{timestamp()} | Publish failed.")
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}\n")


def fetch():
    print(f"{timestamp()} | Fetching data...")

    json_bin = "https://api.jsonbin.io/v3/b/659b6e0a1f5677401f18ffe1"

    headers = {
        'Content-Type': 'application/json',
        'X-Master-Key': '$2a$10$iTnNq06UFXSRHIYKj1EoCuNZEjdkvpZLt9rWEJva7c08HOEdwVDJq'
    }

    response = requests.get(json_bin, headers=headers)

    if response.status_code == 200:
        print(f"{timestamp()} | Fetch successful.")
        print(f"Current published data:\n{response.text}")
    else:
        print(f"{timestamp()} | Fetch failed.")
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}\n")


def timestamp():
    return datetime.datetime.now().strftime('%m/%d/%Y - %H:%M')


if __name__ == "__main__":
    while True:
        hour = datetime.datetime.now().hour
        if hour == 11:
            truck_data = scrape()
            pretty_truck_data = json.dumps(truck_data, indent=2)
            print("\nScraped data:\n")
            print(f"{pretty_truck_data}\n")
            if truck_data:
                publish(truck_data)
            print("Script will run again in 24 hours.\n")
            time.sleep(86400)
        else:
            print(
                f"{timestamp()} | Current time not check time. Retrying in 1 hour.\n")
            time.sleep(3600)