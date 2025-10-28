"""
Initialize Qdrant collections for codebase and documentation indexing.
"""

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

# Connect to Qdrant
client = QdrantClient(url="http://localhost:6333")

print("Initializing Qdrant collections...")

# Check existing collections
existing_collections = client.get_collections().collections
existing_names = [col.name for col in existing_collections]

# Create collection for codebase if it doesn't exist
if "codebase" not in existing_names:
    client.create_collection(
        collection_name="codebase",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print("[OK] Created 'codebase' collection (vector size: 384, distance: COSINE)")
else:
    print("[OK] 'codebase' collection already exists")

# Create collection for documentation if it doesn't exist
if "documentation" not in existing_names:
    client.create_collection(
        collection_name="documentation",
        vectors_config=VectorParams(size=384, distance=Distance.COSINE),
    )
    print("[OK] Created 'documentation' collection (vector size: 384, distance: COSINE)")
else:
    print("[OK] 'documentation' collection already exists")

print("\nCollection initialization complete!")
print("\nNext steps:")
print("1. Run 'python index_codebase.py' to index your codebase")
print("2. The Qdrant MCP server is now available to all agents")
