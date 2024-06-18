from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import pandas as pd
import boto3
import io

load_dotenv()
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET_NAME = os.getenv("AWS_BUCKET_NAME")
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY or not AWS_BUCKET_NAME:
    raise ValueError("AWS env vars are not set.")

try:
    print(f"Try connecting to {AWS_BUCKET_NAME} ")
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
except Exception as e:
    print(e)
finally:
    print(f"{AWS_BUCKET_NAME} connected.")

s3_folder = "raw_data/lecture_data/"
chrome_options = Options()
chrome_options.add_argument("--headless")


def save_to_s3(data, filename):
    df = pd.DataFrame(
        data,
        columns=[
            "course_class_id",
            "course_id",
            "class_id",
            "course_name",
            "grade",
            "credits",
            "course_classification",
            "time_classroom",
            "professor",
            "assessment_method",
            "notes",
        ],
    )
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
    s3_client.put_object(
        Bucket=AWS_BUCKET_NAME, Key=s3_folder + filename, Body=csv_buffer.getvalue()
    )
    print(f'"{filename}" is saved in {AWS_BUCKET_NAME} {s3_folder}.')


def scrape_data(select_element_id, button_name, kita=False):
    select_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, select_element_id))
    )
    options = select_element.find_elements(By.TAG_NAME, "option")

    for i in range(len(options)):
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, select_element_id))
        )
        options = select_element.find_elements(By.TAG_NAME, "option")

        option = options[i]
        option_text = option.text
        option.click()

        search_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, button_name))
        )
        search_button.click()

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "dgList"))
        )

        table = driver.find_element(By.ID, "dgList")
        rows = table.find_elements(By.TAG_NAME, "tr")

        local_data = []

        for row in rows[1:]:
            cells = row.find_elements(By.TAG_NAME, "td")

            course_class_id = cells[0].find_element(By.TAG_NAME, "a").text
            course_id, class_id = course_class_id.split("-")
            course_name = cells[2].text
            grade = cells[3].text
            credits = float(cells[4].text)
            course_classification = cells[5].text
            time_classroom = cells[6].text
            professor = cells[7].text
            assessment_method = cells[8].text
            notes = cells[9].text if len(cells) > 9 else ""

            local_data.append(
                (
                    course_class_id,
                    course_id,
                    class_id,
                    course_name,
                    grade,
                    credits,
                    course_classification,
                    time_classroom,
                    professor,
                    assessment_method,
                    notes,
                )
            )

        if kita:
            filename = f"기타_{option_text}.csv".replace("/", "_")
        else:
            filename = f"학과_{option_text}.csv".replace("/", "_").replace(" ", "")

        save_to_s3(local_data, filename)


def run_crawl():
    print("Crawling started.")
    global driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    driver.get("https://sugang.inha.ac.kr/sugang/")

    mainIframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@name='ifrm']"))
    )
    driver.switch_to.frame(mainIframe)

    menuFrame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//frame[@name='MenuFrame']"))
    )
    driver.switch_to.frame(menuFrame)

    course_search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "교과조회"))
    )
    course_search_button.click()

    lecture_timetable_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "강의시간표"))
    )
    lecture_timetable_button.click()

    window_handles = driver.window_handles

    driver.switch_to.window(window_handles[-1])

    lectureMainIframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@id='ifmdtl']"))
    )
    driver.switch_to.frame(lectureMainIframe)

    scrape_data("ddlDept", "ibtnSearch1", kita=False)
    scrape_data("ddlKita", "ibtnSearch2", kita=True)

    print("Crawling finished.")
    driver.quit()


def get_year_term_text():
    print("Check year term changed.")
    global driver
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=chrome_options
    )

    driver.get("https://sugang.inha.ac.kr/sugang/")

    mainIframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@name='ifrm']"))
    )
    driver.switch_to.frame(mainIframe)

    menuFrame = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//frame[@name='MenuFrame']"))
    )
    driver.switch_to.frame(menuFrame)

    course_search_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "교과조회"))
    )
    course_search_button.click()

    lecture_timetable_button = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.LINK_TEXT, "강의시간표"))
    )
    lecture_timetable_button.click()

    window_handles = driver.window_handles

    driver.switch_to.window(window_handles[-1])

    lectureMainIframe = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//iframe[@id='ifmdtl']"))
    )
    driver.switch_to.frame(lectureMainIframe)

    # Get the text of the span with id="lblYearTerm"
    year_term_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lblYearTerm"))
    )
    current_year_term = year_term_element.text
    driver.quit()
    return current_year_term
