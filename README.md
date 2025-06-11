![badge-labs](https://user-images.githubusercontent.com/327285/230928932-7c75f8ed-e57b-41db-9fb7-a292a13a1e58.svg)

# DTCC AI Hackathon 2025: Empowering India's Innovators
The purpose of hackathon is to leverage AI and ML Technologies to address critical challenges in the financial markets. The overall goal is to progress industry through Innovation, Networking and by providing effective Solutions.

**Hackathon Key Dates** 
•	June 6th - Event invites will be sent to participants
•	June 9th - Hackathon Open
•	June 9th-11th - Team collaboration and Use Case development
•	June 12th - Team presentations & demos
•	June 16th - Winners Announcement

More Info - https://communications.dtcc.com/dtcc-ai-hackathon-registration-17810.html

Commit Early & Commit Often!!!

## Project Name

Tax Event Detection & Categorization

### Project Details

# AI-Driven Tax Intelligence Platform

Our solution is a AI-driven platform that users can rely on for their tax-related issues. The platform has two major components – a chat system where users can ask questions about financial matters to get reliable answers with citations, and an alerting system where users can subscribe to financial-tax topics relevant to them.

The core of the system works with a knowledge base composed of credible, reliable sources such as officially released government circulars and top news providers. New information is periodically fetched/scraped from pre-decided online sources, which then:

- Becomes part of the knowledge base
- Gets categorized into one of the subscription categories, triggering an alert to the subscribers.

This helps our platform always stay updated with the most recent information.

---

## Technical Stuff

### Getting Information from the Web

The combination of web scraping, RSS feeds, and publicly available APIs is used to fetch data. These scrapers and fetchers are in the form of Lambda functions `taxLLMScraperFunction` and `incometaxGovScraper` that get triggered periodically, storing the information in an S3 bucket.

### Metadata Tagging

The documents stored in the S3 bucket are run through the Named Entity Recognition service provided by AWS Comprehend to identify the relevant entities referenced in a document. This information is made part of the metadata to ensure better knowledge retrieval and prioritization.

### Classification & Alerts

Whenever a document is added to S3, it triggers a Lambda function `classifyTaxArticle` that uses an LLM model to categorize the new information into one of many pre-determined categories mentioned below. 

- Tax Policy or Regulatory Updates
- Deadline Changes
- Global Tax Updates
- Litigations and Rulings
- Technology and Compliance Innovations
- Funding & Mergers and Acquisitions
- Security and Fraud Alerts
- Emerging Tech Trends
- General Updates 

This classification is stored in DynamoDB `ArticlesClassification` for later access, which in turn triggers another Lambda function `sendEmailNotifications` to send out emails to subscribed users.

### Document Search Engine

Amazon Kendra acts as our main search engine. On a periodic basis, Amazon Kendra goes through the S3 buckets containing the curated documents and their metadata, indexing the information for easy retrieval. Kendra, in addition, crawls through a number of relevant websites, adding more information to the knowledge base system.

### Chatbot Interface

The chatbot part of the application utilizes `taxLLMRAGFunction` as the interface to this application. This Lambda is responsible for accepting user queries, fetching relevant context snippets from Kendra, and then querying the Bedrock LLM model to generate reliable answers back to the users.

---

## Security Features

1. In AWS Bedrock, guardrails are used to redact any PII from both the user query as well as the LLM response.
2. An on-prem server-hosted ML NRE model, which will also redact PII from the user query can be used. The reasoning behind this approach is to have the benefit of making user query anonymous even before it leaves the company network, making it more secure.  
   To simulate this, the set up is done on an EC2 server powered by the open-source model – `iiiorg/piiranha-v1-detect-personal-information`.

---

## Software Features

- User authentication system  
- Chat history  
- News feed of subscribed topics  
- Alerting system based on categorized tax updates

## Future Enhancements

- Convert any numerical figure in the prompt into a range to support redaction or normalization.
- Integrate a quantitative data source and processing engine to support mathematical and tax-related calculations.


### Team Information

Nanda Kumar 
Sidharth Anil
Anagha M
Kavya Gonuguntla

## Using DCO to sign your commits

**All commits** must be signed with a DCO signature to avoid being flagged by the DCO Bot. This means that your commit log message must contain a line that looks like the following one, with your actual name and email address:

```
Signed-off-by: John Doe <john.doe@example.com>
```

Adding the `-s` flag to your `git commit` will add that line automatically. You can also add it manually as part of your commit log message or add it afterwards with `git commit --amend -s`.

See [CONTRIBUTING.md](./.github/CONTRIBUTING.md) for more information

### Helpful DCO Resources
- [Git Tools - Signing Your Work](https://git-scm.com/book/en/v2/Git-Tools-Signing-Your-Work)
- [Signing commits
](https://docs.github.com/en/github/authenticating-to-github/signing-commits)


## License

Copyright 2025 FINOS

Distributed under the [Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0).

SPDX-License-Identifier: [Apache-2.0](https://spdx.org/licenses/Apache-2.0)








