import hashlib
import json
import trafilatura
from utils.logger import logger
from datetime import datetime, timezone, timedelta
from config import EXEC_TIME_LEFT
from googlenewsdecoder import gnewsdecoder
from newspaper import Article
import boto3
from dateutil import parser, tz
from dateutil.tz import UTC
from config import S3_BUCKET, META_BUCKET
from trafilatura.settings import use_config

s3 = boto3.client("s3")

HASH_KEY = "meta/seen_hashes.json"
LAST_RUN_KEY = "meta/last_run.txt"

TZINFOS = {
    'EDT': tz.gettz('America/New_York'),
    'EST': tz.gettz('America/New_York'),
    'PDT': tz.gettz('America/Los_Angeles'),
    'PST': tz.gettz('America/Los_Angeles'),
    'CDT': tz.gettz('America/Chicago'),
    'CST': tz.gettz('America/Chicago'),
    'GMT': tz.gettz('Etc/GMT'),
    'BST': tz.gettz('Europe/London'),
    'CET': tz.gettz('Europe/Paris'),
    'IST': tz.gettz('Asia/Kolkata')  # Only if you expect Indian feeds
}

def safe_parse_datetime(dt_str):
    try:
        dt = parser.parse(dt_str, tzinfos=TZINFOS)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except Exception as e:
        logger.warning(f"Failed to parse datetime '{dt_str}': {type(e).__name__}: {e}")
        return None

def hash_entry(title, link):
    base_string = f"{title}|{link}"
    return hashlib.sha256(base_string.encode("utf-8")).hexdigest()

def fetch_article(url, timeout=10):
    try:
        if "news.google.com/rss/articles/" in url:
            try:
                dec_url = gnewsdecoder(url)
                if dec_url['status'] == True:
                    real_url = dec_url['decoded_url']
                logger.info(f"Decoded Google News URL: {url} → {real_url}")
            except Exception as e:
                logger.warning(f"Failed to decode Google News URL: {e}")
                real_url = url
        else:
            real_url = url

        config = use_config()
        config.set("DEFAULT", "timeout", str(timeout))
        config.set("DEFAULT", "MAXLENGTH", "5000")
        config.set("DEFAULT", "MAXCHARS", "100000")
        config.set("DEFAULT", "EXTRACTION_TIMEOUT", "5") 

        downloaded = trafilatura.fetch_url(real_url, config=config)
        if downloaded:
            logger.info(f"Fetched article contents from: {url}")
            return trafilatura.extract(downloaded, config=config)
        else:
            logger.info(f"Trafilatura returned no content for: {real_url}")
            return None

    except Exception as e:
        logger.warning(f"Trafilatura failed for {url}: {e}")
        return None

def is_near_lambda_timeout(context):
    if not context:
        return False
    
    remaining = context.get_remaining_time_in_millis() / 1000

    is_near = remaining < int(EXEC_TIME_LEFT)

    if is_near:
        logger.warning("Low time remaining in Lambda. Exiting early.")

    return is_near

def upload_single_article_s3(article, source_type, hash_id):
    key = f"data/{source_type}/{hash_id}.json"
    try:
        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=json.dumps(article).encode("utf-8")
        )
        logger.info(f"Uploaded {article['title']} to {key}")
    except Exception as e:
        logger.error(f"Failed to upload {key} to S3: {e}")

def load_seen_hashes():
    try:
        response = s3.get_object(Bucket=META_BUCKET, Key=HASH_KEY)
        seen = json.loads(response["Body"].read().decode("utf-8"))
        return set(seen)
    except s3.exceptions.NoSuchKey:
        return set()
    except Exception as e:
        logger.warning(f"Failed to load seen hashes: {e}")
        return set()

def save_seen_hashes(hashes):
    try:
        s3.put_object(
            Bucket=META_BUCKET,
            Key=HASH_KEY,
            Body=json.dumps(list(hashes)).encode("utf-8")
        )
    except Exception as e:
        logger.error(f"Failed to save seen hashes to S3: {e}")