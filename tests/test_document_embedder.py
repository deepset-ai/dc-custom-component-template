import os
from typing import Literal
from unittest.mock import MagicMock

import pytest
from haystack import Document
from haystack.utils import Secret

from dc_custom_component.components.embedders.nvidia import (
    EmbeddingTruncateMode,
    NvidiaDocumentEmbedder,
)

from . import MockBackend


class TestNvidiaDocumentEmbedder:
    def test_init_default(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-api-key")
        embedder = NvidiaDocumentEmbedder()

        assert embedder.api_key == Secret.from_env_var("NVIDIA_API_KEY")
        assert embedder.model == "nvidia/nv-embedqa-e5-v5"
        assert embedder.api_url == "https://ai.api.nvidia.com/v1/retrieval/nvidia"
        assert embedder.prefix == ""
        assert embedder.suffix == ""
        assert embedder.batch_size == 32
        assert embedder.progress_bar is True
        assert embedder.meta_fields_to_embed == []
        assert embedder.embedding_separator == "\n"

    def test_init_with_parameters(self):
        embedder = NvidiaDocumentEmbedder(
            api_key=Secret.from_token("fake-api-key"),
            model="nvolveqa_40k",
            api_url="https://ai.api.nvidia.com/v1/retrieval/nvidia/test",
            prefix="prefix",
            suffix="suffix",
            batch_size=30,
            progress_bar=False,
            meta_fields_to_embed=["test_field"],
            embedding_separator=" | ",
        )

        assert embedder.api_key == Secret.from_token("fake-api-key")
        assert embedder.model == "nvolveqa_40k"
        assert embedder.api_url == "https://ai.api.nvidia.com/v1/retrieval/nvidia/test"
        assert embedder.prefix == "prefix"
        assert embedder.suffix == "suffix"
        assert embedder.batch_size == 30
        assert embedder.progress_bar is False
        assert embedder.meta_fields_to_embed == ["test_field"]
        assert embedder.embedding_separator == " | "

    def test_init_fail_wo_api_key(self, monkeypatch):
        monkeypatch.delenv("NVIDIA_API_KEY", raising=False)
        embedder = NvidiaDocumentEmbedder("nvolveqa_40k")
        with pytest.raises(ValueError):
            embedder.warm_up()

    def test_init_basic_auth(self):
        embedder = NvidiaDocumentEmbedder(
            api_url="https://host.com/v1",
            model="nvidia/nv-embedqa-e5-v5",
            username=Secret.from_token("fake-username"),
            password=Secret.from_token("fake-password"),
        )
        embedder.warm_up()

        assert embedder.username == Secret.from_token("fake-username")
        assert embedder.password == Secret.from_token("fake-password")
        assert embedder.api_url == "https://host.com/v1"
        assert embedder.model == "nvidia/nv-embedqa-e5-v5"
        assert embedder._backend == "nim"

    def test_init_basic_auth_triton(self):
        embedder = NvidiaDocumentEmbedder(
            api_url="host.com/v1",
            model="ensemble_model",
            backend="triton-http",
            username=Secret.from_token("fake-username"),
            password=Secret.from_token("fake-password"),
        )
        embedder.warm_up()

        assert embedder.username == Secret.from_token("fake-username")
        assert embedder.password == Secret.from_token("fake-password")
        assert embedder.api_url == "host.com/v1"
        assert embedder.model == "ensemble_model"
        assert embedder._backend == "triton-http"

    def test_client_kwargs(self, monkeypatch: pytest.MonkeyPatch):
        embedder = NvidiaDocumentEmbedder(
            api_url="host.com/v1",
            model="ensemble_model",
            backend="triton-http",
            api_key=Secret.from_token("fake-api-key"),
            backend_kwargs={
                "client_kwargs": {
                    "concurrency": 10,
                }
            },
        )
        tritonclient_http = MagicMock()
        monkeypatch.setattr(
            "tritonclient.http.InferenceServerClient", tritonclient_http
        )
        embedder.warm_up()

        tritonclient_http.assert_called_once_with(url="host.com/v1", concurrency=10)

    def test_infer_kwargs(self):
        embedder = NvidiaDocumentEmbedder(
            api_url="host.com/v1",
            model="ensemble_model",
            backend="triton-http",
            api_key=Secret.from_token("fake-api-key"),
            backend_kwargs={
                "infer_kwargs": {
                    "request_compression_algorithm": "deflate",
                    "response_compression_algorithm": "deflate",
                }
            },
        )
        embedder.warm_up()

        client_mock = MagicMock()
        embedder.backend.client = client_mock

        embedder.run([Document(content="test")])

        client_mock.infer.assert_called_once()
        client_mock.infer.call_args[1]["request_compression_algorithm"] == "deflate"
        client_mock.infer.call_args[1]["response_compression_algorithm"] == "deflate"

    def test_to_dict(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-api-key")
        component = NvidiaDocumentEmbedder("playground_nvolveqa_40k")
        data = component.to_dict()
        assert data == {
            "type": "dc_custom_component.components.embedders.nvidia.document_embedder.NvidiaDocumentEmbedder",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["NVIDIA_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "api_url": "https://ai.api.nvidia.com/v1/retrieval/nvidia",
                "model": "playground_nvolveqa_40k",
                "prefix": "",
                "suffix": "",
                "batch_size": 32,
                "progress_bar": True,
                "meta_fields_to_embed": [],
                "embedding_separator": "\n",
                "truncate": None,
                "backend": "nim",
                "timeout": None,
                "username": None,
                "password": None,
                "backend_kwargs": None,
            },
        }

    @pytest.mark.parametrize("backend", ["triton-http", "triton-grpc"])
    def test_init_with_triton_backend(
        self, monkeypatch, backend: Literal["nim", "triton-http", "triton-grpc"]
    ):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-api-key")
        embedder = NvidiaDocumentEmbedder(
            backend=backend, model="my-triton-model", api_url="localhost:8000"
        )

        assert embedder.api_key == Secret.from_env_var("NVIDIA_API_KEY")
        assert embedder.api_url == "localhost:8000"
        assert embedder.model == "my-triton-model"
        assert embedder.prefix == ""
        assert embedder.suffix == ""
        assert embedder._backend == backend

    def test_to_dict_with_custom_init_parameters(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-api-key")
        component = NvidiaDocumentEmbedder(
            model="playground_nvolveqa_40k",
            api_url="https://example.com",
            prefix="prefix",
            suffix="suffix",
            batch_size=10,
            progress_bar=False,
            meta_fields_to_embed=["test_field"],
            embedding_separator=" | ",
            truncate=EmbeddingTruncateMode.END,
        )
        data = component.to_dict()
        assert data == {
            "type": "dc_custom_component.components.embedders.nvidia.document_embedder.NvidiaDocumentEmbedder",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["NVIDIA_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "api_url": "https://example.com",
                "model": "playground_nvolveqa_40k",
                "prefix": "prefix",
                "suffix": "suffix",
                "batch_size": 10,
                "progress_bar": False,
                "meta_fields_to_embed": ["test_field"],
                "embedding_separator": " | ",
                "truncate": "END",
                "backend": "nim",
                "timeout": None,
                "username": None,
                "password": None,
                "backend_kwargs": None,
            },
        }

    def from_dict(self, monkeypatch):
        monkeypatch.setenv("NVIDIA_API_KEY", "fake-api-key")
        data = {
            "type": "haystack_integrations.components.embedders.nvidia.document_embedder.NvidiaDocumentEmbedder",
            "init_parameters": {
                "api_key": {
                    "env_vars": ["NVIDIA_API_KEY"],
                    "strict": True,
                    "type": "env_var",
                },
                "api_url": "https://example.com",
                "model": "playground_nvolveqa_40k",
                "prefix": "prefix",
                "suffix": "suffix",
                "batch_size": 10,
                "progress_bar": False,
                "meta_fields_to_embed": ["test_field"],
                "embedding_separator": " | ",
                "truncate": "START",
            },
        }
        component = NvidiaDocumentEmbedder.from_dict(data)
        assert component.model == "nvolveqa_40k"
        assert component.api_url == "https://example.com/v1"
        assert component.prefix == "prefix"
        assert component.suffix == "suffix"
        assert component.batch_size == 32
        assert component.progress_bar
        assert component.meta_fields_to_embed == []
        assert component.embedding_separator == "\n"
        assert component.truncate == EmbeddingTruncateMode.START

    def test_prepare_texts_to_embed_w_metadata(self):
        documents = [
            Document(
                content=f"document number {i}:\ncontent",
                meta={"meta_field": f"meta_value {i}"},
            )
            for i in range(5)
        ]

        embedder = NvidiaDocumentEmbedder(
            "playground_nvolveqa_40k",
            api_key=Secret.from_token("fake-api-key"),
            meta_fields_to_embed=["meta_field"],
            embedding_separator=" | ",
        )

        prepared_texts = embedder._prepare_texts_to_embed(documents)

        # note that newline is replaced by space
        assert prepared_texts == [
            "meta_value 0 | document number 0:\ncontent",
            "meta_value 1 | document number 1:\ncontent",
            "meta_value 2 | document number 2:\ncontent",
            "meta_value 3 | document number 3:\ncontent",
            "meta_value 4 | document number 4:\ncontent",
        ]

    def test_prepare_texts_to_embed_w_suffix(self):
        documents = [Document(content=f"document number {i}") for i in range(5)]

        embedder = NvidiaDocumentEmbedder(
            "playground_nvolveqa_40k",
            api_key=Secret.from_token("fake-api-key"),
            prefix="my_prefix ",
            suffix=" my_suffix",
        )

        prepared_texts = embedder._prepare_texts_to_embed(documents)

        assert prepared_texts == [
            "my_prefix document number 0 my_suffix",
            "my_prefix document number 1 my_suffix",
            "my_prefix document number 2 my_suffix",
            "my_prefix document number 3 my_suffix",
            "my_prefix document number 4 my_suffix",
        ]

    def test_embed_batch(self):
        texts = ["text 1", "text 2", "text 3", "text 4", "text 5"]
        model = "playground_nvolveqa_40k"
        api_key = Secret.from_token("fake-api-key")
        embedder = NvidiaDocumentEmbedder(
            model,
            api_key=api_key,
        )

        embedder.warm_up()
        embedder.backend = MockBackend(
            model=model,
            api_key=api_key,
        )

        embeddings, metadata = embedder._embed_batch(texts_to_embed=texts, batch_size=2)

        assert isinstance(embeddings, list)
        assert len(embeddings) == len(texts)
        for embedding in embeddings:
            assert isinstance(embedding, list)
            assert len(embedding) == 3
            assert all(isinstance(x, float) for x in embedding)

        assert metadata == {"usage": {"prompt_tokens": 3 * 4, "total_tokens": 3 * 4}}

    @pytest.mark.usefixtures("mock_local_models")
    def test_run_default_model(self):
        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]
        api_key = Secret.from_token("fake-api-key")

        embedder = NvidiaDocumentEmbedder(
            api_key=api_key,
            model=None,
            api_url="http://localhost:8080/v1",
            prefix="prefix ",
            suffix=" suffix",
            meta_fields_to_embed=["topic"],
            embedding_separator=" | ",
        )

        with pytest.warns(UserWarning) as record:
            embedder.warm_up()
        assert len(record) == 1
        assert "Default model is set as:" in str(record[0].message)
        assert embedder.model == "model1"

        embedder.backend = MockBackend(model=embedder.model, api_key=api_key)

        result = embedder.run(documents=docs)

        documents_with_embeddings = result["documents"]
        metadata = result["meta"]

        assert isinstance(documents_with_embeddings, list)
        assert len(documents_with_embeddings) == len(docs)
        for doc in documents_with_embeddings:
            assert isinstance(doc, Document)
            assert isinstance(doc.embedding, list)
            assert len(doc.embedding) == 3
            assert all(isinstance(x, float) for x in doc.embedding)
        assert metadata == {"usage": {"prompt_tokens": 4, "total_tokens": 4}}

    def test_run(self):
        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]
        api_key = Secret.from_token("fake-api-key")
        model = "playground_nvolveqa_40k"
        embedder = NvidiaDocumentEmbedder(
            api_key=api_key,
            model=model,
            prefix="prefix ",
            suffix=" suffix",
            meta_fields_to_embed=["topic"],
            embedding_separator=" | ",
        )

        embedder.warm_up()
        embedder.backend = MockBackend(model=model, api_key=api_key)

        result = embedder.run(documents=docs)

        documents_with_embeddings = result["documents"]
        metadata = result["meta"]

        assert isinstance(documents_with_embeddings, list)
        assert len(documents_with_embeddings) == len(docs)
        for doc in documents_with_embeddings:
            assert isinstance(doc, Document)
            assert isinstance(doc.embedding, list)
            assert len(doc.embedding) == 3
            assert all(isinstance(x, float) for x in doc.embedding)
        assert metadata == {"usage": {"prompt_tokens": 4, "total_tokens": 4}}

    def test_run_custom_batch_size(self):
        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]
        api_key = Secret.from_token("fake-api-key")
        model = "playground_nvolveqa_40k"
        embedder = NvidiaDocumentEmbedder(
            api_key=api_key,
            model=model,
            prefix="prefix ",
            suffix=" suffix",
            meta_fields_to_embed=["topic"],
            embedding_separator=" | ",
            batch_size=1,
        )

        embedder.warm_up()
        embedder.backend = MockBackend(model=model, api_key=api_key)

        result = embedder.run(documents=docs)

        documents_with_embeddings = result["documents"]
        metadata = result["meta"]

        assert isinstance(documents_with_embeddings, list)
        assert len(documents_with_embeddings) == len(docs)
        for doc in documents_with_embeddings:
            assert isinstance(doc, Document)
            assert isinstance(doc.embedding, list)
            assert len(doc.embedding) == 3
            assert all(isinstance(x, float) for x in doc.embedding)

        assert metadata == {"usage": {"prompt_tokens": 2 * 4, "total_tokens": 2 * 4}}

    def test_run_wrong_input_format(self):
        model = "playground_nvolveqa_40k"
        api_key = Secret.from_token("fake-api-key")
        embedder = NvidiaDocumentEmbedder(model, api_key=api_key)

        embedder.warm_up()
        embedder.backend = MockBackend(model=model, api_key=api_key)

        string_input = "text"
        list_integers_input = [1, 2, 3]

        with pytest.raises(
            TypeError,
            match="NvidiaDocumentEmbedder expects a list of Documents as input",
        ):
            embedder.run(documents=string_input)

        with pytest.raises(
            TypeError,
            match="NvidiaDocumentEmbedder expects a list of Documents as input",
        ):
            embedder.run(documents=list_integers_input)

    def test_run_on_empty_list(self):
        model = "playground_nvolveqa_40k"
        api_key = Secret.from_token("fake-api-key")
        embedder = NvidiaDocumentEmbedder(model, api_key=api_key)

        embedder.warm_up()
        embedder.backend = MockBackend(model=model, api_key=api_key)

        empty_list_input = []
        result = embedder.run(documents=empty_list_input)

        assert result["documents"] is not None
        assert not result["documents"]  # empty list

    @pytest.mark.skipif(
        not os.environ.get("NVIDIA_API_KEY", None),
        reason="Export an env var called NVIDIA_API_KEY containing the Nvidia API key to run this test.",
    )
    @pytest.mark.skipif(
        not os.environ.get("NVIDIA_NIM_EMBEDDER_MODEL", None)
        or not os.environ.get("NVIDIA_NIM_ENDPOINT_URL", None),
        reason="Export an env var called NVIDIA_NIM_EMBEDDER_MODEL containing the hosted model name and "
        "NVIDIA_NIM_ENDPOINT_URL containing the local URL to call.",
    )
    @pytest.mark.integration
    def test_run_integration_with_nim_backend(self):
        model = os.environ["NVIDIA_NIM_EMBEDDER_MODEL"]
        url = os.environ["NVIDIA_NIM_ENDPOINT_URL"]
        embedder = NvidiaDocumentEmbedder(
            model=model,
            api_url=url,
            api_key=None,
        )
        embedder.warm_up()
        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]

        result = embedder.run(docs)
        docs_with_embeddings = result["documents"]

        assert isinstance(docs_with_embeddings, list)
        assert len(docs_with_embeddings) == len(docs)
        for doc in docs_with_embeddings:
            assert isinstance(doc.embedding, list)
            assert isinstance(doc.embedding[0], float)

    @pytest.mark.parametrize(
        "model, api_url",
        [
            ("NV-Embed-QA", None),
            ("snowflake/arctic-embed-l", "https://integrate.api.nvidia.com/v1"),
            ("nvidia/nv-embed-v1", "https://integrate.api.nvidia.com/v1"),
            ("nvidia/nv-embedqa-mistral-7b-v2", "https://integrate.api.nvidia.com/v1"),
            ("nvidia/nv-embedqa-e5-v5", "https://integrate.api.nvidia.com/v1"),
            ("baai/bge-m3", "https://integrate.api.nvidia.com/v1"),
        ],
        ids=[
            "NV-Embed-QA",
            "snowflake/arctic-embed-l",
            "nvidia/nv-embed-v1",
            "nvidia/nv-embedqa-mistral-7b-v2",
            "nvidia/nv-embedqa-e5-v5",
            "baai/bge-m3",
        ],
    )
    @pytest.mark.skipif(
        not os.environ.get("NVIDIA_API_KEY", None),
        reason="Export an env var called NVIDIA_API_KEY containing the NVIDIA API key to run this test.",
    )
    @pytest.mark.integration
    def test_run_integration_with_api_catalog(self, model, api_url):
        embedder = NvidiaDocumentEmbedder(
            model=model,
            **({"api_url": api_url} if api_url else {}),
            api_key=Secret.from_env_var("NVIDIA_API_KEY"),
        )
        embedder.warm_up()

        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]

        result = embedder.run(docs)
        docs_with_embeddings = result["documents"]

        assert isinstance(docs_with_embeddings, list)
        assert len(docs_with_embeddings) == len(docs)
        for doc in docs_with_embeddings:
            assert isinstance(doc.embedding, list)
            assert isinstance(doc.embedding[0], float)

    @pytest.mark.skipif(
        not os.environ.get("NVIDIA_TRITON_EMBEDDER_MODEL", None)
        or not os.environ.get(
            "NVIDIA_TRITON_HTTP_ENDPOINT_URL",
            os.environ.get("NVIDIA_TRITON_GRPC_ENDPOINT_URL", None),
        ),
        reason="Export an env var called NVIDIA_TRITON_EMBEDDER_MODEL containing the hosted model name and "
        "NVIDIA_TRITON_HTTP_ENDPOINT_URL or NVIDIA_TRITON_GRPC_ENDPOINT_URL containing the local URL to call.",
    )
    @pytest.mark.parametrize("backend", ["triton-http", "triton-grpc"])
    @pytest.mark.integration
    def test_run_integration_with_triton_backend(
        self, backend: Literal["nim", "triton-http", "triton-grpc"]
    ):
        model = os.environ["NVIDIA_TRITON_EMBEDDER_MODEL"]
        url = os.environ[
            "NVIDIA_TRITON_HTTP_ENDPOINT_URL"
            if backend == "triton-http"
            else "NVIDIA_TRITON_GRPC_ENDPOINT_URL"
        ]
        embedder = NvidiaDocumentEmbedder(
            model=model,
            api_url=url,
            api_key=None,
            backend=backend,
        )
        embedder.warm_up()

        docs = [
            Document(content="I love cheese", meta={"topic": "Cuisine"}),
            Document(
                content="A transformer is a deep learning architecture",
                meta={"topic": "ML"},
            ),
        ]

        result = embedder.run(docs)
        docs_with_embeddings = result["documents"]

        assert isinstance(docs_with_embeddings, list)
        assert len(docs_with_embeddings) == len(docs)
        for doc in docs_with_embeddings:
            assert isinstance(doc.embedding, list)
            assert isinstance(doc.embedding[0], float)
