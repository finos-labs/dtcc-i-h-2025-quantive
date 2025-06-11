# Income Tax Website Scraper (Gov Portal Parser)

This AWS Lambda function scrapes the [Indian Income Tax Department's website](https://www.incometax.gov.in/iec/foportal/latest-news) for the latest news and updates. It extracts textual news content, downloads attached PDF files, generates metadata, and uploads the data to an Amazon S3 bucket.

## Features

- Crawls news articles across multiple paginated years.
- Extracts:
  - News content
  - PDF links
  - Nested links and inner news text
- Uploads:
  - Extracted content to `incometax/` path in S3
  - Attached PDFs to `incometax/pdfs/`
  - Associated metadata JSON to `metadata/` prefix
- Maintains a `last-updated` timestamp to avoid reprocessing older news.

## Technologies Used

- **Python**
- **AWS Lambda**
- **Amazon S3** – storage for articles, PDFs, and metadata
- **Requests & BeautifulSoup** – web scraping
- **UUID & Datetime** – for filename and metadata tracking

## Directory Structure in S3

```
s3://quantive-tax-llm-bucket/
│
├── incometax/
│   ├── incometax_YYYYMMDD.txt
│   └── last-updated
│
├── incometax/pdfs/
│   └── incometax_YYYYMMDD_i.pdf
│
└── metadata/
    ├── incometax/incometax_YYYYMMDD.txt.metadata.json
    └── incometax/pdfs/incometax_YYYYMMDD_i.pdf.metadata.json
```

## Environment Configuration

- No explicit environment variables required.
- Ensure the S3 bucket `quantive-tax-llm-bucket` exists and Lambda has access to it.

## Input

This function does **not** require external input. It runs periodically (e.g., via CloudWatch trigger or manually) and determines whether new updates are available by checking the `last-updated` object in S3.

## Output

- **Text Files**: News content
- **PDF Files**: Attached documents
- **Metadata**: Document metadata (e.g., title, source URI, related files)

## Function Workflow

1. **Last Updated Fetch**: Checks S3 for `incometax/last-updated` to determine cutoff date.
2. **HTML Fetch**: Crawls the main portal and paginated yearly links.
3. **Date Check**: Skips entries older than the last known update.
4. **Content Extraction**:
   - Extracts update date and text
   - Collects PDF URLs (and optionally parses them)
   - Parses nested article links recursively
5. **Upload**:
   - Text content is saved to `incometax/`
   - PDFs to `incometax/pdfs/`
   - Metadata to `metadata/`
6. **Update Timestamp**: Writes the latest news date back to `incometax/last-updated`.

## IAM Permissions Required

The Lambda function requires the following permissions:

- `s3:GetObject`
- `s3:PutObject`
- `logs:CreateLogGroup`
- `logs:CreateLogStream`
- `logs:PutLogEvents`

## Notes

- ZIP files are ignored but detection is in place for future handling.
- Recursive scraping supports nested links within each article block.
- Fails gracefully for missing or malformed content, logging any exceptions.
- PDF parsing logic exists but is currently limited to download and metadata generation.