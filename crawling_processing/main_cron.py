import os
from datetime import datetime
from crawling.crawl_lecture_data import get_year_term_text, run_crawl
from processing.process_and_save import process_all

# 절대 경로 설정
STATE_FILE = '/home/ubuntu/environment/crawling_processing/previous_year_term.txt'

def load_previous_year_term():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'r') as file:
            return file.read().strip()
    return ""

def save_previous_year_term(year_term):
    with open(STATE_FILE, 'w') as file:
        file.write(year_term)

def check_and_run_crawl():
    # Get the current time
    now = datetime.now()
    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # Log start message with current time
    print(f"\n*** Starting cron job at {current_time_str}. ***")
    
    # Load the previous year term from the file
    previous_year_term = load_previous_year_term()

    # Get the current year term text from the website
    current_year_term = get_year_term_text()

    # Compare the current year term with the previous one
    if current_year_term != previous_year_term:
        print(f"Year term has changed.(\"{previous_year_term}\"->\"{current_year_term}\")\nRunning the crawl.")
        ####crawling####
        run_crawl()
        ####processing####
        process_all()
        # Update the previous year term in the file
        save_previous_year_term(current_year_term)
        print(f"previous_year_term is updated to \"{current_year_term}\"")
    else:
        print("Year term has not changed. No crawl needed.")
        
    # Get the current time
    now = datetime.now()
    current_time_str = now.strftime('%Y-%m-%d %H:%M:%S')
    
    # Log start message with current time
    print(f"*** Cron job at {current_time_str} finished. ***")

if __name__ == "__main__":
    check_and_run_crawl()
