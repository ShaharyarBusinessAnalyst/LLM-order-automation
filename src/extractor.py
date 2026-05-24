"""
extractor.py — Extract order intent from customer emails using OpenAI.

Takes raw email text and returns structured order items:
    [{"product_query": "...", "quantity": N}, ...]

Uses GPT-4o-mini with JSON mode for reliable structured output.
"""

import json
from openai import OpenAI
from src.config import get_openai_key, OPENAI_CHAT_MODEL


def extract_order_items(email_body: str) -> list[dict]:
    """
    Extract product queries and quantities from an order email.

    Args:
        email_body: Raw email text from customer

    Returns:
        List of dicts: [{"product_query": str, "quantity": int}, ...]
        Returns empty list if no valid order items found.
    """
    client = OpenAI(api_key=get_openai_key())

    system_prompt = """You are an order processing assistant for a medical device distributor.
Extract all product order items from the customer email.

Return a JSON object with this exact structure:
{
  "items": [
    {"product_query": "<product name or description from email>", "quantity": <integer>}
  ]
}

Rules:
- Only include products that are explicitly ordered with a clear quantity
- If quantity is a range (e.g. "3-4"), use the higher number
- If a product is mentioned but no quantity is specified, skip it
- If the email contains no clear order items, return {"items": []}
- product_query should be the exact product name or description as mentioned in the email
- Return valid JSON only, no explanation text"""

    user_prompt = f"Extract order items from this email:\n\n{email_body}"

    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content
    parsed = json.loads(content)
    items = parsed.get("items", [])

    # Validate structure
    valid_items = []
    for item in items:
        if (
            isinstance(item, dict)
            and "product_query" in item
            and "quantity" in item
            and isinstance(item["quantity"], (int, float))
            and item["quantity"] > 0
        ):
            valid_items.append({
                "product_query": str(item["product_query"]).strip(),
                "quantity": int(item["quantity"]),
            })

    return valid_items
