from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import pandas as pd
import os

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def finding_video():
    # 파일에서 마지막 인덱스 번호 읽기
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    last_index_file = os.path.join(BASE_DIR, 'last_index.txt')

    if os.path.exists(last_index_file):
        with open(last_index_file, 'r') as f:
            last_index = int(f.read()) + 1
    else:
        last_index = 1


    group_id = 'lms_group_id'
    lms_id = 'lms_id'
    lms_pw = 'lms_pw.'

    driver = webdriver.Chrome()
    url = 'https://ieilms.jbnu.ac.kr/'
    driver.get(url)

    # WebDriverWait를 사용하여 페이지가 로드될 때까지 최대 10초 기다림
    wait = WebDriverWait(driver, 10)
    element_id = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="id"]')))
    element_pw = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="passwd"]')))

    # LMS 아이디와 비밀번호를 입력
    element_id.send_keys(lms_id)
    element_pw.send_keys(lms_pw)

    # 로그인
    loginbtn = driver.find_element(By.XPATH, '//*[@id="loginform"]/table/tbody/tr[1]/td[2]/input')
    loginbtn.click()
    wait.until(EC.invisibility_of_element_located((By.ID, 'loginform')))

    # 영상 출석부 페이지로 이동
    driver.get(f'https://ieilms.jbnu.ac.kr/attend/videoDataViewAttendListStudent.jsp?group_id={group_id}')

    # 비디오 개수 카운트
    elements_count = len(driver.find_elements(By.CSS_SELECTOR, '#dataBox > table > tbody > tr'))

    if elements_count >= 1:
        index_list = []
        title_list = []
        date_list = []

        for i in range(last_index, elements_count + 1):
            last_index = driver.find_element(By.XPATH, f'//*[@id="dataBox"]/table/tbody/tr[{i}]/td[1]').text
            index_list.append(str(last_index))
            titleresult = driver.find_element(By.XPATH, f'//*[@id="dataBox"]/table/tbody/tr[{i}]/td[2]').text
            title_list.append(str(titleresult))
            dateresult = driver.find_element(By.XPATH, f'//*[@id="dataBox"]/table/tbody/tr[{i}]/td[3]').text
            date_list.append(str(dateresult))

        df = pd.DataFrame({'index': index_list, 'title': title_list, 'date': date_list})

        if not df.empty:

            last_num = df['index'].iloc[-1]

            # 마지막 비디오 번호를 파일에 저장
            with open(last_index_file, 'w') as f:
                f.write(str(last_num))

        return df


def main():
    df = finding_video()

    SCOPES = ['https://www.googleapis.com/auth/calendar']

    CREDENTIALS_FILE = 'client_secret.json'

    creds = None
    # token.pickle은 사용자의 접근과 토큰을 저장합니다.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES)
            creds = flow.run_local_server(port=5090)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    for r in range(len(df)):
        title = '[과목이름] ' + df['title'][r]
        start_date = pd.to_datetime(df['date'][r].split(' ~ ')[0], format='%Y/%m/%d %H:%M').isoformat()
        end_date = pd.to_datetime(df['date'][r].split(' ~ ')[-1], format='%Y/%m/%d %H:%M').isoformat()

        service.events().insert(calendarId='primary',
                                               body={
                                                   'summary': title,
                                                   'start': {'dateTime': start_date, 'timeZone': 'Asia/Seoul'},
                                                   'end': {'dateTime': end_date, 'timeZone': 'Asia/Seoul'},
                                               }
                                               ).execute()


if __name__ == '__main__':
    main()
