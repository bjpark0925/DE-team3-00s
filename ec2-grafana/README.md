# 📊 Grafana 시각화 자동화 시스템 (with DynamoDB & Docker)

## 개요

이 프로젝트는 **AWS DynamoDB의 실시간 데이터를 주기적으로 수집하여 Grafana에서 자동 시각화**하는 시스템입니다.  
CSV 파일은 Docker 컨테이너에 마운트된 경로로 저장되며, Grafana는 백업된 설정을 자동 복원하여 **재설정 없이도 바로 시각화**가 가능합니다.

---

## 🔁 주요 구성요소

### 1. Python 스크립트: `save_csv_for_grafana.py`

- DynamoDB 테이블에서 데이터를 주기적으로 수집
- Pandas로 가공 후 CSV 파일로 저장
- `flag-dynamodb` 테이블은 타임스탬프 추가 후 append 저장
- 저장 경로: `/home/ubuntu/data`

### 2. Grafana Docker 컨테이너

```bash
docker run -d   --name=grafana   -p 3000:3000   -v /home/ubuntu/grafana_backup/grafana.ini:/etc/grafana/grafana.ini   -v /home/ubuntu/grafana_backup/grafana.db:/var/lib/grafana/grafana.db   -v /home/ubuntu/grafana_backup/plugins:/var/lib/grafana/plugins   -v /home/ubuntu/data:/var/lib/grafana/data   grafana/grafana
```

- 설정 파일 및 DB는 백업된 볼륨을 통해 자동 복원
- `/var/lib/grafana/data`에 마운트된 CSV를 실시간으로 반영

---

## 📦 파일 구조

```
.
├── save_csv_for_grafana.py     # DynamoDB → CSV 자동화 스크립트
└── /home/ubuntu/data/          # Grafana에서 참조하는 CSV 저장 경로
```

---

## 💾 수집 대상 테이블

1. **zone-count-dynamodb** → `zone-count-dynamodb.csv`
2. **pickup-zone-dynamodb** → `pickup-zone-dynamodb.csv`
3. **flag-dynamodb** → `flag-dynamodb.csv` (append, timestamp 포함)
4. **taxi-destination-dynamodb** → `taxi-destination-dynamodb.csv`

---

## 🧪 실행 방법

```bash
python save_csv_for_grafana.py
```

- 30초 간격으로 위 4개의 DynamoDB 테이블을 주기적으로 스캔 및 저장
- Grafana는 변경된 CSV를 자동 반영

---

## 📈 시각화 구성

### 실시간 패널
- API 서버 상태 (`Running` 상태 여부)
- API 서버 CPUUtilization, NetworkIO (In/Out)
- 실시간 택시 목적지 및 탑승 분포
- 일일 누적 탑승 수 및 분포

### 주간 통계
- 일자별 총 탑승 수 및 배차 성공률
- 가장 많이/적게 탑승한 지역
- 평균 배차 성공률 및 주간 변화 추이

---

## 🚨 Grafana Alert 조건

Grafana Alert 규칙은 다음 조건에 따라 Slack Webhook 등으로 전송됩니다:

| 알림 조건 | 설명 |
|-----------|------|
| `CPUUtilization ≥ 90%` | API 서버 과부하 감지 |
| `NetworkIn == 0` 또는 `NetworkOut == 0` | 네트워크 장애 의심 |
| `API 서버 상태 ≠ Running` | 서버 다운 감지 |
| `배정되지 않은 택시 존재` | 실시간 경고 패널에 노출됨 |

---

## 📝 참고 사항

- Grafana에는 **CSV 데이터 소스 플러그인**이 설치되어 있어야 함
- Grafana 설정은 `grafana.ini`로 자동 복원되므로 최초 UI 설정 불필요
- 컨테이너 재시작 시에도 동일 환경에서 시각화 가능

---

## 🔐 보안

- AWS 권한은 `~/.aws/credentials` 또는 EC2 인스턴스 프로파일을 통해 설정
- Grafana 비밀번호 및 Webhook은 환경에 맞게 수정

---