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
- Street Hailing 기반으로만 택시를 운영하는 Yellow Taxi 회사의 뉴욕 맨해튼 지부 개발팀 소프트웨어 엔지니어

## 💰문제
- **택시의 행선지가 정해지지 않았을 때(차고지에서 나온 직후 + 승객 하차 직후),** 
- **어느 곳으로 택시를 운행해야 Street Hailing 횟수를 늘릴지 알 수 없는 문제**

## 💡 해결 방법  
- 택시의 좌표를 보내면 과거의 택시 탑승 횟수를 기반으로 인접한 장소(zone)중에서 가장 탑승횟수를 최대화 할 수 있는 지점(zone)을 추천해준다

- 대안 선택을 위한 지표 :
  - 통제 도로 지표
  - Zone의 시간별 탑승 횟수 
  - Zone간 걸리는 시간
  - Zone별 평균 운임 요금
  - 택시가 속한 zone_count

## 🛠 ETL 파이프라인

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
- 🛠 기술 스택: Python, Docker, AWS, Redis
- 🚀 배포 링크 :

```bash
📁 저장소 구조
├── 
├── 
├── 
└── README.md
```

