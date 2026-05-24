"""
azure_function/__init__.py — Azure Functions HTTP trigger for order automation.

In production (Surgitech), this was triggered by Microsoft Graph API webhooks
watching the orders@company.com Outlook inbox. When a new email arrives:
    1. Graph API sends a notification to this Azure Function endpoint
    2. Function fetches the full email via Graph API
    3. Runs the order pipeline
    4. Sends auto-reply via Graph API (high-confidence orders)
    5. Moves flagged emails to 'Review Queue' Outlook folder (low-confidence)

This file shows the Azure Functions trigger structure.
Replace GRAPH_API placeholders with your actual Microsoft Graph API calls.

Deployment:
    func azure functionapp publish <your-function-app-name>

Requirements:
    - Azure Function App (Consumption or Premium plan)
    - Microsoft Graph API app registration with Mail.ReadWrite + Mail.Send permissions
    - Environment variables set in Function App Configuration (see .env.example)
"""

import json
import logging
import azure.functions as func

from src.pipeline import OrderPipeline
from src.human_review import export_review_queue

# Module-level pipeline instance — reused across warm invocations
# Azure Functions keeps the instance alive between calls (warm start)
_pipeline: OrderPipeline | None = None


def _get_pipeline() -> OrderPipeline:
    """Lazy-initialize pipeline (singleton per function instance)."""
    global _pipeline
    if _pipeline is None:
        _pipeline = OrderPipeline()
    return _pipeline


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    Azure Functions HTTP trigger entry point.

    Triggered by Microsoft Graph API change notification when a new email
    arrives in the monitored Outlook inbox.

    Request body (from Graph API notification):
    {
        "value": [{
            "subscriptionId": "...",
            "changeType": "created",
            "resource": "users/.../messages/<messageId>",
            "resourceData": {"id": "<messageId>", "@odata.type": "#Microsoft.Graph.Message"}
        }]
    }
    """
    logging.info("Order automation pipeline triggered.")

    # Parse Graph API notification
    try:
        body = req.get_json()
    except ValueError:
        return func.HttpResponse("Invalid JSON in request body.", status_code=400)

    notifications = body.get("value", [])
    if not notifications:
        # Graph API validation request (subscription setup)
        validation_token = req.params.get("validationToken")
        if validation_token:
            return func.HttpResponse(validation_token, mimetype="text/plain")
        return func.HttpResponse("No notifications in request.", status_code=200)

    results_summary = []

    for notification in notifications:
        message_id = notification.get("resourceData", {}).get("id", "")
        if not message_id:
            logging.warning("Notification missing message ID, skipping.")
            continue

        # Fetch full email from Graph API
        # In production: use requests + OAuth token to call
        # GET https://graph.microsoft.com/v1.0/users/{userId}/messages/{messageId}
        email_data = _fetch_email_from_graph(message_id)
        if not email_data:
            logging.error(f"Failed to fetch email {message_id}")
            continue

        # Run pipeline
        pipeline = _get_pipeline()
        result = pipeline.process_email(
            email_id=message_id,
            email_from=email_data["from"],
            email_subject=email_data["subject"],
            email_body=email_data["body"],
            verbose=False,
        )

        # Route based on pipeline result
        if result["review_items"]:
            # Move to Review Queue folder in Outlook
            _move_to_review_folder(message_id, result["review_items"])
            logging.info(f"Email {message_id}: {len(result['review_items'])} item(s) flagged for review")

        if result["reply_email"] and result["summary"] != "no_items":
            # Send auto-reply via Graph API
            _send_reply(
                original_message_id=message_id,
                to_address=email_data["from"],
                reply_body=result["reply_email"],
            )
            logging.info(f"Email {message_id}: Auto-reply sent ({result['summary']})")

        results_summary.append({
            "email_id": message_id,
            "summary": result["summary"],
            "auto_items": len(result["auto_items"]),
            "review_items": len(result["review_items"]),
        })

    return func.HttpResponse(
        json.dumps({"processed": len(results_summary), "results": results_summary}),
        mimetype="application/json",
        status_code=200,
    )


# ── Graph API helpers (replace with real implementation) ──────────────────────

def _fetch_email_from_graph(message_id: str) -> dict | None:
    """
    Fetch email content from Microsoft Graph API.

    Production implementation:
        import requests, os
        token = _get_access_token()  # OAuth2 client credentials flow
        url = f"https://graph.microsoft.com/v1.0/users/{os.getenv('MAILBOX_USER_ID')}/messages/{message_id}"
        response = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        if response.ok:
            msg = response.json()
            return {
                "from": msg["from"]["emailAddress"]["address"],
                "subject": msg["subject"],
                "body": msg["body"]["content"],
            }
        return None
    """
    # Placeholder — replace with real Graph API call
    logging.warning(f"_fetch_email_from_graph: placeholder called for {message_id}")
    return None


def _send_reply(original_message_id: str, to_address: str, reply_body: str) -> None:
    """
    Send reply via Microsoft Graph API.

    Production implementation:
        import requests, os
        token = _get_access_token()
        url = f"https://graph.microsoft.com/v1.0/users/{os.getenv('MAILBOX_USER_ID')}/messages/{original_message_id}/reply"
        requests.post(url, headers={"Authorization": f"Bearer {token}"},
                      json={"message": {"body": {"contentType": "Text", "content": reply_body}}})
    """
    logging.info(f"_send_reply: would send reply to {to_address}")


def _move_to_review_folder(message_id: str, review_items: list) -> None:
    """
    Move email to Review Queue folder in Outlook via Graph API.
    Also saves review items as a draft note in the folder.

    Production implementation:
        import requests, os
        token = _get_access_token()
        folder_id = os.getenv('REVIEW_FOLDER_ID')
        url = f"https://graph.microsoft.com/v1.0/users/{os.getenv('MAILBOX_USER_ID')}/messages/{message_id}/move"
        requests.post(url, headers={"Authorization": f"Bearer {token}"},
                      json={"destinationId": folder_id})
    """
    logging.info(f"_move_to_review_folder: would move {message_id} to review folder")
    review_json = export_review_queue(review_items)
    logging.info(f"Review queue: {review_json}")
