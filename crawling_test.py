import pandas as pd
import requests
import time
from tqdm import trange
from bs4 import BeautifulSoup as bs

headers = {"user-agent": "Mozilla/5.0"}

def get_url(item_code, page_no=1):
    url = f"https://finance.naver.com/item/board.nhn"
    url = f"{url}?code={item_code}&page={page_no}"
    return url  

def get_one_page(item_code, page_no):  
    "한 페이지 수집"
    # 종목 URL 만들기
    url = get_url(item_code, page_no)
    # requests
    response = requests.get(url, headers=headers)
    # 데이터프레임 만들기
    table = pd.read_html(response.text)[1]
    
    return table

def get_last_page(item_code):
    url = get_url(item_code)
    response = requests.get(url, headers=headers)
    html = bs(response.text)
    last_page = int(html.select("#content > div.section.inner_sub > table > tbody > tr > td > table > tbody > tr > td.pgRR > a")[-1]['href'].split('=')[-1])
    return last_page

num = get_last_page("377740")
#print(num)

def get_all_pages(item_code):
    "모든 페이지 수집"
    last = get_last_page(item_code)
    page_list = []
 
    # 1페이지 ~ 끝페이지
    for page_num in trange(1, last+1):
        page = get_one_page(item_code, page_num)
        page_list.append(page)
        time.sleep(0.1)
    
    # 모든 페이지 하나의 데이터프레임으로 합치기
    df_all_page = pd.concat(page_list)
    # 결측치 제거
    df_all_page = df_all_page.dropna(how="all").iloc[:, :-1]
    # 조회, 공감, 비공감 정수형 변환
    df_all_page.loc[:, '조회':'비공감'] = df_all_page.loc[:, '조회':'비공감'].astype('int')
    # 인덱스 리셋
    df_all_page = df_all_page.reset_index(drop=True)
 
    return df_all_page


item_code='377740' #바이오 노트
df_all=get_all_pages(item_code)
df_all

df_all.to_excel('bionote.xlsx', index=False)