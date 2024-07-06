'''
문제 정의: 비정형 데이터를 정제하고 정형화할 필요성 및 목표 정의
주어진 데이터는 사용자의 리뷰로 이루어진 비정형 데이터입니다. 이 데이터를 정제하고 정형화하여 RAG 모델을 적용하고, 검색 및 텍스트 생성 기능을 구현하는 것이 목표입니다.

솔루션 도출: 데이터 정제 및 정형화 방법과 RAG 모델 적용 방안 도출
데이터 정제: 중복 제거, 결측치 처리, 특수 문자 제거, 불필요한 공백 제거
데이터 정형화: 데이터의 카테고리화, 구조화된 형식으로 변환
RAG 모델 적용: 학습 데이터 준비, 모델 학습, 검색 및 텍스트 생성 기능 구현

설계: 데이터 정제 및 정형화 프로세스와 RAG 모델 적용 설계
초기 데이터 수집 및 분석
데이터 정제 기준 설정 및 코드 작성
데이터 정형화 기준 설정 및 코드 작성
정제 및 정형화된 데이터 검토 및 수정
RAG 모델 학습 데이터 준비
RAG 모델 적용 코드 작성
성능 평가 기준 설정 및 테스트
성능 평가 결과 수집 및 보고서 작성
최종 결과물 제출'''

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from transformers import RagTokenizer, RagRetriever, RagSequenceForGeneration


# 1. 데이터 수집 (예: CSV 파일 로드)
data = pd.read_csv('reg/spotify_reviews.csv')
# 필드 종류 확인
#print(data.info())
# 결과 출력

print("데이터 길이: ",data.size)
print("필드별 공백값 수:")
print(data.isnull().sum())


# 2. 데이터 정제 기준 설정 
# 중복 제거
# 결측치 처리
# 특수 문자 및 불필요한 공백 제거
# + review content에 결측치는 없으므로 따로 중복 제거 및 결측처리 작업은 진행하지 않는다. 아래는 예시코드
'''
# 중복 제거
data_drop_duplicates = data.drop_duplicates()

# 결측치 처리 (예: NaN 값 제거)

data_drop = data_drop_duplicates.dropna(subset=['content'])
print("drop 후 데이터 길이: ",data_drop.size)
print("drop 후 필드별 공백값 수:")
print(data_drop.isnull().sum())
'''

# 특수 문자 제거 및 불필요한 공백 제거
import re

def clean_text(text):
    text = re.sub(r'\s+', ' ', text)  # 여러 공백을 하나로
    text = re.sub(r'[^A-Za-z0-9\s]', '', text)  # 특수 문자 제거
    return text.strip()

data_refined=data
data_refined['cleaned_content'] = data['content'].apply(clean_text)

print("정제후 일부결과확인")
print(data_refined[['content','cleaned_content']].iloc[20:25]) #정제후 일부결과확인


# 3.데이터 정형화 기준 설정 (예: 카테고리화, 구조화 등)
#데이터 카테고리화 (예: 점수별 분류)
#데이터 구조화 (예: JSON, CSV 등 구조화된 형식)

# 예: 점수별 카테고리화
def categorize(score):
    if score >= 4:
        return 'Positive'
    elif score == 3:
        return 'Neutral'
    else:
        return 'Negative'

data_categorized=data_refined
# data_refined['score']의 분포도 확인
# score 열의 각 값(점수)별 빈도수 계산
score_counts = data_refined['score'].value_counts()

print(score_counts) # 1점> 2점> 5점> 3점> 4점 순

# 빈도수 시각화
sns.barplot(x=score_counts.index, y=score_counts.values, palette='Blues_d')  # seaborn의 barplot 사용
plt.title('Score Distribution')
plt.xlabel('Score')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

# positive, neutral, negative으로 범주화
data_categorized['category'] = data_refined['score'].apply(categorize)

# 예: 구조화된 형식으로 저장 (CSV 파일로 저장)
#data_categorized.to_csv('reg/structured_reviews.csv', index=False)

# 정형화된 데이터 검토 및 수정
print(data_categorized['category'].head())

# 4. RAG 모델 학습 데이터 준비
# 학습 데이터 준비 (예: 텍스트와 카테고리로 구성된 데이터셋 생성)

train_data = data_categorized[['cleaned_content', 'category']]
#train_data.to_csv('reg/rag_train_data.csv', index=False)

''' (오류 수정중)
from datasets import load_dataset

# wiki_dpr 데이터셋의 구성(config) 중 하나를 선택하여 로드
dataset = load_dataset('wiki_dpr', 'psgs_w100.nq.exact')


# 데이터셋 구조 확인
#print(dataset)
'''

# 5. RAG 모델 적용 코드 작성 + dataset, faiss-cpu 라이브러리 설치 필요
# RAG 모델 및 토크나이저 설정
tokenizer = RagTokenizer.from_pretrained("facebook/rag-sequence-nq")
retriever = RagRetriever.from_pretrained("facebook/rag-sequence-nq")
model = RagSequenceForGeneration.from_pretrained("facebook/rag-sequence-nq", retriever=retriever)

# 예시 입력 텍스트
input_text = "I love this app"
input_ids = tokenizer(input_text, return_tensors="pt")["input_ids"]

# 검색 및 생성
generated_ids = model.generate(input_ids)
generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]

print(generated_text)


'''
# 6.RAG 모델 성능 평가 기준 설정
# 검색 정확도
# 생성된 텍스트의 품질

#검색 및 텍스트 생성 테스트
# 성능 테스트를 위한 코드 (예: 여러 테스트 케이스에 대해 검색 및 생성 수행)
test_cases = ["I love this app", "The app is good but it will start to ask premium", "too many ads"]
for test in test_cases:
    input_ids = tokenizer(test, return_tensors="pt")["input_ids"]
    generated_ids = model.generate(input_ids)
    generated_text = tokenizer.batch_decode(generated_ids, skip_special_tokens=True)[0]
    print(f"Input: {test}")
    print(f"Generated: {generated_text}")

'''