# PRGuardian

An AI-powered code review and product release decision-making tool that automatically evaluates pull requests to identify the best time to release software.

## Overview

PRGuardian integrates directly with GitHub through a custom GitHub App. When a pull request is labeled `audit-requested`, the system retrieves the pull request changes and analyzes them using Azure AI technologies to help developers and product managers make informed release decisions.

## Features

- **Automatic PR Analysis**: Triggered by the `audit-requested` label on pull requests
- **Code Quality Evaluation**: Evaluates PRs against best practices and company-specific guidelines
- **Risk Assessment**: Reports concerns as high, medium, or low severity levels
- **AI-Powered Suggestions**: Provides actionable suggestions to improve code
- **Release Decision Support**: Analyzes code quality, timeline, and budget to recommend Go/No-Go decisions
- **GitHub Integration**: Posts findings as inline comments and decision labels on PRs
- **Policy-Based Search**: Retrieves relevant organizational policies and guidelines using Azure AI Search

## Architecture

```
GitHub PR + "audit-requested" label
           ↓
    GitHub App Webhook
           ↓
    Azure Functions App
           ↓
    ┌──────────────────────────────────┐
    │  Fetch PR Diff                   │
    │  Parse Changes                   │
    │  Search Policy Index (AI Search) │
    └──────────────────────────────────┘
           ↓
    Azure OpenAI (GPT-4o-mini)
           ↓
    ┌──────────────────────────────────┐
    │  AI-Powered Code Review          │
    │  Risk Assessment (High/Med/Low)  │
    │  Suggestions & Insights          │
    └──────────────────────────────────┘
           ↓
    Post PR Comments & Go/No-Go Label
```

## Key Components

- **`src/main.py`** - Azure Functions HTTP trigger for GitHub webhooks
- **`src/integration.py`** - Entry point for the audit workflow
- **`src/orchestrator.py`** - Main workflow orchestration and coordination
- **`src/fetch_pr_diff.py`** - Retrieves PR diffs from GitHub API
- **`src/azure_review.py`** - AI-powered code review using Azure OpenAI
- **`src/policy_search.py`** - Searches policy snippets via Azure AI Search
- **`src/github_actions.py`** - Posts findings and decisions back to GitHub
- **`src/github_app_auth.py`** - Handles GitHub App authentication

## Setup

### Prerequisites

- Python 3.10+
- Azure Functions runtime
- GitHub App with appropriate permissions
- Azure OpenAI endpoint with GPT-4o-mini deployment
- Azure AI Search with indexed policy documents

### Environment Variables

Create a `.env` file with:

```
AZURE_OPENAI_API_KEY=<your-key>
AZURE_OPENAI_ENDPOINT=<your-endpoint>
AZURE_OPENAI_API_VERSION=<api-version>
AZURE_SEARCH_ENDPOINT=<your-endpoint>
AZURE_SEARCH_INDEX_NAME=<index-name>
AZURE_SEARCH_API_KEY=<your-key>
GITHUB_APP_ID=<your-app-id>
GITHUB_PRIVATE_KEY=<your-private-key>
```

### Installation

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Local Testing

```bash
python script.py
```

### Deployment

Deploy to Azure Functions:

```bash
func azure functionapp publish <app-name>
```

### Triggering an Audit

1. Open a pull request in a GitHub repository with PRGuardian enabled
2. Add the `audit-requested` label to the PR
3. PRGuardian automatically receives the webhook and begins the analysis
4. Review the inline comments and decision summary posted to the PR

## How It Works

1. **Webhook Trigger**: GitHub sends a webhook when `audit-requested` label is applied to a PR
2. **Fetch PR Diff**: Retrieves the raw pull request diff via GitHub API
3. **Parse Changes**: Maps code changes to specific line numbers for accurate inline comments
4. **Policy Search**: Searches Azure AI Search index for relevant organizational policies and guidelines
5. **AI Analysis**: GPT-4o-mini analyzes code changes against retrieved policies and best practices
6. **Risk Assessment**: Generates findings with severity levels (high, medium, low)
7. **Post Review**: Posts inline comments with suggestions and a summary review with Go/No-Go decision label

## Benefits

- **Boost Code Quality**: Identify issues before they reach production
- **Accelerate Delivery**: Automate code review process to reduce review time
- **Informed Decisions**: Get AI-driven insights to support Go/No-Go release decisions
- **Minimize Overruns**: Catch risks early to prevent timeline and budget impacts
- **Consistency**: Apply organizational standards consistently across all PRs

## Testing

```bash
pytest tests/
```


