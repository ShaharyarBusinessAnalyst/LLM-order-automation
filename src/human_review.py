"""
human_review.py — Separate matched results into auto-processed and review queues.

In production (Surgitech), flagged orders appear in a dedicated Outlook folder
with pre-populated draft responses for human verification before sending.

This module handles that separation logic and formats the review queue output.
"""

from dataclasses import dataclass, field
from typing import Optional
import json
from datetime import datetime


@dataclass
class ReviewItem:
    """A single order item flagged for human review."""
    email_id: str
    email_from: str
    email_subject: str
    product_query: str
    quantity: int
    best_match_sku: str
    best_match_name: str
    similarity_score: float
    review_reason: str
    alternatives: list = field(default_factory=list)
    flagged_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    def to_dict(self) -> dict:
        return {
            "email_id": self.email_id,
            "email_from": self.email_from,
            "email_subject": self.email_subject,
            "product_query": self.product_query,
            "quantity": self.quantity,
            "best_match_sku": self.best_match_sku,
            "best_match_name": self.best_match_name,
            "similarity_score": self.similarity_score,
            "review_reason": self.review_reason,
            "alternatives": self.alternatives,
            "flagged_at": self.flagged_at,
        }


def split_results(
    matched_items: list[dict],
    email_id: str,
    email_from: str,
    email_subject: str,
) -> tuple[list[dict], list[ReviewItem]]:
    """
    Split matched items into auto-processable and review-required groups.

    Args:
        matched_items: Output from SKUMatcher.match_order_items()
        email_id: Source email ID
        email_from: Sender email address
        email_subject: Email subject line

    Returns:
        Tuple of (auto_items, review_items)
        - auto_items: High-confidence matches, safe to auto-process
        - review_items: Low-confidence matches, need human verification
    """
    auto_items = []
    review_items = []

    for item in matched_items:
        if item["needs_review"]:
            review_items.append(ReviewItem(
                email_id=email_id,
                email_from=email_from,
                email_subject=email_subject,
                product_query=item["product_query"],
                quantity=item["quantity"],
                best_match_sku=item.get("sku_id", ""),
                best_match_name=item.get("name", ""),
                similarity_score=item["similarity_score"],
                review_reason=item["review_reason"],
                alternatives=item.get("alternatives", []),
            ))
        else:
            auto_items.append(item)

    return auto_items, review_items


def format_review_queue(review_items: list[ReviewItem]) -> str:
    """
    Format review items as a human-readable summary.
    In production, this would populate a draft Outlook email in the review folder.
    """
    if not review_items:
        return "No items require review."

    lines = [
        "=" * 60,
        "HUMAN REVIEW QUEUE",
        f"Items requiring verification: {len(review_items)}",
        "=" * 60,
    ]

    for i, item in enumerate(review_items, 1):
        lines += [
            f"\n[{i}] Email: {item.email_id} | From: {item.email_from}",
            f"    Customer requested: '{item.product_query}' x{item.quantity}",
            f"    Best match: {item.best_match_sku} — {item.best_match_name}",
            f"    Similarity score: {item.similarity_score:.2f}",
            f"    Reason: {item.review_reason}",
        ]
        if item.alternatives:
            lines.append("    Alternatives:")
            for alt in item.alternatives:
                lines.append(
                    f"      - {alt['sku_id']}: {alt['name']} (score: {alt['score']:.2f})"
                )

    lines += ["\n" + "=" * 60]
    return "\n".join(lines)


def export_review_queue(review_items: list[ReviewItem], output_path: Optional[str] = None) -> str:
    """Export review queue to JSON. Returns JSON string."""
    data = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_items": len(review_items),
        "items": [item.to_dict() for item in review_items],
    }
    json_str = json.dumps(data, indent=2)

    if output_path:
        with open(output_path, "w") as f:
            f.write(json_str)
        print(f"Review queue exported to {output_path}")

    return json_str
