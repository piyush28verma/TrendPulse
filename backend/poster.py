"""
TrendPulse — Reddit Poster
Posts generated content to Reddit using PRAW.
Tries Swytchcode SDK first, falls back to direct PRAW.
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
    Tries Swytchcode SDK first → falls back to PRAW.
    Returns (PostResult, SwytchcodeLogEntry).
    """
    tool_id = "reddit.submit_post.post"
    start = time.time()

    # Try Swytchcode SDK first
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
            latency = int((time.time() - start) * 1000)
            post_result = PostResult(
                reddit_url=result.get("url", ""),
                post_id=result.get("id", ""),
                subreddit=settings.REDDIT_TARGET_SUBREDDIT,
            )
            log = _log_entry(tool_id, "success", 201, latency,
                             f"Posted via Swytchcode to r/{settings.REDDIT_TARGET_SUBREDDIT}")
            return post_result, log
        except Exception:
            pass  # Fall through to PRAW

    # PRAW fallback
    try:
        if not all([settings.REDDIT_CLIENT_ID, settings.REDDIT_CLIENT_SECRET,
                     settings.REDDIT_USERNAME, settings.REDDIT_PASSWORD]):
            latency = int((time.time() - start) * 1000)
            post_result = PostResult(
                reddit_url="",
                post_id="",
                subreddit=settings.REDDIT_TARGET_SUBREDDIT,
                success=False,
                error="Reddit credentials not configured. Set REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USERNAME, REDDIT_PASSWORD in .env",
            )
            log = _log_entry(tool_id, "error", 401, latency, "Reddit credentials missing")
            return post_result, log

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
        log = _log_entry(tool_id, "success", 201, latency,
                         f"Posted via PRAW to r/{settings.REDDIT_TARGET_SUBREDDIT}: {submission.permalink}")
        return post_result, log

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        post_result = PostResult(
            reddit_url="",
            post_id="",
            subreddit=settings.REDDIT_TARGET_SUBREDDIT,
            success=False,
            error=str(e),
        )
        log = _log_entry(tool_id, "error", 500, latency, str(e))
        return post_result, log
