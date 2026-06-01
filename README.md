# 📊 CrossAlpha – 시간과 전문성이 부족한 개인 투자자를 위한,  포트폴리오 기반 투자 행동 인사이트 & 학습 서비스

## 📝 팀 주제  
시간과 전문성이 부족한 개인 투자자를 위한,  
포트폴리오 기반 **투자 행동 인사이트 & 학습 서비스**

<br>

## 📌 프로젝트 개요

CrossAlpha는 초보 투자자의 투자 행동 데이터를 실제 시장 데이터와 연결하여,
개인의 투자 패턴·리스크 요인·학습 포인트를 스스로 인식할 수 있도록 돕는 AI 기반 인사이트 대시보드입니다.

뉴스·차트 지표·매매 기록을 통합 분석하여,
사용자가 "왜 그때 그런 결정을 했는지"를 데이터로 이해하고 투자 역량을 성장시키는 것을 목표로 합니다.

<br>

## 👩‍💻 팀원 소개  

| 학번 | 이름 | 역할 |
|------|------|------|
| 2376175 | **유채은** | Backend / AI |
| 2276256 | **이혜령** | Frontend / AI / 팀장 |
| 2376302 | **최지희** | Backend / AI |

📌 [팀 그라운드룰 보기](https://github.com/ahrixxx/Graduation-Project/blob/main/GroundRule.md)  

<br>

## 🔗 저장소

| 역할 | 링크 |
|------|------|
| Backend | [teamCrossAlpha/BE](https://github.com/teamCrossAlpha/BE) |
| Frontend | [ahrixxx/CrossAlpha-FE](https://github.com/ahrixxx/CrossAlpha-FE) |

<br>

## 🔑 주요 기능
- **정성적 분석  — 섹터별 뉴스 요약 및 톤 분석**  
  - 매일 오전 9시, Alpha Vantage API로 섹터별 뉴스 수집
  - AI가 긍정·중립·부정 톤으로 시장 심리 요약 
- **정량적 분석 — 포트폴리오 지표 해석 + RAG 챗봇**
  - FinanceDataReader로 주요 지표(SMA, RSI, Bollinger 등) 계산
  - RAG 기반 챗봇이 사용자 눈높이에 맞춰 차트 해석
- **투자 행동 학습 로그— 나의 패턴을 인식하고 개선**
  - 사용자가 매매 이유 기록시, AI가 당시 시장 지표를 자동으로 캡처 → 투자 결정의 맥락과 감정적 요인을 함께 분석
   -> 사용자의 반복되는 판단 패턴과 편향을 시각화함으로써 사용자가 스스로 인식하고 학습할 수 있도록 피드백
<br>

## 🛠 기술 스택  

### 📊 데이터 분석 및 모델링
- [Python](https://www.python.org) – 데이터 처리 및 분석  
- [Pandas](https://pandas.pydata.org) – 시계열 데이터 처리 및 지표 계산  
- [NumPy](https://numpy.org) – 수치 계산  

### ⚙️ 백엔드
- [FastAPI](https://fastapi.tiangolo.com) – Python 기반 경량 웹 프레임워크  
- [PostgreSQL](https://www.postgresql.org) – 포트폴리오 및 시계열 데이터 저장  

### 💻 프론트엔드
- [React.js](https://react.dev) + TypeScript – 대시보드 UI 개발  
- [Tailwind CSS](https://tailwindcss.com) – 스타일링  
- [TradingView](https://www.tradingview.com) – 차트 시각화  
- [Vite](https://vitejs.dev) – 빌드 도구  

### 🤖 AI / NLP
- [OpenAI GPT API](https://platform.openai.com) – 뉴스 요약, 리스크 이벤트 설명, 개인화 코멘트  

### 📡 외부 데이터 소스
- [Alpha Vantage](https://www.alphavantage.co) – 금융/경제 데이터 API  
- [Yahoo Finance API (yfinance)](https://pypi.org/project/yfinance/) – 주식/ETF 시세 데이터