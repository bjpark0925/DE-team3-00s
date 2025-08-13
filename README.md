# 💻 Softeer6th - team3 공공즈

## 📌 Ground Rule
1. 아이디어를 제시할 때 어느정도 문제가 존재한다는 실제 사례를 함께 제시할 것
    1. 그것을 바탕으로 상대를 설득하는 방향으로 아이디어 제시 (실제 발표도 설득을 바탕)
2. 누군가가 제시한 아이디어에 대한 문제점을 생각 해줄 것
    1. 이것 또한 실제 사례를 들고와서 제시할 것
    2. 다른 사람의 의견을 보았을 때 문제점이 더 잘 보이는 경향이 있음
    3. 여기서 문제점을 제시하는 것의 목적이 Kill 이 되어서는 안됨 더 좁은 문제로 좁히기 위함임을 명심할 것
3. 누군가가 과도하게 본인의 주장을 제시할 시 팀원이 저지해줄 것
   
## 📦 Data Product  
### 이용횟수를 최대화 하기 위한 거리 탑승을 위한 자율 주행 택시 경로 추천 서비스

## 🔍 상황  
- 자율주행 택시는 호출기반으로 운영이 되고 있고, 이용자를 내린 후 차고지로 이동하거나, 정차하는 방식으로 다음 호출을 대기한다
- 자율주행 택시 회사인 waymo가 이미 큰 규모의 사용자를 점유하고 있어 진입 장벽이 되어 신규 진입이 어려워졌다. 
- 스타트업 택시 회사는, waymo가 고려하지 않은 운영 방법인 거리 탑승(hailing)을 도입하려고 한다
- 거리 탑승을 통해 이용횟수를 늘려 새로운 고객층을 끌어모으려고 한다

## 👨‍💻 누구의
- 자율주행 택시 시장에 진입한지 얼마안된 스타트업 회사의 BI(business inteligence) 담당자 A, 신규 이용자가 늘어나지않아 CEO에게 큰 압박을 받는중

## 💰문제
- **승객 하차 이후 차량을 어느 곳으로 보내야 이용횟수가 최대가 되는지 알 수 없는 문제**

## 💡 해결 방법  
- 택시의 승객 하차 이후, 택시는 현재 위치와 현재 시각을 API 서버에 요청을 하면, 그 상황에 맞는 추천 대기 장소를 알려줌으로써 해결
- 필요한 지표 :  
	- 지역간 이동시간 지표
	- 실시간 교통체증 지표
	- 다른지역의 같은 시간대 탑승횟수 지표
	- 회사내 다른 택시 위치 지표
	- 연례 행사(주기성 이벤트) 지표 - 날짜 기반 or 요일 기반
 
## 🛠 ETL 파이프라인
<img width="800" alt="pipelining" src="https://github.com/user-attachments/assets/26b4851e-c41f-416f-9d60-ea13cad1a004" />

### &nbsp;
### &nbsp;

## 🧠 협업 노션  
📎 [Notion 바로가기](https://chayhyeon.notion.site/245331850b7b80b299e9c01ba572cc63)

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
        <img width="200" alt="박병준" src="https://private-user-images.githubusercontent.com/65696808/475629747-48382c0d-6da8-405f-957b-b6c375ebefda.jpg?jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJnaXRodWIuY29tIiwiYXVkIjoicmF3LmdpdGh1YnVzZXJjb250ZW50LmNvbSIsImtleSI6ImtleTUiLCJleHAiOjE3NTQ2MTI2NzgsIm5iZiI6MTc1NDYxMjM3OCwicGF0aCI6Ii82NTY5NjgwOC80NzU2Mjk3NDctNDgzODJjMGQtNmRhOC00MDVmLTk1N2ItYjZjMzc1ZWJlZmRhLmpwZz9YLUFtei1BbGdvcml0aG09QVdTNC1ITUFDLVNIQTI1NiZYLUFtei1DcmVkZW50aWFsPUFLSUFWQ09EWUxTQTUzUFFLNFpBJTJGMjAyNTA4MDglMkZ1cy1lYXN0LTElMkZzMyUyRmF3czRfcmVxdWVzdCZYLUFtei1EYXRlPTIwMjUwODA4VDAwMTkzOFomWC1BbXotRXhwaXJlcz0zMDAmWC1BbXotU2lnbmF0dXJlPThiMzE1ZWI1ODMzYWQwYTliOWI3MmNjNGI3NTUxNjhmOWI0NjYwYzBhYmZiM2JjYjY5ODFlM2U1ZTBlZjVmNjgmWC1BbXotU2lnbmVkSGVhZGVycz1ob3N0In0.dcvZgdnTPYStDvk9R9BfspSCGWmfnE1sl3iRsGHBshc" />
      </td>
    </tr>
  </table>
</div>
<br />
<br />


---

## 📂 프로젝트 정보

- ⏱ 기간: 2025.08.04 ~ 2025.08.30  
- 🛠 기술 스택: Python, Docker, AWS, Airflow, DynamoDB
- 🚀 배포 링크:

```bash
📁 저장소 구조
├── preprocessing/
├── extract/
├── data/
└── README.md
```

