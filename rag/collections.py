"""Simple utilities for managing multiple ChromaDB collections.

This module provides basic functions for creating, listing, and managing
collections without heavy abstractions. Keeps it simple and functional.
"""

from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings

from rag.config import CHROMA_DB_DIR


def get_client() -> chromadb.Client:
    """Get ChromaDB client (reusable across collections).

    Returns:
        Configured ChromaDB persistent client
    """
    CHROMA_DB_DIR.mkdir(parents=True, exist_ok=True)

    return chromadb.PersistentClient(
        path=str(CHROMA_DB_DIR),
        settings=Settings(
            anonymized_telemetry=False,
            allow_reset=True,
        ),
    )


def create_collection(
    collection_name: str,
    client: Optional[chromadb.Client] = None
) -> chromadb.Collection:
    """Create or get a collection.

    Args:
        collection_name: Name of the collection
        client: Optional ChromaDB client (creates new if not provided)

    Returns:
        ChromaDB collection object
    """
    if client is None:
        client = get_client()

    return client.get_or_create_collection(
        name=collection_name,
        metadata={"description": f"Collection: {collection_name}"}
    )


def list_collections(client: Optional[chromadb.Client] = None) -> List[str]:
    """List all collection names.

    Args:
        client: Optional ChromaDB client

    Returns:
        List of collection names
    """
    if client is None:
        client = get_client()

    collections = client.list_collections()
    return [col.name for col in collections]


def get_collection_stats(
    collection_name: str,
    client: Optional[chromadb.Client] = None
) -> Dict[str, Any]:
    """Get statistics for a collection.

    Args:
        collection_name: Name of the collection
        client: Optional ChromaDB client

    Returns:
        Dictionary with count and metadata
    """
    if client is None:
        client = get_client()

    try:
        collection = client.get_collection(name=collection_name)
        return {
            "name": collection_name,
            "count": collection.count(),
            "metadata": collection.metadata
        }
    except Exception as e:
        return {
            "name": collection_name,
            "error": str(e)
        }


def delete_collection(
    collection_name: str,
    client: Optional[chromadb.Client] = None
) -> None:
    """Delete a collection.

    Args:
        collection_name: Name of the collection to delete
        client: Optional ChromaDB client

    Warning:
        This operation is irreversible!
    """
    if client is None:
        client = get_client()

    client.delete_collection(name=collection_name)
    print(f"✓ Deleted collection: {collection_name}")


def get_all_stats(client: Optional[chromadb.Client] = None) -> Dict[str, Dict[str, Any]]:
    """Get stats for all collections.

    Args:
        client: Optional ChromaDB client

    Returns:
        Dictionary mapping collection names to their stats
    """
    if client is None:
        client = get_client()

    stats = {}
    for collection_name in list_collections(client):
        stats[collection_name] = get_collection_stats(collection_name, client)

    return stats


# CLI for testing
if __name__ == "__main__":
    print("=" * 60)
    print("COLLECTION UTILITIES TEST")
    print("=" * 60)

    client = get_client()

    print("\n📊 All Collections:")
    stats = get_all_stats(client)
    if not stats:
        print("  (No collections found)")
    else:
        for name, stat in stats.items():
            if "error" in stat:
                print(f"  - {name}: ERROR - {stat['error']}")
            else:
                count = stat.get("count", "?")
                print(f"  - {name}: {count} documents")

    print("\n✓ Collection utilities working!")
