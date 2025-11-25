# 💻 Softeer6th - Team3: 공공즈

## 🧠 협업 노션  
📎 [Notion 바로가기](https://chayhyeon.notion.site/24c331850b7b80f09ef4cee3c6056ebc)

---

## 🚕 프로젝트 개요: Street Hailing 기반 실시간 운행 지역 추천 서비스

### 🔍 문제 상황
- Uber, Lyft 등 호출형 서비스 확산으로 Yellow Taxi 시장 점유율 하락
- Yellow Taxi CEO는 탑승 횟수를 통한 점유율 확대에 초점
- BI팀은 기사에게 **탑승 횟수를 극대화할 지역**을 실시간으로 추천하는 시스템을 제안

### 👨‍💻 사용 대상
- 뉴욕 맨해튼에서 Street Hailing만 운영하는 Yellow Taxi사의 **배차 관리자(Fleet Manager)**

### 💰 핵심 기능
- **승객이 없는 상태(차고지 출발 직후, 승객 하차 직후)** 의 택시에게
- **가장 승차 가능성이 높은 지역(zone)** 을 실시간으로 추천

---

## 💡 해결 방법: 점수 기반 추천 알고리즘

### 알고리즘
- 택시가 배차 요청을 보내면, 인접한 지역(zone) 중에서 아래 지표를 기반으로 점수 계산:
  - **지표 1**: 과거 시간대별 승차 횟수
  - **지표 2**: 해당 zone에 위치한 빈 택시 수

### 점수 계산 예시 (17시 기준)

| zone | 과거 탑승 횟수 | 빈 택시 수 | 점수 (탑승횟수 ÷ (빈 택시 + 1)) |
|:---:|:---:|:---:|:---:|
| 브로드웨이 | 100 | 2 | 33.3 |
| 블루밍데일 | 50 | 1 | 25.0 |
| 미드타운 | 40 | 1 | 20.0 |
| 할렘 | 30 | 1 | 15.0 |


→ 점수가 가장 높은 **브로드웨이**를 추천

### 점수 계산용 테이블

| 테이블명 | 설명 |
|----------|------|
| `taxi-destination` | 택시별 현재 이동 중인 zone 정보 저장 |
| `zone-count` | zone별 빈 택시 수 저장 (빈 택시 많을수록 점수 하락) |

### 배차 관리자용 통계 테이블

| 테이블명 | 설명 |
|----------|------|
| `pickup-zone` | zone별 하루 누적 승차 횟수 저장 |
| `flag-dynamodb` | 배차 요청 수 (`dispatch_count`) 및 승차 완료 수 (`pickup_count`) 기록 → 배차 성공률 계산 |

---

## 👀 시각화: Grafana 대시보드

### 실시간 패널
- API 서버 상태 (`Running`, CPU 사용률, Network I/O)
- 실시간 zone 택시 수/목적지
- 일일 누적 승차 횟수
- 배정되지 않은 택시 경고

> 대시보드:  
> ![실시간](https://github.com/user-attachments/assets/6561fee5-c289-4183-afb2-7c437c7821ec)  

### 주간 통계
- 하루 단위 승차 수 및 성공률
- 주간 추이, 지역별 편차 시각화

> 대시보드:  
> ![주간](https://github.com/user-attachments/assets/85998310-2362-4669-a983-4d990ad1cd18)

---

## 🔔 알림 기능 (Slack 연동)

| 조건 | 설명 |
|------|------|
| `CPUUtilization ≥ 90%` | 서버 과부하 감지 |
| `NetworkIn/Out == 0` | 네트워크 장애 탐지 |
| `API 서버 상태 ≠ Running` | 서버 다운 감지 |
| `배정되지 않은 택시 존재` | 실시간 대시보드에 경고 표시 |

> 추가: AWS Lambda가 NYC TLC 데이터 업데이트 여부를 주기적으로 체크

---

## ⚙️ 시스템 구조 및 운영 고려 사항

- **인접 zone 정의**: 과거 기준 5분 내 도달 가능한 지역
- **비운행 시간 활용**: RDS가 DynamoDB 일일 통계를 백업 → DynamoDB 초기화

---

## 🛠 ETL 파이프라인

📌 [Miro ETL 다이어그램 보기](https://miro.com/app/board/uXjVJSgeANA=/)
<img width="904" height="321" alt="파이프라인 drawio (1)" src="https://github.com/user-attachments/assets/9e57fdc3-b2ff-4d00-9006-f738a03f06b9" />

---

## 👨‍👩‍👦‍ 팀원 소개

<div align="center">
<table>
<tr>
  <th>정세종</th>
  <th>임채현</th>
  <th>박병준</th>
</tr>
<tr>
  <td><img width="200" src="https://github.com/user-attachments/assets/a09d2be5-0c3c-43a5-b895-f252d5839374" /></td>
  <td><img width="200" src="https://i.namu.wiki/i/05iTwXCQEzxWuzq2DJJcIO6Kz-EgzR8778fH3eDDvhI_g5lg8Wo57Rp_KefumgoL5fUe8mg-as5eUJ8uYaNSnw.webp" /></td>
  <td><img width="200" src="https://github.com/user-attachments/assets/48382c0d-6da8-405f-957b-b6c375ebefda" /></td>
</tr>
<tr>
  <td><a href="https://github.com/sejjong">GitHub</a></td>
  <td><a href="https://github.com/bkindtoevery1">GitHub</a></td>
  <td><a href="https://github.com/bjpark0925">GitHub</a></td>
</tr>
</table>
</div>

---

## 📂 프로젝트 정보

- ⏱ 기간: `2025.08.04 ~ 2025.08.30`  
- 🛠 기술 스택: `Python`, `Docker`, `AWS Lambda`, `AWS S3`, `AWS EC2`, `Apache Spark`, `AWS RDS`, `DynamoDB`, `Grafana`

```
📁 저장소 구조
├── ec2-grafana
├── ec2-spark
├── fastapi-server-simulation
├── fastapi-server
├── lambda-functions
├── rds
└── README.md
```
