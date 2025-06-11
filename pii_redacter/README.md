# PII Redaction API

This project provides a RESTful API for detecting and redacting Personally Identifiable Information (PII) from text using the `piiranha-v1-detect-personal-information` model from Hugging Face Transformers. It is implemented using Flask and PyTorch.

## Overview

The API loads a token classification model for PII detection and exposes two endpoints:

- `/health` – Health check endpoint
- `/redact` – Accepts raw text and returns the redacted version

Redaction can be done in two modes:
- **Aggregate mode**: Replaces entire PII spans with `[REDACTED]`
- **Type-specific mode**: Replaces with `[PII_TYPE]` such as `[NAME]`, `[PHONE]`, etc.

## Endpoints

### `GET /health`

Returns model health status.

### `POST /redact`

**Request body:**
```json
{
  "text": "My name is John and I live in New York.",
}