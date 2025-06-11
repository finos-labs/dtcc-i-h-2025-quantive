import json
from datetime import datetime
from sources.rss import fetch_rss
from sources.api import fetch_apis
from config import RSS_FEEDS, NEWS_APIS
from utils.logger import logger
from utils.util_miscs import (
    hash_entry,
    load_seen_hashes,
    save_seen_hashes,
    is_near_lambda_timeout
)
def main(context=None):
    seen = load_seen_hashes()
    new_hashes = set()

    new_hashes |= fetch_rss(RSS_FEEDS, seen, context)
    if not is_near_lambda_timeout(context):
        new_hashes |= fetch_apis(NEWS_APIS, seen, context)

    save_seen_hashes(seen.union(new_hashes))

    logger.info(f"Scraping complete. Total new items: {len(new_hashes)}")


def lambda_handler(event, context):
    logger.info(f"Lambda Started - Remaining time till timeout: {context.get_remaining_time_in_millis() / 1000:.2f}s")
    main(context)

    return {
        "statusCode": 200,
        "body": json.dumps("Scraping completed successfully"),
    }

if __name__ == "__main__":
    main()