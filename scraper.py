'''Retrieves local brewery food trucks operating today in the Twin Cities, MN.'''
import requests
from bs4 import BeautifulSoup
import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
import time
import requests
import json

# webdriver setup
def webdriver_init():
    chromedriver = Service("/Users/andrew/Developer/chromedriver")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
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

# -------------------- per-brewery scrape functions -------------------- #

# beautifulsoup: WORKING

def bauhaus():
    response = requests.get("https://www.bauhausbrewlabs.com/food")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.find("div", class_="sqs-html-content")
    truck = schedule.select(f'p:-soup-contains("{today.upper()}")')[0].get_text().split("-")[1].strip()
    return truck.title()

def elm_creek():
    response = requests.get("https://www.elmcreekbrewing.com/events")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    today_num = current_date_time.strftime("%d")
    event_strings = []

    event_list = soup.find("div", class_="eventlist eventlist--upcoming")
    date_elements = event_list.find_all("div", class_="eventlist-datetag-startdate eventlist-datetag-startdate--day")

    if today_num[0] == "0":
        today_num = today_num[1]
    today_elements = [element for element in date_elements if element.get_text() == today_num]

    for element in today_elements:
        container = element.parent.parent.parent.parent
        event = container.find("a", class_="eventlist-title-link").get_text()
        event_strings.append(event)
    
    print(event_strings)


def fifty_six():
    response = requests.get("https://56brewing.com/events/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    schedule = soup.find("div", id=f"tribe-events-calendar-mobile-day-{date_str_no_zeros}")
    if schedule:
        truck = schedule.select_one('a:-soup-contains("Food")')
        if truck:
            return truck.get_text().split(":")[1].strip()
        else:
            return "No truck listed for today."
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
    truck = soup.find_all("p", attrs={'style':'white-space:pre-wrap;'})[2].get_text().strip()
    return truck

def headflyer():
    response = requests.get("https://www.headflyerbrewing.com/food/")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    dates = soup.find_all("div", class_="hidden md:block text-4xl fjalla")
    try:
        top_date = dates[0].get_text()
        if top_date == today_num:
            truck = soup.find_all("div", class_="font-fjalla pb-2")[0].get_text()
            return truck
        else:
            return "No truck listed for today."
    except IndexError:
        return "No food truck listed for today."
    
def blackstack():
    response = requests.get("https://www.blackstackbrewing.com/events")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")

    if today_num[0] == "0":
        today_num_no_zero = today_num[1]
        date_element = soup.find("div", attrs={'data-hook':f'calendar-day-{today_num_no_zero}'})
    else:
        date_element = soup.find("div", attrs={'data-hook':f'calendar-day-{today_num}'})
    
    truck = date_element.find("div", attrs={'data-hook':'cell-event-title'}).get_text()
    return(truck)


# beautifulsoup: IN PROGRESS

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

def bad_weather(): # may need to switch to webdriver...
    response = requests.get(f"https://www.badweatherbrewery.com/events?view=calendar&month={current_date_time.strftime('%m-%Y')}")
    html = response.text
    soup = BeautifulSoup(html, "html.parser")
    calendar = soup.find("div", class_="yui3-u-1")
    # today_element = calendar.find("div", class_="marker-daynum", string=today_num)
    # day_events = element.next_element
    return calendar

    # driver = webdriver_init()
    # driver.get(f"https://www.badweatherbrewery.com/events?view=calendar&month={current_date_time.strftime('%m-%Y')}")
    # today_element = driver.find_element(By.XPATH, f'//div[@class="marker-daynum" and text()={today_num}]')
    # # day_events = element.next_element
    # return today_element


# selenium webdriver: WORKING

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

def steeltoe():
    driver = webdriver_init()
    driver.get("https://www.steeltoebrewing.com/")

    truck = ""
    pop_up = ""

    if today_num[0] == "0":
        today_num_no_zero = today_num[1]
        element = driver.find_element(By.XPATH, f"//div[@class='marker-daynum' and contains(text(), '{today_num_no_zero}')]")
    else:
        element = driver.find_element(By.XPATH, f"//div[@class='marker-daynum' and contains(text(), '{today_num}')]")

    grandparent_element = element.find_element(By.XPATH, "../..")

    try:
        truck = grandparent_element.find_element(By.XPATH, "//span[@class='item-title' and contains(text(), 'Food Truck')]").text
        driver.close()
        return truck
    except NoSuchElementException:
        return "No food truck listed for today."

def alloy():
    month_year = current_date_time.strftime("%m-%Y")
    driver = webdriver_init()
    driver.get(f"https://www.alloybrewingcompany.com/taproom?view=calendar&month={month_year}")
    
    if today_num[0] == "0":
        today_num_no_zero = today_num[1]
        element = driver.find_element(By.XPATH, f"//div[@class='marker-daynum' and contains(text(), '{today_num_no_zero}')]")
    else:
        element = driver.find_element(By.XPATH, f"//div[@class='marker-daynum' and contains(text(), '{today_num}')]")

    grandparent_element = element.find_element(By.XPATH, "../..")

    try:
        truck = grandparent_element.find_element(By.XPATH, "//span[@class='item-title' and contains(text(), 'Food Truck')]").text
        driver.close()
        return truck
    except NoSuchElementException:
        return "No food truck listed for today."

# selenium webdriver: IN PROGRESS

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

# ------------------------------- CORE ------------------------------- #

def scrape():
    data = {
        f"56": fifty_six(),
        f"alloy": alloy(),
        f"bauhaus": bauhaus(),
        f"blackstack": blackstack(),
        f"headflyer": headflyer(),
        f"inbound": inbound(),
        f"lake monster": lake_monster(),
        f"sociable ciderwerks": sociable_ciderwerks(),
        f"steel toe": steeltoe()
    }

    json_data = json.dumps(data)
    return json_data

def publish(data):
    response = requests.post("https://api.npoint.io/7ba92b78266e329bc829", data=data)
    return response

def timestamp():
    return datetime.datetime.now().strftime('%m/%d/%Y - %H:%M')

if __name__ == "__main__":
    # while True:
    #     hour = datetime.datetime.now().hour
    #     if hour == 9:
    #         print(f"{timestamp()} | Attempting scrape...")
    #         truck_data = scrape()
    #         if truck_data:
    #             print(f"{timestamp()} | Scrape successful.")
    #             print(f"\nScraped data: {truck_data}\n")
    #             print(f"{timestamp()} | Attempting publish...")
    #             response = publish(truck_data)
    #             if response.status_code == 200:
    #                 print(f"{timestamp()} | Publish successful.")
    #             else:
    #                 print(f"{timestamp()} | Publish failed.")
    #                 print(f"Error: {response.status_code}")
    #                 print(f"Response: {response.text}\n")
    #         else:
    #             print(f"{timestamp()} | Scrape unsuccessful.\n")
    #         print("Script will run again in 24 hours.\n")
    #         time.sleep(86400)
    #     else:
    #         print(f"{timestamp()} | Current time not check time. Retrying in 1 hour.\n")
    #         time.sleep(3600)
    elm_creek()