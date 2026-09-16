# 4. 데이터 출처와 수치 검증

[전체 분석으로 돌아가기](../README.md)

## 출처

| 항목 | 참조 자료 |
|---|---|
| 분석 흐름·의사결정 | 제공 포트폴리오 수정2차 복사본의 반도체 장표 3–15 |
| 센서와 참고 범위 | 프로젝트2.xlsx / 추가 분석 예시_Si2H6 |
| Recipe 연결 | 프로젝트3.xlsx / 공정 파라미터, 계측 데이터 |
| 조건 요약·초기 규격 | 프로젝트3.xlsx / 계측 Output 전처리, 과제 3-1 답변 예시 |
| 위치별 절대편차 | 프로젝트3.xlsx / 과제 3-2 답변 예시, 좌표 |
| 9개 Split과 예측 | 4회차 과제 간단예시.xlsx / Reference·Split 표 |

공개 파일은 기존 저장소의 센서·대표 wafer 샘플과 교육용 집계 데이터를 사용합니다. 원본 workbook 전체, PPT, 개인정보는 배포하지 않습니다. 추가 표는 제공 Excel에서 추출·재계산한 값이며 합성된 측정 결과가 아닙니다.

## 수식 확인

- Uniformity: 프로젝트3 `계측 Output 전처리!M8 = (K8/H8)/2*100`.
- 위치 절대편차: `과제 3-2 답변 예시!D30 = ABS(D3-$BA3)`.
- 위치별 평균: `AZ55 = AVERAGE(AZ30:AZ54)`. 결측 대응 셀은 비워져 있어 유효 값만 평균에 포함됩니다.
- 프로젝트4 참고값: `K25 = 600/3500/2`. 퍼센트로 표시하면 8.57%.
- 프로젝트4 온도·시간: `N25=L25/M25*100`, `R25=45*(3500/P25)`.

## Run21 평균이 일치하지 않는 부분

| 출처 | 평균 두께 (Å) | 사용 방식 |
|---|---:|---|
| 계측 Output 전처리 요약표 | 2,549.72687 | PPT 조건 비교 재현 |
| 과제 3-2 위치분석 시트의 저장된 평균 | 2,524.73507 | 원본 차이 기록 |
| 현재 계측표의 유효 두께 44개 재계산 | 2,552.97106 | 수정된 위치별 MAD 계산 |
| 이전 대화에 제시된 비교 이미지 | 2,552.97 | 원본 요약표와 구분 |

원본 시트의 저장된 평균을 직접 변경하지 않았습니다. 공개 저장소의 `condition_evaluation.csv`에는 원본 AVG와 재계산 AVG를 나란히 기록했습니다. 위치 분석은 유효값 기준으로 일관되게 다시 계산했으며, 49번·48번의 순위와 수치는 유지됐습니다. Run21에서 두 위치가 결측이므로 해당 위치 집계에 Run21은 포함되지 않습니다.

## 공개 파일별 재현 범위

| 파일 | 포함 내용·범위 |
|---|---|
| process_sensor_summary.csv | 시간별 3개 Run 유량 샘플, stable_interval |
| deposition_condition_summary.csv | 원본 조건 요약표의 AVG·MIN·MAX·RANGE·STD |
| condition_evaluation.csv | 조건 식별자·원본/재계산 통계·유효 개수·초기 규격 비교 |
| measurement_quality_summary.csv | 조건별 GOF 범위·두께 결측 수 |
| missing_measurement_audit.csv | 9개 결측의 조건·위치·GOF, 두께 복원값 없음 |
| wafer_uniformity_sample.csv | 첫 번째 Pre wafer의 49개 위치 샘플 |
| wafer_location_error_summary.csv | 위치별 절대편차 합계·유효 개수·평균·좌표·원본 캐시 평균 |
| parameter_comparison.csv | Power·온도·시간 비교에 사용한 원본 요약값 |
| follow_up_estimate.csv | 선형 가정에 따른 온도·시간·두께 예측 |
| follow_up_split_plan.csv | 원본 9개 Split, 모든 행 미측정 |

공개 노트북은 집계표의 계산과 그래프를 재현합니다. 모든 wafer의 원시 계측값부터 다시 계산하려면 원본 Excel이 필요하며 `src.detailed_analysis.load_measurements`와 `point_deviation`을 사용할 수 있습니다.

## 해석을 위한 구분

- 원본 요약표로 계산한 온도 감소율과 프로젝트4가 사용한 반올림 상수 20.8%·14.4%를 구분했습니다.
- GOF 임계값·기존 삭제 규칙은 확인되지 않아 임의로 추가하지 않았습니다.
- 원본 Excel의 센서 통합 3σ와 노트북의 Run별 3σ는 동일한 기준이 아닙니다.
- 49개 위치 전체가 있는 wafer와 일부 결측 wafer를 구분하고, 관측 규격 충족을 전체 wafer 보증으로 표현하지 않았습니다.
