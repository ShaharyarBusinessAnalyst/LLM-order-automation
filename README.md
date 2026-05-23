# 📦 LLM Order Automation Pipeline

An end-to-end order processing pipeline that reads customer order emails, matches requested products against a 1,000+ SKU catalog via **Pinecone RAG**, auto-generates professional reply emails using **OpenAI**, and flags ambiguous matches for human review — deployed on **Azure Functions**.

> Built as a sanitized demo of a production system delivered at US Surgitech (medical devices distributor), which reduced per-order processing time by ~95% (from 2–3 minutes to seconds across 50+ daily orders).

---

## Architecture

```
Outlook Inbox (orders@company.com)
        │
        ▼
Microsoft Graph API Webhook
        │
        ▼
Azure Functions Trigger  (azure_function/__init__.py)
        │
        ▼
OrderPipeline.process_email()
        │
   ┌────┴──────────────────────────┐
   ▼                               ▼
extract_order_items()         OpenAI GPT-4o-mini
   │                          (JSON mode, temp=0)
   ▼
SKUMatcher.match_order_items()
   │                          OpenAI text-embedding-3-small
   │                          + Pinecone cosine similarity search
   │
   ├── score ≥ 0.75 → auto_items → check_stock() → generate_reply()
   │                                                      │
   │                                              Auto-reply via Graph API
   │
   └── score < 0.75 → review_items → Outlook 'Review Queue' folder
                                     (pre-populated draft for human)
```

---

## Features

| Feature | Implementation |
|---|---|
| **Email intent extraction** | GPT-4o-mini with JSON mode — extracts product name + quantity |
| **Semantic SKU matching** | Pinecone cosine search over OpenAI embeddings (text-embedding-3-small) |
| **Confidence threshold** | Matches below 0.75 similarity flagged for human review |
| **Human-in-the-loop** | Flagged emails moved to Outlook review folder with pre-populated draft |
| **Stock checking** | Real-time inventory check before confirming order |
| **Auto-reply generation** | GPT-4o-mini generates professional replies (confirmed / partial / OOS) |
| **Serverless deployment** | Azure Functions HTTP trigger via Microsoft Graph API webhook |
| **Batch processing** | Pipeline processes multiple emails per invocation |

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

```bash
cp .env.example .env
# Fill in your OpenAI and Pinecone keys
```

### 3. Index your SKU catalog (run once)

```bash
python src/setup_index.py
```

This embeds all SKU descriptions and upserts them into Pinecone. Re-run when catalog changes.

### 4. Run the demo notebook

```bash
jupyter lab demo.ipynb
```

Or run the pipeline directly:

```python
from src.pipeline import OrderPipeline

pipeline = OrderPipeline()
result = pipeline.process_email(
    email_id="EMAIL-001",
    email_from="purchasing@hospital.com",
    email_subject="Order Request",
    email_body="Please send 5x Universal Lateral Positioner and 10x OR Safety Strap.",
)
print(result["reply_email"])
```

---

## Project Structure

```
order-automation-pipeline/
├── src/
│   ├── config.py           # Environment config, model settings, thresholds
│   ├── setup_index.py      # Embed SKUs and upsert to Pinecone (run once)
│   ├── extractor.py        # OpenAI — extract product + quantity from email
│   ├── matcher.py          # Pinecone RAG — match query against SKU catalog
│   ├── human_review.py     # Split auto vs review, format review queue
│   ├── responder.py        # Stock check + generate reply email (OpenAI)
│   └── pipeline.py         # End-to-end orchestrator
├── azure_function/
│   ├── __init__.py         # Azure Functions HTTP trigger + Graph API integration
│   └── function.json       # Trigger binding config
├── data/
│   ├── sample_skus.csv     # 100 sample medical device SKUs
│   ├── generate_skus.py    # Script to regenerate SKU catalog
│   └── sample_emails.py    # 6 sample order emails for demo
├── demo.ipynb              # End-to-end walkthrough notebook
├── requirements.txt
├── .env.example            # Credential template
└── .gitignore
```

---

## Configuration

All thresholds and model choices are in `src/config.py`:

```python
SIMILARITY_THRESHOLD = 0.75    # Below this → human review queue
TOP_K_RESULTS = 3              # Pinecone candidates per query
OPENAI_EMBEDDING_MODEL = "text-embedding-3-small"
OPENAI_CHAT_MODEL = "gpt-4o-mini"
PINECONE_DIMENSION = 1536
```

---

## Human Review Flow

When a product query scores below the similarity threshold:

1. The matched item is added to the **review queue** instead of auto-processing
2. In production: email is moved to a dedicated **Outlook folder** via Graph API
3. A **pre-populated draft reply** is created with the best-match candidate
4. Human verifies the match and sends (or edits) the draft
5. High-confidence items in the same email are still auto-processed immediately

```
Review Queue Item:
  Email: EMAIL-006 | From: nurse@hospital.com
  Customer requested: 'gel pads for heels' x5
  Best match: GP-001 — Heel Protector Gel Pad (score: 0.68)
  Reason: Low similarity — please verify correct product
  Alternatives:
    - GP-002: Elbow Gel Pad (score: 0.61)
    - GP-008: Occiput Gel Donut (score: 0.58)
```

---

## Azure Deployment

```bash
# Install Azure Functions Core Tools
npm install -g azure-functions-core-tools@4

# Deploy to Azure
func azure functionapp publish <your-function-app-name>

# Set environment variables in Azure Portal
# Function App → Configuration → Application Settings
# Add: OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX_NAME,
#      AZURE_TENANT_ID, AZURE_CLIENT_ID, AZURE_CLIENT_SECRET,
#      MAILBOX_USER_ID, REVIEW_FOLDER_ID
```

Set up Microsoft Graph API webhook to trigger the function on new inbox emails:
```
POST https://graph.microsoft.com/v1.0/subscriptions
{
  "changeType": "created",
  "notificationUrl": "https://<function-app>.azurewebsites.net/api/orders/webhook",
  "resource": "users/{userId}/mailFolders/inbox/messages",
  "expirationDateTime": "2025-12-31T00:00:00Z"
}
```

---

## Tech Stack

| Component | Technology |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Vector database | Pinecone (serverless, cosine similarity) |
| Deployment | Azure Functions (serverless, HTTP trigger) |
| Email integration | Microsoft Graph API (Outlook) |
| Language | Python 3.11+ |

---

## Production Impact

Deployed at a medical device distributor processing 50+ customer orders daily:
- **~95% reduction** in per-order processing time (2–3 minutes → seconds)
- **~$13,000/year** in labor cost savings
- Human review rate: ~15% of orders (ambiguous product references)
- Zero missed orders due to out-of-stock — all flagged proactively
