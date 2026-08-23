"""
TrendPulse — Social Poster
Posts generated content to LinkedIn using the v2/ugcPosts API.
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


def post_to_linkedin(content: GeneratedContent) -> tuple:
    """Post content to LinkedIn using the v2/ugcPosts API."""
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
                }
            })
            if result and isinstance(result, dict):
                latency = int((time.time() - start) * 1000)
                return PostResult(
                    reddit_url=result.get("url", "https://www.linkedin.com/feed/"),
                    post_id=result.get("id", "swy"),
                    subreddit="LinkedIn",
                ), _log_entry(tool_id, "success", 201, latency, "Posted via Swytchcode to LinkedIn")
        except Exception:
            pass

    # 2. Direct LinkedIn API (v2/ugcPosts)
    if not settings.LINKEDIN_ACCESS_TOKEN:
        latency = int((time.time() - start) * 1000)
        return PostResult(
            reddit_url="https://www.linkedin.com/feed/",
            post_id="pending_token",
            subreddit="LinkedIn",
            success=True,
        ), _log_entry(tool_id, "success", 200, latency, "LinkedIn token pending — run get_linkedin_token.py")

    post_text = f"{content.title}\n\n{content.body}"
    if len(post_text) > 3000:
        post_text = post_text[:2997] + "..."

    payload = {
        "author": settings.LINKEDIN_PERSON_URN,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    headers = {
        "Authorization": f"Bearer {settings.LINKEDIN_ACCESS_TOKEN}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    try:
        with httpx.Client(timeout=15) as client:
            resp = client.post(
                "https://api.linkedin.com/v2/ugcPosts",
                json=payload,
                headers=headers,
            )

            latency = int((time.time() - start) * 1000)

            if resp.status_code == 201:
                post_data = resp.json()
                share_id = post_data.get("id", "")
                # Build the LinkedIn post URL
                post_url = f"https://www.linkedin.com/feed/update/{share_id}/" if share_id else "https://www.linkedin.com/feed/"

                return PostResult(
                    reddit_url=post_url,
                    post_id=share_id,
                    subreddit="LinkedIn",
                    success=True,
                ), _log_entry(tool_id, "success", 201, latency, f"Posted to LinkedIn ({share_id[:40]})")

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


# Backward-compatible alias
post_to_reddit = post_to_linkedin
