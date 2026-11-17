# 🚂 Rail News

White page, beech me rail track, har lakri par ek khabar. The Hindu, BBC, Reuters aur ANI ki khabrein khud update hoti hain.

## Repo me ye files rakho

| File | Repo me kahan |
|------|---------------|
| index.html | root (sabse upar) |
| fetch_news.py | root |
| news.json | root (pehle se ek starter hai, Action isse update karega) |
| README.md | root |
| news.yml | `.github/workflows/news.yml` |

## Setup

1. Repo Settings > Actions > General > Workflow permissions me **Read and write permissions** chuno.
2. Repo Settings > Pages me branch `main`, folder `/ (root)` chuno.
3. Actions tab > **Update news** > **Run workflow** ek baar chalao.
4. Site `https://<username>.github.io/<repo>/` par khulegi. Uske baad news har 30 min me khud update hogi.

## Local test

```
python fetch_news.py
python -m http.server
```
Phir browser me `http://localhost:8000` kholo.
