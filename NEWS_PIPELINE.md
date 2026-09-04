# COMPOUND.OS Real AI News Pipeline - Quick Reference

## Data flow
```
   [4 RSS sources]                                    [browser]
        |                                                 ↑
        v                                                 |
   fetch_news.py  -->  news.json  --> deploy to workbuddy --┘
        |                   ↑
        +-- DeepSeek trans. +-- localStorage fallback
        |
   run_daily.bat (Task Scheduler 10:00 daily)
        |
   notify.ps1 (Windows Toast)
```

## 4 verified sources (200 OK on this machine)
- OpenAI News · https://openai.com/news/rss.xml
- GitHub Changelog · https://github.blog/changelog/feed/
- Google DeepMind · https://deepmind.google/blog/rss.xml
- AWS ML Blog · https://aws.amazon.com/blogs/machine-learning/feed/

## Key files
- `fetch_news.py` Python fetcher (RSS parse / dedupe / scoring / optional translation)
- `news.json` Fetch output (deploy with index.html)
- `run_daily.bat` Daily entry point: fetch -> notify
- `notify.ps1` Windows desktop notification (PowerShell + WinForms NotifyIcon)
- `setup_scheduler.bat` Create daily 10:00 Task Scheduler task
- `remove_scheduler.bat` Remove the Task Scheduler task
- `index.html` Workspace (fetches ./news.json; shows push enable hint)

## Standardized fields (each item in news.json)
```json
{
  "original_title": "English original title",
  "title": "Chinese title (or original_title if no key)",
  "summary": "Chinese summary",
  "original_summary": "English summary",
  "source": "OpenAI News",
  "source_url": "https://openai.com/news/",
  "date": "2026-09-04",
  "url": "https://openai.com/index/...",
  "image": null,
  "tags": [],
  "translated": false,
  "score": 17,
  "fetched_at": "2026-09-04T14:34:57Z"
}
```

## Live vs Cache
- `state.news.mode === 'live'` -> current fetch of ./news.json succeeded
- `state.news.mode === 'cache'` -> fetch failed, fell back to localStorage
- Card tag "译" (green) = translated, "EN" (orange) = English original kept

## Failure fallback
1) Browser load -> fetch ./news.json fails -> read localStorage -> still empty -> prompt to run fetch_news.py
2) Single source fails -> other sources continue; news.json still generated
3) Translation fails -> keep English original, no "译" tag
4) Missing image -> show fixed source placeholder (OpenAI green, GitHub purple, DeepMind blue, AWS orange)

## Hard rules
- Do NOT fabricate AI news with LLM
- Do NOT fake news images
- Do NOT label old news as live
- Do NOT fall back to fake data when fetch fails
