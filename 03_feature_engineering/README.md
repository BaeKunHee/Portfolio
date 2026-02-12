03_feature_engineering — 분석 기본 데이터셋 구축 (build_dataset.py)
1. 목적 (Goal)

build_dataset.py는 02_data_cleaning 단계에서 정제된 KMA 데이터를 기반으로,
분석의 기준이 되는 기본 시간 단위(hourly base) 데이터셋을 생성한다.

이 단계의 목적은 다음과 같다:

분석 단위 (TM, STN)을 명확히 고정

항상 존재하는 핵심 기상 변수만 선택

정렬된 구조의 base dataset 생성

이후 분석/모델링 단계의 기준 데이터 확보

이 단계에서는 추가적인 정제, 필터링, 집계, 파생변수 생성은 수행하지 않는다.

---

2. 핵심 변수 정의 (Core Variables)

기본 데이터셋은 다음 변수들로 구성된다:

변수	설명
TM	관측 시각 (datetime)
STN	관측소 ID
TA	기온 (Air Temperature)
WS	풍속 (Wind Speed)
HM	상대습도 (Relative Humidity)
PA	기압 (Station Pressure)
PS	해면기압 (Sea Level Pressure)
CORE_VARS = [
    "TM", "STN",
    "TA", "WS", "HM", "PA", "PS",
]


이 변수들은 항상 관측되는 핵심 연속형 변수로 구성되며,
분석의 기준 데이터셋으로 사용된다.

---

3. 처리 과정 (Processing Steps)
  a. 정제 데이터 로드
  df = pd.read_csv(args.input_clean, parse_dates=["TM"])
  
  TM은 datetime으로 파싱
  
  입력은 02_data_cleaning 단계에서 생성된 CSV 파일
  
  b. 필수 컬럼 검증
  missing_cols = [c for c in CORE_VARS if c not in df.columns]
  
  
  핵심 컬럼이 누락된 경우 즉시 오류 발생
  
  데이터 스키마 일관성 확보
  
  c. 핵심 변수 선택
  base = df[CORE_VARS].copy()
  
  
  분석 단위 (TM, STN) 유지
  
  불필요한 컬럼 제거
  
  d. 정렬 및 구조 고정
  base = base.sort_values(["TM", "STN"]).reset_index(drop=True)
  
  
  시간 → 관측소 기준 정렬
  
  재현 가능한 데이터 구조 확보
  
  e. Parquet 형식으로 저장
  base.to_parquet(out_path, index=False)
  
  
  출력 파일:
  
  datasets/hourly_base.parquet
  
  
  Parquet 형식을 사용함으로써:
  
  대용량 데이터 처리 효율 확보
  
  스키마 유지
  
  이후 분석 단계 속도 향상

---

4. 실행 방법 (How to Run)
python build_dataset.py --input_clean path/to/cleaned.csv --output_dir datasets


예시:

python build_dataset.py --input_clean ../02_data_cleaning/data_clean/kma_clean.csv


실행 결과:

[OK] Base hourly dataset saved: datasets/hourly_base.parquet
[INFO] Rows: N, Columns: 7

---

5. 품질 설계 관점 (Data Quality Perspective)

이 단계는 파생 변수를 생성하는 단계가 아니라,
분석의 기준이 되는 “Base Dataset”을 정의하는 단계이다.

주요 품질 보장 요소:

필수 컬럼 존재 여부 검증

분석 단위 고정 (TM × STN)

명시적 변수 선택

정렬을 통한 구조 일관성 확보

Parquet 저장으로 스키마 유지

이 설계는 이후 분석 결과가
“변수 선택 차이” 또는 “정렬/구조 불일치”로 왜곡되는 것을 방지하기 위함이다.

---

6. 이 단계에서 수행하지 않는 것

결측값 대체

이상치 제거

시간 집계

변수 생성

통계적 가정 적용

이러한 결정은 04_statistical_analysis_examples 단계에서
분석 목적이 정의된 이후 수행한다.
