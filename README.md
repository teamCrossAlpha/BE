# 📊 CrossAlpha — 초보 투자자를 위한 트레이딩 저널 & AI 기반 투자 행동 분석 서비스

> **그로쓰 11팀 | 이화여자대학교 컴퓨터공학과 | 산학 트랙**  
> 지도교수: 이민수 교수님

[![Frontend](https://img.shields.io/badge/Frontend-React%20%2B%20TypeScript-blue)](https://github.com/ahrixxx/CrossAlpha-FE)
[![Backend](https://img.shields.io/badge/Backend-FastAPI-green)](https://github.com/teamCrossAlpha/BE)
[![DB](https://img.shields.io/badge/Database-PostgreSQL-blue)](https://www.postgresql.org/)
[![Deploy](https://img.shields.io/badge/Deploy-Railway%20%2B%20Vercel-black)](https://crossalpha-production.up.railway.app)

---

## 🔗 배포 서비스

| 구분 | URL |
|------|-----|
| **서비스 (FE)** | https://cross-alpha.vercel.app |
| **백엔드 API** | https://crossalpha-production.up.railway.app |

---

## 📌 프로젝트 개요

**CrossAlpha**는 해외주식 개인 투자자가 겪는 3가지 구조적 문제를 해결하는 트레이딩 저널 & AI 기반 투자 행동 분석 서비스입니다.

| 문제 | CrossAlpha의 해결 방식 |
|------|----------------------|
| 거래 기록에 "왜"가 없다 | 매 거래마다 의도(자유 텍스트) + 확신도(0~100) + 행동 태그(15개 카테고리) 기록 |
| 자기 투자 패턴을 인지하지 못한다 | 행동 태그 분포 시각화, 확신도-수익률 산점도, 나쁜 패턴 자동 집계 |
| 피드백 루프가 없다 | 10건 단위 퍼포먼스 스코어링 → 구간 비교 → LLM 기반 AI 액션 플랜 |

기존 증권사 앱이 **결과(수익률)** 만 보여준다면, CrossAlpha는 그 결과를 만들어낸 **의사결정 과정(행동 패턴)** 을 기록하고 AI로 분석합니다.

---

## 👩‍💻 팀원 소개

| 학번 | 이름 | 역할 | 담당 |
|------|------|------|------|
| 2276256 | **이혜령** | 팀장 | 서비스 기획, UI/UX 설계, 프론트엔드 개발, 산출물 관리 |
| 2376175 | **유채은** | 팀원 | FastAPI 백엔드 개발, AI 기반 분석 기능 구현, 기획 |
| 2376302 | **최지희** | 팀원 | FastAPI 백엔드 개발, AI 기반 분석 기능 구현, 기획 |

---

## 🔗 저장소

| 역할 | 링크 |
|------|------|
| **Frontend** | https://github.com/ahrixxx/CrossAlpha-FE |
| **Backend** | https://github.com/teamCrossAlpha/BE |
| **팀 그라운드룰** | https://github.com/ahrixxx/Graduation-Project/blob/main/GroundRule.md |

---

## 📸 화면 예시

**1) 매매일지** — 거래 기록과 의사결정 맥락을 한눈에 확인

![거래상세](./assets/trade_detail.png)

**2) 포트폴리오** — 보유 종목별 현재가, 수익률, 총 평가금액 요약

![포트폴리오](./assets/portfolio.png)

**ㄴ 종목 상세** — 실시간 시세, 기술적 지표 분석, 거래 시점 시장 스냅샷, RAG 기반 차트 분석 AI 어시스턴트

![종목상세](./assets/stock_detail.png)

**3) 분석 대시보드** — 섹터 트리맵과 누적 수익률 추이 시각화

![분석](./assets/analytics.png)

**4) 인사이트** — 행동 패턴 분석, 확신도-수익률 산점도, AI 트레이딩 코치

![인사이트](./assets/insight.png)

**5) 섹터 전망** — 섹터별 시장 동향과 AI 뉴스 요약

![섹터](./assets/sector.png)

---

## 🔑 주요 기능

### 1. 매매일지 (Home)
- **수동 거래 추가 (AddTradeModal)**: 종목, 가격, 수량, 의도, 확신도(0~100), 행동 태그를 한 화면에서 입력
- **거래 요약 통계**: 총 거래 수, 승률, 총 손익 요약
- **시장 스냅샷 자동 저장**: 매매 시점의 RSI, SMA, Bollinger Band 등 기술적 지표를 자동으로 캡처하여 기록

### 2. 행동 태그 분류 체계
투자 심리학 문헌과 실제 투자자 행동 사례를 기반으로 설계한 **15개 카테고리, 31개 하위 태그** 체계

- **매수 태그 (8개 카테고리)**: 추세추종형, 역추세형, 이벤트반응형, 가치신념형, 기술적분석형, 전략적매수형, 복구형, FOMO형
- **매도 태그 (7개 카테고리)**: 이익실현형, 손절형, 추세전환형, 리스크회피형, 기회비용형, 자금관리형, 감정반응형

### 3. 포트폴리오 (Portfolio)
- 보유 종목 카드 뷰 (현재가, 일일 변동, 수익률)
- 관심종목(Watchlist) 관리
- 총 평가금액 / 총 수익률 / 총 손익 요약

### 4. 분석 (Analytics)
- **섹터 트리맵**: Squarified Treemap 알고리즘으로 섹터별 비중과 손익 시각화
- **누적 수익률 차트**: 기간별(1M/3M/6M/1Y/YTD/ALL/커스텀) 성과 추이

### 5. 인사이트 (Insights)
- **퍼포먼스 스코어링**: 매도 완료 10건 단위로 0~100점 산출 (승률 + 평균 수익률 + 확신도 정확도 − 나쁜 패턴 감점)
- **매수/매도 패턴 분석**: 행동 태그 분포 도넛 차트 시각화
- **확신도-수익률 산점도**: 확신도와 실제 수익률의 상관관계 시각화
- **확신도 구간별 성과 분석**: 저(1\~49) / 중(50\~79) / 고(80\~100) 구간 평균 수익률 비교
- **AI 트레이딩 코치**: LLM 기반 행동 액션 플랜 생성 (gpt-4o-mini, 10건 단위 DB 캐싱)

### 6. 섹터 전망 (Sectors)
- 11개 섹터별 수익률 및 관심 섹터 관리
- Alpha Vantage API 뉴스 수집 → GPT AI 섹터 요약 카드

### 7. 종목 상세 / 거래 상세
- **종목 상세**: Yahoo Finance API 연동 실시간 시세, 기간별 차트, RSI/SMA20/SMA50/Bollinger Band 기술적 지표 제공 및 AI 해설, 뉴스 피드, RAG 기반 차트 분석 AI 어시스턴트
- **거래 상세**: 거래 정보, 의사결정 맥락, 거래 시점 시장 스냅샷, 연관 거래 복기

---

## 🛠 기술 스택

### Frontend
| 기술 | 용도 |
|------|------|
| React 18 + TypeScript | UI 개발, Vite 빌드 |
| Tailwind CSS | 스타일링, 다크모드 지원 |
| React Router v6 | 라우팅, Lazy loading |
| Plotly | 데이터 시각화 (산점도, 도넛 차트, 트리맵) |
| TradingView Widget | 종목 차트 렌더링 |
| React Context | 상태 관리 (AuthContext, ThemeContext) |

### Backend
| 기술 | 용도 |
|------|------|
| FastAPI (Python) | REST API 서버 |
| PostgreSQL | 관계형 DB (13개 테이블, JSONB 활용) |
| SQLAlchemy | ORM |
| Docker | 컨테이너 |
| Railway | 서버 및 DB 배포 |
| Redis (LangChain) | RAG 챗봇 대화 히스토리 저장 |

### AI / 외부 API
| 기술 | 용도 |
|------|------|
| OpenAI GPT-4o-mini | AI 트레이딩 코치, RAG 챗봇, 섹터 요약, 기술 지표 해설 |
| Yahoo Finance API (yfinance) | 실시간 주가, 기간별 차트, 기술 지표 데이터 |
| Alpha Vantage API | 섹터별 뉴스 수집 |
| Pandas | 기술적 지표 계산 (RSI, SMA, Bollinger Band) |

### DevOps
| 기술 | 용도 |
|------|------|
| GitHub Actions | CI/CD 자동화 |
| Railway | 백엔드 배포 |
| Vercel | 프론트엔드 배포 |

---

## 🏗 시스템 아키텍처

![시스템 아키텍처](./assets/architecture.png)

---

## 🚀 설치 및 실행 방법

### 사전 요구사항

- Node.js 18+
- Python 3.11+
- PostgreSQL 17+
- Git

### 1. 저장소 클론

```bash
# Frontend
git clone https://github.com/ahrixxx/CrossAlpha-FE.git

# Backend
git clone https://github.com/teamCrossAlpha/BE.git
```

### 2. Backend 설치 및 실행

```bash
cd BE

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 아래 값을 입력
```

`.env` 파일에 설정할 환경변수:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/crossalpha

# OpenAI
OPENAI_API_KEY=your_openai_api_key

# Alpha Vantage (섹터 뉴스)
ALPHA_VANTAGE_API_KEY=your_alpha_vantage_key

# JWT
SECRET_KEY=your_secret_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Kakao OAuth
KAKAO_CLIENT_ID=your_kakao_client_id
KAKAO_REDIRECT_URI=http://localhost:3000/auth/kakao/callback
```

#### DB 스키마 적용

PostgreSQL에 DB를 생성한 후, 레포 루트의 `schema.sql`을 적용합니다:

```bash
# DB 생성
createdb crossalpha

# 스키마 적용
psql -U your_user -d crossalpha < schema.sql
```

#### 서버 실행

```bash
uvicorn main:app --reload --port 8000
```

API 문서: http://localhost:8000/docs

### 3. Frontend 설치 및 실행

```bash
cd CrossAlpha-FE

# 의존성 설치
npm install

# 환경변수 설정
cp .env.example .env.local
```

`.env.local` 파일에 설정할 환경변수:

```env
VITE_API_BASE_URL=http://localhost:8000
VITE_KAKAO_CLIENT_ID=your_kakao_client_id
VITE_KAKAO_REDIRECT_URI=http://localhost:3000/auth/kakao/callback
```

```bash
# 개발 서버 실행
npm run dev
```

브라우저에서 http://localhost:3000 접속

### 4. 빌드 (프로덕션)

```bash
# Frontend 빌드
cd CrossAlpha-FE
npm run build

# Backend (Docker)
cd BE
docker build -t crossalpha-be .
docker run -p 8000:8000 --env-file .env crossalpha-be
```

---

## 🗄 DB 스키마

전체 스키마는 레포 루트의 [`schema.sql`](./schema.sql)을 참고하세요.

PostgreSQL 기반 13개 테이블로 구성됩니다.

| 테이블 | 설명 |
|--------|------|
| `users` | 사용자 정보, 카카오 OAuth |
| `trades` | 거래 기록 (종목, 가격, 수량, 의도, 확신도, 행동 태그, is_decision_complete) |
| `trade_results` | 거래 손익 결과 (pnl_rate, pnl_status) |
| `trade_market_snapshots` | 거래 시점 기술 지표 스냅샷 (RSI, SMA, BB — JSONB) |
| `holdings` | 보유 종목 |
| `watchlist` | 관심 종목 |
| `action_plans` | AI 트레이딩 코치 결과 (10건 단위 캐싱) |
| `performance_scores` | 구간별 퍼포먼스 스코어 |
| `sector_summaries` | 섹터별 AI 뉴스 요약 캐시 |
| `ticker_news` | Alpha Vantage 수집 뉴스 |

---

## 📁 소스코드 구조

### Backend (`BE`)

```
BE/
├── main.py                      # 앱 진입점, 라우터 등록
├── requirements.txt             # 의존성 목록
├── schema.sql                   # DB 스키마
├── trades/                      # 매매일지 (거래 기록)
├── portfolio/                   # 포트폴리오
├── watchlist/                   # 관심종목
├── insights/
│   ├── action_plan/             # AI 트레이딩 코치
│   ├── performance/             # 퍼포먼스 스코어링
│   ├── behavior_pattern/
│   │   ├── buy/                 # 매수 패턴 분석
│   │   └── sell/                # 매도 패턴 분석
│   └── confidence/
│       ├── scatter/             # 확신도-수익률 산점도
│       └── range/               # 확신도 구간별 성과
├── analysis/                    # 섹터 트리맵, 누적 수익률
├── sector/                      # 섹터 전망
├── sector_summary/              # 섹터 뉴스 AI 요약
├── interest_sector/             # 관심 섹터 관리
├── tickers/                     # 종목 시세 및 기술 지표
├── marketdata/                  # 거래 시점 시장 스냅샷
├── rag/                         # RAG 차트 분석 AI 어시스턴트
│   ├── docs/                    # 기술적 분석 개념 문서
│   └── vectorstore/             # 벡터 DB
├── auth/                        # 카카오 OAuth, JWT 인증
├── refresh_token/               # 토큰 갱신
├── user/                        # 사용자 정보
└── common/                      # 공통 유틸
```

---

## 📡 주요 API 엔드포인트

| 메서드 | 엔드포인트 | 설명 |
|--------|-----------|------|
| GET | `/api/trades` | 전체 거래 목록 |
| GET | `/api/trades/summary` | 거래 요약 (건수, 승률, 총손익) |
| POST | `/api/trades` | 거래 추가 |
| PATCH | `/api/trades/{id}` | 의사결정 정보 추가 (확신도, 행동태그 등) |
| GET | `/api/portfolio/summary` | 포트폴리오 요약 |
| GET | `/api/portfolio/holdings` | 보유 종목 목록 |
| GET | `/api/insights/action-plan` | AI 트레이딩 코치 액션 플랜 |
| GET | `/api/insights/performance-score` | 퍼포먼스 스코어 |
| GET | `/api/insights/pattern-analysis` | 행동 패턴 분석 |
| GET | `/api/sector-outlook/{sector}` | 섹터별 AI 뉴스 요약 |
| GET | `/api/stocks/{ticker}` | 종목 시세 및 기술 지표 |
| POST | `/api/chat/{ticker}` | RAG 차트 분석 챗봇 |

전체 API 명세: https://crossalpha-production.up.railway.app/docs

---

## 🔐 인증

- **카카오 OAuth 2.0** 소셜 로그인
- **JWT** (Access Token + Refresh Token) 기반 인증
- 모든 API 엔드포인트는 인증된 사용자만 접근 가능
