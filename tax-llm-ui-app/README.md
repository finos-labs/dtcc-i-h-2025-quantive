# Tax LLM UI

**Tax LLM UI** is a web-based interface that enables users to interact with our Tax LLM. Built using Streamlit, it integrates with backend systems for secure user authentication, session management, and persistent chat history.

## Overview

This application serves as the front end for our tax intelligence platform. It allows users to ask questions about tax laws, receive context-aware answers from an LLM, and manage personalized subscriptions and alerts.

The backend integrates AWS services such as Lambda, S3, and DynamoDB

## Features

- User login and session tracking
- Chat interface backed by a tax-aware LLM
- Session-based chat memory using DynamoDB
- Notification and alert management
- Integration with scheduled AWS Lambda scraper
- Modular architecture for easy extension

## Project Structure
tax-llm-ui/
├── app.py # Main application entry point
├── auth/ # Authentication logic
│ └── login.py
├── chat/
│ └── chat_ui.py # Chat UI rendering
├── memory/
│ └── chat_memory.py # Manages chat history
├── model/
│ └── llm_client.py # Connects to the LLM backend
├── notification/
│ ├── alerts.py # User alert logic
│ └── subscription.py # Subscription category handling
├── utils/
│ ├── session.py # Session management utilities
│ └── aws.py # AWS helpers
└── requirements.txt # Dependency list

## AWS Integration

The application uses the following AWS services:

- **AWS Lambda** for querying the LLM with user data
- **Amazon S3** to get article category information
- **Amazon DynamoDB** for storing chat history and article categories