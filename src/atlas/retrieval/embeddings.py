from fastembed import TextEmbedding


class EmbeddingService:
    def __init__(
        self,
        *,
        model_name: str,
    ) -> None:
        self._model_name = model_name

        self._model = TextEmbedding(
            model_name=model_name
        )

    @property
    def dimension(self) -> int:
        test_vector = next(
            iter(
                self._model.embed(
                    ["dimension check"]
                )
            )
        )

        return len(test_vector)

    def embed_documents(
        self,
        texts: list[str],
    ) -> list[list[float]]:
        embeddings = self._model.embed(texts)

        return [
            embedding.tolist()
            for embedding in embeddings
        ]

    def embed_query(
        self,
        query: str,
    ) -> list[float]:
        embedding = next(
            iter(
                self._model.query_embed(
                    query
                )
            )
        )

        return embedding.tolist()