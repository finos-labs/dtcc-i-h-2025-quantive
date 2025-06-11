import feedparser
from utils.logger import logger
from config import KEYWORDS
from utils.util_miscs import (
    fetch_article,
    safe_parse_datetime,
    hash_entry,
    is_near_lambda_timeout,
    upload_single_article_s3
)

MAX_ARTICLES = 30

def fetch_rss(feeds, seen, context=None):
    new_hashes = set()
    count = 0

    for url in feeds:
        if is_near_lambda_timeout(context): break
        if count >= MAX_ARTICLES: break
        
        try:
            d = feedparser.parse(url)
            if not d.entries:
                logger.warning(f"No entries found in feed: {url}")
                if is_near_lambda_timeout(context): break
                continue

            for entry in d.entries:      
                if is_near_lambda_timeout(context): break
                if count >= MAX_ARTICLES: break

                published_str = entry.get("published") or entry.get("updated") or ""
                published_time = safe_parse_datetime(published_str)

                title = entry.get("title", "")
                summary = entry.get("summary", "")

                if not any(kw.lower() in (title + summary).lower() for kw in KEYWORDS):
                    continue

                link = entry.get("link") or entry.get("url")

                hash_id = hash_entry(title, link)

                if hash_id in seen:
                    logger.info(f"Skipping duplicate RSS article: {title}")
                    continue
                
                article_text = fetch_article(link) if link else "Content unavailable"

                article = {
                    "source": url,
                    "title": title,
                    "summary": summary,
                    "link": link,
                    "published": published_str,
                    "article_text": article_text,
                    "kendra_metadata": {
                        "title": title,
                        "excerpt": summary,
                        "sourceUri": link,
                        "source": "rss"
                    }
                }

                upload_single_article_s3(article, "rss", hash_id)
                new_hashes.add(hash_id)
                count += 1

        except Exception as e:
            logger.warning(f"Failed to parse RSS feed {url}: {e}")

    logger.info(f"Total fetched from RSS: {len(new_hashes)}")
    return new_hashes