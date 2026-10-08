# Public data contract

## 공개 가능
- 차량 제조사/차종/세대/플랫폼 코드
- 생산연도 범위
- 사용자 검색용 별칭
- 정비 주제
- 안전 분류
- 검증 상태
- 공개용 opaque source reference

## 공개 금지
- 원본 URL 목록
- collector/parser 이름과 규칙
- raw snapshot 경로
- 내부 source registry
- 내부 endpoint/API mapping
- correction/reconciliation rule
- 비공개 품질 판정 세부 로직

## 링크 정책
브라우저가 받는 HTML/JavaScript/JSON에 원본 URL을 직접 포함하지 않는 것을 기본으로 합니다.
