# AI-study 위키 규칙

매일 AI에게 배운 것을 저장·추적하는 공부 위키. 흐름: 다른 세션에서 `/ppaangss-study-capture`(개인 스킬)를 부르면 _raw·index·daily에 저장되고 topics까지 갱신된다. 저녁에 index를 보며 복습하고 블로그에 직접 타이핑한 뒤, daily에 블로그 링크를 채우고 `/sync`로 반영한다.

## 구조와 역할

| 경로 | 역할 | 누가 쓰나 |
| --- | --- | --- |
| `_raw/<YYYY>년/<M>월/<D>일/<제목>.md` | 세션 공부 원본 그대로 | capture 스킬만 — **불변**, 기존 파일 수정 금지 |
| `index/<개념>.md` | 개념 단위 세부 정리 (플랫, 공부·블로그 작성 재료) | capture가 초안, **사용자가 언제든 수정** |
| `daily/YYYY-MM-DD.md` | 그날 공부한 주제 목록 | capture가 추가, 사용자가 블로그 링크 등 수정 |
| `topics/<카테고리>/<주제>.md` | 주제별 이력 테이블 (링크만) | sync 스크립트만 (직접 편집 금지) |
| `README.md`의 SYNC 마커 사이 | 주제별 인덱스 + 최근 공부 | sync 스크립트만 |

**daily가 topics/README의 원본이다.** 파생물(topics, README 마커 사이)을 손으로 고치지 않는다 — 다음 sync 때 덮어써진다. 실제 공부 내용은 전부 index에 있고, topics는 날짜·개념·블로그 링크만 담는다.

## daily 항목 형식

`daily/_template.md` 참조. `## 제목` + `카테고리:`(필수, `대분류/주제`) + `요약:`(필수) + `개념:`(index 파일명 쉼표 구분) + `블로그:`(글 쓴 후).

## 링크 규칙

GitHub 웹에서도 동작해야 하므로 Obsidian `[[위키링크]]`가 아닌 **일반 마크다운 상대 링크**만 쓴다.

## 스킬

- `/ppaangss-study-capture` (개인 스킬, 다른 세션에서 호출) — _raw 저장 + index 초안 + daily 항목 + sync까지 한 번에
- `/sync` (이 repo 스킬) — daily를 원본으로 topics/README 재생성. 블로그 링크를 나중에 채웠을 때 재실행(멱등)
