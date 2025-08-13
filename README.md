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
### Niro EV 소비자 반응 모니터링 서비스


## 🔍 문제 상황  
- 미국은 현대차그룹에 매우 큰 비중의 시장이며, 미국 판매가 한국의 약 4배 수준임
- 올해 상반기(1~6월) 현대차그룹의 판매량은 4만 4533대로 지난해 같은 기간(6만 1883대에)보다 28% 줄었음
- 전체 차량 판매량은 90만대에 육박하며 상반기 기준 역대 최고의 미국 판매 실적을 기록했는데, 전기차는 역성장함
- 기아에서 전기차 판매 감소폭이 두드러지고 전년 동기(2만 9392대) 대비 53.4% 감소하며 반토막 남
- 특히 소형 전기 스포츠유틸리티차량(SUV)인 니로EV의 판매량이 67% 줄어든 2861대로 집계됨

## 💡 해결 방법  
- 미국 차량 커뮤니티에서 니로ev 모델에 대한 의견을 수집하여 성능 측면과 소비자 반응 측면에서 어느 부분에 문제가 있는지 분석하고 알려줌

## 🛠 ETL 파이프라인

### E : 소비자 반응을 트위터, 레딧, edmund.com에서 하루 단위로 모아서 추출 
### &nbsp; &nbsp; (+ JDpower는 1년주기로 지표 업데이트하니 1년), lambda로 하루에 한 번 크롤링 cronjob 돌려서 가져옴.
### &nbsp;
### T: 추출한 리뷰 중에서 키워드 기반 모델을 쓰던 키워드 라이브러리를 쓰던 aws lambda로 
### &nbsp; &nbsp; &nbsp; jd power 4개 지표중 어느 지표와 연관되어 있는지 판단하고, 긍정/부정을 분류함
### &nbsp;
### L: RDS에 적재후 ec2 t4.micro 대시보드 서버에 업데이트해서 보여주기


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

<img width="800" alt="pipelining" src="https://github.com/user-attachments/assets/26b4851e-c41f-416f-9d60-ea13cad1a004" />
