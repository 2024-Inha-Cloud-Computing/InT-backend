import schedule
import time
from datetime import datetime
from crawling.crawl_lecture_data import get_year_term_text, run_crawl
from processing.process_and_save import process_all

# Initialize the previous year term
previous_year_term = ""


def check_and_run_crawl():
    global previous_year_term
    # Get the current year term text from the website
    current_year_term = get_year_term_text()

    # Compare the current year term with the previous one
    if current_year_term != previous_year_term:
        print(f"Year term has changed.(\"{previous_year_term}\"->\"{current_year_term}\")\nRunning the crawl.")
        ####crawling####
        run_crawl()
        ####processing####
        process_all()
        # Update the previous year term
        previous_year_term = current_year_term
        print(f"previous_year_term is updated to \"{previous_year_term}\"")
        
    else:
        print("Year term has not changed. No crawl needed.")


# Schedule the task to run daily at a specific time (KST 18:00)
schedule.every().day.at("09:00").do(check_and_run_crawl)
#schedule.every().day.at("08:27").do(check_and_run_crawl)

print(
    "Scheduler started. It will check the date every day at midnight and run the crawl if needed."
)

while True:
    now = datetime.now()
    
    if now.minute == 0:
        print(f"Current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
    schedule.run_pending()
    
    time.sleep(60)  # Check every minute
