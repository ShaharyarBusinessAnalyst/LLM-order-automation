"""
matcher.py — Match product queries against SKU catalog using Pinecone RAG.

For each extracted order item:
    1. Embed the product query using OpenAI
    2. Search Pinecone index for top-K similar SKUs
    3. Return best match with similarity score
    4. Flag low-confidence matches for human review
"""

from openai import OpenAI
from pinecone import Pinecone
from src.config import (
    get_openai_key,
    get_pinecone_key,
    get_pinecone_index,
    OPENAI_EMBEDDING_MODEL,
    SIMILARITY_THRESHOLD,
    TOP_K_RESULTS,
)


class SKUMatcher:
    """
    Matches free-text product queries to SKUs via Pinecone vector search.
    Instantiate once and reuse across multiple emails (avoids re-init overhead).
    """

    def __init__(self):
        self._openai_client = OpenAI(api_key=get_openai_key())
        pc = Pinecone(api_key=get_pinecone_key())
        self._index = pc.Index(get_pinecone_index())

    def _embed(self, text: str) -> list[float]:
        """Embed a single text string using OpenAI."""
        response = self._openai_client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=[text],
        )
        return response.data[0].embedding

    def match(self, product_query: str, quantity: int) -> dict:
        """
        Match a product query against the Pinecone SKU index.

        Args:
            product_query: Free-text product description from email
            quantity: Requested quantity

        Returns:
            dict with keys:
                product_query, quantity, sku_id, name, category, description,
                unit_price, stock, similarity_score, needs_review, review_reason
        """
        query_vector = self._embed(product_query)

        results = self._index.query(
            vector=query_vector,
            top_k=TOP_K_RESULTS,
            include_metadata=True,
        )

        if not results.matches:
            return self._no_match_result(product_query, quantity, "No matches found in catalog")

        top_match = results.matches[0]
        score = top_match.score
        metadata = top_match.metadata

        needs_review = score < SIMILARITY_THRESHOLD
        review_reason = ""
        if needs_review:
            review_reason = (
                f"Low similarity score ({score:.2f} < threshold {SIMILARITY_THRESHOLD}). "
                f"Best match: '{metadata.get('name', 'Unknown')}'. "
                f"Please verify this is the correct product."
            )

        return {
            "product_query": product_query,
            "quantity": quantity,
            "sku_id": metadata.get("sku_id", ""),
            "name": metadata.get("name", ""),
            "category": metadata.get("category", ""),
            "description": metadata.get("description", ""),
            "unit_price": float(metadata.get("unit_price", 0.0)),
            "stock": int(metadata.get("stock", 0)),
            "similarity_score": round(score, 4),
            "needs_review": needs_review,
            "review_reason": review_reason,
            "alternatives": [
                {
                    "sku_id": m.metadata.get("sku_id", ""),
                    "name": m.metadata.get("name", ""),
                    "score": round(m.score, 4),
                }
                for m in results.matches[1:]  # runner-up candidates
            ],
        }

    def match_order_items(self, order_items: list[dict]) -> list[dict]:
        """
        Match a list of extracted order items against the SKU catalog.

        Args:
            order_items: Output from extractor.extract_order_items()

        Returns:
            List of match results, one per order item
        """
        return [
            self.match(item["product_query"], item["quantity"])
            for item in order_items
        ]

    @staticmethod
    def _no_match_result(product_query: str, quantity: int, reason: str) -> dict:
        return {
            "product_query": product_query,
            "quantity": quantity,
            "sku_id": "",
            "name": "",
            "category": "",
            "description": "",
            "unit_price": 0.0,
            "stock": 0,
            "similarity_score": 0.0,
            "needs_review": True,
            "review_reason": reason,
            "alternatives": [],
        }
