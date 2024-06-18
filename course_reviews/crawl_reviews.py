from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import WebDriverException
import time
import pandas as pd
from datetime import datetime


# 강의, 교수 데이터프레임
def get_cor_prof():
    df = pd.read_csv("data/all_lecture_data_20240602_202154.csv")
    return df[["course_name", "professor"]].drop_duplicates(keep="first")


# 강의 상세 페이지 리뷰
def get_reviews(browser, href, url):
    browser.get(href + "?tab=article")
    time.sleep(1)
    while True:
        try:
            reviews = browser.find_elements(By.CLASS_NAME, 'text')
            rating = browser.find_element(By.CSS_SELECTOR,
                                          'body > div > div > div.pane > div > div.header > div.average > span.title').text
        except WebDriverException as e:
            return None, None
        browser.find_element(By.CLASS_NAME, 'articles').click()
        browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        time.sleep(1)
        n_reviews = browser.find_elements(By.CLASS_NAME, 'text')
        if len(n_reviews) == len(reviews):
            article: str = ""
            if reviews:
                for review in reviews:
                    article += review.text
                    article += "\n"
                browser.get(url)
                return article, rating
            else:
                browser.get(url)
                return None, None

# 강의 상세 페이지 href
def get_course_href(browser, course, professor):
    search_field = browser.find_element(By.CSS_SELECTOR,
                                        'body > div > div > div.header > form > input[type=search]:nth-child(1)').send_keys(
        professor)
    submit_button = browser.find_element(By.CSS_SELECTOR,
                                         'body > div > div > div.header > form > input.submit').click()
    time.sleep(1)
    while True:
        try:
            lectures = browser.find_elements(By.CLASS_NAME, 'lecture')
        except WebDriverException as e:
            print(e)
            continue
        browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)
        for lecture in lectures:
            name = lecture.find_element(By.CLASS_NAME, 'name').text
            if name == course:
                return lecture.get_attribute('href')
        browser.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
        time.sleep(1)
        n_lectures = browser.find_elements(By.CLASS_NAME, 'lecture')
        if len(n_lectures) == len(lectures):
            break

    return None


'''
강의,교수 정보 > 검색 > 강의 href 접속 > 강의평 수집
'''


def run():
    browser = webdriver.Chrome()

    url = "https://everytime.kr/lecture/search?condition=professor"
    browser.get(url)
    time.sleep(1)

    # 로그인
    id = "whail14"
    pw = "qkrckswns123"
    id_field = browser.find_element(By.CSS_SELECTOR,
                                    'body > div:nth-child(2) > div > form > div.input > input[type=text]:nth-child(1)')
    id_field.send_keys(id)
    pw_field = browser.find_element(By.CSS_SELECTOR,
                                    'body > div:nth-child(2) > div > form > div.input > input[type=password]:nth-child(2)')
    pw_field.send_keys(pw)
    submit_button = browser.find_element(By.CSS_SELECTOR,
                                         'body > div:nth-child(2) > div > form > input[type=submit]')
    submit_button.click()
    time.sleep(1)

    # 과목 별 조회
    course_prof: pd.DataFrame = get_cor_prof()
    i = 0
    for index, row in course_prof.iterrows():
        time.sleep(3)
        course, professor = row[0], row[1]
        course_href = get_course_href(browser, course, professor)
        if course_href is None:
            print("error")
            browser.get(url)
        else:
            course_prof.at[index, "review"], course_prof.at[index, "rating"] = get_reviews(browser,
                                                                                       course_href,
                                                                                       url)

        i += 1
        print(str(i) + course_prof.at[index, "course_name "])
    # 저장
    course_prof.to_csv(f"{datetime.now().date()}.csv", index=False, encoding='utf-8')


if __name__ == '__main__':
    run()
