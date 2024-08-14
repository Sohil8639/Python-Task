import time
import json
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Configure Selenium WebDriver
opt = Options()
opt.add_argument("--headless")  # Run in headless mode
opt.add_argument("--no-sandbox")
opt.add_argument("--disable-dev-shm-usage")

# Path to your WebDriver executable
webdriver_path = 'C:/chromedriver-win64/chromedriver.exe'
driver = webdriver.Chrome(service = Service(webdriver_path), options=opt)

# List of job search URLs
urls = [
    "https://www.linkedin.com/jobs/search?location=India&geoId=102713980&f_C=1035&position=1&pageNum=0",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_C=1441",
    "https://www.linkedin.com/jobs/search?keywords=&location=India&geoId=102713980&f_TPR=r86400&f_C=1586&position=1&pageNum=0"
]

# Helper functions
def parse_posted_date(text):
    """Extracts the posted date from the 'posted_on' field."""
    today = datetime.now()
    text = text.lower()
    if 'hours' in text:
        return today.strftime("%d-%m-%Y")
    if 'today' in text:
        return today.strftime("%d-%m-%Y")
    elif 'week' in text:
        try:
            days_ago = int(text.split(' ')[0])
            return (today - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'month' in text:
        try:
            months_ago = int(text.split(' ')[0])
            return (today - timedelta(days=months_ago * 30)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    elif 'day' in text:
        try:
            days_ago = int(text.split(' ')[0])
            return (today - timedelta(days=days_ago)).strftime("%d-%m-%Y")
        except ValueError:
            return None
    return None

def extract_job_data(job_element):
    """Extracts job data from a job posting element."""
    job_data = {}

    # Extract company name
    try:
        company = job_element.find("h4", class_="base-search-card__subtitle").find("a").get_text(strip=True)
    except AttributeError:
        company = None
    job_data["company"] = company

    # Extract job title
    try:
        job_title = job_element.find("h3", class_="base-search-card__title").get_text(strip=True)
    except AttributeError:
        job_title = None
    job_data["job_title"] = job_title

    # Extract LinkedIn job ID
    try:
        linkedin_job_id =job_element.find("a",{"data-tracking-control-name": "public_jobs_jserp-result_search-card"})["href"].split("?")[0].split("-")[-1]
    except (AttributeError, IndexError):
        linkedin_job_id = None
    job_data["linkedin_job_id"] = linkedin_job_id

    # Extract location
    try:
        location = job_element.find("span", class_="job-search-card__location").get_text(strip=True)
    except AttributeError:
        location = None
    job_data["location"] = location

    # Extract posted date
    try:
        posted_on = job_element.find("time", class_="job-search-card__listdate--new").get_text(strip=True)
        posted_date = parse_posted_date(posted_on)
    except AttributeError:
        posted_on = job_element.find("time", class_="job-search-card__listdate").get_text(strip=True)
        posted_date = parse_posted_date(posted_on)
    except:
        posted_on=None
        posted_date=None
    job_data["posted_on"] = posted_on
    job_data["posted_date"] = posted_date

    # Extract employment type (if available elsewhere)
    employment_type = None  # Update with correct class if available
    
    job_data["employment_type"] = employment_type

    # Extract seniority level (if available elsewhere)
    seniority_level = None  # Update with correct class if available

    job_data["seniority_level"] = seniority_level

    return job_data

def scrape(url):
    """Scrapes jobs from the given LinkedIn URL."""
    driver.get(url)
    time.sleep(5)  # Wait for the page to load
    
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    job_ele = soup.find_all("div", {"class": "job-search-card"})

    jobs = []
    for j in job_ele:
        job_data = extract_job_data(j)
        if job_data:
            jobs.append(job_data)

    return jobs

# Main script
data = []
for url in urls:
    jobs = scrape(url)
    data.extend(jobs)

# Save data to JSON
with open('data.json', 'w') as json_file:
    json.dump(data, json_file, indent=4)

# Save data to CSV
df = pd.DataFrame(data)
df.to_csv('data.csv', index=False)

# Clean up
driver.quit()

print("Scraping completed. Data saved to jobs_data.json and jobs_data.csv.")
