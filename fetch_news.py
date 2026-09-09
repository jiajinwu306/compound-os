#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
COMPOUND.OS 真实 AI 资讯抓取脚本
=================================

设计原则：
- 严格只从可验证的官方公开 RSS 源读取，不引入任何第三方 RSS 聚合或观点类博客。
- 关键词过滤：保留模型发布 / Agent / MCP / 工具调用 / API / 图像 / 视频 / 语音 / 推理类
  资讯，过滤融资、人事变动、观点文章、纯营销稿和重复内容。
- 翻译：优先 DeepSeek（用户已用国产路线，且 batch 接口便宜）。无 key 时保留英文原文
  并在 summary 字段注明 "(en, no translation)"，不编造中文内容。
- 容错：单个源失败不影响其他源；RSS 解析失败用 try/except；超时 10s。
- 每日输出重要性最高的 10 条，字段标准化为
  {original_title, title, summary, source, source_url, date, url, image, tags, fetched_at}。
- 图片：优先 RSS <enclosure> 或 <media:thumbnail>，其次原文 og:image；都没有则 image=null
  让前端使用来源视觉占位，禁止伪造新闻配图。

使用：
    # 1. 安装依赖（仅需一次）
    pip install requests deepseek

    # 2. 设置 DeepSeek key（可选；不设则只输出原文）
    $env:DEEPSEEK_API_KEY = "sk-xxx"  # Windows PowerShell
    export DEEPSEEK_API_KEY=sk-xxx     # bash

    # 3. 运行
    python fetch_news.py

    # 输出: ./news.json （与 index.html 同目录，部署时一起上传）

退出码：
    0 至少 1 条资讯成功
    1 所有源都失败
"""
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any
from xml.etree import ElementTree as ET

try:
    import requests
except ImportError:
    print("[ERROR] 缺少 requests，请先运行: pip install requests", file=sys.stderr)
    sys.exit(2)


# ============================================================================
# RSS 源（经实测 https 200 验证，2026-09-04 佳锦哥本机）
# ============================================================================
SOURCES: List[Dict[str, str]] = [
    {
        "id": "openai",
        "name": "OpenAI News",
        "url": "https://openai.com/news/rss.xml",
        "homepage": "https://openai.com/news/",
    },
    {
        "id": "github-changelog",
        "name": "GitHub Changelog",
        "url": "https://github.blog/changelog/feed/",
        "homepage": "https://github.blog/changelog/",
    },
    {
        "id": "deepmind",
        "name": "Google DeepMind",
        "url": "https://deepmind.google/blog/rss.xml",
        "homepage": "https://deepmind.google/blog/",
    },
    {
        "id": "aws-ml",
        "name": "AWS ML Blog",
        "url": "https://aws.amazon.com/blogs/machine-learning/feed/",
        "homepage": "https://aws.amazon.com/blogs/machine-learning/",
    },
]

# 关键词打分（命中加分，命中否定词则直接 -100 过滤）
# 优先保留：模型发布、Agent、MCP、工具调用、API、图像/视频/语音、推理
POSITIVE_KEYWORDS = [
    "model", "gpt", "claude", "gemini", "llama", "mistral", "qwen", "deepseek", "gemma",
    "agent", "copilot", "tool use", "tool call", "mcp", "function calling", "rag",
    "image", "vision", "video", "audio", "voice", "speech", "tts", "asr", "diffusion",
    "embed", "embedding", "fine-tun", "fine tun", "reason", "inference",
    "api", "sdk", "open source", "open-source", "release", "launch", "preview", "ga ",
    "gpt-4", "gpt-5", "claude 3", "claude 4", "embedding", "stable diffusion", "sora",
    "deploy", "endpoint", "inference", "training", "checkpoint", "weights", "dataset",
    "transformer", "diffusion", "rlhf", "dpo", "context window", "context length",
    "multimodal", "multi-modal", "real-time", "realtime", "code review", "models ",
    "chatgpt", "codex", "llm", "rag", "vector", "guardrail", "fine-tuning",
]
NEGATIVE_KEYWORDS = [
    "fundrais", "raised", "series a", "series b", "valuation", "ipo ", "acquired", "acquisition",
    "hires", "joins", "appointment", "named ceo", "leaves", "resigns", "named ",
    "opinion", "editorial", "viewpoint", "predictions for", "year in review",
    "celebrity", "chatgpt replaces", " ai is ", " ai will ", " AI 取代", "AI 取代",
    "giveaway", "sweepstakes",
    # GitHub Changelog 类目降权
    "npm ", "actions:", "cli ", "enterprise signups", "signing key", "trusted publishing",
]


# ============================================================================
# 数据模型
# ============================================================================
@dataclass
class NewsItem:
    original_title: str
    title: str            # 中文标题；翻译失败时 = original_title
    summary: str          # 中文摘要；翻译失败时 = original_summary
    original_summary: str = ""
    source: str = ""
    source_url: str = ""  # 来源主页
    date: str = ""        # YYYY-MM-DD
    url: str = ""         # 原文链接
    image: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    translated: bool = False
    score: int = 0
    fetched_at: str = ""  # 抓取时间 ISO8601


# ============================================================================
# HTTP / 解析
# ============================================================================
def fetch(url: str, timeout: int = 10) -> Optional[str]:
    """下载 RSS XML 文本，失败返回 None"""
    try:
        r = requests.get(
            url,
            timeout=timeout,
            headers={
                "User-Agent": "COMPOUND-OS-NewsBot/1.0",
                "Accept": "application/rss+xml, application/xml, text/xml, */*",
            },
        )
        if r.status_code == 200:
            return r.text
        print(f"  [warn] {url} -> HTTP {r.status_code}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"  [warn] {url} -> {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
        return None


def parse_rss(xml: str) -> List[Dict[str, str]]:
    """解析 RSS 2.0 / Atom 的 item/entry，返回原始 dict 列表"""
    items: List[Dict[str, str]] = []
    if not xml:
        return items
    try:
        root = ET.fromstring(xml)
    except ET.ParseError as e:
        print(f"  [warn] parse error: {e}", file=sys.stderr)
        return items

    # RSS 2.0
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        desc = (item.findtext("description") or "").strip()
        pub = (item.findtext("pubDate") or "").strip()
        # 图片
        img = None
        for child in item:
            if child.tag.endswith("content") and child.attrib.get("url"):
                img = child.attrib["url"]; break
            if child.tag.endswith("thumbnail") and child.attrib.get("url"):
                img = child.attrib["url"]; break
            if child.tag.endswith("enclosure") and child.attrib.get("url"):
                img = child.attrib["url"]; break
        # 提取 og:image（不在线解析原文页面，留给前端兜底）
        m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', desc)
        if m and not img:
            img = m.group(1)
        if title and link:
            items.append({"title": title, "link": link, "desc": desc, "pub": pub, "image": img or ""})

    # Atom
    for entry in root.iter("{http://www.w3.org/2005/Atom}entry"):
        title = (entry.findtext("{http://www.w3.org/2005/Atom}title") or "").strip()
        link_el = entry.find("{http://www.w3.org/2005/Atom}link")
        link = (link_el.attrib.get("href", "") if link_el is not None else "").strip()
        desc = (entry.findtext("{http://www.w3.org/2005/Atom}summary")
                or entry.findtext("{http://www.w3.org/2005/Atom}content")
                or "").strip()
        pub = (entry.findtext("{http://www.w3.org/2005/Atom}published")
               or entry.findtext("{http://www.w3.org/2005/Atom}updated") or "").strip()
        if title and link:
            items.append({"title": title, "link": link, "desc": desc, "pub": pub, "image": ""})

    return items


# ============================================================================
# 过滤 / 评分 / 去重
# ============================================================================
def score_item(title: str, summary: str, date_str: str = "") -> int:
    """给一条资讯打分；负分会被过滤。
    时效性加成：14 天内 +10，60 天内 +6，180 天内 +2，1 年内 -4，>1 年 -15。"""
    text = (title + " " + summary).lower()
    s = 0
    for kw in POSITIVE_KEYWORDS:
        if kw in text:
            s += 1
    for kw in NEGATIVE_KEYWORDS:
        if kw in text:
            s -= 100
    if date_str:
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
            days = (datetime.now(timezone.utc).date() - d).days
            if days < 0: s += 10
            elif days <= 14: s += 10
            elif days <= 60: s += 6
            elif days <= 180: s += 2
            elif days <= 365: s -= 4
            else: s -= 15
        except ValueError:
            pass
    return s


def normalize_date(s: str) -> str:
    """把 RFC822 / ISO 8601 格式的日期转成 YYYY-MM-DD"""
    if not s:
        return ""
    s = s.strip()
    # RFC822: "Fri, 04 Sep 2026 12:34:56 +0000"
    for fmt in (
        "%a, %d %b %Y %H:%M:%S %z",
        "%a, %d %b %Y %H:%M:%S %Z",
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ):
        try:
            dt = datetime.strptime(s, fmt)
            return dt.date().isoformat()
        except ValueError:
            continue
    # 暴力截前 10 个字符
    m = re.match(r"(\d{4}-\d{2}-\d{2})", s)
    return m.group(1) if m else ""


def clean_html(s: str) -> str:
    """剥掉 HTML 标签和实体"""
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    # 常见实体
    s = (s.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
           .replace("&quot;", '"').replace("&#39;", "'").replace("&nbsp;", " "))
    return s[:500]


# ============================================================================
# 翻译（DeepSeek，可选）
# ============================================================================
TRANSLATE_CACHE: Dict[str, Dict[str, str]] = {}

def deepseek_translate(text: str, api_key: str, max_retries: int = 2) -> Optional[str]:
    """调用 DeepSeek chat completion 翻译为中文；失败返回 None"""
    if not text or not api_key:
        return None
    if text in TRANSLATE_CACHE:
        return TRANSLATE_CACHE[text]["zh"]
    url = "https://api.deepseek.com/v1/chat/completions"
    prompt = (
        "你是一名资深 AI 行业译者。请将下列英文标题和摘要翻译为简体中文，"
        "要求：1) 准确传达技术含义（保留 model / API / Agent / MCP / RAG / RLHF / TTS / ASR 等专有名词不译）；"
        "2) 句式自然，新闻摘要风格；3) 标题不超过 30 字，摘要不超过 110 字；4) 只输出翻译结果，不要任何解释或前缀。\n\n"
        + text
    )
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2,
        "max_tokens": 600,
    }
    for attempt in range(max_retries + 1):
        try:
            r = requests.post(
                url,
                json=payload,
                headers={"Authorization": "Bearer " + api_key, "Content-Type": "application/json"},
                timeout=20,
            )
            if r.status_code == 200:
                d = r.json()
                zh = d["choices"][0]["message"]["content"].strip().strip('"').strip("'")
                TRANSLATE_CACHE[text] = {"zh": zh}
                return zh
            print(f"  [warn] DeepSeek HTTP {r.status_code}: {r.text[:120]}", file=sys.stderr)
        except Exception as e:
            print(f"  [warn] DeepSeek attempt {attempt+1} {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)
        time.sleep(0.8 * (attempt + 1))
    return None


# ============================================================================
# 主流程
# ============================================================================
def build_items() -> List[NewsItem]:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if api_key:
        print(f"[info] DeepSeek 翻译已启用（key 末 4 位 = ***{api_key[-4:]}）")
    else:
        print("[info] 未设置 DEEPSEEK_API_KEY，将只保留英文原文（无 key 不编造中文）")

    raw_pool: List[NewsItem] = []
    for src in SOURCES:
        print(f"[fetch] {src['name']} <- {src['url']}")
        xml = fetch(src["url"])
        if not xml:
            continue
        entries = parse_rss(xml)
        print(f"  parsed {len(entries)} items")
        for e in entries:
            title = clean_html(e["title"])
            summary = clean_html(e["desc"])
            if not title or not e["link"]:
                continue
            date = normalize_date(e["pub"])
            s = score_item(title, summary, date)
            if s <= 0:
                continue
            ni = NewsItem(
                original_title=title,
                title=title,  # 后面翻译
                summary=summary,  # 后面翻译
                original_summary=summary,
                source=src["name"],
                source_url=src["homepage"],
                date=normalize_date(e["pub"]),
                url=e["link"],
                image=e["image"] or None,
                tags=[],
                translated=False,
                score=s,
                fetched_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            )
            raw_pool.append(ni)

    # 去重（按 url 精确去重 + 标题 60 字模糊去重）
    seen_url, seen_title, dedup = set(), set(), []
    for it in sorted(raw_pool, key=lambda x: x.score, reverse=True):
        if it.url in seen_url:
            continue
        title_key = it.original_title[:60].lower()
        if title_key in seen_title:
            continue
        seen_url.add(it.url)
        seen_title.add(title_key)
        dedup.append(it)
    print(f"[info] 池中 {len(raw_pool)} -> 去重后 {len(dedup)}")

    # 多源配额：每个来源最多 4 条，避免单源占满 10 条
    per_source: Dict[str, int] = {}
    balanced: List[NewsItem] = []
    for it in sorted(dedup, key=lambda x: (x.score, x.date), reverse=True):
        cnt = per_source.get(it.source, 0)
        if cnt >= 4:
            continue
        per_source[it.source] = cnt + 1
        balanced.append(it)
    print(f"[info] 多源配额后: {len(balanced)} 条，分布: {per_source}")
    dedup = balanced

    # 翻译
    for it in dedup:
        if not api_key:
            it.translated = False
            it.title = it.original_title
            it.summary = it.original_summary
            continue
        zh = deepseek_translate(it.original_title + "\n" + it.original_summary, api_key)
        if zh and "\n" in zh:
            zh_title, _, zh_summary = zh.partition("\n")
            it.title = zh_title.strip() or it.original_title
            it.summary = zh_summary.strip() or it.original_summary
            it.translated = True
        else:
            it.translated = False
            it.title = it.original_title
            it.summary = it.original_summary

    # 按分数 + 时效性排序
    dedup.sort(key=lambda x: (x.score, x.date), reverse=True)
    return dedup[:10]


def write_news_json(items: List[NewsItem], out_path: Path) -> None:
    payload = {
        "version": 1,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "count": len(items),
        "items": [asdict(it) for it in items],
    }
    text = json.dumps(payload, ensure_ascii=False, indent=2)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(text, encoding="utf-8")
    print(f"[ok] 已写入 {out_path} · {len(items)} 条")


def _localappdata_news_path() -> Path:
    """返回桌面端缓存 news.json 路径，与 desktop/api.py 的 NEWS_FILE 完全一致：
    %LOCALAPPDATA%/CompoundOS/news.json（macOS/Linux 兜底到 ~/.CompoundOS）。"""
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        base = os.path.expanduser("~")
    return Path(base) / "CompoundOS" / "news.json"


def sync_to_desktop_cache(items: List[NewsItem]) -> None:
    """双写：把抓取结果额外复制到桌面端缓存目录，让 COMPOUND.OS 桌面应用
    在下一次打开/点「立即刷新」时读到当天数据。

    根因（2026-09-09）：
    旧流程只写项目根 news.json，桌面端 loadNews() 优先读
    %LOCALAPPDATA%/CompoundOS/news.json，二者从不自动同步，导致桌面端
    永远停在首次安装时拷贝的历史快照。这里补上管道断了的那一环。"""
    try:
        # 复用 write_news_json 生成同一份 payload 文本，保证两边完全一致
        payload = {
            "version": 1,
            "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": len(items),
            "items": [asdict(it) for it in items],
        }
        text = json.dumps(payload, ensure_ascii=False, indent=2)
        dst = _localappdata_news_path()
        dst.parent.mkdir(parents=True, exist_ok=True)
        tmp_fd, tmp_path = tempfile.mkstemp(dir=dst.parent, prefix="news.tmp")
        try:
            with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                os.fsync(f.fileno())
            os.replace(tmp_path, dst)
            print(f"[ok] 已同步到桌面端缓存 {dst} · {len(items)} 条")
        except Exception:
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            raise
    except Exception as e:
        # 桌面缓存同步失败不应阻断主流程（项目根已写成功）
        print(f"  [warn] 同步桌面端缓存失败（不影响项目根 news.json）: {type(e).__name__}: {str(e)[:80]}", file=sys.stderr)


def main() -> int:
    print("=" * 64)
    print("COMPOUND.OS 真实 AI 资讯抓取  ·  " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 64)
    items = build_items()
    if not items:
        print("[FAIL] 所有源都失败，未生成任何条目", file=sys.stderr)
        return 1
    write_news_json(items, Path(__file__).parent / "news.json")
    # 双写：同步到桌面端缓存目录，桌面应用下次打开/刷新即可读到当天数据
    sync_to_desktop_cache(items)
    print("[done]")
    return 0


if __name__ == "__main__":
    sys.exit(main())
