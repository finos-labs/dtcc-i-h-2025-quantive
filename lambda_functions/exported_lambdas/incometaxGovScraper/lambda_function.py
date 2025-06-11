
from bs4 import BeautifulSoup
import requests
import io
from datetime import datetime
import boto3
from botocore.exceptions import ClientError, BotoCoreError, NoCredentialsError
from urllib.parse import urlparse
import uuid
import os
import json


# Parses news and pdf content from income tax website and prints it out to stdout
# Run "python income_tax_gov_parser.py > filename.txt" and save it to file


# -------- CONFIG -------- #

main_url = "https://www.incometax.gov.in/iec/foportal/latest-news"
bucket = "quantive-tax-llm-bucket"
s3 = boto3.client('s3')

# Change this to get a different year
# Need to extend it to get between two specific date ranges
# main_url_with_date = main_url + "?year=2024"

visited_webpages = set()

def fetch_html(url):
    try:
        response = requests.get(url, timeout=10)
        return response.text
    except Exception:
        return ""
    

def extract_text_from_pdf(pdf_bytes):
    text = ""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        doc.close()
    except Exception as e:
        print(f"Failed to extract PDF: {e}")
    return text.strip()

def download_and_upload_pdf(pdf_url, filename):
    try:
        # Download the PDF
        response = requests.get(pdf_url)
        response.raise_for_status()

        # Verify it's a PDF
        content_type = response.headers.get('Content-Type', '')
        if 'application/pdf' not in content_type:
            raise ValueError(f"URL does not point to a PDF. Content-Type: {content_type}")

        # Upload to S3
        s3.put_object(Bucket=bucket, Key=filename, Body=response.content, ContentType='application/pdf')
        print(f"Successfully uploaded to s3://{bucket}/{filename}")

    except requests.RequestException as e:
        print(f"Error downloading PDF: {e}")
    except (BotoCoreError, NoCredentialsError) as e:
        print(f"Error uploading to S3: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")


def is_pdf(url):
    return url.lower().endswith(".pdf")

def is_zip(url):
    return url.lower().endswith(".zip")

# To get the views_row divs that does not have
# views_row divs inside it
def is_leaf_views_row(tag):
    return (
        tag.name == "div" and
        "views-row" in tag.get("class", []) and
        not tag.find("div", class_="views-row")
    )

def is_pager_next(tag):
    return (
        tag.name == "a" and
        tag.find("span", class_="pager_next_page")
    )

def generate_metadata(doc_date: datetime, uri, related_files, path):
    return {
        "DocumentId": path,
        "Attributes": {
            "_category": "IncGov",
            "_created_at": doc_date.isoformat(),
            "_last_updated_at": doc_date.isoformat(),
            "_source_uri": uri,
            "related_files": related_files
        },
        "Title": doc_date.strftime("Income Tax News - %Y%m%d"),
        "ContentType": "text/plain"
    }

def generate_pdf_metadata(source_metadata, s3_path, uri, i):
    temp = source_metadata["DocumentId"]
    source_metadata["DocumentId"] = s3_path
    source_metadata["Attributes"]["_source_uri"] = uri
    source_metadata["Attributes"]["related_files"] = [temp]
    source_metadata["Title"] = source_metadata["Title"] + " Pdf " + str(i)
    source_metadata["ContentType"] = "pdf"
    
    return source_metadata

def parse_website(url, level=0, date_threshold=None):
    file_content  = {}
    latest_date = None    
    visited_webpages.add(url)
    page_raw_html = fetch_html(url)
    soup = BeautifulSoup(page_raw_html, "html.parser")
    news_rows = soup.find_all(is_leaf_views_row)
    next_page_link_el = soup.find(is_pager_next)
    next_page_link = ""
    if next_page_link_el:
        next_page_link = main_url + next_page_link_el['href']
    text = ""
    for news_row in news_rows:
        up_date =  news_row.find("div", class_ = "up-date")
        up_date_text = ""
        up_date_obj = None
        if up_date:
            up_date_text = up_date.text
            up_date_obj = datetime.strptime(up_date_text.strip(), "%d-%b-%Y")
            if not latest_date or up_date_obj > latest_date:
                latest_date = up_date_obj

        # Stop processing if we have reached dates that has already been processed
        if level == 0 and up_date_obj and date_threshold and up_date_obj < date_threshold:
            break
            
        if up_date:
            print(f"Fetching news for {up_date_text}")

        # Textual content
        content_el = news_row.find("p")
        if not content_el:
            continue
        content = content_el.text

        #Links
        links = news_row.find_all("a", href=True)

        inner_text = ""
        attached_pdfs = []
        for link in links:
            if not link:
                pass
            elif is_pdf(link['href']):
                # downloaded_text += get_pdf_from_url(link['href'])
                # downloaded_text += "\n"
                attached_pdfs.append(link["href"])
                pass
            elif is_zip(link['href']):
                # Maybe handle zip files later
                pass
            else:
                inner_text += parse_website(link['href'], level+1) or ""
                inner_text += "\n"
        

        text += f"""{up_date_text}:\n{content}\n"""
        # if downloaded_text:
        #     text += f"""## Downloaded Content:{downloaded_text}\n{header_md_prefix}"""
        if inner_text.strip():
            text+=f"""Inner Content: {inner_text}"""
        text += "\n"


        if level == 0:
            if up_date_obj:
                filename = up_date_obj.strftime("incometax_%Y%m%d.txt")
            else:
                filename= f"incometax_{uuid.uuid4()}.txt"


            metadata = generate_metadata(up_date_obj, 
                                         url, 
                                         [f"incometax/pdfs/{filename}_{i}.pdf" for i,_ in enumerate(attached_pdfs)],
                                         f"s3://{bucket}/incometax/{filename}")
                
            file_content[filename] = {"content": text, "attached_files": attached_pdfs, "metadata": metadata}
            text = ""

            
    if next_page_link and next_page_link not in visited_webpages:
        paginated_file_contents, _ = parse_website(next_page_link, level=0, date_threshold=date_threshold)
        file_content.update(paginated_file_contents)
    if level == 0:
        return file_content, latest_date
    else:
        return text

def scrape_data_v2(last_date):
    current_year = datetime.today().year
    
    if not last_date:
        years = list(range(current_year, 2011, -1))
    else:
        years = list(range(current_year, last_date.year - 1, -1))

    latest_date = None
    for year in years:
        new_files, new_latest_date = parse_website(main_url + f"?year={year}", level=0, date_threshold=last_date)
        if not latest_date or new_latest_date > latest_date:
            latest_date = new_latest_date

        for filename, file_content in new_files.items():
            file_key = f"incometax/{filename}"
            s3.put_object(Bucket=bucket, Key=file_key, Body=file_content["content"].encode('utf-8'))
            
            if file_content["metadata"]:
                s3.put_object(Bucket=bucket, Key=f"metadata/{file_key}.metadata.json", Body=json.dumps(file_content["metadata"]), ContentType='application/json')
            
            for i, pdf_link in enumerate(file_content["attached_files"]):
                pdf_s3_path = f"incometax/pdfs/{file_key.replace('incometax/', '')}_{i}.pdf"
                download_and_upload_pdf(pdf_link, pdf_s3_path)
                pdf_metadata = generate_pdf_metadata(file_content["metadata"], pdf_s3_path, pdf_link, i)
                s3.put_object(Bucket=bucket, Key=f"metadata/{pdf_s3_path}.metadata.json", Body=json.dumps(pdf_metadata), ContentType='application/json')

    return latest_date



def scraper_v2():


    last_date = None
    
    try:
        obj = s3.get_object(Bucket=bucket, Key="incometax/last-updated")
        original_content = obj['Body'].read().decode('utf-8')
        lines = original_content.splitlines()
        if len(lines) > 0:
            first_line = lines[0].strip()
            last_date = datetime.strptime(first_line, "%Y-%m-%d")
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            pass
        else:
            raise e
    

    new_latest_date = scrape_data_v2(last_date=last_date)
    print("Added income tax news till ", new_latest_date.strftime('%Y-%m-%d'))
    s3.put_object(Bucket=bucket, Key="incometax/last-updated", Body=new_latest_date.strftime('%Y-%m-%d').encode('utf-8'))


def lambda_handler(event, context):
    # TODO implement
    scraper_v2()
    return {
        'statusCode': 200,
        'body': json.dumps('Finished running income tax gov - scraper')
    }
