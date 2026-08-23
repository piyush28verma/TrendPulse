"""
TrendPulse — Multi-Source Trend Fetcher
Fetches current trends from NewsAPI, Reddit, HackerNews, Dev.to, and Google News RSS.
Uses Swytchcode SDK when available, falls back to direct HTTP calls.
"""
import time
import httpx
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import List, Tuple

from backend.config import settings
from backend.models import TrendItem, SwytchcodeLogEntry


def _log_entry(tool_id: str, status: str, code: int, latency: int, details: str = "") -> SwytchcodeLogEntry:
    """Create a Swytchcode audit log entry."""
    return SwytchcodeLogEntry(
        timestamp=datetime.utcnow().isoformat(),
        tool_id=tool_id,
        status=status,
        status_code=code,
        latency_ms=latency,
        details=details,
    )


def _try_swytchcode(tool_id: str, args: dict):
    """
    Attempt to call via Swytchcode SDK.
    Returns (result, True) if successful, (None, False) if SDK not available.
    """
    if settings.SWYTCHCODE_AVAILABLE:
        try:
            from swytchcode_runtime import exec as swy_exec
            return swy_exec(tool_id, args), True
        except Exception:
            pass
    return None, False


def fetch_newsapi() -> Tuple[List[TrendItem], SwytchcodeLogEntry]:
    """Fetch top headlines from NewsAPI via Swytchcode or direct HTTP."""
    tool_id = "newsapi.top_headlines.get"
    start = time.time()
    trends = []

    try:
        result, used_swy = _try_swytchcode(tool_id, {
            "params": {"category": "technology", "pageSize": 15, "language": "en"}
        })

        if not used_swy:
            if not settings.NEWSAPI_KEY:
                latency = int((time.time() - start) * 1000)
                return [], _log_entry(tool_id, "error", 401, latency, "NEWSAPI_KEY not configured")

            with httpx.Client(timeout=10) as client:
                resp = client.get(
                    "https://newsapi.org/v2/top-headlines",
                    params={"category": "technology", "pageSize": 15, "language": "en", "apiKey": settings.NEWSAPI_KEY},
                )
                resp.raise_for_status()
                result = resp.json()

        articles = result.get("articles", []) if result else []
        for article in articles:
            if article.get("title") and article.get("title") != "[Removed]":
                trends.append(TrendItem(
                    title=article.get("title", ""),
                    description=article.get("description", "") or "",
                    source="NewsAPI",
                    source_type="news",
                    url=article.get("url", ""),
                    timestamp=article.get("publishedAt", ""),
                ))

        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "success", 200, latency, f"Fetched {len(trends)} news articles")
        return trends, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return [], log


def fetch_reddit() -> Tuple[List[TrendItem], SwytchcodeLogEntry]:
    """Fetch hot posts from Reddit subreddits (social chatter) via Swytchcode or direct HTTP."""
    tool_id = "reddit.hot_posts.get"
    start = time.time()
    trends = []
    subreddits = ["technology", "worldnews", "programming", "artificial"]

    try:
        result, used_swy = _try_swytchcode(tool_id, {
            "params": {"subreddits": subreddits, "limit": 10}
        })

        if not used_swy:
            with httpx.Client(timeout=10, headers={"User-Agent": "TrendPulse/1.0"}) as client:
                all_posts = []
                for sub in subreddits:
                    try:
                        resp = client.get(f"https://www.reddit.com/r/{sub}/hot.json", params={"limit": 5})
                        resp.raise_for_status()
                        data = resp.json()
                        posts = data.get("data", {}).get("children", [])
                        all_posts.extend(posts)
                    except Exception:
                        continue
                result = {"posts": all_posts}

        posts = result.get("posts", []) if result else []
        for post in posts:
            post_data = post.get("data", post) if isinstance(post, dict) else {}
            title = post_data.get("title", "")
            selftext = post_data.get("selftext", "")
            if title:
                trends.append(TrendItem(
                    title=title,
                    description=selftext[:300] if selftext else title,
                    source=f"Reddit r/{post_data.get('subreddit', 'tech')}",
                    source_type="social_chatter",
                    url=f"https://reddit.com{post_data.get('permalink', '')}",
                    timestamp=datetime.utcfromtimestamp(
                        post_data.get("created_utc", time.time())
                    ).isoformat() if post_data.get("created_utc") else "",
                ))

        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "success", 200, latency, f"Fetched {len(trends)} social posts from Reddit")
        return trends, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return [], log


def fetch_hackernews() -> Tuple[List[TrendItem], SwytchcodeLogEntry]:
    """Fetch top stories from HackerNews (emerging topics) via Swytchcode or direct HTTP."""
    tool_id = "hackernews.topstories.get"
    start = time.time()
    trends = []

    try:
        result, used_swy = _try_swytchcode(tool_id, {
            "params": {"limit": 10}
        })

        if not used_swy:
            with httpx.Client(timeout=10) as client:
                resp = client.get("https://hacker-news.firebaseio.com/v0/topstories.json")
                resp.raise_for_status()
                story_ids = resp.json()[:10]

                stories = []
                for sid in story_ids:
                    try:
                        item_resp = client.get(f"https://hacker-news.firebaseio.com/v0/item/{sid}.json")
                        item_resp.raise_for_status()
                        stories.append(item_resp.json())
                    except Exception:
                        continue
                result = {"stories": stories}

        stories = result.get("stories", []) if result else []
        for story in stories:
            if story and story.get("title"):
                trends.append(TrendItem(
                    title=story.get("title", ""),
                    description=story.get("text", story.get("title", ""))[:300],
                    source="HackerNews",
                    source_type="emerging_topic",
                    url=story.get("url", f"https://news.ycombinator.com/item?id={story.get('id', '')}"),
                    timestamp=datetime.utcfromtimestamp(
                        story.get("time", time.time())
                    ).isoformat() if story.get("time") else "",
                ))

        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "success", 200, latency, f"Fetched {len(trends)} HackerNews stories")
        return trends, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return [], log


def fetch_devto() -> Tuple[List[TrendItem], SwytchcodeLogEntry]:
    """Fetch top trending articles from Dev.to (social & developer chatter)."""
    tool_id = "devto.articles.get"
    start = time.time()
    trends = []

    try:
        result, used_swy = _try_swytchcode(tool_id, {"params": {"top": 1, "per_page": 10}})

        if not used_swy:
            with httpx.Client(timeout=10) as client:
                resp = client.get("https://dev.to/api/articles?top=1&per_page=10")
                resp.raise_for_status()
                result = {"articles": resp.json()}

        articles = result.get("articles", []) if result else []
        for art in articles:
            title = art.get("title", "")
            desc = art.get("description", "") or title
            if title:
                trends.append(TrendItem(
                    title=title,
                    description=desc,
                    source="Dev.to",
                    source_type="social_chatter",
                    url=art.get("url", ""),
                    timestamp=art.get("published_at", ""),
                ))

        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "success", 200, latency, f"Fetched {len(trends)} articles from Dev.to")
        return trends, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return [], log


def fetch_googlenews_rss() -> Tuple[List[TrendItem], SwytchcodeLogEntry]:
    """Fetch trending technology news from Google News RSS."""
    tool_id = "googlenews.rss.get"
    start = time.time()
    trends = []

    try:
        result, used_swy = _try_swytchcode(tool_id, {})

        if not used_swy:
            rss_url = "https://news.google.com/rss/headlines/section/topic/TECHNOLOGY?hl=en-US&gl=US&ceid=US:en"
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(rss_url)
                resp.raise_for_status()

                # Parse RSS XML
                root = ET.fromstring(resp.text)
                items = []
                for item in root.findall("./channel/item")[:10]:
                    title = item.findtext("title", "")
                    link = item.findtext("link", "")
                    pub_date = item.findtext("pubDate", "")
                    if title:
                        items.append({"title": title, "link": link, "pubDate": pub_date})
                result = {"items": items}

        items = result.get("items", []) if result else []
        for item in items:
            trends.append(TrendItem(
                title=item.get("title", ""),
                description=f"Trending Google News story: {item.get('title', '')}",
                source="Google News",
                source_type="news",
                url=item.get("link", ""),
                timestamp=item.get("pubDate", ""),
            ))

        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "success", 200, latency, f"Fetched {len(trends)} Google News items")
        return trends, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return [], log


def fetch_all_trends() -> Tuple[List[TrendItem], List[SwytchcodeLogEntry]]:
    """
    Fetch trends from ALL sources (NewsAPI, Reddit, HackerNews, Dev.to, Google News).
    Returns (all_trends, swytchcode_audit_log).
    """
    all_trends = []
    all_logs = []

    # Source 1: NewsAPI
    news_trends, news_log = fetch_newsapi()
    all_trends.extend(news_trends)
    all_logs.append(news_log)

    # Source 2: Reddit (Social Chatter)
    reddit_trends, reddit_log = fetch_reddit()
    all_trends.extend(reddit_trends)
    all_logs.append(reddit_log)

    # Source 3: HackerNews (Emerging Topics)
    hn_trends, hn_log = fetch_hackernews()
    all_trends.extend(hn_trends)
    all_logs.append(hn_log)

    # Source 4: Dev.to (Developer Social Chatter)
    dev_trends, dev_log = fetch_devto()
    all_trends.extend(dev_trends)
    all_logs.append(dev_log)

    # Source 5: Google News RSS (Global News)
    gn_trends, gn_log = fetch_googlenews_rss()
    all_trends.extend(gn_trends)
    all_logs.append(gn_log)

    return all_trends, all_logs
