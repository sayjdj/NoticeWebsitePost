# Serverless Web Scraper & Notification System

이 프로젝트는 주기적으로 지정된 웹사이트(게시판 등)를 크롤링하여 새로운 글이 올라오면 텔레그램으로 알림을 보내고, 누적된 데이터를 GitHub Pages를 통해 웹 화면으로 제공하는 Serverless 아키텍처 기반의 시스템입니다.

## 아키텍처 및 기술 스택
- **언어**: Python 3.11+
- **크롤링**: `requests`, `BeautifulSoup4`
- **알림**: 텔레그램 Bot API
- **자동화**: GitHub Actions (Cron Job)
- **데이터베이스/상태**: JSON 파일 (`docs/data/posts.json`)
- **프론트엔드**: HTML, Vanilla JS, Tailwind CSS (GitHub Pages 호스팅)

## 설정 가이드

### 1. 텔레그램 봇 생성 및 정보 획득
1. 텔레그램에서 **BotFather**를 검색하여 대화를 시작합니다.
2. `/newbot` 명령어를 입력하고 봇의 이름과 사용자명을 설정합니다.
3. 생성 완료 후 발급되는 **HTTP API Token**을 복사합니다. (`TELEGRAM_TOKEN`에 사용)
4. 생성한 봇에게 메시지를 한 번 보냅니다. (예: `/start` 또는 안녕)
5. 웹 브라우저에서 `https://api.telegram.org/bot<발급받은_토큰>/getUpdates`에 접속합니다.
6. 응답 JSON에서 `"chat":{"id":123456789,...}` 부분의 숫자를 확인합니다. (`TELEGRAM_CHAT_ID`에 사용)

### 2. GitHub 저장소 Secrets 설정
이 프로젝트를 자신의 GitHub 계정으로 Fork(또는 Push)한 후, **Settings > Secrets and variables > Actions** 메뉴로 이동하여 다음 3개의 Repository Secrets를 추가합니다.

- **`TELEGRAM_TOKEN`**: 위에서 획득한 텔레그램 봇 토큰
- **`TELEGRAM_CHAT_ID`**: 위에서 획득한 텔레그램 채팅 ID
- **`TARGET_SITES`**: 크롤링할 웹사이트 목록과 CSS Selector 설정을 담은 JSON 배열 (반드시 유효한 JSON 형식이어야 합니다)

**`TARGET_SITES` 예시 (금천구청 고시공고):**
```json
[
  {
    "name": "금천구청 고시공고",
    "url": "https://www.geumcheon.go.kr/portal/selectBbsNttList.do?bbsNo=4&key=293",
    "base_url": "https://www.geumcheon.go.kr",
    "row_selector": "table.p-table tbody tr",
    "title_selector": "td.p-subject a",
    "link_selector": "td.p-subject a",
    "date_selector": "time"
  }
]
```
> **팁:** `link_selector`로 찾은 태그가 javascript 링크 형태인 경우 스크립트(`src/scraper.py`) 내에 예외 처리 로직이 구현되어 있습니다. 다른 사이트 추가 시 형태가 다르면 `src/scraper.py`의 `scrape_site` 함수를 적절히 수정해 주세요.

### 3. GitHub Pages 활성화
1. GitHub 저장소의 **Settings > Pages** 로 이동합니다.
2. **Build and deployment** 섹션의 Source 항목을 `Deploy from a branch`로 설정합니다.
3. Branch 항목에서 `main` (또는 작업 중인 브랜치명)을 선택하고 폴더를 `/docs`로 설정한 뒤 Save를 누릅니다.
4. 잠시 후 상단에 표시되는 GitHub Pages URL에 접속하여 수집된 게시글을 확인할 수 있습니다.

### 4. 로컬 테스트 방법
1. `.env.example` 파일을 복사하여 `.env` 파일을 생성하고, 내부의 값들을 본인의 설정에 맞게 수정합니다.
2. 의존성을 설치하고 스크립트를 실행합니다.
   (python 3 가상 환경을 생성하고 활성화 한 뒤에 진행하는 것을 권장합니다.)
