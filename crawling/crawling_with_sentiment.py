import pandas as pd
from transformers import pipeline

# Hugging Face의 Transformers 라이브러리에서 제공하는 감성 분석 모델 정의
def predict_sentiment(text):
    classifier = pipeline("sentiment-analysis")
    result = classifier(text)
    return result[0]['label']

# landf_crawling.xlsx 파일 불러오기
excel_file = 'landf_crawling.xlsx'
df = pd.read_excel(excel_file)

# 감성 분석을 위한 함수 적용
df['감성'] = df['제목'].apply(predict_sentiment)

# 결과 확인
print(df)

# 감성 분석 결과를 엑셀 파일로 저장
output_excel = 'landf_crawling_with_sentiment.xlsx'
df.to_excel(output_excel, index=False)

print(f"감성 분석 결과가 {output_excel} 파일로 저장되었습니다.")
