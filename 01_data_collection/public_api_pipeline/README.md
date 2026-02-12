Public API 파이프라인: KMA 지상관측 데이터

1. 목적 (Goal)

본 단계는 신뢰 가능한 원시(raw) 데이터 수집에 초점을 둔다.
주요 목적은 KMA 지상관측 텍스트 데이터를 수정 없이 그대로 저장하여 데이터 무결성을 보존하는 것이다.

이 단계에서는 다음 작업을 수행하지 않는다:

정제(cleaning)

변환(transformation)

결측 대체(imputation)

집계(aggregation)

수집 단계와 처리 단계를 엄격히 분리함으로써,
원본 데이터가 의도치 않게 왜곡되는 것을 방지하고 **재현 가능성(reproducibility)**을 확보한다.

---

2. 품질 설계 원칙 (Quality Design Principles)

원본 보존(Raw Data Preservation)
API 응답 데이터는 어떠한 변환도 수행하기 전에 그대로 저장한다.

관심사의 분리(Separation of Concerns)
데이터 수집 단계와 정제 단계를 명확히 구분한다.

경량 파싱(Light Parsing, 선택 사항)
CSV 변환 기능은 편의를 위해 제공되며, 데이터 값을 수정하지 않는다.

재현 가능성(Reproducibility)
조회 시점(tm)과 관측소(stn) 파라미터를 기록하여 추적 가능성을 유지한다.

---

3. 실행 환경 설정 (Auth Key)

본 파이프라인은 KMA API 인증 키가 필요하다.

옵션 A) 환경 변수 설정 (권장)
Windows CMD
set KMA_AUTH_KEY=YOUR_KEY_HERE
python ingest.py --tm 202211300900 --stn 0 --save_csv

PowerShell
$env:KMA_AUTH_KEY="YOUR_KEY_HERE"
python ingest.py --tm 202211300900 --stn 0 --save_csv
