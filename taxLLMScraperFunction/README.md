# Tax LLM Scraper

### **Tax LLM Scraper** is a Python-based tool we wrote to extract, preprocess, and organize tax-related articles/documents from publicly available sources.

Input for the scraper -

- RSS feeds -
https://www.internationaltaxreview.com/rssfeeds/direct-tax
https://news.google.com/rss/search?q=corporate+tax&hl=en-US&gl=US&ceid=US:en
https://taxfoundation.org/feed/
https://blog.turbotax.intuit.com/feed/
https://kluwertaxblog.com/feed/
https://tax.thomsonreuters.com/blog/feed/
https://feeds.bbci.co.uk/news/business/rss.xml

- News APIs -
gnews.io
newsdata.io

Output -
Each article is stored as json file with the following attributes along with other metadata -
Title, Summary, Link, Published Date, Article Text

This scraper has been implemented as an **AWS Lambda function** and is **scheduled to run periodically** using Amazon EventBridge (CloudWatch Events)

