# PRGuardian

An AI-powered GitHub pull request auditor that automatically reviews code changes against organizational policies.

## Overview

PRGuardian is an Azure Functions application that integrates with GitHub via webhooks. It uses Azure OpenAI to analyze pull request diffs and provide policy compliance feedback directly on GitHub.

## Features

- **Automatic PR Analysis**: Triggered by the `audit-requested` label on pull requests
- **Policy-Based Review**: Searches relevant organizational policies using Azure Cognitive Search
- **AI-Powered Insights**: Uses Azure OpenAI to identify compliance issues and code concerns
- **GitHub Integration**: Posts findings as inline comments and risk assessments on PRs
- **Risk Scoring**: Provides decision levels (GO, GO WITH CAUTION, NO-GO) based on severity


### Key Components

- **`src/main.py`** - Azure Functions HTTP trigger for GitHub webhooks
- **`src/orchestrator.py`** - Main workflow orchestration
- **`src/fetch_pr_diff.py`** - Retrieves PR diffs from GitHub API
- **`src/azure_review.py`** - AI-powered code review using Azure OpenAI
- **`src/policy_search.py`** - Searches organizational policies via Azure Cognitive Search
- **`src/github_actions.py`** - Posts findings back to GitHub as PR reviews
- **`src/github_app_auth.py`** - Handles GitHub authentication

## Setup

### Prerequisites

- Python 3.10+
- Azure Functions Core Tools
- GitHub account with app credentials
- Azure OpenAI instance
- Azure Cognitive Search index with policies

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

1. Open a PR in a GitHub repository
2. Add the `audit-requested`or any other label
3. PRGuardian will automatically analyze the PR and post findings

## How It Works

1. **Webhook Event**: GitHub sends a webhook when `audit-requested` label is applied
2. **Fetch Diff**: Retrieves the raw PR diff via GitHub API
3. **Parse Positions**: Maps changes to specific line numbers for accurate comments
4. **Policy Search**: Finds relevant organizational policies using semantic search
5. **AI Review**: Azure OpenAI analyzes code changes against policies
6. **Post Results**: Posts a comprehensive review with inline comments and risk assessment

## Testing

```bash
pytest tests/
```


