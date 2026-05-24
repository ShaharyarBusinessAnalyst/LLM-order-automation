"""
pipeline.py — Main order processing pipeline orchestrator.

Flow for each incoming email:
    1. Extract order items from email text (OpenAI)
    2. Match each item against SKU catalog (Pinecone RAG)
    3. Split into auto-processable vs human review queue
    4. Check stock for auto-processable items
    5. Generate and return customer reply email (OpenAI)

Usage:
    from src.pipeline import OrderPipeline
    pipeline = OrderPipeline()
    result = pipeline.process_email(email_id, email_from, email_subject, email_body)
"""

from src.extractor import extract_order_items
from src.matcher import SKUMatcher
from src.human_review import split_results, format_review_queue, ReviewItem
from src.responder import check_stock, generate_reply


class OrderPipeline:
    """
    End-to-end order processing pipeline.
    Instantiate once — SKUMatcher holds Pinecone connection across calls.
    """

    def __init__(self):
        print("Initializing Order Pipeline...")
        self._matcher = SKUMatcher()
        print("Pipeline ready.")

    def process_email(
        self,
        email_id: str,
        email_from: str,
        email_subject: str,
        email_body: str,
        verbose: bool = True,
    ) -> dict:
        """
        Process a single order email end-to-end.

        Args:
            email_id: Unique email identifier
            email_from: Sender email address
            email_subject: Email subject line
            email_body: Full email body text
            verbose: Print progress to console

        Returns:
            dict with keys:
                email_id, order_items, matched_items, auto_items,
                review_items, fulfillable, out_of_stock, reply_email, summary
        """
        if verbose:
            print(f"\n{'='*60}")
            print(f"Processing: {email_id} | {email_subject}")
            print("="*60)

        # Step 1: Extract order items
        if verbose:
            print("[1/4] Extracting order items from email...")
        order_items = extract_order_items(email_body)

        if not order_items:
            if verbose:
                print("  No order items found in email.")
            return {
                "email_id": email_id,
                "order_items": [],
                "matched_items": [],
                "auto_items": [],
                "review_items": [],
                "fulfillable": [],
                "out_of_stock": [],
                "reply_email": "No order items detected in this email.",
                "summary": "no_items",
            }

        if verbose:
            print(f"  Found {len(order_items)} order item(s):")
            for item in order_items:
                print(f"    - '{item['product_query']}' x{item['quantity']}")

        # Step 2: Match against Pinecone SKU catalog
        if verbose:
            print("[2/4] Matching against SKU catalog via Pinecone RAG...")
        matched_items = self._matcher.match_order_items(order_items)

        if verbose:
            for match in matched_items:
                status = "⚠ REVIEW" if match["needs_review"] else "✓ AUTO"
                print(
                    f"  [{status}] '{match['product_query']}' → "
                    f"{match['sku_id']} '{match['name']}' "
                    f"(score: {match['similarity_score']:.2f})"
                )

        # Step 3: Split auto vs review
        if verbose:
            print("[3/4] Splitting auto-processable vs human review queue...")
        auto_items, review_items = split_results(
            matched_items, email_id, email_from, email_subject
        )

        if verbose:
            print(f"  Auto-processable: {len(auto_items)} | Review queue: {len(review_items)}")
            if review_items:
                print(format_review_queue(review_items))

        # Step 4: Check stock and generate reply
        if verbose:
            print("[4/4] Checking stock and generating reply email...")
        fulfillable, out_of_stock = check_stock(auto_items)

        if verbose:
            print(f"  Fulfillable: {len(fulfillable)} | Out of stock: {len(out_of_stock)}")

        reply_email = generate_reply(
            email_body=email_body,
            fulfillable_items=fulfillable,
            out_of_stock_items=out_of_stock,
            review_items_count=len(review_items),
        )

        # Determine overall summary
        if fulfillable and not out_of_stock and not review_items:
            summary = "fully_confirmed"
        elif fulfillable and (out_of_stock or review_items):
            summary = "partially_confirmed"
        elif not fulfillable and out_of_stock:
            summary = "out_of_stock"
        else:
            summary = "pending_review"

        if verbose:
            print(f"\n--- GENERATED REPLY ({summary.upper()}) ---")
            print(reply_email)
            print("-" * 60)

        return {
            "email_id": email_id,
            "order_items": order_items,
            "matched_items": matched_items,
            "auto_items": auto_items,
            "review_items": review_items,
            "fulfillable": fulfillable,
            "out_of_stock": out_of_stock,
            "reply_email": reply_email,
            "summary": summary,
        }

    def process_batch(self, emails: list[dict], verbose: bool = True) -> list[dict]:
        """
        Process a batch of emails.

        Args:
            emails: List of dicts with keys: email_id, from, subject, body
            verbose: Print progress

        Returns:
            List of result dicts, one per email
        """
        results = []
        for email in emails:
            result = self.process_email(
                email_id=email["email_id"],
                email_from=email.get("from", ""),
                email_subject=email.get("subject", ""),
                email_body=email["body"],
                verbose=verbose,
            )
            results.append(result)
        return results
