# 자동차 정비 URL 및 도메인 전환 파일럿 (2026-10-10)

## 최신 구조 확인
- `index.html`: 차량 검색·연식/세대 필터; /fuel/, /purchase/ 별도 경로.
- `app-v2.js`: 공개 차량 카드에서 `/vehicles/<public-id>/` 링크. 이미 사람에게 읽히는 공개 영문 식별자.
- `vehicle.html?id=...`는 기존 쿼리 링크의 이전 버전 호환 shell로서 유지 (noindex).
- `scripts/build_vehicle_pages.py`가 `data/vehicles.json`과 승인된 `data/vehicle-details.json`에서 실제 HTML 생성. 저장소에 `vehicles/` 결과물을 매번 커밋하지 않고 CI/Pages Action이 빌드 단계에 생성.
- 검증 전 차량은 개별 HTML에 정보를 검증 중이라고 표기하지만 상세 내용이 빈약하므로 이번 단계에서는 noindex.

## 이번 PR
- `site.config.json`: 미선택 `public_origin=null`, 특정 루트 도메인에 종속되지 않는 origin 제어.
- `SITE_ORIGIN` 환경변수를 제공한 **검증된 운영 배포에서만** canonical과 sitemap 생성. 값은 `https://verified-host/` 또는 `https://verified-host/project-path/`로 실제 배포 기준.
- 상세 검증된 차량에만 canonical/sitemap. 정보 수집 예정 차량은 robots noindex, Google/Naver에 빈 정보 페이지 남발 방지.
- 정적 페이지 링크 `../../`는 GitHub 프로젝트 Pages의 경로와 맞춤 서브도메인의 루트 모두에서 유효. 기본 /fuel/, /purchase/ 경로 유지.
- `scripts/check_url_routes.py`와 Actions CI는 생성 파일, 내부 CSS, 기존 vehicle.html 쿼리, HTTP 직접 GET 200 검증. 실제 GitHub Pages Custom domain, DNS/Cloudflare 변경 없음.

## 주소 예시 (실제 파일 생성, 배포 확정 링크가 아님)
- /vehicles/hyundai-avante-md/
- /vehicles/mercedes-eclass-w212/
- /fuel/
- /purchase/
- 향후 `auto.<root>` 밑에서 동일한 경로 적용 가능 (루트 미확정).

## 점진 확장
1. 기존 영문 차량 공개 ID 자체가 안정적이고 검색에 읽히므로 이번에는 `/vehicles/{id}/`를 canonical 후보로 유지. `/maintenance/hyundai/avante-md/` 등 중복 별칭 자동 대량 생성은 보류.
2. 향후 제조사·차종·세대별 계층 탐색을 별도 의미 있는 랜딩 페이지로 만들 때까지 레거시 URL/슬러그 변경하지 않는다.
3. DNS 연결은 실제 도메인 결정 후 소유권 검증 → GitHub Pages Custom domain → CNAME/HTTPS 확인. Actions 기반 Pages 배포는 CNAME 파일을 커밋할 필요가 없음.
4. 개인 정비 안전 주의와 차량별 공식 사실/불확실성 표시를 유지하고 내부 원본 수집 정보를 공개하지 않는다.
5. 운영 배포 결과는 PR CI 통과와 구분해서 보고하고, 중요한 변경은 브랜치→PR→검토 후 병합.

## 용량/SEO 참고
- GitHub Pages 현재 권장 source 1GB, published site 1GB, Actions 배포 시간 및 서비스 제한을 고려해 페이지 수를 늘리기 전에 빌드 시간·크기·품질 측정.
- sitemap/canonical과 `SITE_ORIGIN`은 실제 운영 URL에서만 활성화. 미확정 후보인 evococoons.com / prince-in-wonderworld.com은 소스의 고정 URL로 배포하지 않음.
