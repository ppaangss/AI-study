# Redis Eviction 정책

TTL이 "예약된 삭제"라면, eviction은 **"메모리가 한계에 닥쳤을 때의 강제 퇴거"**다. ([redis TTL과 키만료](<redis TTL과 키만료.md>)와 세트)

## maxmemory

```
maxmemory 2gb                      ← 메모리 상한
maxmemory-policy allkeys-lru       ← 꽉 찼을 때 뭘 버릴지
```

`maxmemory` 도달 상태에서 새 쓰기가 들어오면, 정책에 따라 기존 키를 버려 자리를 만든다.

## 정책 7종 — "어떤 범위 × 무슨 기준"의 조합

| 정책 | 버리는 범위 | 기준 |
|---|---|---|
| `noeviction` | 안 버림 | 쓰기 요청에 **에러 반환** (기본값) |
| `allkeys-lru` | 모든 키 | 가장 오래 안 쓴 것(LRU)부터 |
| `allkeys-lfu` | 모든 키 | 가장 드물게 쓰인 것(LFU)부터 |
| `allkeys-random` | 모든 키 | 무작위 |
| `volatile-lru` | **TTL 있는 키만** | LRU |
| `volatile-lfu` | TTL 있는 키만 | LFU |
| `volatile-ttl` | TTL 있는 키만 | 남은 수명 짧은 것부터 |

## LRU vs LFU

- **LRU** (Least Recently Used): "**최근에** 안 쓴 놈부터 퇴거" — 마지막 접근 시각 기준.
- **LFU** (Least Frequently Used): "**자주** 안 쓰인 놈부터 퇴거" — 접근 빈도 기준. 어쩌다 한 번 접근된 키가 LRU에선 살아남지만 LFU에선 밀려난다. 인기 키를 지키는 데는 LFU가 보통 더 정확.

Redis의 LRU/LFU는 정확한 계산이 아니라 **근사(approximation)** — 전체 정렬 대신 몇 개(기본 5개)를 샘플링해 그중 최악을 버린다. "정확함보다 싸게".

## 어떤 정책을 고르나 — 용도가 결정한다

| 상황 | 정책 | 이유 |
|---|---|---|
| 캐시 전용 (날아가도 DB에서 재조회) | `allkeys-lru` / `allkeys-lfu` | 꽉 차면 안 쓰는 것부터 버리는 게 캐시의 정의 |
| 세션·락 등 지워지면 안 되는 데이터 혼재 | `volatile-lru` | TTL 붙인 것(버려도 되는 캐시)만 퇴거 대상, TTL 없는 키는 보호 |
| 하나라도 유실 불가 (저장소로 사용) | `noeviction` | 꽉 차면 쓰기 에러 — "조용히 사라지는" 사고는 없음. 용량 모니터링 필수 |

**함정: 기본값이 `noeviction`** — 캐시로 쓰면서 정책을 안 바꾸면, 메모리가 차는 순간 캐시 쓰기가 전부 에러 나기 시작한다.

> 출처: [_raw/2026년/9월/13일/Redis 개요·자료구조·키 만료.md](<../_raw/2026년/9월/13일/Redis 개요·자료구조·키 만료.md>)
