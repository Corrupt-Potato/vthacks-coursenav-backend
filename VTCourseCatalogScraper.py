from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import json
import time
import re

# Specify the path to your ChromeDriver
chrome_driver_path = "C:\\Users\\Sam\\Documents\\PythonShenanigans\\CityDataHack\\chromedriver-win64\\chromedriver.exe"

# Initialize the WebDriver using the Service class
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)
courseList = ["AAD", "AAEC", "ACIS", "ADS", "ADV", "AFST", "AHRM", "AINS", "AIS", "ALCE", "ALS", "AOE", "APS", "APSC", "ARBC", "ARCH", "ART", "AS", "ASPT", "AT", "BC", "BCHM", "BDS", "BIOL", "BIT", "BMES", "BMSP", "BMVS", "BSE", "BTDM", "BUS", "C21S", "CAUS", "CEE", "CEM", "CEP", "CHE", "CHEM", "CHN", "CINE", "CL", "CLA", "CMDA", "CMST", "CNST", "COMM", "CONS", "COS", "CRIM", "CS", "CSES", "DANC", "DASC", "ECE", "ECON", "EDCI", "EDCO", "EDCT", "EDEL", "EDEP", "EDHE", "EDHL", "EDHP", "EDIT", "EDP", "EDPE", "EDRE", "EDTE", "ENGE", "ENGL", "ENGR", "ENSC", "ENT", "ES", "ESM", "FA", "FCS", "FIN", "FIW", "FL", "FMD", "FNAD", "FR", "FREC", "FST", "GBCB", "GEN", "GEOG", "GEOS", "GER", "GIA", "GR", "GRAD", "HD", "HEB", "HIST", "HNFE", "HORT", "HR", "HTM", "HUM", "IDS", "IS", "ISC", "ISE", "ITAL", "ITDS", "JMC", "JPN", "JUD", "KOR", "LAHS", "LAR", "LAT", "LDRS", "MACR", "MASC", "MATH", "ME", "MGT", "MINE", "MKTG", "MN", "MS", "MSE", "MTRG", "MUS", "NANO", "NEUR", "NR", "NSEG", "PAPA", "PHIL", "PHS", "PHYS", "PM", "PORT", "PPE", "PPWS", "PR", "PSCI", "PSVP", "PSYC", "REAL", "RED", "REG", "RLCL", "RTM", "RUS", "SBIO", "SOC", "SPAN", "SPES", "SPIA", "STAT", "STL", "STS", "SUMA", "SYSB", "TA", "TBMH", "UAP", "UCCS", "UH", "UNIV", "UNR", "VM", "VT", "WATR", "WGS"]

for i in courseList:
    # Open the webpage
    url = "https://catalog.vt.edu/course-search/"
    driver.get(url)

    # Find the search bar element and type "CS"
    search_bar = driver.find_element(By.ID, "crit-keyword")
    search_bar.send_keys(i)  # Type the course type

    # Press 'Enter' to initiate the search
    search_bar.send_keys(Keys.ENTER)

    # Wait for the page to load
    time.sleep(1)  # Adjust the wait time as needed

    # Extract the course codes and titles
    courses = []
    course_elements = driver.find_elements(By.CSS_SELECTOR, "div.result--group-start")

    for course_element in course_elements:
        course_code = course_element.find_element(By.CSS_SELECTOR, "span.result__code").text
        course_title = course_element.find_element(By.CSS_SELECTOR, "span.result__title").text

        # Extract the numeric part of the course code and check if it's below 5000
        course_number = int(re.search(r'\d+', course_code).group())  # Extract the numeric part
        
        if re.match(rf'^{i}\s\d+$', course_code) and course_number < 5000:  # Only scrape if the course is below 5000 level
            # Click on the course to open the panel
            course_element.click()
            time.sleep(0.3)  # Wait for the panel to open
        
            # Extract details from the panel
            try:
                # Extract the panel's HTML and create BeautifulSoup object
                panel_html = driver.find_element(By.CSS_SELECTOR, "div.panel--kind-details").get_attribute('innerHTML')
                panel_soup = BeautifulSoup(panel_html, "html.parser")

                # Extract the desired information
                description = panel_soup.find("div", class_="section__content").text.strip() if panel_soup.find("div", class_="section__content") else "Not found"
                prerequisites = panel_soup.find("div", class_="detail-prereq").get_text(strip=True).replace("Prerequisite(s):", "").strip() if panel_soup.find("div", class_="detail-prereq") else "Not found"
                corequisites = panel_soup.find("div", class_="detail-coreq").get_text(strip=True).replace("Corequisite(s):", "").strip() if panel_soup.find("div", class_="detail-coreq") else "Not found"
                
                # Add details to the course information
                courses.append({
                    "course_code": course_code,
                    "course_title": course_title,
                    "description": description,
                    "prerequisites": prerequisites,
                    "corequisites": corequisites
                })

                # Click the "back" button to return to the course list
                back_button = driver.find_element(By.CSS_SELECTOR, "a.panel__back[style*='left: 700px;']")
                driver.execute_script("arguments[0].scrollIntoView(true);", back_button)
                back_button.click()
                time.sleep(0.3)  # Wait for the list to reload

            except Exception as e:
                print(f"Error occurred: {e}")

    # Save the results to a JSON file
    with open(f"{i}_courses.json", "w") as file:
        json.dump(courses, file, indent=4)



# Close the browser
driver.quit()
print("Course scraping completed.")