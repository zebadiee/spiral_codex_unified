#!/usr/bin/env python3
"""
reddit_fetcher.py - Reddit content fetcher using Pushshift API

Fetches public Reddit posts and comments with ethical compliance.
Only accesses publicly available content and respects Reddit's terms of service.
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode

from .base_fetcher import BaseFetcher


class RedditFetcher(BaseFetcher):
    """Reddit content fetcher using Pushshift API"""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.pushshift_api = "https://api.pushshift.io/reddit"
        self.reddit_api = "https://www.reddit.com"

    async def _fetch_impl(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Fetch Reddit posts and comments"""
        results = []

        try:
            # Search for posts using Pushshift API
            posts = await self._search_posts(query, max_items)

            for post in posts:
                try:
                    result = await self._process_post(post)
                    if result:
                        results.append(result)
                except Exception as e:
                    self.logger.error(f"Error processing Reddit post {post.get('id')}: {e}")

        except Exception as e:
            self.logger.error(f"Error fetching Reddit content: {e}")

        return results

    async def _search_posts(self, query: str, max_items: int) -> List[Dict[str, Any]]:
        """Search for Reddit posts using Pushshift API"""
        posts = []

        # Prepare search parameters
        params = {
            "q": query,
            "size": min(max_items, 100),  # Pushshift limit
            "sort": "desc",
            "sort_type": "score",
            "filter": "id,title,selftext,author,subreddit,created_utc,url,score,num_comments,over_18"
        }

        try:
            # Make request to Pushshift API
            url = f"{self.pushshift_api}/search/submission/?{urlencode(params)}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                posts = data.get("data", [])
                self.logger.info(f"Found {len(posts)} Reddit posts for query: {query}")
            else:
                self.logger.warning(f"Pushshift API request failed with status: {response.status if response else 'None'}")

        except Exception as e:
            self.logger.error(f"Error searching Reddit posts: {e}")

        return posts

    async def _process_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single Reddit post"""
        post_id = post.get("id")
        if not post_id:
            return None

        # Skip NSFW content if configured
        if post.get("over_18", False) and self.config.get("skip_nsfw", True):
            self.logger.debug(f"Skipping NSFW post: {post_id}")
            return None

        # Check if subreddit is appropriate
        subreddit = post.get("subreddit", "").lower()
        if self._should_skip_subreddit(subreddit):
            self.logger.debug(f"Skipping post from restricted subreddit: {subreddit}")
            return None

        # Extract post content
        title = post.get("title", "")
        selftext = post.get("selftext", "")
        url = post.get("url", "")
        author = post.get("author", "[deleted]")

        # Skip deleted/removed content
        if author == "[deleted]" or title == "[deleted]" or title == "[removed]":
            return None

        # Get full content
        content = await self._get_post_content(post_id, title, selftext, url)

        if not content or len(content.strip()) < self.config.get("min_content_length", 100):
            return None

        # Extract metadata
        created_utc = post.get("created_utc")
        publish_date = None
        if created_utc:
            try:
                publish_date = datetime.fromtimestamp(created_utc, tz=timezone.utc).strftime("%Y-%m-%d")
            except Exception:
                pass

        # Build Reddit URL
        reddit_url = f"https://reddit.com/r/{subreddit}/comments/{post_id}"

        # Get additional comments if available
        comments_content = await self._get_top_comments(post_id)
        if comments_content:
            content += "\n\n## Top Comments\n\n" + comments_content

        return self._create_result(
            url=reddit_url,
            title=title,
            content=content,
            author=author,
            publish_date=publish_date,
            source_type="reddit",
            metadata={
                "subreddit": subreddit,
                "score": post.get("score", 0),
                "num_comments": post.get("num_comments", 0),
                "post_id": post_id,
                "external_url": url if not url.startswith("https://reddit.com") else None
            }
        )

    async def _get_post_content(self, post_id: str, title: str, selftext: str, url: str) -> str:
        """Get full post content"""
        content_parts = [f"# {title}"]

        # Add selftext if available
        if selftext and selftext.strip():
            content_parts.append(selftext)

        # If link post, add URL
        if url and not url.startswith("https://reddit.com") and url != selftext:
            content_parts.append(f"\n**Linked URL:** {url}")

        return "\n\n".join(content_parts)

    async def _get_top_comments(self, post_id: str, max_comments: int = 5) -> Optional[str]:
        """Get top comments for a post"""
        try:
            # Use Reddit API to get comments
            url = f"{self.reddit_api}/comments/{post_id}.json?sort=top&limit={max_comments}"
            response = await self._make_request(url)

            if response and response.status == 200:
                data = await response.json()
                if len(data) >= 2:
                    comments = data[1].get("data", {}).get("children", [])
                    comment_texts = []

                    for comment in comments[:max_comments]:
                        comment_data = comment.get("data", {})
                        comment_body = comment_data.get("body", "")
                        comment_author = comment_data.get("author", "[deleted]")
                        comment_score = comment_data.get("score", 0)

                        if (comment_body and
                            comment_author != "[deleted]" and
                            not comment_body.startswith("[deleted]") and
                            not comment_body.startswith("[removed]")):

                            comment_text = f"**{comment_author}** ({comment_score} points):\n{comment_body}"
                            comment_texts.append(comment_text)

                    return "\n\n---\n\n".join(comment_texts)

        except Exception as e:
            self.logger.debug(f"Error fetching comments for post {post_id}: {e}")

        return None

    def _should_skip_subreddit(self, subreddit: str) -> bool:
        """Check if subreddit should be skipped"""
        # List of subreddits to skip for content quality
        skip_subreddits = {
            # NSFW/controversial
            "gonewild", "nsfw", "sex", "porn", "erotic",
            # Hate speech
            "nazi", "racist", "whitepower", "altright",
            # Low quality/memes
            "dankmemes", "memes", "pewdiepiesubmissions", "im14andthisisdeep",
            # Personal/relationship
            "relationships", "relationship_advice", "amiugly", "rateme",
            # Drama/conspiracy
            "conspiracy", "drama", "subredditdrama",
            # Commercial
            "deals", "frugal", "buildapcsales",
        }

        return subreddit in skip_subreddits

    def _sanitize_reddit_content(self, content: str) -> str:
        """Sanitize Reddit-specific content"""
        # Remove Reddit markdown quirks
        content = re.sub(r'^\s*>\s+', '', content, flags=re.MULTILINE)  # Remove quotes
        content = re.sub(r'\^\([^^]*\)', '', content)  # Remove superscript footnotes
        content = re.sub(r'~~(.+?)~~', r'\1', content)  # Remove strikethrough

        # Clean up excessive formatting
        content = re.sub(r'\*{3,}', '**', content)  # Limit bold/italic
        content = re.sub(r'\n{3,}', '\n\n', content)  # Limit empty lines

        return content.strip()

    def _detect_reddit_license(self, content: str, subreddit: str) -> Optional[str]:
        """Detect license for Reddit content"""
        # Most Reddit content is under Reddit's Content Policy
        # Some subreddits may have specific licensing

        # Check for CC mentions in content
        if "creative commons" in content.lower() or "cc by" in content.lower():
            return "CC BY-SA"  # Reddit's default for public content

        # Check for specific subreddit licensing
        cc_subreddits = {
            "askscience": "CC BY-SA",
            "explainlikeimfive": "CC BY-SA",
            "todayilearned": "CC BY-SA",
        }

        if subreddit.lower() in cc_subreddits:
            return cc_subreddits[subreddit.lower()]

        return "Reddit Content Policy"  # Default Reddit license

    async def _make_request(self, url: str, method: str = "GET", **kwargs) -> Optional[aiohttp.ClientResponse]:
        """Override to add Reddit-specific headers"""
        # Add Reddit-specific headers
        if "reddit.com" in url:
            headers = kwargs.get("headers", {})
            headers.update({
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
            })
            kwargs["headers"] = headers

        return await super()._make_request(url, method, **kwargs)

    def _create_result(self, url: str, title: str, content: str, **kwargs) -> Dict[str, Any]:
        """Create Reddit-specific result"""
        result = super()._create_result(url, title, content, **kwargs)

        # Sanitize Reddit content
        result["content"] = self._sanitize_reddit_content(content)

        # Detect Reddit-specific license
        subreddit = kwargs.get("metadata", {}).get("subreddit", "")
        result["license"] = self._detect_reddit_license(content, subreddit)

        # Add Reddit-specific metadata
        result["metadata"]["platform"] = "reddit"
        result["metadata"]["content_type"] = "social_discussion"

        return result