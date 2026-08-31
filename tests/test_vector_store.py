from uuid import uuid4

from qdrant_client import QdrantClient
from qdrant_client.models import SparseVector

from atlas.retrieval.store import QdrantVectorStore
from atlas.retrieval.types import DocumentChunk


def test_vector_store_search():
    client = QdrantClient(":memory:")

    store = QdrantVectorStore(
        client=client,
        collection_name="test",
        vector_size=3,
    )

    store.ensure_collection()

    first_chunk_id = str(uuid4())
    second_chunk_id = str(uuid4())

    chunks = [
        DocumentChunk(
            chunk_id=first_chunk_id,
            document_id="doc",
            filename="test.pdf",
            page_number=1,
            chunk_index=0,
            text="cats",
        ),
        DocumentChunk(
            chunk_id=second_chunk_id,
            document_id="doc",
            filename="test.pdf",
            page_number=2,
            chunk_index=1,
            text="databases",
        ),
    ]

    store.upsert(
        chunks=chunks,
        dense_vectors=[
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
        ],
        sparse_vectors=[
            SparseVector(
                indices=[0],
                values=[1.0],
            ),
            SparseVector(
                indices=[1],
                values=[1.0],
            ),
        ],
    )

    results = store.hybrid_search(
        dense_query=[1.0, 0.0, 0.0],
        sparse_query=SparseVector(
            indices=[0],
            values=[1.0],
        ),
        limit=1,
    )

    assert len(results) == 1
    assert results[0].chunk_id == first_chunk_id
    assert results[0].document_id == "doc"
    assert results[0].filename == "test.pdf"
    assert results[0].page_number == 1
    assert results[0].chunk_index == 0
    assert results[0].text == "cats"
