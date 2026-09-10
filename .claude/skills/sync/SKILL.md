---
name: sync
description: daily/ 날짜 로그를 원본으로 topics/ 주제 페이지와 README 인덱스를 재생성하고 커밋·푸시한다. 사용자가 "/sync", "위키 동기화해줘", "sync 돌려줘"라고 명시적으로 요청할 때만 실행한다. 일반적인 대화·질문에는 절대 자동 발동하지 않는다.
allowed-tools:
  - Bash
  - Read
  - Edit
---

# daily → topics 동기화 (sync)

daily가 원본, topics와 README 인덱스는 파생물이다. 이 스킬은 파생물을 통째로 재생성한다 — 몇 번을 다시 돌려도 안전하다(멱등). 블로그 링크를 daily에 나중에 추가하고 재실행하면 topics에도 반영된다.

## 절차

1. 스크립트 실행:

```bash
python3 .claude/skills/sync/scripts/sync.py
```

2. 출력의 `⚠` 경고를 확인한다:
   - **카테고리/요약 누락·형식 오류** — 해당 daily 파일을 사용자 대신 고치지 말고, 어떤 항목이 왜 빠졌는지 보고한다. 사용자가 고치면 재실행.
   - **카테고리 대소문자 불일치** — 오타 가능성. 사용자에게 확인.
   - **참조 없는 주제 파일 삭제** — daily에서 카테고리를 바꿨을 때 정상 동작. 보고만 한다.

3. 변경 확인 후 커밋·푸시:

```bash
git add -A && git status --short
git commit -m "sync: <오늘 날짜>" && git push origin main
```

4. 보고: 항목 수, 주제 수, 블로그 링크 미기입 건수, 경고 내용.

## 지켜야 할 선

- `daily/` 파일을 수정하지 않는다 — 기입은 사용자만 한다 (경고로 알려줄 뿐).
- `raw/`를 건드리지 않는다.
- `topics/`와 README 마커 사이를 손으로 고치지 않는다 — 스크립트가 전부 재생성한다.
