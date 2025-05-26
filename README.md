# Final-PJT

SSAFY 1학기 최종 관통 프로젝트 - 금융 서비스

## 프로젝트 개요

이 프로젝트는 금융 서비스를 제공하는 웹 애플리케이션으로, Django를 백엔드로, Vue.js를 프론트엔드로 사용하여 개발되었습니다. 주요 기능은 사용자 계정 관리, 금융 상품 관리, 기사 및 유튜브 콘텐츠 제공 등입니다.

## 주요 기능

### 백엔드
- **사용자 관리**: 사용자 등록, 로그인, 로그아웃, 프로필 관리
- **금융 상품 관리**: 금융 상품 CRUD 및 추천 서비스
- **기사 관리**: 기사 작성, 조회, 좋아요 기능
- **유튜브 콘텐츠**: 유튜브 API를 활용한 콘텐츠 제공

### 프론트엔드
- **Vue.js 기반 SPA**: 사용자 친화적인 인터페이스 제공
- **다국어 지원**: i18n을 활용한 다국어 지원
- **라우팅**: Vue Router를 사용한 페이지 전환

## 프로젝트 구조

### 백엔드
- `accounts/`: 사용자 관리 앱
- `articles/`: 기사 관리 앱
- `products/`: 금융 상품 관리 앱
- `youtube/`: 유튜브 콘텐츠 관리 앱
- `final_pjt/`: 프로젝트 설정 및 URL 라우팅

### 프론트엔드
- `src/`: Vue.js 소스 코드
  - `components/`: 재사용 가능한 Vue 컴포넌트
  - `views/`: 페이지 단위 Vue 컴포넌트
  - `router/`: Vue Router 설정
  - `stores/`: 상태 관리 (Vuex 또는 Pinia)

## 설치 및 실행

### 백엔드
1. Python 가상 환경 설정:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
2. 의존성 설치:
   ```bash
   pip install -r requirements.txt
   ```
3. 데이터베이스 마이그레이션:
   ```bash
   python manage.py migrate
   ```
4. 서버 실행:
   ```bash
   python manage.py runserver
   ```

### 프론트엔드
1. 의존성 설치:
   ```bash
   npm install
   ```
2. 개발 서버 실행:
   ```bash
   npm run dev
   ```

## 기술 스택

- **백엔드**: Django, SQLite
- **프론트엔드**: Vue.js, Vite
- **기타**: 유튜브 API, ESLint