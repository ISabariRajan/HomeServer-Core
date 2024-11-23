# from selenium import webdriver
# from webdriver_manager.chrome import ChromeDriverManager
# from webdriver_manager.core.os_manager import ChromeType

from selenium.webdriver import ChromeOptions, Chrome, Remote
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as BraveService
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from Selenium_Scraper import Scraper

from time import sleep
from bs4 import BeautifulSoup
from datetime import datetime
from json import loads, dumps
import traceback
import pandas as pd
import re
from phonenumbers import parse
from phonenumbers.phonenumberutil import region_code_for_country_code, region_code_for_number
import pycountry
from globals import join, dirname


curr_dir = dirname(__file__)
chrome_install_location = join(curr_dir, "chrome-linux64")
chromedriver_install_location = join(curr_dir, "chromedriver-linux64/chromedriver")
chrome_headless_shell_install_location = join(curr_dir, "chrome-headless-shell-linux64")
remote_location = "http://selenium:4444/wd/hub"
user_data_dir = "/home/seluser/.config/google-chrome/Default"

scrapper = Scraper(browser="chrome", remote=remote_location, user_data_dir=user_data_dir)

def clean_phone_number(number):
    number = f"{number}"
    if not number.startswith("+"):
        index = number.find("+")
        if index != -1:
            number = number[index:]
            index = number.find('"')
            if index != -1:
                number = number[:index]
        else:
            return None
    return re.sub(r'\D', "", number)

def extract_phone_number_details(number: str):
    print(f"Extracting Details for {number}")
    number = clean_phone_number(number)
    try:
        number = int(number)
    except:
        return {
            "national_number": f"{number}",
            "Country": f"UNKNOWN",
            "number": f"{number}"
        }

    if number:
        number = f"+{number}"
        pn = parse(number)
        country_code = pn.country_code
        country = region_code_for_country_code(country_code)
        country = pycountry.countries.get(alpha_2=country)
        return {
            "national_number": f"{pn.national_number}",
            "Country": f"{country.name} (+{pn.country_code})",
            "number": f"{number}"
        }

def load_json_from_file(file_path: str):
    lines = []
    with open(file_path, "r") as f:
        lines = f.readlines()
    return loads("".join(lines))

# def get_driver(headless=False):
#     options = ChromeOptions()
#     options.binary_location = f"{chrome_install_location}/chrome"
#     options.add_argument(f"user-data-dir={join(curr_dir, '.config/Default')}")
#     if headless:
#         options.binary_location = f"{chrome_headless_shell_install_location}/chrome-headless-shell"
#         options.add_argument("--headless")
#         # options.add_argument("--remote-control")
#         options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
#     options.add_argument("--no-sandbox")
#     options.add_argument("--disable-dev-shm-usage")
#     print(options)
#     return Chrome(service=BraveService(chromedriver_install_location), options=options)

def get_driver(headless=False):
    options = ChromeOptions()
    # options.binary_location = f"{chrome_install_location}/chrome"
    options.add_argument(f"user-data-dir=/home/seluser/.config/google-chrome/Default")
    if headless:
        # options.binary_location = f"{chrome_headless_shell_install_location}/chrome-headless-shell"
        options.add_argument("--headless")
        # options.add_argument("--remote-control")
        options.add_argument("user-agent=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    print(options)
    return Remote("http://selenium:4444/wd/hub", options=options)

def wait_for_element_to_load(search_value: str, wait_time=10, by=By.XPATH):
    try:
        wait = WebDriverWait(driver, wait_time)
        return wait.until(EC.visibility_of_element_located((by, search_value)))
    except TimeoutException as e:
        return None

def perform_scroll(element: WebElement, value):
    # print(f"Scrolling {value}")
    driver.execute_script("arguments[0].scrollTop = arguments[1]", element, value)
    sleep(1)

def S_BS4(element: WebElement):
    return BS4(html=element.get_attribute("outerHTML"))

def BS4(html: str):
    return BeautifulSoup(html, features="html.parser")

def get_text(element: WebElement):
    html = element.get_attribute("outerHTML")
    soup = BS4(html)
    return soup.text.strip()

def get_children_contains_text(element: WebElement, test_string: str):
    children = element.find_elements(By.XPATH, './*')
    test_string = test_string.lower()
    return get_element_contain_text(children, test_string)

def get_element_contain_text(elements: list[WebElement], test_string: str):
    test_string = test_string.lower()
    for element in elements:
        if test_string in get_text(element).lower():
            return element
    return None

def write_group_info_to_json():
    with open("group_info.json", "w") as f:
        f.write(dumps(group_phone_numbers, indent=2))


def grandchildren(element: WebElement, index=0):
    return element.find_elements(By.XPATH, './*')[index].find_elements(By.XPATH, './*')

def extract_hidden_number_from_member_list(element: WebElement, name: str, number: str):
    name = clean_phone_number(name)
    try:
        name = int(name)
        number = f"+{name}"
    except:
        click(element)
        appliation = driver.find_element(By.XPATH, '//div[@role="application"]')
        elements = appliation.find_elements(By.TAG_NAME, "li")
        message_element = get_element_contain_text(elements, "message")
        if message_element:
            number = get_text(message_element).replace("message", "").strip()
        click(element)
    return name, number

def get_number_detail_from_list_element(element: WebElement, group_number_details):
    if "Past members" in get_text(element):
        return
    divs = element.find_elements(By.XPATH, "./*")
    first_divs = divs[0].find_elements(By.XPATH, "./*")
    second_divs = divs[1].find_elements(By.XPATH, "./*")
    desg = "Member"
    name = get_text(first_divs[0])
    if name == "You":
        return
    if len(first_divs) == 2:
        desg = get_text(first_divs[1])

    status = get_text(second_divs[0])
    number = get_text(second_divs[1])
    if (number in group_number_details) or (name in group_number_details):
        return
    if not number:
        name, number = extract_hidden_number_from_member_list(element, name, number)
    return {
        "name": name,
        "desg": desg,
        "status": status,
        "number": number
    }

def check_and_close_members_modal(driver:WebDriver):
    try:
        modal_element = driver.find_element(By.XPATH, '//div[@data-animate-modal-body="true"]')
    except:
        return True
    inner_elements = modal_element.find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')
    print(f"Closing Modal")
    header_element = inner_elements[0]
    close_button = header_element.find_element(By.XPATH, './/div[@role="button"]')
    close_button.click()
    sleep(2)
    return True

def find_and_click_past_members(driver: WebDriver, contact_grid: WebElement):
    buttons = contact_grid.find_elements(By.TAG_NAME, "button")
    for button in buttons:
        text = get_text(button).replace(" ", "").lower()
        if "viewpastmembers" in text:
            button.click()
            print(f"Click Past members")
            return extract_member_details_from_modal(driver, 9999, skip_inner=True)

    return None, None

def extract_member_details_from_modal(driver: WebDriver, members_count, skip_inner=False):
    print(f"Modal Open")
    modal_element = wait_for_element_to_load('//div[@data-animate-modal-body="true"]')
    if not modal_element:
        return None, None
    group_number_details = {}
    skip_number_details = {}
    scroll_value = 0
    can_loop = True
    prev_count = 0
    skip_chance = 1
    additional_chance = 0
    inner_done = False
    while can_loop and skip_chance > 0:
        inner_elements = modal_element.find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')
        contact_grid = inner_elements[2]
        if (not skip_inner) and (not inner_done):
            skip_number_details, _ = find_and_click_past_members(driver, contact_grid)
            modal_element = wait_for_element_to_load('//div[@data-animate-modal-body="true"]')
            inner_elements = modal_element.find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')
            contact_grid = inner_elements[2]
            perform_scroll(contact_grid, scroll_value)
            inner_done = True

        contacts = contact_grid.find_elements(By.XPATH, './/div[@role="listitem"]')
        for element in contacts:
            try:
                element = element.find_element(By.XPATH, './/div[@role="button"]')
            except:
                continue
            element = element.find_element(By.TAG_NAME, "div").find_elements(By.XPATH, "./*")[1]
            number_detail = get_number_detail_from_list_element(element, group_number_details)
            if number_detail:
                number = number_detail["number"]
                if number not in group_number_details:
                    group_number_details[number] = number_detail
        count = len(group_number_details.keys())
        can_loop = count < (members_count - 1)
        if count == prev_count:
            if additional_chance < 2:
                additional_chance += 1
                print(f"Giving additional chance")
            elif skip_inner:
                can_loop = False
                skip_chance = 0
            skip_chance -= 1
            scroll_value -= 1000
        else:
            skip_chance += 1
            scroll_value += 1000
        perform_scroll(contact_grid, scroll_value)
        prev_count = count
    check_and_close_members_modal(driver)
    return group_number_details, skip_number_details

def get_members_count(driver:WebDriver):
    print(f"Getting Member count")
    complementary_element = wait_for_element_to_load('.//div[@role="complementary"]')
    if complementary_element:
        section = complementary_element.find_element(By.TAG_NAME, "section")
        perform_scroll(section, 1000)
        members = get_children_contains_text(section, "memberssearch")
        print(f"Got Members: {members}")
        if members:
            members = members.find_element(By.XPATH, './/div[@role="button"]')
            members_count = get_text(members)
            members_count = members_count.replace("memberssearch", "").replace(",", "").strip()
            check_and_close_members_modal(driver)
            click(members)
            return int(members_count)
    return 0

def get_contacts(group_name: str):
    print(f"Getting Contacts for Group {group_name}")
    members_count = get_members_count(driver)
    print(f"Members: {members_count}")
    if members_count:
        group_phone_numbers[group_name] = {
            "status": "started",
            "numbers": {},
            "skip_numbers": {},
            "total_members": members_count
        }
        numbers, skip_numbers = extract_member_details_from_modal(driver, members_count)
        group_phone_numbers[group_name]["numbers"] = numbers
        group_phone_numbers[group_name]["skip_numbers"] = skip_numbers
        group_phone_numbers[group_name]["status"] = "completed"
    else:
        group_phone_numbers[group_name] = {
            "status": "completed",
            "numbers": {},
            "skip_numbers": {},
            "total_members": 0
        }

def click(element: WebElement):
    try:
        element.click()
        sleep(2)
    except StaleElementReferenceException as e :
        print(f"Stale Element: {element}")
    except Exception as e:
        pass


def get_group_info(driver: WebDriver, group_name):
    start = datetime.now()
    print(f"Get group info started @{start}")
    main_element = driver.find_element(By.ID, "main")
    button = main_element.find_elements(By.XPATH, './/header//div[@role="button"]')[1]
    click(button)
    # group_name = button.find_element(By.XPATH, './/span[@dir="auto"]').text
    # print(f"Group: {group_name}")
    get_contacts(group_name)
    write_group_info_to_json()
    end = datetime.now()
    print(f"Get group info ended @{end}")
    print(f"Time Elapsed: {end - start}")

def process_groups(elements: list[WebElement]):
    for element in elements:
        group_element = element.find_element(By.XPATH, './/div[@role="gridcell"]')
        group_element = group_element.find_element(By.XPATH, './/span[@dir="auto"]')
        group_name = get_text(group_element)
        # Skip if the group is already processed
        if group_name in group_phone_numbers:
            group_details = group_phone_numbers[group_name]
            status = group_details["status"].lower()
            total_members = group_details["total_members"]
            total_numbers = len(group_details["numbers"].keys())
            if (status != "completed"):
                print(f"Running Because Group {group_name} Status is {status}")
                click(element)
                get_group_info(driver, group_name)
            elif (total_members - 1 != total_numbers):
                print(f"Running Because Group {group_name} has member mismatch {total_members} != {total_numbers}")
                click(element)
                get_group_info(driver, group_name)
            else:
                print(f"Skipping Group {group_name}, Already Present")
        else:
            print(f"Running Because Group {group_name} is not started")
            click(element)
            get_group_info(driver, group_name)

def get_groups_from_side_pane():
    print(f"Getting group info from side-panel")
    side_element = driver.find_element(By.XPATH, '//div[@id="side"]')
    side_pane = side_element.find_element(By.ID, "pane-side")
    grid_element = side_pane.find_element(By.XPATH, './/div[@role="grid"]')
    elements = side_pane.find_elements(By.XPATH, './/div[@role="listitem"]')
    process_groups(elements)
    return side_pane, grid_element.get_attribute("aria-rowcount")


def get_groups():
    print(f"Getting groups")
    vertical_ordinate = 0
    can_loop = True
    skip_chance = 0
    prev_count = 0
    additional_chance = 0
    while can_loop:
        side_pane, row_count = get_groups_from_side_pane()
        sleep(2)
        count = len(group_phone_numbers.keys())
        can_loop = count < int(row_count)
        # if can_loop and (prev_count == count):
        #     if additional_chance < 2:
        #         additional_chance += 1
        #         print(f"Giving additional chance")
        #     skip_chance -= 1
        #     vertical_ordinate -= 800
        # else:
        skip_chance += 1
        vertical_ordinate += 800
        perform_scroll(side_pane, vertical_ordinate)
        prev_count = count

def find_and_click_group_button(side_element: WebElement):
    group_buttons = side_element.find_elements(By.TAG_NAME, 'button')
    for button in group_buttons:
        if "Groups" == button.text:
            click(button)
            break


def capture_whatsapp_data():
    print(f"Started Capturing Whatsapp Data")
    driver.get("https://web.whatsapp.com")
    
    print(f"1. Opening Web-browser")
    side_element = wait_for_element_to_load('//div[@id="side"]', 200)
    # wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@id="side"]')))
    
    print(f"2. Side panel available, Finding and clicking 'Group' Button")
    find_and_click_group_button(side_element)

    # whatsapp_groups = get_whatsapp_groups(side_element)
    # whatsapp_groups = {'Saree discussed ', 'Sasti sarees wholesale group 2', 'MK TEX', 'SV PATTU SAREES CUSTOMERS GROUP ', 'Cotten Saree', 'Product Discussions', 'Singhaar pure Kanchi silks', 'WHOLESALERS GROUP 87', 'Shobha Creation- Saree wholesaler ', 'Nithi Tex-4', 'Siranjeevi Textiles', '🚩Jarimari\xa0\xa0ki Amma adi shakti 🚩', 'SSPT FT G51', 'Thaya Thread Reseller Kanchipuram Silks', 'sri Sakthi Pugazh Tex G67', 'Mahadev fashion girl', 'Our Price 💵💵💸💸📈📈📈', 'Heathy/Plant/Cook/Exercis', 'Introduction Reseller group', 'PRIYAM TEX 2', 'GOPINATH FASHION (102) ', 'Guess the price', 'Premium ₹15,001 - 40,000 Sarees', 'Thalaiva 2024', 'My Self Saree Details', 'RICH FEELERS HOUSEHOLD', 'Sri Murugan Tex - 22', 'Bhagalpur manufacture', 'Vmy Resellers 4th Grp', 'MURUGAN. TEX 1', 'Confirm Order', '🛍️YATHAV TEX 02🛍️', 'Test', 'Thaya Thread', 'Vishnu Sarees 777', 'Murugan cotton sarees', 'Luxury ₹40,001 & above Sarees', 'Charlesthayafashion1️⃣', 'Lilian silk saree All', 'Mathi Tex G2', 'SGS Textiles G _ 2🛍️', 'Elegant ₹5,001 - 15,000 Sarees', 'KumKum Creation 5', 'Marriage - Anand Fam', 'ஜெரிமெரி தமிழ் உறவுகள்❤️ Jarimari Tamil Relations❤️', 'SVT SILKS Elampillai\xa0\xa0G01', 'Dicuss saree', 'Poornas Customer Grp 5701', 'Online Reseller Group Only Manufacturer Banarasi Sarees', 'Sri Lakshmi Sarees', '32-2 816_2024DATA-DRIVE DIGITAL COMPANY ', 'Vishwamukha reseller grp1', '🔥BRAND STORE 🔥✅10✅', '🛫🛬SRI SASTHA TEX 13🛬🛫', 'Kanchi Lakshaya Silks 55', 'Money/Learn/Job/income', 'Kanjivarams group 2', 'Sree Durga silks sarees 🚩 🙏', '🙏AMAAN HANDLOOM 👌', 'NS COTTON 4', 'KHSS Reseller Group', 'Shubham update 10', 'Marriage discussion ', 'House Of Aishwaryam', 'Talk', 'Veedu Parkum Group', 'Kudil Handlooms grp 1', 'Banarasi silk sarees GRP ', 'Me and u', 'Hospital ', 'Home ', 'Entertainment', 'TF High Budget Saree', 'Family business Discuss 😁', 'Kanchi candy silks cus 04', 'Silk saree', 'Test reseller ', 'Food', 'Sarashwathi tex 2', '11 BlackRock Stock Retail and Institutional Club', 'Sampath', 'Group A aishwaryam', 'Bagruprintesareesuits(2)', 'Value ₹399 - 5,000 Sarees', 'Family', '22 SREE PATHIRAKALIAMMAN TEXTILE', 'Pure HANDLOOM SILK SAREES ', 'Life lesson ', 'All Price Range Kanchipuram Saree', 'DNP grp 3', '🥻Ms Silk Saree 6👗'}
    # print(f"3. Got Whatsapp Groups: {whatsapp_groups} \n count: {len(whatsapp_groups)}")
    
    # sleep(10000)
    print(f"3. Capturing Contact Info: ")
    try:
        get_groups()
    except Exception as e:
        print(f"Exception: {e}")
        traceback.print_exc()
        input()
    pass

updated_phone_numbers = {}

def process_phone_numbers(numbers: list, group_name: str):
    if not numbers:
        return

    for number in numbers:
        number_details = numbers[number]
        number_details.update(extract_phone_number_details(number))
        number = number_details["number"]
        if number in updated_phone_numbers:
            existing_details = updated_phone_numbers[number]
            existing_details["groups"].append(group_name)
            if existing_details["desg"] != number_details["desg"]:
                existing_details["desg"] += number_details["desg"]
            updated_phone_numbers[number] = existing_details
        else:
            number_details["groups"] = [group_name]
            updated_phone_numbers[number] = number_details

def process_group_phone_numbers():
    for group_name in group_phone_numbers:
        group_details = group_phone_numbers[group_name]
        if "numbers" in group_details:
            process_phone_numbers(group_details["numbers"], group_name)
        if "skip_numbers" in group_details:
            process_phone_numbers(group_details["skip_numbers"], group_name)

    keys = list(updated_phone_numbers.keys())
    columns = updated_phone_numbers[keys[0]].keys()
    output = pd.DataFrame(columns=columns)
    count = 0
    for number in keys:
        data = []
        number_detail = updated_phone_numbers[number]
        for col in columns:
            data.append(f"{number_detail[col]}")
        output.loc[count] = data
        count += 1
    output.to_excel("contacts.xlsx")


if __name__ == "__main__":
    start = datetime.now()
    print(f"Start {start}")
    try:
        group_phone_numbers = load_json_from_file("group_info.json")
    except:
        group_phone_numbers = {}
    print(f"Group Phone Numbers Loaded, Total: {len(group_phone_numbers)}")
    driver = get_driver(headless=True)
    print(driver)
    capture_whatsapp_data()
    process_group_phone_numbers()
    end = datetime.now()
    print(f"End: {end}")
    print(f"Completed in {end - start}")