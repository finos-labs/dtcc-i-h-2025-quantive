import requests
from utils.logger import logger
from config import KEYWORDS
from utils.util_miscs import (
    fetch_article,
    safe_parse_datetime,
    hash_entry,
    is_near_lambda_timeout,
    upload_single_article_s3
)

MAX_ARTICLES = 20

def fetch_apis(apis, seen, context=None):
    new_hashes = set()
    count = 0

    for name, details in apis.items():

        if is_near_lambda_timeout(context): break
        if count >= MAX_ARTICLES: break

        key = details.get("key")
        url = details.get("url")

        if not key or "YOUR_" in key:
            logger.warning(f"{name} API key missing or default — skipping")
            continue

        try:
            response = requests.get(url, timeout=10)

            if response.status_code != 200:
                logger.warning(f"Non-200 response {response.status_code} for URL: {url}")

            data = response.json()

            articles = data.get("articles") or data.get("results") or []

            if not articles:
                logger.warning(f"{name}: No articles found in API response")

            for article in articles:
                if is_near_lambda_timeout(context): break
                if count >= MAX_ARTICLES: break
                    
                published_str = article.get("publishedAt") or article.get("pubDate") or ""
                published_time = safe_parse_datetime(published_str)

                title = article.get("title", "")
                summary = article.get("description", "") or article.get("content", "")
                link = article.get("link") or article.get("url")

                if not any(kw.lower() in (title + summary).lower() for kw in KEYWORDS):
                    continue

                hash_id = hash_entry(title, link)

                if hash_id in seen:
                    logger.info(f"Skipping duplicate API article: {title}")
                    continue

                article_text = fetch_article(link) if link else "Content Unavailable"

                doc = {
                    "source": name,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published_str,
                    "article_text": article_text,
                    "kendra_metadata": {
                        "title": title,
                        "excerpt": summary,
                        "sourceUri": link,
                        "source": "api"
                    }
                }

                upload_single_article_s3(article, "api", hash_id)
                new_hashes.add(hash_id)
                count += 1

        except Exception as e:
            logger.warning(f"{name} API error: {e}")

    logger.info(f"Total fetched from APIs: {len(new_hashes)}")
    return new_hashes