# Metadata Enhancer for Amazon Comprehend

This script processes Amazon Comprehend's entity detection output and generates metadata files compatible with Amazon Kendra. It enhances document metadata by extracting high-confidence entities and structuring them in a way that improves Kendra's indexing and retrieval capabilities.

The script fetches the Comprehend output from an S3 bucket, parses the detected entities, filters them based on a confidence threshold, and stores the most relevant ones. If metadata files already exist, the script merges the new attributes while preserving the top frequent entries.

## Input

- **Amazon Comprehend Output File**: A JSON file stored in S3 containing detected entities for each document.
- **S3 Metadata Directory Path**: The target location where enhanced metadata files will be written.
- **(Optional) Existing Metadata Files**: If a metadata file already exists for a document, it is read and merged with new data.

## Output

- **Kendra-Compatible Metadata Files**: JSON files written back to S3 containing document-level attributes grouped by entity type. These files follow a format compatible with Amazon Kendra and include the most frequent values per entity type, capped at a limit (e.g., top 10).