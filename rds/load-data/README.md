# 🛠️ NYC TLC Parquet → RDS 적재 및 스키마 생성

## 📦 생성할 테이블

### 1. 예상 픽업 테이블  
- 승객의 예상 탑승 수요 데이터 저장  

### 2. 인접 존 테이블  
- 각 존에 인접한 존 리스트 저장 (배열 컬럼 포함)

### ✅ 스키마 정의 파일
- 파일명: `create_schema.sql`

---

## 🧪 EC2에서 Parquet 생성 → RDS 적재 테스트

### 0. 사전 준비  
- EC2와 RDS의 **보안 그룹(inbound/outbound)** 규칙 확인

### 1. 의존성 설치  
필요한 패키지 설치 (예: `pandas`, `pyarrow`, `psycopg2`, `sqlalchemy` 등)

### 2. 환경 변수 설정  
- RDS 접속 정보 및 비밀번호는 **하드코딩하지 않고 환경 변수로 관리**

### 3. 테스트용 Parquet 생성  
- `make_test_parquet.py` 작성 및 실행

### 4. Parquet → RDS로 적재  
- `load_parquet_to_rds.py` 작성 및 실행

### 5. 적재 데이터 확인  
- RDS 접속 후 SQL로 데이터 정상 저장 여부 확인

---

## ⚠️ 고려 사항

### 🧬 배열 컬럼 처리 이슈  
- `adjacent_zones (smallint[])`: Spark JDBC를 통한 직접 적재는 까다로움  
- `java.sql.Array`로 처리해야 하지만, `DataFrameWriter.jdbc()`의 기본 배치 insert에서는 자동 매핑이 잘 되지 않음

### 🚀 성능 최적화 옵션  
- `reWriteBatchedInserts=true` 설정  
- 필요 시 `batchSize` 또는 `coalesce`로 파티션 개수 조절

---

## 🔧 구현 과정 요약

### 1. 로컬에서 EC2로 스키마 파일 전송
```bash
scp -i {pem_파일_경로} create_schema.sql ubuntu@{EC2_public_DNS}:~
```

### 2. EC2 SSH 접속 및 스키마 파일 확인
```bash
ssh -i {pem_파일_경로} ubuntu@{EC2_public_DNS}
ls -l create_schema.sql
```

### 3. EC2에서 RDS 접속
```bash
psql -h {RDS_endpoint} -U {user_name} -d {db_name} -p 5432
```

### 4. RDS 내 유용한 psql 명령어
```sql
-- 스키마 목록 보기
\dn

-- 특정 스키마 테이블 목록
\dt nyc_tlc_data.*

-- 스키마 삭제 (전체 테이블 포함)
DROP SCHEMA IF EXISTS nyc_tlc_data CASCADE;
```

### 5. EC2에서 RDS에 SQL 파일 실행
```bash
psql -h {RDS_endpoint} -U {user_name} -d {db_name} -p 5432 -f create_schema.sql
```
