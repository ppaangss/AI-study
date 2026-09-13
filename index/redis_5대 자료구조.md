# Redis 5대 자료구조

Redis의 값(value)은 단순 문자열이 아니라 자료구조다. **"어떤 자료구조를 고르느냐"가 곧 Redis 설계의 절반.**

## 한눈에 정리

| 자료구조 | 자바로 치면 | 킬러 유스케이스 |
|---|---|---|
| String | `String` / `AtomicLong` | 캐시, 카운터, 분산 락 |
| List | `Deque` | 작업 큐, 최근 목록 |
| Hash | `HashMap` | 객체/세션 저장 |
| Set | `HashSet` | 중복 방지, 집합 연산 |
| Sorted Set | `TreeMap` 비슷 | 랭킹, 시간순 정렬 |

## ① String — 만능 기본형

키 하나에 값 하나(최대 512MB — 문자열, 숫자, JSON, 바이너리). 숫자도 문자열로 저장되며 `INCR`/`DECR` 때만 숫자로 해석된다. 실무 사용량의 절반 이상.

```
SET user:1:name "ppaangss"
GET user:1:name              → "ppaangss"
DECR stock:seat:42           → 원자적 감소 (재고 차감)
INCR view:post:7             → 조회수 +1
SET session:abc "{...}" EX 1800   → EX는 값이 아니라 TTL 옵션(1800초 뒤 만료)
SET lock:seat:42 "sv1" NX         → NX = 키가 없을 때만 저장 (분산 락의 기초)
```

## ② List — 양쪽에서 넣고 빼는 연결 리스트

덱(deque). 양끝 push/pop이 O(1), 중간 접근(`LINDEX`)은 O(N).

```
LPUSH queue:email "job1"     → 왼쪽 삽입
RPOP queue:email             → 오른쪽에서 꺼냄 = FIFO 큐
LRANGE timeline:u1 0 9       → 최근 10개
```

- **작업 큐**: `LPUSH` + `RPOP`. `BRPOP queue 30`은 블로킹 pop — 큐가 비면 최대 30초 대기하다가 작업이 들어오는 순간 반환. 폴링 없는 워커를 만든다 (자바 `Queue.poll()` vs `BlockingQueue.take()` 차이).
- **최근 목록**: `LPUSH` 후 `LTRIM`으로 N개만 유지.

## ③ Hash — 객체 저장용 미니 해시맵

값 자리에 **필드→값 쌍의 묶음**이 들어간다. Redis 전체가 `Map<String, Map<String, String>>`이 되는 셈.

```
HSET user:1 name "ppaangss" age 30 city "seoul"   ← 필드 값 번갈아 (쌍 내부 순서 중요, 쌍끼리 순서 무관)
HGET user:1 name        → 필드 하나만
HGETALL user:1          → 키 안의 미니 맵 통째로 (필드1,값1,필드2,값2,... → 클라이언트가 Map으로 변환)
HINCRBY user:1 age 1    → 필드 단위 숫자 연산
```

**String+JSON vs Hash 선택:** 필드 하나만 자주 읽고 쓰면 Hash, 항상 통째로 읽고 쓰면 String+JSON이 단순해서 낫다.

용도: 세션 데이터, 객체 캐시, 장바구니(`HSET cart:u1 상품ID 수량`).

## ④ Set — 중복 없는 집합

순서 없음, 중복 없음.

```
SADD like:post:7 "user1"      → 중복이면 0 반환(무시)
SISMEMBER like:post:7 "user1" → 있는지 O(1) 확인
SCARD like:post:7             → 좋아요 수
SINTER friends:A friends:B    → 교집합 (공통 친구)
```

용도: 좋아요/방문자 중복 방지, 집합 연산(`SINTER`/`SUNION`/`SDIFF` 내장).

## ⑤ Sorted Set (ZSet) — 점수로 정렬되는 집합 ★

각 멤버가 score(숫자)를 갖고 **항상 score 순으로 정렬된 상태를 유지**한다. 조회할 때 정렬하는 게 아니라 넣을 때부터 정렬돼 있다. 내부는 [skip list](<skip list.md>)로 삽입/삭제/조회 모두 O(log N).

```
ZADD ranking 1500 "userA"
ZREVRANGE ranking 0 2 WITHSCORES  → 상위 3명
ZREVRANK ranking "userA"          → 내 순위 (0부터)
ZINCRBY ranking 100 "userA"       → 점수 +100, 순위 자동 재배치
```

용도: 리더보드. score에 타임스탬프를 넣으면 시간순 정렬 — 활동 피드, 예약 대기열(선착순), rate limiter.

## 심화 자료구조 (이름만)

| 이름 | 한 줄 요약 | 예시 |
|---|---|---|
| Bitmap | 비트 단위 플래그. 1억 유저 출석 체크가 12MB | 출석부, DAU |
| HyperLogLog | 고유 개수를 근사치로(오차 0.81%, 12KB) | 고유 방문 IP 수 |
| Streams | Kafka 비슷한 로그, 소비자 그룹 지원 | 이벤트 스트리밍 |
| Geo | 위경도 저장, 반경 검색 | "내 주변 3km 매장" |

> 출처: [_raw/2026년/9월/13일/Redis 개요·자료구조·키 만료.md](<../_raw/2026년/9월/13일/Redis 개요·자료구조·키 만료.md>)
