# ChatGPT API를 사용하여 감성 분석을 수행하는 함수
from bs4 import BeautifulSoup
import pandas as pd
import requests
import json

def analyze_sentiment(text, api_key):
    url = "https://api.openai.com/v1/engines/davinci-codex/completions"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "model": "text-davinci-003",
        "prompt": f"Sentiment analysis: {text}\nPositive or negative?",
        "max_tokens": 1
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if 'choices' in result and len(result['choices']) > 0 and 'text' in result['choices'][0]:
            sentiment = result['choices'][0]['text'].strip()
            return sentiment
        else:
            print(f"Invalid response format from API: {result}")
    else:
        print(f"Failed to request sentiment analysis from API. Status code: {response.status_code}")

    return "Unknown"

# 네이버 금융 포럼을 크롤링하고 감성 분석을 수행하는 함수
def NS_users_crawler(codes, page, api_key):
    # User-Agent 설정
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.67 Safari/537.36'
    }
    result_df = pd.DataFrame([])

    n_ = 0
    for page in range(1, page + 1):  # 페이지 수만큼 반복
        n_ += 1
        if (n_ % 10 == 0):
            print('================== Page ' + str(page) + ' is done ==================')
        url = f"https://finance.naver.com/item/board.naver?code={codes}&page={page}"
        # html → 파싱
        html = requests.get(url, headers=headers).content
        # 한글 깨짐 방지를 위해 decode
        soup = BeautifulSoup(html.decode('euc-kr', 'replace'), 'html.parser')
        table = soup.find('table', {'class': 'type2'})
        tb = table.select('tbody > tr')

        for i in range(2, len(tb)):
            if len(tb[i].select('td > span')) > 0:
                date = tb[i].select('td > span')[0].text
                title = tb[i].select('td.title > a')[0]['title']
                views = tb[i].select('td > span')[1].text
                pos = tb[i].select('td > strong')[0].text
                neg = tb[i].select('td > strong')[1].text

                # ChatGPT API를 사용하여 감성 분석 수행
                sentiment = analyze_sentiment(title, api_key)

                table = pd.DataFrame({
                    '날짜': [date],
                    '제목': [title],
                    '조회': [views],
                    '공감': [pos],
                    '비공감': [neg],
                    '감성': [sentiment]
                })
                result_df = pd.concat([result_df, table], ignore_index=True)

    return result_df

# 메인 실행 부분
def main():
    # ChatGPT API 키를 사용하여 초기화
    api_key = 'YOUR_API_KEY'  
    codes = "066970"  # 예시 종목 코드

    data = NS_users_crawler(codes, 3, api_key)  # 3페이지의 데이터 크롤링
    print(data.head(10))

    # excel_file = 'landf_crawling.xlsx'
    # data.to_excel(excel_file, index=False)
    # print(f"Data saved to {excel_file}")

if __name__ == "__main__":
    main()
