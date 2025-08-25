# 💻 Softeer6th - team3 공공즈

## 🧠 협업 노션  
📎 [Notion 바로가기](https://chayhyeon.notion.site/24c331850b7b80f09ef4cee3c6056ebc)

## 🚕 Data Product  
### Street Hailing 택시의 과거 수요 기반 실시간 운행 지역 추천 서비스


## 🔍 상황  
- 최근 Uber, Lyft와 같은 on-call 서비스들이 많아짐에 따라 Yellow Taxi의 점유율은 감소하였다. 
- Yellow Taxi CEO는 택시의 탑승횟수를 늘려 이용자를 늘리면서 시장점유율을 높이는 것에 초점을 두었고, 
- Yellow Taxi 회사의 BI는 택시 기사에게 탑승횟수를 최대화하기 위한 지점을 추천해주는 서비스를 도입하는 것을 제안한다.
- 2,000대(맨해튼 내)의 택시를 운영하는 Yellow Taxi의 소프트웨어 엔지니어는 BI가 제안한 거리탑승 도입을 위한 택시 대기 장소 추천 알고리즘을 만들어야 한다.
- 우선적으로 뉴욕 맨해튼에서 이를 시행하려고 한다

## 👨‍💻 누구의
- Street Hailing 기반으로만 택시를 운영하는 Yellow Taxi 회사의 뉴욕 맨해튼 지부 배차 관리자 (Fleet Manager)

## 💰문제
- **택시의 행선지가 정해지지 않았을 때(차고지에서 나온 직후 + 승객 하차 직후),** 
- **어느 곳으로 택시를 운행해야 Street Hailing 횟수를 늘릴지 알 수 없는 문제**

## 💡 해결 방법  
- 택시가 배차 요청(나 어디로 가?)을 보내면, 과거 택시 탑승 횟수를 기반으로 인접한 지역(zone)중에서 가장 탑승횟수를 최대화 할 수 있는 지역(zone)을 추천해준다.

- 추천할 Zone 선정을 위한 지표:
  - 지표 1: Zone의 시간대별 탑승 횟수(과거 승객 탑승 이력 기반)
  - 지표 2: 현재 Zone에 위치한 빈 택시(승객을 태우지 못한 택시) 수
- 점수 계산 방식 예시
  - 시나리오
    	택시 A는 현재 브로드웨이, 블루밍데일, 미드타운, 할렘에 인접한 지역에 있다.
    	현재 시각은 17시. 과거 데이터 중 17시에 해당하는 과거 탑승 횟수를 zone별로 가져온다.
	```
	| zone | 과거 탑승 횟수 | 현재 zone에 위치한 빈 택시 수 |
	| --- | --- | --- |
	| 브로드웨이 | 100 | 2 |
	| 블루밍데일 | 50 | 1 |
	| 미드타운 | 40 | 1 |
	| 할렘 | 30 | 1 |
	```
  		zone별 과거 탑승 횟수를 (현재 zone에 위치한 빈 택시 수 + 1)로 나눠, 점수를 계산한다.
    ```
    | zone | 과거 탑승 횟수 | 현재 zone에 위치한 빈 택시 수 | 점수 |
	| --- | --- | --- | --- |
	| 브로드웨이 | 100 | 3 | 33.3 |
	| 블루밍데일 | 50 | 2 | 25 |
	| 미드타운 | 40 | 2 | 20 |
	| 할렘 | 30 | 2 | 15 |
    ```
		택시 A는 점수가 가장 높은 '브로드웨이'를 다음 행선지로 추천받는다.
	- 이런 점수 계산 방식은 수천 대의 택시가 동시에 운행 중인 경우에도, 전체 탑승 횟수를 최대화하도록 설계했다.

- 점수 지표 계산을 위한 테이블
  	1. taxi-destination 테이블
 		- Key: taxi_id
			- 택시 구분자
		- Value: next_zone_id
  			- 택시가 향하던 지역
  		- 설명: next_zone_id가 없는 택시는 차고지에서 처음 출발하는 택시인 점을 알 수 있고, next_zone_id를 이용해 점수 계산 시 next_zone에 증가시켰던 빈 택시 수를 업데이트하여 로직이 올바르게 동작하도록 만든다.
	2. zone-count 테이블
		- Key: zone_id
			- zone 구분자 겸 지역명(ex. 브로드웨이)
  		- Value: count
  			- 이 zone에 존재하는 빈 택시 수
  		- 설명: 추천 zone 점수 계산에 활용됨(zone에 빈 택시 수가 많으면 많을수록 점수가 떨어지는 식). 택시가 현재 지역에서 승객을 태웠으면 count가 업데이트된다.

- 배차 담당자에게 실시간, 일일, 일주일 지표 제공을 위한 테이블
  	1. pickup-zone 테이블
  	   - Key: pickup_zone_id
  	   - Value: count
  	   - 설명: 승차 요청(승객을 태운)한 택시만 기록하는 테이블. 하루 동안 count가 계속 누적되어, 어느 지역에서 승차가 많이 혹은 적게 일어나는지 알 수 있다.
  	2. flag-dynamodb 테이블
  	   - Value: dispatch_count
  	     	- 배차 요청 count
  	    - Vaule: pickup_count
  	      	- 승차 요청 count
  		- 설명: 하루 동안 count가 계속 누적된다. 배차 요청 수, 승차 요청 수를 파악해 배차 성공률을 계산할 수 있다.

- 시각화
  Grafana
  <img width="1891" height="921" alt="image" src="https://github.com/user-attachments/assets/56dfb7af-07dc-47de-8d6d-ef7b48da041b" />

- 알림 기능
	1. AWS Lambda가 매달 업데이트되는 NYC TLC 데이터를 가져오기 위해, 매일 알림을 보내 NYC TLC 데이터가 업데이트 됐는지 확인한다.
	2. API 서버에 과부하가 일어나 다운되는 것을 방지하기 위해, CPU 사용량과 네트워크 IO를 기반으로 일정 수준 이상이면 알림을 보낸다.

## 💡 고려 사항
- 인접한 zone의 정의: 과거 데이터 기준으로, 5분 이내에 도달 가능한 zone
- 택시를 운행하지 않는 시간이 존재한다. 이 시간에 RDS가 DynamoDB의 일일 통계를 가져오고, DynamoDB를 초기화한다.

## 🛠 ETL 파이프라인

[Miro 바로가기](https://miro.com/app/board/uXjVJSgeANA=/)

### &nbsp;
### &nbsp;



---

## 👨‍💻 팀원 소개

<br/>

<div align="center">
<table>
<th>팀원</th>
    <th> 정세종 <a href="https://github.com/sejjong"><br/><img src="https://img.shields.io/badge/Github-181717?style=flat-square&logo=Github&logoColor=white"/><a></th>
	  <th> 임채현 <a href="http://github.com/bkindtoevery1"><br/><img src="https://img.shields.io/badge/Github-181717?style=flat-square&logo=Github&logoColor=white"/></a></th>
    <th> 박병준 <a href="https://github.com/bjpark0925"><br/><img src="https://img.shields.io/badge/Github-181717?style=flat-square&logo=Github&logoColor=white"/></a></th>
    <tr>
    <td> 팀원 소개 </td>
    	<td>
        <img width="200" alt="정세종" src="https://github.com/user-attachments/assets/a09d2be5-0c3c-43a5-b895-f252d5839374" />
      </td>
    	<td>
        <img width="200" alt="임채현" src="https://i.namu.wiki/i/05iTwXCQEzxWuzq2DJJcIO6Kz-EgzR8778fH3eDDvhI_g5lg8Wo57Rp_KefumgoL5fUe8mg-as5eUJ8uYaNSnw.webp" />
     </td>
      <td>
        <img width="200" alt="박병준" src="https://github.com/user-attachments/assets/48382c0d-6da8-405f-957b-b6c375ebefda" />
      </td>
    </tr>
  </table>
</div>
<br />
<br />


---

## 📂 프로젝트 정보

- ⏱ 기간: 2025.08.04 ~ 2025.08.30  
- 🛠 기술 스택: Python, Docker, AWS Lambda, AWS S3, AWS EC2, Apache Spark, AWS RDS, AWS DynamoDB, Grafana
- 🚀 배포 링크 :

```bash
📁 저장소 구조
├── 
├── 
├── 
└── README.md
```

