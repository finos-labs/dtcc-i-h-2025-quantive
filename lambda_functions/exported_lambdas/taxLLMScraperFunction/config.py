import os
from dotenv import load_dotenv

load_dotenv()

RSS_FEEDS = [
    "https://www.internationaltaxreview.com/rssfeeds/direct-tax",
    "https://news.google.com/rss/search?q=corporate+tax&hl=en-US&gl=US&ceid=US:en",
    "https://taxfoundation.org/feed/",
    "https://blog.turbotax.intuit.com/feed/",
    "https://kluwertaxblog.com/feed/",
    "https://tax.thomsonreuters.com/blog/feed/",
    "https://feeds.bbci.co.uk/news/business/rss.xml"
]

NEWS_APIS = {
    "gnews": {
        "key": os.getenv('GNEWS_API_KEY'),
        "url": f"https://gnews.io/api/v4/search?q=corporate%20tax&lang=en&apikey={os.getenv('GNEWS_API_KEY')}"
    },
    "newsdata": {
        "key": os.getenv('NEWSDATA_API_KEY'),
        "url": f"https://newsdata.io/api/1/news?apikey={os.getenv('NEWSDATA_API_KEY')}&q=corporate+tax&language=en"
    }
}

S3_BUCKET = os.getenv("S3_BUCKET", "quantive-tax-llm-bucket")
META_BUCKET = os.getenv("META_BUCKET", "quantive-tax-llm-scraper-code-bucket")

EXEC_TIME_LEFT = os.getenv("EXEC_TIME_LEFT", 10)

KEYWORDS = ["corporate tax", "tax reform", "business tax", "international tax", "tax regulation", "tax law", "tax deadline", "tax deduction", "tax relief", "finance"]