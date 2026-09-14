# Semiconductor Process Data Analysis

반도체 증착 공정 데이터를 바탕으로  
**설비 센서의 안정성, 공정조건에 따른 박막 두께 변화, wafer 내 위치별 분포**를 분석한 프로젝트입니다.

**recipe 조건 → 설비 sensor → wafer 계측 결과**를 연결해 공정 조건별 차이를 비교하고  
다음에 확인해야 할 조건을 좁혀보는 데 초점을 두었습니다.

---

## Project overview

분석은 크게 세 단계로 진행했습니다.

1. **설비 센서 데이터 전처리 및 Run 비교**
   - 동일 recipe로 진행된 Run의 Si2H6 유량을 비교
   - 공정 초반 ramp-up 구간과 안정 구간을 분리
   - 안정 구간의 평균과 변동 폭 확인

2. **공정조건별 박막 두께 비교**
   - Si2H6 유량, RF Power, 온도, 공정 시간을 Input으로 정리
   - 평균 두께와 산포를 Output으로 연결
   - 조건별 두께 변화와 변수 간 관계 비교

3. **Wafer 위치별 분포 확인**
   - 49개 측정 위치를 wafer 좌표에 배치
   - 평균값만으로 보이지 않는 위치별 두께 편차 확인
   - 공정조건 평가 시 wafer 전체 분포를 함께 확인

---

# 1. Process sensor stability

![Si2H6 flow stability by run](images/sensor_stability_by_run.png)

## 분석 목적

동일한 recipe가 반복되었을 때  
설비가 설정한 Si2H6 유량을 각 Run에서 비슷하게 구현하는지 확인했습니다.

원본 설비 데이터에는 공정 시작 전후의 값과 실제 공정 진행 구간이 함께 포함될 수 있기 때문에,  
**실제 증착이 진행되는 구간을 기준으로 데이터를 나누는 작업**이 먼저 필요하다고 판단했습니다.

## Data preprocessing

공정 초반에는 목표 유량에 도달하기 전의 변화가 크게 나타났기 때문에  
초기 3개 측정값을 ramp-up 구간으로 분리하고 이후 구간을 안정 구간으로 두었습니다.

안정 구간만 사용해 Run별 평균과 표준편차를 계산했습니다.

| Run | 안정 구간 평균 유량 | 표준편차 |
|---|---:|---:|
| Run 1 | 200.0693 sccm | 0.1488 sccm |
| Run 2 | 200.0496 sccm | 0.1194 sccm |
| Run 3 | 200.0111 sccm | 0.1025 sccm |

## 해석

세 Run 모두 안정 구간에서는 평균 유량이 목표값인 `200 sccm`에 매우 가깝게 유지됐습니다.

Run 1 → Run 2 → Run 3 순으로 표준편차도 작아져,  
적어도 분석한 안정 구간에서는 세 Run 모두 큰 흔들림 없이 비슷한 수준의 유량을 유지한 것으로 확인했습니다.

초기값까지 포함하면 Run별 차이가 크게 보이지만,  
실제 공정 안정 구간을 분리한 뒤 비교하면 Run 간 차이가 훨씬 작아집니다.

이 과정을 통해 **분석 전에 어떤 구간을 사용할지 정하는 전처리가 결과 해석에 큰 영향을 줄 수 있다는 점**을 확인했습니다.

±3σ는 세 Run의 변동 폭을 비교하기 위한 참고 범위로 사용했습니다.

---

# 2. Deposition parameter analysis

![Gas flow and mean thickness](images/gas_flow_vs_thickness.png)

![Condition variation](images/process_condition_variation.png)

## 분석 목적

공정 recipe에서 변경한 조건이 실제 wafer의 박막 두께에 어떤 차이를 만드는지 확인했습니다.

Input으로는 다음 네 가지 조건을 사용했습니다.

- Si2H6 flow rate
- RF Power
- Temperature
- Process Time

Output으로는 wafer 계측 결과의

- 평균 두께
- 최솟값
- 최댓값
- Range
- Standard deviation

을 비교했습니다.

---

## Input과 Output 연결

공정조건만 따로 보는 대신  
각 recipe의 Input과 실제 측정된 두께 Output을 연결해서 비교했습니다.

이렇게 정리하면

> 어떤 조건을 바꿨을 때 실제 두께가 어떻게 달라졌는가?

를 조건별로 확인할 수 있습니다.

---

## Si2H6 flow rate

`400 W`, `400°C`, `30 s`로 나머지 조건을 고정한 뒤  
Si2H6 유량을 변경한 Run들을 따로 비교했습니다.

해당 조건군에서는 Si2H6 유량이 증가할수록 평균 두께도 증가하는 경향이 나타났고,  
Si2H6 유량과 평균 두께의 상관계수는 `r = 0.904`였습니다.

즉, 이 조건 범위에서는 **Si2H6 유량이 증착량과 관련된 주요 변수 중 하나로 보이는 경향**을 확인할 수 있었습니다.

다만 여러 변수가 동시에 달라지는 Run까지 한 번에 섞으면  
어떤 변수가 결과에 영향을 줬는지 구분하기 어려워지므로,  
다른 조건이 동일한 그룹끼리 먼저 비교했습니다.

---

## RF Power / Temperature / Process Time

복합 Split에서는 Power, 온도, 시간을 함께 변경한 조건이 포함되어 있습니다.

이 경우 단순히 전체 Run의 두께를 나열하기보다  
가능한 한 다른 조건이 같거나 유사한 Run을 묶어서 비교했습니다.

특히 다음과 같은 관점으로 분석했습니다.

- **Process Time**
  - 시간이 증가할 때 평균 두께가 어떻게 변하는지 확인

- **RF Power**
  - 동일하거나 유사한 조건에서 Power 변화에 따른 두께 차이 확인

- **Temperature**
  - 평균 두께뿐 아니라 wafer 내 분포와 산포가 달라지는지 확인

이를 통해 하나의 조건을 단순히 “좋다 / 나쁘다”로 판단하기보다  
**평균 두께를 움직이는 변수와 산포에 영향을 주는 변수를 구분해서 보는 방식**으로 접근했습니다.

---

## 산포가 가장 작은 조건

전체 데이터에서 표준편차가 가장 작은 값은 `155.3101`이었으며  
해당 recipe 조건은 다음과 같습니다.

- Si2H6: `175 sccm`
- Power: `300 W`
- Temperature: `300°C`
- Time: `40 s`

다만 표준편차가 가장 작다는 이유만으로  
이 조건을 최적 공정조건이라고 판단하지는 않았습니다.

공정조건을 선택하려면

- 평균 두께가 target에 가까운지
- wafer 내 위치별 값이 허용 범위에 들어오는지
- 산포가 충분히 작은지

를 함께 확인해야 하기 때문입니다.

---

# 3. Representative wafer map

![Representative wafer thickness map](images/wafer_uniformity_map.png)

## 분석 목적

평균 두께만 보면 wafer 전체가 비슷하게 형성된 것처럼 보일 수 있습니다.

하지만 실제 공정에서는 wafer의 중심과 edge, 특정 방향에서  
서로 다른 두께 분포가 나타날 수 있기 때문에  
대표 wafer의 **49개 측정 위치를 실제 좌표에 배치**했습니다.

---

## 해석

wafer map을 통해 평균값 하나만으로는 확인하기 어려운  
위치별 두께 차이를 시각적으로 비교했습니다.

특히

- 중심부와 edge의 차이
- 특정 방향에서 반복되는 high / low 영역
- 가장 얇거나 두꺼운 위치

를 확인할 수 있도록 구성했습니다.

따라서 조건 평가 시

> 평균 두께가 target에 가까운가?

뿐 아니라

> wafer의 모든 위치에서 안정적인 분포가 나타나는가?

를 함께 확인해야 한다고 판단했습니다.

이 과정은 평균값이 좋아도 특정 위치가 크게 벗어나는 조건을 걸러내는 데 도움이 됩니다.

---

# 4. Process interpretation

이번 프로젝트에서 가장 중요하게 본 부분은  
**숫자가 가장 좋은 조건 하나를 찾는 것보다, 공정조건과 결과를 연결해 다음 판단을 만드는 과정**이었습니다.

분석 흐름을 정리하면 다음과 같습니다.

```text
공정조건 확인
      ↓
설비 sensor 데이터 전처리
      ↓
Run별 정상 진행 여부 비교
      ↓
Recipe Input 정리
      ↓
Wafer 계측 Output 연결
      ↓
조건별 평균·산포 비교
      ↓
Wafer 위치별 분포 확인
      ↓
다음에 확인할 공정조건 선정

공정 데이터는 Input과 Output이 한 파일에 깔끔하게 정리되어 있다고 가정하기 어렵기 때문에
분석 전에 어떤 조건이 바뀌었고 어떤 계측 결과와 연결되는지 정리하는 과정이 중요하다고 느꼈습니다.


# 5. Next experiment

앞선 분석 결과를 바탕으로 다음 실험을 설계한다면
한 번에 여러 조건을 임의로 변경하기보다
변수별 영향을 구분할 수 있도록 Split을 구성하는 방향이 적절하다고 판단했습니다.
예를 들어,
- 평균 두께 조정 → Process Time
- 증착량 / Deposition rate 변화 확인 → Si2H6 flow, RF Power
- wafer 내 분포 변화 확인 → Temperature
처럼 기존 데이터에서 확인된 경향을 바탕으로
다음 실험에서 우선 확인할 변수를 좁힐 수 있습니다.
이 단계에서 제안하는 조건은 기존 데이터의 경향을 이용한 후속 실험 후보이며,
실제로 같은 결과가 재현되는지는 추가 Split 실험을 통해 확인해야 합니다.


What I learned

이번 프로젝트를 통해 단순한 데이터 시각화보다
분석 목적에 맞게 데이터를 나누고 연결하는 과정이 더 중요하다는 점을 배웠습니다.
특히 다음 과정을 직접 정리했습니다.
- 공정 구간과 ramp-up 구간 분리
- Run별 설비 센서 비교
- Recipe Input과 계측 Output 매칭
- 조건을 통제한 그룹별 비교
- 평균값과 산포를 함께 확인
- wafer-level 위치 분포 시각화
- 분석 결과를 다음 실험 조건과 연결
결과적으로 공정 데이터를 보고
어떤 조건에서 차이가 발생했는지
어떤 변수를 먼저 확인해야 하는지
다음 실험에서는 무엇을 바꿔볼지

를 데이터 기준으로 좁혀보는 연습을 할 수 있었습니다.


Repository structure

analysis/  Reproducible Jupyter notebooks
data/      Aggregated educational sample data
images/    Analysis figures
src/       Source loading and calculation functions
tests/     Calculation, build, and privacy checks



Tools

- Python
- pandas
- NumPy
- Matplotlib
- openpyxl
- Jupyter Notebook
- Excel


Data

공개 저장소에는 교육용 공정 데이터를 바탕으로 재구성한 집계·샘플 데이터만 포함했습니다.
분석 목적은 공정·설비 데이터를 전처리하고 조건별 차이를 해석하는 분석 과정을 구현하는 것입니다.
