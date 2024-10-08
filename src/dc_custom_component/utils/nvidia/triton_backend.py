from typing import Any, Dict, List, Literal, Optional, Tuple

import gevent
import numpy as np
from haystack import Document
from haystack.lazy_imports import LazyImport
from haystack.utils import Secret

from .utils import REQUEST_TIMEOUT, Model
import base64

with LazyImport("Run 'pip install tritonclient[http]'") as tritonclient_http:
    import tritonclient.http

with LazyImport("Run 'pip install tritonclient[grpc]'") as tritonclient_grpc:
    import tritonclient.grpc


class TritonBackend:
    def __init__(
        self,
        model: str,
        api_url: str,
        api_key: Optional[Secret] = Secret.from_env_var("NVIDIA_API_KEY"),
        backend_kwargs: Optional[Dict[str, Any]] = None,
        protocol: Literal["http", "grpc"] = "http",
        timeout: Optional[float] = None,
        username: Optional[Secret] = None,
        password: Optional[Secret] = None,
    ):
        self.model = model
        self.api_url = api_url
        self.backend_kwargs = backend_kwargs or {}

        if timeout is None:
            timeout = REQUEST_TIMEOUT
        self.timeout = int(timeout)
        self.headers = {}

        if username and password:
            auth_str = f"{username.resolve_value()}:{password.resolve_value()}"
            auth_bytes = auth_str.encode("utf-8")
            auth_base64 = base64.b64encode(auth_bytes).decode("utf-8")
            self.headers["authorization"] = f"Basic {auth_base64}"
        elif api_key:
            self.headers["authorization"] = f"Bearer {api_key.resolve_value()}"

        client_kwargs: Dict[str, Any] = self.backend_kwargs.get("client_kwargs", {})
        if protocol == "grpc":
            tritonclient_grpc.check()
            self.triton = tritonclient.grpc
            self.client = tritonclient.grpc.InferenceServerClient(
                url=api_url, **client_kwargs
            )
        else:
            tritonclient_http.check()
            self.triton = tritonclient.http
            ssl = client_kwargs.get("ssl", False)
            if ssl:
                client_kwargs["ssl_context_factory"] = client_kwargs.get(
                    "ssl_context_factory", gevent.ssl.create_default_context
                )
            self.client = tritonclient.http.InferenceServerClient(
                url=api_url, **client_kwargs
            )

    def embed(self, texts: List[str]) -> Tuple[List[List[float]], Dict[str, Any]]:
        inputs = []
        text_input = self.triton.InferInput("text", [len(texts)], "BYTES")
        text_input.set_data_from_numpy(np.array(texts, dtype=object))
        inputs.append(text_input)

        infer_kwargs = self.backend_kwargs.get("infer_kwargs", {})

        results = self.client.infer(
            model_name=self.model,
            inputs=inputs,
            headers=self.headers,
            timeout=self.timeout,
            **infer_kwargs,
        )

        embeddings = results.as_numpy("embeddings").tolist()

        return embeddings, {}

    def generate(self, prompt: str) -> Tuple[List[str], List[Dict[str, Any]]]:
        raise NotImplementedError()

    def models(self) -> List[Model]:
        data = self.client.get_model_repository_index(
            headers=self.headers,
        )

        models = [Model(result["name"]) for result in data]
        if not models:
            msg = f"No hosted model were found at URL '{self.api_url}'."
            raise ValueError(msg)
        return models

    def rank(
        self,
        query: str,
        documents: List[Document],
        endpoint: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        raise NotImplementedError()
