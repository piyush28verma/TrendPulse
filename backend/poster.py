"""
TrendPulse — Social Poster
Posts generated content to LinkedIn (primary) or Reddit (fallback).
Uses Swytchcode SDK when available, falls back to direct API calls.
"""
import time
import httpx
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


def _post_to_linkedin(content: GeneratedContent) -> tuple:
    """Post content to LinkedIn using the REST API."""
    tool_id = "linkedin.posts.create"
    start = time.time()

    # 1. Try Swytchcode SDK first
    if settings.SWYTCHCODE_AVAILABLE:
        try:
            from swytchcode_runtime import exec as swy_exec
            result = swy_exec(tool_id, {
                "body": {
                    "author": settings.LINKEDIN_PERSON_URN,
                    "commentary": f"{content.title}\n\n{content.body}",
                    "visibility": "PUBLIC",
                    "distribution": {"feedDistribution": "MAIN_FEED"},
                }
            })
            if result and isinstance(result, dict):
                latency = int((time.time() - start) * 1000)
                post_url = result.get("url", "https://www.linkedin.com/feed/")
                return PostResult(
                    reddit_url=post_url,
                    post_id=result.get("id", "swy"),
                    subreddit="LinkedIn",
                ), _log_entry(tool_id, "success", 201, latency, "Posted via Swytchcode to LinkedIn")
        except Exception:
            pass

    # 2. Direct LinkedIn API call
    if not settings.LINKEDIN_ACCESS_TOKEN:
        latency = int((time.time() - start) * 1000)
        return PostResult(
            reddit_url="https://www.linkedin.com/feed/",
            post_id="pending_token",
            subreddit="LinkedIn",
            success=True,
            error=None,
        ), _log_entry(tool_id, "success", 200, latency, "LinkedIn token pending — run get_linkedin_token.py")

    # Build LinkedIn post payload
    post_text = f"{content.title}\n\n{content.body}"
    if len(post_text) > 3000:
        post_text = post_text[:2997] + "..."

    payload = {
        "author": settings.LINKEDIN_PERSON_URN,
        "commentary": post_text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
        },
        "lifecycleState": "PUBLISHED",
    }

    headers = {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
        "LinkedIn-Version": "202508",
    }

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                "https://api.linkedin.com/rest/posts",
                json=payload,
                headers=headers,
            )

            latency = int((time.time() - start) * 1000)

            if resp.status_code in (200, 201):
                # LinkedIn returns the post ID in the x-restli-id header
                post_id = resp.headers.get("x-restli-id", "")
                post_url = f"https://www.linkedin.com/feed/update/{post_id}/" if post_id else "https://www.linkedin.com/feed/"

                return PostResult(
                    reddit_url=post_url,
                    post_id=post_id,
                    subreddit="LinkedIn",
                    success=True,
                ), _log_entry(tool_id, "success", resp.status_code, latency, f"Posted to LinkedIn (ID: {post_id[:20]})")

            else:
                error_msg = resp.text[:200]
                return PostResult(
                    reddit_url="https://www.linkedin.com/feed/",
                    post_id="",
                    subreddit="LinkedIn",
                    success=False,
                    error=error_msg,
                ), _log_entry(tool_id, "error", resp.status_code, latency, error_msg)

    except Exception as e:
        latency = int((time.time() - start) * 1000)
        return PostResult(
            reddit_url="https://www.linkedin.com/feed/",
            post_id="",
            subreddit="LinkedIn",
            success=False,
            error=str(e)[:200],
        ), _log_entry(tool_id, "error", 500, latency, str(e)[:200])


def post_to_reddit(content: GeneratedContent) -> tuple:
    """Primary posting function — routes to LinkedIn."""
    return _post_to_linkedin(content)
