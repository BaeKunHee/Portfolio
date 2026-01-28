# KMA Surface Observation Data Pipeline & Analysis

기상청(KMA) 지상관측 데이터를 대상으로  
**데이터 수집 → 정제 → 구조화 → 탐색적 분석(EDA)** 까지의 전 과정을 직접 설계·구현한 프로젝트입니다.

본 프로젝트는 단순한 분석 결과 도출이 아니라,  
**분석 이전에 반드시 검토되어야 할 데이터 구조와 통계적 가정을 명시적으로 드러내는 것**을 목표로 합니다.

---

## Project Overview

- **Data Source**: KMA API Hub (Surface Observation, sfctm2)
- **Observation Unit**: (Time `TM`, Station `STN`)
- **Core Variables**:
  - TA: Air Temperature
  - WS: Wind Speed
  - HM: Humidity
  - PA / PS: Pressure
- **Output Format**: CSV (clean), Parquet (feature)

---

## Pipeline Structure

00_raw_data
01_data_collection
02_data_cleaning
03_feature_engineering
04_analysis

각 단계는 독립적인 책임을 가지며,  
이전 단계의 데이터를 수정하지 않는 것을 원칙으로 설계되었습니다.

---

## 01. Data Collection

- Python 기반 API ingestion 스크립트 (`ingest.py`) 작성
- CLI(argparse) 기반 파라미터 입력
- API 원본 응답을 가공 없이 raw 데이터로 저장
- 수집 시점 및 조건이 파일명에 명시되도록 설계

**Goal**  
> 데이터의 출처와 수집 조건을 항상 추적 가능하게 유지

---

## 02. Data Cleaning

정제 단계에서는 데이터의 의미를 변경하지 않는 최소한의 처리만 수행했습니다.

### Cleaning Policy
- Placeholder 값(-9, -99 등)을 결측값으로 변환
- 컬럼별 자료형을 명시적으로 캐스팅
- 파싱 불가 행은 제거하지 않고 로그로 기록

### Explicitly Not Done
- 결측값 대체
- 이상치 제거
- 시간/공간 집계

> 정제 단계에서 불필요한 통계적 가정을 도입하지 않기 위함입니다.

---

## 03. Feature Engineering

분석의 기준점이 되는 **base dataset**을 생성했습니다.

### Design Principles
- Observation unit: (TM, STN)
- No aggregation
- No derived features
- Neutral structure for downstream analysis

### Output
- `datasets/hourly_base.parquet`
- Efficient columnar format for scalability

---

## 04. Exploratory Analysis (EDA)

결측 구조 분석을 시도하였으나,  
이전 정제 과정에서 결측이 제거된 상태임을 확인하고 분석 방향을 전환했습니다.

본 단계에서는 **관측소(STN) 간 이질성**에 초점을 맞춘 탐색적 분석을 수행했습니다.

### Key Analysis
- STN별 평균 기온(TA)과 평균 풍속(WS) 비교
- 관측소 단위 평균값 산점도 시각화

### Findings
- 관측소 간 평균 기온 및 풍속 분포가 매우 이질적
- 동일한 평균 기온 구간에서도 풍속의 분산이 크게 나타남
- 평균 기온과 평균 풍속 간 단순 선형 관계는 관찰되지 않음

### Interpretation
> 관측소(STN)를 단일한 모집단으로 가정한 분석은 통계적 왜곡 가능성이 있으며,  
> 풍속과 같은 변수는 관측소 고유 특성의 영향을 크게 받는 것으로 보인다.

이는 이후 분석에서 **관측소 효과를 명시적으로 고려할 필요성**을 시사합니다.

---

## Limitations

- 단일 시점 데이터 기반 분석
- 관측소 메타데이터(고도, 지형 등) 미포함

---

## Future Work

- 장기간 시계열 데이터 확장 수집
- 관측소 메타데이터 결합
- 관측소 군집화 또는 계층적 모델링 적용
- 시간 효과와 공간 효과 분리 분석

---

## Key Takeaway

> 이 프로젝트는 분석 결과보다  
> **분석이 가능해지기까지의 데이터 설계와 가정 검증 과정**에 초점을 둔 프로젝트입니다.

---

## Tech Stack

- Python
- pandas
- pyarrow
- matplotlib / seaborn

