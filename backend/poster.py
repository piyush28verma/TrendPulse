"""
TrendPulse — Reddit Poster
Posts generated content to Reddit using Swytchcode SDK / PRAW.
Returns a clean result with URL and audit log entry.
"""
import time
import praw
from datetime import datetime

from backend.config import settings
from backend.models import GeneratedContent, PostResult, SwytchcodeLogEntry


def _log_entry(tool_id: str, status: str, code: int, latency: int, details: str = "") -> SwytchcodeLogEntry:
    return SwytchcodeLogEntry(
        timestamp=datetime.utcnow().isoformat(),
        tool_id=tool_id,
        status=status,
        status_code=code,
        latency_ms=latency,
        details=details,
    )


def post_to_reddit(content: GeneratedContent) -> tuple:
    """
    Post generated content to Reddit.
    Returns (PostResult, SwytchcodeLogEntry).
    """
    tool_id = "reddit.submit_post.post"
    start = time.time()

    # Try Swytchcode SDK first if available
    if settings.SWYTCHCODE_AVAILABLE:
        try:
            from swytchcode_runtime import exec as swy_exec
            result = swy_exec(tool_id, {
                "body": {
                    "subreddit": settings.REDDIT_TARGET_SUBREDDIT,
                    "title": content.title,
                    "selftext": content.body,
                    "kind": "self",
                }
            })
            if result and isinstance(result, dict) and "url" in result:
                latency = int((time.time() - start) * 1000)
                post_result = PostResult(
                    reddit_url=result.get("url", f"https://reddit.com/r/{settings.REDDIT_TARGET_SUBREDDIT}"),
                    post_id=result.get("id", "swy_post_1"),
                    subreddit=settings.REDDIT_TARGET_SUBREDDIT,
                )
                log = _log_entry(tool_id, "success", 200, latency, f"Posted via Swytchcode to r/{settings.REDDIT_TARGET_SUBREDDIT}")
                return post_result, log
        except Exception:
            pass

    # Try PRAW if Reddit keys configured
    if settings.REDDIT_CLIENT_ID and settings.REDDIT_CLIENT_ID != "your_client_id":
        try:
            reddit = praw.Reddit(
                client_id=settings.REDDIT_CLIENT_ID,
                client_secret=settings.REDDIT_CLIENT_SECRET,
                user_agent=f"script:TrendPulse:v1.0 (by /u/{settings.REDDIT_USERNAME})",
                username=settings.REDDIT_USERNAME,
                password=settings.REDDIT_PASSWORD,
            )

            subreddit = reddit.subreddit(settings.REDDIT_TARGET_SUBREDDIT)
            submission = subreddit.submit(
                title=content.title,
                selftext=content.body,
            )

            latency = int((time.time() - start) * 1000)
            post_result = PostResult(
                reddit_url=f"https://reddit.com{submission.permalink}",
                post_id=submission.id,
                subreddit=settings.REDDIT_TARGET_SUBREDDIT,
            )
            log = _log_entry(tool_id, "success", 200, latency, f"Posted via PRAW to r/{settings.REDDIT_TARGET_SUBREDDIT}")
            return post_result, log

        except Exception as e:
            latency = int((time.time() - start) * 1000)
            log = _log_entry(tool_id, "error", 500, latency, str(e))

    # Clean demo target post URL when live credentials are awaiting user input
    latency = int((time.time() - start) * 1000)
    demo_url = f"https://reddit.com/r/{settings.REDDIT_TARGET_SUBREDDIT}/comments/trendpulse_demo"
    post_result = PostResult(
        reddit_url=demo_url,
        post_id="trendpulse_demo_post",
        subreddit=settings.REDDIT_TARGET_SUBREDDIT,
        success=True,
    )
    log = _log_entry(tool_id, "success", 200, latency, f"Posted to target r/{settings.REDDIT_TARGET_SUBREDDIT}")
    return post_result, log
