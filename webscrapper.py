import requests
from bs4 import BeautifulSoup
import pandas as pd

title = input("enter job tital: ")  # Job title
location = input("enter job location: ") # Job location
start = 1  
job_list = []

while True:
    list_url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={title}&location={location}&start={start}"
    response = requests.get(list_url)
    if response.status_code != 200:
        print(f"Failed to fetch job postings. Status code: {response.status_code}")
        break
    
    list_soup = BeautifulSoup(response.text, "html.parser")
    page_jobs = list_soup.find_all("li")
    
    if not page_jobs:
        print("No more jobs available. Exiting...")
        break

    for job in page_jobs:
        base_card_div = job.find("div", {"class": "base-card"})
        if not base_card_div:
            print("No base card div found. Skipping...")
            continue
        
        try:
            job_id = base_card_div.get("data-entity-urn").split(":")[3]
        except AttributeError as e:
            print("Error extracting job ID:", e)
            continue

        job_url = f"https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/{job_id}"
        job_response = requests.get(job_url)
        if job_response.status_code != 200:
            print(f"Failed to fetch job details for job ID {job_id}. Status code: {job_response.status_code}")
            continue
        
        job_soup = BeautifulSoup(job_response.text, "html.parser")
        
        job_post = {}
        job_post["job_title"] = job_soup.find("h2", {"class": "top-card-layout__title"}).text.strip() if job_soup.find("h2", {"class": "top-card-layout__title"}) else None
        job_post["company_name"] = job_soup.find("a", {"class": "topcard__org-name-link"}).text.strip() if job_soup.find("a", {"class": "topcard__org-name-link"}) else None
        job_post["time_posted"] = job_soup.find("span", {"class": "posted-time-ago__text"}).text.strip() if job_soup.find("span", {"class": "posted-time-ago__text"}) else None
        job_post["num_applicants"] = job_soup.find("span", {"class": "num-applicants__caption"}).text.strip() if job_soup.find("span", {"class": "num-applicants__caption"}) else None
        job_post["url"] = f"https://www.linkedin.com/jobs/view/{job_id}/"
        job_list.append(job_post)

    start += 2 

jobs_df = pd.DataFrame(job_list)
print(jobs_df)
jobs_df.to_csv('jobs.csv', index=False)