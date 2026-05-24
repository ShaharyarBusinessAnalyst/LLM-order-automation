"""
responder.py — Generate professional customer reply emails using OpenAI.

Takes matched and confirmed order items and generates:
    - Order confirmation emails (all items in stock)
    - Partial fulfillment emails (some items out of stock)
    - Out-of-stock notification emails (no items available)
"""

from openai import OpenAI
from src.config import get_openai_key, OPENAI_CHAT_MODEL


def check_stock(matched_items: list[dict]) -> tuple[list[dict], list[dict]]:
    """
    Split matched items into fulfillable and out-of-stock groups.

    Args:
        matched_items: High-confidence matches from matcher (needs_review=False)

    Returns:
        Tuple of (fulfillable_items, out_of_stock_items)
    """
    fulfillable = []
    out_of_stock = []

    for item in matched_items:
        if item["stock"] >= item["quantity"]:
            fulfillable.append(item)
        else:
            out_of_stock.append(item)

    return fulfillable, out_of_stock


def generate_reply(
    email_body: str,
    fulfillable_items: list[dict],
    out_of_stock_items: list[dict],
    review_items_count: int = 0,
) -> str:
    """
    Generate a professional order reply email using GPT.

    Args:
        email_body: Original customer email text
        fulfillable_items: Items that can be fulfilled
        out_of_stock_items: Items that cannot be fulfilled
        review_items_count: Number of items pending human review

    Returns:
        Professional reply email as a string
    """
    client = OpenAI(api_key=get_openai_key())

    # Build order summary for the prompt
    fulfilled_summary = ""
    if fulfillable_items:
        lines = []
        total = 0.0
        for item in fulfillable_items:
            line_total = item["unit_price"] * item["quantity"]
            total += line_total
            lines.append(
                f"  - {item['name']} (SKU: {item['sku_id']}) "
                f"x{item['quantity']} @ ${item['unit_price']:.2f} = ${line_total:.2f}"
            )
        lines.append(f"  Order Total: ${total:.2f}")
        fulfilled_summary = "\n".join(lines)

    out_of_stock_summary = ""
    if out_of_stock_items:
        lines = []
        for item in out_of_stock_items:
            lines.append(
                f"  - {item['name']} (SKU: {item['sku_id']}) "
                f"requested: {item['quantity']}, available: {item['stock']}"
            )
        out_of_stock_summary = "\n".join(lines)

    # Determine order status
    if fulfillable_items and not out_of_stock_items and review_items_count == 0:
        status = "fully_confirmed"
    elif fulfillable_items and (out_of_stock_items or review_items_count > 0):
        status = "partially_confirmed"
    elif not fulfillable_items and out_of_stock_items:
        status = "out_of_stock"
    else:
        status = "pending_review"

    system_prompt = """You are a professional customer service representative for a medical device 
distributor (surgical positioning equipment and OR supplies). Write clear, professional, 
and empathetic order confirmation emails. Always include specific product names and SKU codes.
Keep the tone warm but professional. Do not use placeholders — write the complete email."""

    user_prompt = f"""Write a professional order response email based on the following:

ORDER STATUS: {status}

ORIGINAL CUSTOMER EMAIL:
{email_body}

CONFIRMED ITEMS (will be shipped):
{fulfilled_summary if fulfilled_summary else "None"}

OUT OF STOCK ITEMS (cannot be fulfilled):
{out_of_stock_summary if out_of_stock_summary else "None"}

ITEMS PENDING REVIEW: {review_items_count} item(s) require manual verification and will be 
confirmed separately within 1 business hour.

Instructions:
- Write a complete, ready-to-send email (include Subject line)
- Be specific about what is confirmed vs out of stock
- For out-of-stock items, offer to notify when restocked or suggest contacting us for alternatives
- For pending review items, mention they are being verified and we'll follow up shortly
- Include expected processing time (same day for confirmed orders)
- Sign as "Order Processing Team, [Company Name] Medical Supplies"
- Keep it concise but complete — ideally under 200 words"""

    response = client.chat.completions.create(
        model=OPENAI_CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
    )

    return response.choices[0].message.content.strip()
