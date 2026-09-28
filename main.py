import csv
import json
import os
import re

import pytest
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

skills_placeholder='//input[@placeholder="Enter skills / designations / companies"]'
exp="//*[@id='expereinceDD']"
location_placeholder="//*[@placeholder='Enter location']"
search_button="//*[text()='Search']"
search_result="//*[@class='srp-jobtuple-wrapper']//h2/a"
company_posted="//*[@class='srp-jobtuple-wrapper']//div[contains(@class,'row2')]/span/a[1]"

load_dotenv()
url = os.getenv("NAUKRI_URL")
driver = None

def read_csv_data():
    with open("test_data.csv", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        return [
            (row["skill"], row["noofexp"], row["location"], row["filter"])
            for row in reader
        ]

def setup_browser():
    global driver
    if not url:
        raise ValueError("NAUKRI_URL is missing from the .env file")
    driver = webdriver.Chrome()
    driver.get(url)
    driver.maximize_window()

    
def enter_data(skills,noofexp,location):
    driver.find_element(By.XPATH,skills_placeholder).send_keys(skills)
    driver.find_element(By.XPATH,exp).click()
    exp_options=f"//span[text()='{noofexp} years']"
    driver.find_element(By.XPATH,exp_options).click()
    driver.find_element(By.XPATH,location_placeholder).send_keys(location)
    driver.find_element(By.XPATH,search_button).click()





def get_result_andstore(skills,noofexp,location,filter,wait):
    filter_option=f"//p//span[text()='{filter}']"
    filter_element=wait.until(EC.element_to_be_clickable((By.XPATH,filter_option)))
    # driver.execute_script("arguments[0].scrollIntoView();", filter_element)
    filter_element.click()
    wait.until(EC.presence_of_element_located((By.XPATH,search_result)))
    data_map = driver.execute_script("""
        return Array.from(document.querySelectorAll('.srp-jobtuple-wrapper'))
            .map(card => ({
                name: card.querySelector('h2 a')?.innerText.trim() || '',
                price: card.querySelector('.row2 span a')?.innerText.trim() || ''
            }))
            .filter(item => item.name || item.price);
    """)
    results = [
        {
            "skill": skills,
            "experience": noofexp,
            "location": location,
            "filter": filter,
            **result,
        }
        for result in data_map
    ]

    os.makedirs("results", exist_ok=True)
    file_name = re.sub(r"[^a-z0-9]+", "_", skills.lower()).strip("_")
    output_path = os.path.join("results", f"{file_name}.json")
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(results, file, indent=4)



@pytest.mark.parametrize("skills,noofexp,location,filter", read_csv_data())
def test_naukri_search(skills,noofexp,location,filter):
    setup_browser()
    try:
        driver.implicitly_wait(15)
        enter_data(skills,noofexp,location)
        wait=WebDriverWait(driver,10)
        wait.until(EC.presence_of_element_located((By.XPATH,search_result)))
        get_result_andstore(skills,noofexp,location,filter,wait)
    finally:
        driver.quit()


if __name__ == "__main__":
    raise SystemExit(pytest.main([__file__]))

