import pandas as pd
import os
import re
from phonenumbers import parse
from phonenumbers.phonenumberutil import region_code_for_country_code, region_code_for_number
import pycountry
from  threading import Thread

def clean_phone_number(number):
    # Cleaning non numbers
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
    # print(number, column)
    if number:
        number = f"+{number}"
        pn = parse(number)
        country_code = pn.country_code
        country = region_code_for_country_code(country_code)
        country = pycountry.countries.get(alpha_2=country)
        return{
            "national_number": f"{pn.national_number}",
            "Country": f"{country.name} (+{pn.country_code})",
            "number": f"{number}"
        }

def data():
    # df = pd.read_excel("thaya_oil_contact.xlsx", engine="openpyxl", sheet_name=None)
    df = pd.read_excel("thaya_oil_contact.xlsx", engine="openpyxl", sheet_name="ORIGINAL")


    numbers = {}
    output = pd.DataFrame(columns=["Phone Number", "Group Name", "Country", "Full Number"])
    count = 0
    column_names = df.columns.tolist()
    for column in column_names:
        col_data = df[column]
        for number in col_data:
            original_number = number
            number = clean_phone_number(number)
            # print(number, column)
            if number:
                number = f"+{number}"
                pn = parse(number)
                country_code = pn.country_code
                country = region_code_for_country_code(country_code)
                country = pycountry.countries.get(alpha_2=country)
                data = [f"{pn.national_number}", column, f"{country.name} (+{pn.country_code})", number]
                # df = df.append(pd.Series(data, index=df.columns), ignore_index=True)
                print(len(output))
                print(data)
                output.loc[count] = data
                count += 1
    output = output.drop_duplicates(subset=["Full Number"], keep='first', inplace=False)
    output.to_excel("output.xlsx")
    
# from selenium import webdriver
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service as BraveService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType

from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from time import sleep
from bs4 import BeautifulSoup


def find_and_click_group_button(side_element: WebElement):
    group_buttons = side_element.find_elements(By.TAG_NAME, 'button')
    for button in group_buttons:
        if "Groups" == button.text:
            button.click()
            break

def get_contact_info():
    pass

def add_phone_numbers_to_group(group_name, numbers):
    verified_numbers = []
    replacers = ["+", " ", "(", ")", '"', "'", "-"]
    for number in numbers:
        for repl in replacers:
            number = number.replace(repl, "").strip()
        if number == "You":
            continue
        try:
            number = int(number)
        except:
            print(f"{number} is not a Number. Will click and check info")
            return
        verified_numbers.append(number)
    group_phone_numbers[group_name] = {
        "numbers": verified_numbers,
        "status": "completed"
        }
    return True

def perform_click(title: str, button: WebElement, group_name: str):
    print(f"Perform click??")
    if not title:
        print(f"Getting info from title Pane: {title}")
        if title in ["click here for group info", "Announcements"]:
            button.click()
        elif "more" in title:
            button.click()
        else:
            numbers = title.split(",")
            if not add_phone_numbers_to_group(group_name, numbers):
                button.click()
        sleep(2)

def extract_phone_number_from_header_HTML(html:str):
    soup = BeautifulSoup(html, features="html.parser")
    spans = soup.find_all("span")
    group_name = spans[0].get_text().strip()
    title = spans[1].get("title")
    if (group_name in group_phone_numbers) and (group_phone_numbers[group_name]["status"] == "completed"):
        print(f"{group_name} is Completed")
        return group_name
    if title:
        # print(f"Getting info from title Pane: {title}")
        if title in ["click here for group info", "Announcements"]:
            group_phone_numbers[group_name] = {
                "status": "open"
            }
        elif "more" in title:
            group_phone_numbers[group_name] = {
                "status": "open"
            }
        else:
            numbers = title.split(",")
            if not add_phone_numbers_to_group(group_name, numbers):
                group_phone_numbers[group_name] = {
                   "status": "open"
                }

    return group_name


def get_group_info(driver: WebDriver):
    print(f"Get group info")
    main_element = driver.find_element(By.ID, "main")
    button = main_element.find_elements(By.XPATH, './/header//div[@role="button"]')[1]
    button_html = button.get_attribute("outerHTML")
    button.click()
    group_name = button.find_element(By.XPATH, './/span[@dir="auto"]').text
    print(f"Group: {group_name}")
    get_contacts(group_name)

def find_group_info_from_section_HTML(html:str):
    soup = BeautifulSoup(html, features="html.parser")
    ignorers = soup.find_all("div", attrs={"data-ignore-capture":"any"})
    if len(ignorers) < 4:
        pass
    else:
        ignorers[1]

def S_BS4(element: WebElement):
    return BS4(html=element.get_attribute("outerHTML"))

def BS4(html: str):
    return BeautifulSoup(html, features="html.parser")

def get_text(element: WebElement):
    html = element.get_attribute("outerHTML")
    soup = BS4(html)
    return soup.text

def save_element_as_html_file(element: WebElement):
    soup = S_BS4(element)
    with open("output.html", "w") as f:
        f.write(f"{soup}")

def extract_contact_from_HTML(html):
    soup = BS4(html)
    list_items = soup.find_all("div", attrs={"role": "listitem"})

def get_children_contains_text(element: WebElement, test_string):
    children = element.find_elements(By.XPATH, './*')
    for child in children:
        if test_string in get_text(child):
            return child

def get_contacts(group_name: str):
    print(f"Getting Contacts for Group {group_name}")
    can_loop = True
    while can_loop:
        complementary_element = wait_for_element_to_load('.//div[@role="complementary"]')
        section = complementary_element.find_element(By.TAG_NAME, "section")
        perform_scroll(section, 1000)
        members = get_children_contains_text(section, "memberssearch")
        members = members.find_element(By.XPATH, './/div[@role="button"]')
        members_count = get_text(members)
        members_count = members_count.replace("memberssearch", "").strip()
        print(f"Members COunt {members_count}")
        try:
            members_count = int(members_count)
            can_loop = False
        except Exception as e:
            print(f"Loop again Exeption {e}")
    print(f"Memers: {members_count}")
    members.click()
    
    # modal_element = driver.find_element(By.XPATH, '//div[@data-animate-modal-body="true"]')
    print(f"Modal Open")
    modal_element = wait_for_element_to_load('//div[@data-animate-modal-body="true"]')
    group_number_details = {}
    scroll_value = 0
    while len(group_number_details.keys()) < members_count:
        inner_elements = modal_element.find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')
        contact_grid = inner_elements[2]
        # scroll_element = contact_grid.find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0].find_elements(By.XPATH, './*')[0]
        contacts = contact_grid.find_elements(By.XPATH, './/div[@role="listitem"]')
        for element in contacts:
            try:
                element = element.find_element(By.XPATH, './/div[@role="button"]')
            except:
                continue
            element = element.find_element(By.TAG_NAME, "div").find_elements(By.XPATH, "./*")[1]
            divs = element.find_elements(By.XPATH, "./*")
            first_divs = divs[0].find_elements(By.XPATH, "./*")
            second_divs = divs[1].find_elements(By.XPATH, "./*")
            desg = "Member"
            print(f"DIV TEXXT: {get_text(element)}")
            name = get_text(first_divs[0])
            if name == "You":
                continue
            if len(first_divs) == 2:
                desg = get_text(first_divs[1])

            status = get_text(second_divs[0])
            number = get_text(second_divs[1])
            if not number:
                number = f"{name}"
                name = ""
            number_detail = {
                "name": name,
                "desg": desg,
                "status": status,
                "number": number
            }
            group_number_details[number] = (number_detail)
        print(f"Perform Scroll {len(group_number_details.keys())}, {members_count}")
        perform_scroll(contact_grid, scroll_value)
        scroll_value += 1000

    group_phone_numbers[group_name] = group_number_details

def get_group_names_from_element_list(elements: list[WebElement], groups: set):
    try:
        for element in elements:
            group_element = element.find_element(By.XPATH, ".//span[@dir='auto']")
            group_name = group_element.text
            groups.add(group_name)
    except:
        pass

def get_group_names_from_side_pane_HTML(html:str, groups: set):
    print(f"Getting group names from HTML")
    soup = BeautifulSoup(html, features="html.parser")
    list_items = soup.find_all("div", attrs={"role":"listitem"})
    for item in list_items:
        element = item.find("span", attrs={"dir": "auto"})
        groups.add(element.get("title"))

def get_groups_from_side_pane(groups:set, checking=False):
    print(f"Getting group info from side-panel")
    side_element = driver.find_element(By.XPATH, '//div[@id="side"]')
    side_pane = side_element.find_element(By.ID, "pane-side")
    side_pane_html = side_pane.get_attribute("outerHTML")

    grid_element = side_pane.find_element(By.XPATH, './/div[@role="grid"]')
    elements = side_pane.find_elements(By.XPATH, './/div[@role="listitem"]')
    if checking:
        for element in elements:
            element.click()
            sleep(2)
            get_group_info(driver)
        # Thread(target=get_group_names_from_element_list, args=(elements, groups)).start()
        # get_group_names_from_element_list(elements, groups)
    else:
        Thread(target=get_group_names_from_side_pane_HTML, args=(side_pane_html, groups)).start()
    return side_pane, grid_element.get_attribute("aria-rowcount")

def perform_scroll(element: WebElement, value):
    driver.execute_script("arguments[0].scrollTop = arguments[1]", element, value)

def get_groups(groups: set, checking=False):
    print(f"Getting groups")
    vertical_ordinate = 0
    can_loop = True
    while can_loop:
        side_pane, row_count = get_groups_from_side_pane(groups, checking)
        perform_scroll(side_pane, vertical_ordinate)
        # driver.execute_script("arguments[0].scrollTop = arguments[1]", side_pane, vertical_ordinate)
        vertical_ordinate += 100
        sleep(2)
        if checking:
            can_loop = len(group_phone_numbers.keys()) < len(groups)
        else:
            can_loop = len(groups) < 90
        print(f"{groups} \n {len(groups)} \n {int(row_count)}")



def get_whatsapp_groups(side_element: WebElement, checking=False):
    whatsapp_groups = set()
    try:
        get_groups(whatsapp_groups, checking)
    except Exception as e:
        input(e)
    return whatsapp_groups

def capture_whatsapp_data():
    print(f"Started Capturing Whatsapp Data")
    driver.get("https://web.whatsapp.com")
    
    print(f"1. Opening Web-browser")
    side_element = wait_for_element_to_load('//div[@id="side"]')
    # wait.until(EC.visibility_of_element_located((By.XPATH, '//div[@id="side"]')))
    
    print(f"2. Side panel available, Finding and clicking 'Group' Button")
    find_and_click_group_button(side_element)

    # whatsapp_groups = get_whatsapp_groups(side_element)
    whatsapp_groups = {'Saree discussed ', 'Sasti sarees wholesale group 2', 'MK TEX', 'SV PATTU SAREES CUSTOMERS GROUP ', 'Cotten Saree', 'Product Discussions', 'Singhaar pure Kanchi silks', 'WHOLESALERS GROUP 87', 'Shobha Creation- Saree wholesaler ', 'Nithi Tex-4', 'Siranjeevi Textiles', '🚩Jarimari\xa0\xa0ki Amma adi shakti 🚩', 'SSPT FT G51', 'Thaya Thread Reseller Kanchipuram Silks', 'sri Sakthi Pugazh Tex G67', 'Mahadev fashion girl', 'Our Price 💵💵💸💸📈📈📈', 'Heathy/Plant/Cook/Exercis', 'Introduction Reseller group', 'PRIYAM TEX 2', 'GOPINATH FASHION (102) ', 'Guess the price', 'Premium ₹15,001 - 40,000 Sarees', 'Thalaiva 2024', 'My Self Saree Details', 'RICH FEELERS HOUSEHOLD', 'Sri Murugan Tex - 22', 'Bhagalpur manufacture', 'Vmy Resellers 4th Grp', 'MURUGAN. TEX 1', 'Confirm Order', '🛍️YATHAV TEX 02🛍️', 'Test', 'Thaya Thread', 'Vishnu Sarees 777', 'Murugan cotton sarees', 'Luxury ₹40,001 & above Sarees', 'Charlesthayafashion1️⃣', 'Lilian silk saree All', 'Mathi Tex G2', 'SGS Textiles G _ 2🛍️', 'Elegant ₹5,001 - 15,000 Sarees', 'KumKum Creation 5', 'Marriage - Anand Fam', 'ஜெரிமெரி தமிழ் உறவுகள்❤️ Jarimari Tamil Relations❤️', 'SVT SILKS Elampillai\xa0\xa0G01', 'Dicuss saree', 'Poornas Customer Grp 5701', 'Online Reseller Group Only Manufacturer Banarasi Sarees', 'Sri Lakshmi Sarees', '32-2 816_2024DATA-DRIVE DIGITAL COMPANY ', 'Vishwamukha reseller grp1', '🔥BRAND STORE 🔥✅10✅', '🛫🛬SRI SASTHA TEX 13🛬🛫', 'Kanchi Lakshaya Silks 55', 'Money/Learn/Job/income', 'Kanjivarams group 2', 'Sree Durga silks sarees 🚩 🙏', '🙏AMAAN HANDLOOM 👌', 'NS COTTON 4', 'KHSS Reseller Group', 'Shubham update 10', 'Marriage discussion ', 'House Of Aishwaryam', 'Talk', 'Veedu Parkum Group', 'Kudil Handlooms grp 1', 'Banarasi silk sarees GRP ', 'Me and u', 'Hospital ', 'Home ', 'Entertainment', 'TF High Budget Saree', 'Family business Discuss 😁', 'Kanchi candy silks cus 04', 'Silk saree', 'Test reseller ', 'Food', 'Sarashwathi tex 2', '11 BlackRock Stock Retail and Institutional Club', 'Sampath', 'Group A aishwaryam', 'Bagruprintesareesuits(2)', 'Value ₹399 - 5,000 Sarees', 'Family', '22 SREE PATHIRAKALIAMMAN TEXTILE', 'Pure HANDLOOM SILK SAREES ', 'Life lesson ', 'All Price Range Kanchipuram Saree', 'DNP grp 3', '🥻Ms Silk Saree 6👗'}
    print(f"3. Got Whatsapp Groups: {whatsapp_groups} \n count: {len(whatsapp_groups)}")
    
    # sleep(10000)
    print(f"4. Capturing Contact Info: ")
    try:
        get_groups(whatsapp_groups, True)
    except Exception as e:
        print(f"Exception: {e}")
    pass
