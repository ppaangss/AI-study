#!/usr/bin/env python3
"""daily/ 를 원본으로 topics/ 와 README 인덱스를 재생성한다. 멱등."""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DAILY = ROOT / "daily"
TOPICS = ROOT / "topics"
README = ROOT / "README.md"

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CAT_RE = re.compile(r"^[\w가-힣.-]+/[\w가-힣.-]+$")

warnings = []


def parse_daily(path: Path):
    """한 daily 파일에서 (date, title, category, summary, blog) 목록을 뽑는다."""
    date = path.stem
    entries = []
    cur = None
    for line in path.read_text(encoding="utf-8").splitlines():
        h2 = re.match(r"^##\s+(.+)$", line)
        if h2:
            cur = {"date": date, "title": h2.group(1).strip(),
                   "category": "", "summary": "", "blog": "", "concepts": []}
            entries.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r"^-\s*(카테고리|요약|개념|블로그)\s*:\s*(.*)$", line)
        if m:
            if m.group(1) == "개념":
                cur["concepts"] = [c.strip() for c in m.group(2).split(",") if c.strip()]
            else:
                key = {"카테고리": "category", "요약": "summary", "블로그": "blog"}[m.group(1)]
                cur[key] = m.group(2).strip()

    valid = []
    for e in entries:
        if not e["category"] or not e["summary"]:
            warnings.append(f"{path.name} '{e['title']}': 카테고리/요약 누락 — 건너뜀")
            continue
        if not CAT_RE.match(e["category"]):
            warnings.append(f"{path.name} '{e['title']}': 카테고리 '{e['category']}' 형식 오류(대분류/주제) — 건너뜀")
            continue
        valid.append(e)
    return valid


def main():
    daily_files = sorted(p for p in DAILY.glob("*.md")
                         if DATE_RE.match(p.stem))
    all_entries = [e for p in daily_files for e in parse_daily(p)]

    existing_cats = {p.name for p in TOPICS.iterdir() if p.is_dir()} if TOPICS.exists() else set()

    # topics/<카테고리>/<주제>.md 재생성
    by_topic = {}
    for e in all_entries:
        by_topic.setdefault(e["category"], []).append(e)

    expected = set()
    for cat_topic, entries in sorted(by_topic.items()):
        cat, topic = cat_topic.split("/")
        if cat not in existing_cats and cat not in {c.split("/")[0] for c in by_topic if c < cat_topic}:
            close = [c for c in existing_cats if c.lower() == cat.lower() and c != cat]
            if close:
                warnings.append(f"카테고리 '{cat}' — 기존 '{close[0]}'와 대소문자만 다름. 오타인지 확인")
        out = TOPICS / cat / f"{topic}.md"
        expected.add(out)
        rows = []
        for e in sorted(entries, key=lambda x: x["date"], reverse=True):
            blog = f"[글]({e['blog']})" if e["blog"] else ""
            concepts = []
            for c in e["concepts"]:
                if not (ROOT / "index" / f"{c}.md").exists():
                    warnings.append(f"{e['date']} '{e['title']}': index/{c}.md 없음")
                concepts.append(f"[{c}](../../index/{c}.md)")
            rows.append(f"| [{e['date']}](../../daily/{e['date']}.md) | {e['title']} "
                        f"| {', '.join(concepts)} | {blog} |")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            f"# {topic}\n\n<!-- /sync가 생성한 파일 — 직접 편집 금지, daily/가 원본 -->\n\n"
            "| 날짜 | 공부한 것 | 개념 | 블로그 |\n|------|-----------|------|--------|\n"
            + "\n".join(rows) + "\n",
            encoding="utf-8")

    # 더 이상 참조되지 않는 파생 파일 정리
    for stale in sorted(TOPICS.rglob("*.md")):
        if stale not in expected:
            stale.unlink()
            warnings.append(f"참조 없는 주제 파일 삭제: {stale.relative_to(ROOT)}")
    for d in sorted(TOPICS.rglob("*"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            d.rmdir()

    # README 인덱스 재생성
    lines = ["", "## 주제별 인덱스", ""]
    by_cat = {}
    for cat_topic, entries in by_topic.items():
        cat, topic = cat_topic.split("/")
        by_cat.setdefault(cat, []).append((topic, entries))
    if not by_cat:
        lines.append("(아직 없음)")
    for cat in sorted(by_cat):
        lines.append(f"### {cat}")
        lines.append("")
        for topic, entries in sorted(by_cat[cat]):
            last = max(e["date"] for e in entries)
            lines.append(f"- [{topic}](topics/{cat}/{topic}.md) — {len(entries)}회, 최근 {last}")
        lines.append("")
    lines += ["## 최근 공부", ""]
    recent = sorted(all_entries, key=lambda e: e["date"], reverse=True)[:10]
    if not recent:
        lines.append("(아직 없음)")
    for e in recent:
        cat, topic = e["category"].split("/")
        blog = f" · [글]({e['blog']})" if e["blog"] else ""
        lines.append(f"- {e['date']} — {e['title']} ([{topic}](topics/{cat}/{topic}.md)){blog}")
    lines.append("")

    text = README.read_text(encoding="utf-8")
    new = re.sub(r"(<!-- SYNC:START -->).*(<!-- SYNC:END -->)",
                 lambda m: m.group(1) + "\n" + "\n".join(lines) + "\n" + m.group(2),
                 text, flags=re.S)
    README.write_text(new, encoding="utf-8")

    no_blog = sum(1 for e in all_entries if not e["blog"])
    print(f"항목 {len(all_entries)}건 → 주제 {len(by_topic)}개 (블로그 링크 미기입 {no_blog}건)")
    for w in warnings:
        print(f"⚠ {w}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
