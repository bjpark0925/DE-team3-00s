## 테이블 2개에 대한 스키마 생성  
- create_schema.sql 생성
1. 예상 픽업 테이블
2. 인접 존 테이블

## EC2(스키마 정의용)에서 parquet 생성 후 RDS에 데이터를 저장하고 확인하는 테스트 작업
0. 사전 작업
- EC2, RDS의 inbound, outbound 규칙 확인
1. 의존성 설치
2. 환경변수 설정 (비밀번호 하드코딩 방지)
3. make_test_parquet.py 생성 후 실행
4. load_parquet_to_rds.py 생성 후 실행
5. RDS에서 적재된 데이터 확인

## 고려한 부분
- adjacent_zones (smallint[]): 배열 컬럼 → JDBC로 “바로 배열” 쓰기는 까다롭다. 배열은 java.sql.Array 로 처리해야 하는데, Spark의 일반적인 DataFrameWriter.jdbc() 경로는 파티션별 배치 insert에서 이 매핑을 자동으로 안전하게 해 주지 못하는 경우가 많기 때문이다.

- 성능 조절: reWriteBatchedInserts=true, 필요 시 batchsize/coalesce(파티션 개수 조절) 조정하여 성능을 조절할 수 있다.
---
## 구현 과정
### 로컬에서 EC2로 create_schema.sql 파일 전송
```
scp -i {pem키 경로} create_schema.sql ubuntu@{EC2 public domain}:~
```

### 로컬에서 ssh로 EC2에 접속
```
ssh -i {pem키 경로} ubuntu@{EC2 public domain}
ls -l create_schema.sql
```

### EC2에서 RDS에 접속
```
psql -h {RDS endpoint} -U {user name} -d {db name} -p 5432
```

#### RDS에서 썼던 명령어
- 스키마 목록  
\dn  
- 특정 스키마만 보기  
\dt nyc_tlc_data.*  
- 스키마 통째로 삭제  
DROP SCHEMA IF EXISTS nyc_tlc_data CASCADE;  

## EC2에서 RDS에 접속 + create_schema.sql 바로 실행 명령어
```
psql -h {RDS endpoint} -U {user name} -d {db name} -p 5432 -f create_schema.sql
```
