from typing import Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter
import re


class CompressionLevel:
    RAW = 0
    SUMMARY = 1
    PATTERN = 2


@dataclass
class CompressedResult:
    level: int
    source_ids: List[str]
    output: Dict
    created_at: str = ""


class MemoryCompressor:
    def compress(self, entries: List[Dict], level: int = CompressionLevel.SUMMARY) -> CompressedResult:
        if level == CompressionLevel.SUMMARY:
            return self._summarize(entries)
        elif level == CompressionLevel.PATTERN:
            return self._extract_patterns(entries)
        return CompressedResult(level=CompressionLevel.RAW, source_ids=[e.get("id", "") for e in entries],
                                output={"entries": entries},
                                created_at=datetime.utcnow().isoformat())

    def _summarize(self, entries: List[Dict]) -> CompressedResult:
        ids = [e.get("id", "") for e in entries]
        summary_parts = []
        total_words = 0
        for e in entries:
            content = e.get("content", "") or ""
            title = e.get("title", "") or ""
            words = content.split()
            total_words += len(words)
            preview = " ".join(words[:50]) + ("..." if len(words) > 50 else "")
            summary_parts.append({"title": title, "preview": preview, "word_count": len(words)})

        return CompressedResult(
            level=CompressionLevel.SUMMARY,
            source_ids=ids,
            output={
                "entry_count": len(entries),
                "total_words": total_words,
                "entries": summary_parts,
                "compressed": True,
            },
            created_at=datetime.utcnow().isoformat(),
        )

    def _extract_patterns(self, entries: List[Dict]) -> CompressedResult:
        ids = [e.get("id", "") for e in entries]
        categories = Counter(e.get("category", "unknown") for e in entries)
        tags = Counter()
        all_words: List[str] = []
        titles: List[str] = []
        for e in entries:
            entry_tags = e.get("tags")
            if isinstance(entry_tags, list):
                for t in entry_tags:
                    tags[t] += 1
            content = e.get("content", "") or ""
            title = e.get("title", "") or ""
            all_words.extend(re.findall(r'\b[a-zA-Z]{4,}\b', content.lower()))
            if title:
                titles.append(title)

        word_freq = Counter(all_words).most_common(20)
        common_topics = [w for w, c in word_freq if c >= max(2, len(entries) // 2)]

        return CompressedResult(
            level=CompressionLevel.PATTERN,
            source_ids=ids,
            output={
                "entry_count": len(entries),
                "category_breakdown": dict(categories),
                "common_tags": {k: v for k, v in tags.most_common(10) if v > 1},
                "common_topics": common_topics,
                "titles": titles,
                "pattern_found": len(ids) > 1 and len(common_topics) > 0,
            },
            created_at=datetime.utcnow().isoformat(),
        )

    def suggest_patterns(self, all_entries: List[Dict]) -> List[Dict]:
        groups: Dict[str, List[Dict]] = {}
        for e in all_entries:
            cat = e.get("category", "unknown")
            groups.setdefault(cat, []).append(e)

        suggestions = []
        for category, entries in groups.items():
            if len(entries) >= 3:
                result = self._extract_patterns(entries)
                suggestions.append({
                    "category": category,
                    "entry_count": len(entries),
                    "pattern": result.output,
                    "source_ids": result.source_ids,
                })
        return suggestions


memory_compressor = MemoryCompressor()
