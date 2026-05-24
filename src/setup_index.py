"""
setup_index.py — Run once to create the Pinecone index and upsert SKU embeddings.

Usage:
    python src/setup_index.py

What it does:
    1. Reads sample_skus.csv
    2. Embeds each SKU description using OpenAI text-embedding-3-small
    3. Creates a Pinecone serverless index (if it doesn't exist)
    4. Upserts all SKU vectors with metadata (sku_id, name, category, price, stock)

Run this once before using the pipeline. Re-run if SKU catalog changes.
"""

import pandas as pd
import time
from pathlib import Path
from openai import OpenAI
from pinecone import Pinecone, ServerlessSpec
from src.config import (
    get_openai_key,
    get_pinecone_key,
    get_pinecone_index,
    OPENAI_EMBEDDING_MODEL,
    PINECONE_DIMENSION,
    PINECONE_METRIC,
)


def embed_texts(texts: list[str], client: OpenAI, batch_size: int = 50) -> list[list[float]]:
    """Embed a list of texts in batches. Returns list of embedding vectors."""
    all_embeddings = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        response = client.embeddings.create(
            model=OPENAI_EMBEDDING_MODEL,
            input=batch,
        )
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)
        print(f"  Embedded {min(i + batch_size, len(texts))}/{len(texts)} SKUs...")
        if i + batch_size < len(texts):
            time.sleep(0.5)  # polite rate limiting
    return all_embeddings


def setup_pinecone_index(pc: Pinecone, index_name: str) -> None:
    """Create Pinecone serverless index if it doesn't already exist."""
    existing = [idx.name for idx in pc.list_indexes()]
    if index_name in existing:
        print(f"Index '{index_name}' already exists — skipping creation.")
        return

    print(f"Creating Pinecone index '{index_name}'...")
    pc.create_index(
        name=index_name,
        dimension=PINECONE_DIMENSION,
        metric=PINECONE_METRIC,
        spec=ServerlessSpec(cloud="aws", region="us-east-1"),
    )
    # Wait for index to be ready
    while not pc.describe_index(index_name).status["ready"]:
        print("  Waiting for index to be ready...")
        time.sleep(2)
    print(f"Index '{index_name}' is ready.")


def upsert_skus(skus_path: Path) -> None:
    """Main function: embed all SKUs and upsert into Pinecone."""
    # Load SKU catalog
    df = pd.read_csv(skus_path)
    print(f"Loaded {len(df)} SKUs from {skus_path}")

    # Init clients
    openai_client = OpenAI(api_key=get_openai_key())
    pc = Pinecone(api_key=get_pinecone_key())
    index_name = get_pinecone_index()

    # Create index
    setup_pinecone_index(pc, index_name)
    index = pc.Index(index_name)

    # Build embedding texts: name + category + description for richer matching
    texts = [
        f"{row['name']} | {row['category']} | {row['description']}"
        for _, row in df.iterrows()
    ]

    # Embed
    print("Embedding SKU descriptions...")
    embeddings = embed_texts(texts, openai_client)

    # Build Pinecone vectors
    vectors = []
    for i, (_, row) in enumerate(df.iterrows()):
        vectors.append({
            "id": row["sku_id"],
            "values": embeddings[i],
            "metadata": {
                "sku_id": row["sku_id"],
                "name": row["name"],
                "category": row["category"],
                "description": row["description"],
                "unit_price": float(row["unit_price"]),
                "stock": int(row["stock"]),
            },
        })

    # Upsert in batches of 100
    batch_size = 100
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i: i + batch_size]
        index.upsert(vectors=batch)
        print(f"  Upserted {min(i + batch_size, len(vectors))}/{len(vectors)} vectors")

    print(f"\nDone. {len(vectors)} SKUs indexed in Pinecone index '{index_name}'.")
    stats = index.describe_index_stats()
    print(f"Index stats: {stats}")


if __name__ == "__main__":
    skus_path = Path(__file__).parent.parent / "data" / "sample_skus.csv"
    upsert_skus(skus_path)
