import warnings
from typing import Any, Dict, List, Literal, Optional, Union

from haystack import component, default_from_dict, default_to_dict
from haystack.utils import Secret, deserialize_secrets_inplace

from dc_custom_component.utils.nvidia import NimBackend, TritonBackend, is_hosted

from .truncate import EmbeddingTruncateMode

_DEFAULT_API_URL = "https://ai.api.nvidia.com/v1/retrieval/nvidia"


@component
class NvidiaTextEmbedder:
    """
    A component for embedding strings using embedding models provided by
    [NVIDIA NIMs](https://ai.nvidia.com) or [NIVIDIA Triton](https://developer.nvidia.com/triton-inference-server).

    For models that differentiate between query and document inputs,
    this component embeds the input string as a query.

    Usage example:
    ```python
    from haystack_integrations.components.embedders.nvidia import NvidiaTextEmbedder

    text_to_embed = "I love pizza!"

    text_embedder = NvidiaTextEmbedder(model="NV-Embed-QA", api_url="https://ai.api.nvidia.com/v1/retrieval/nvidia")
    text_embedder.warm_up()

    print(text_embedder.run(text_to_embed))
    ```
    """

    def __init__(
        self,
        model: Optional[str] = None,
        api_key: Optional[Secret] = Secret.from_env_var("NVIDIA_API_KEY"),
        api_url: str = _DEFAULT_API_URL,
        prefix: str = "",
        suffix: str = "",
        truncate: Optional[Union[EmbeddingTruncateMode, str]] = None,
        backend: Literal["nim", "triton-http", "triton-grpc"] = "nim",
        timeout: Optional[float] = None,
        username: Optional[Secret] = None,
        password: Optional[Secret] = None,
        backend_kwargs: Optional[Dict[str, Any]] = None,
    ):
        """
        Create a NvidiaTextEmbedder component.

        :param model:
            Embedding model to use.
            If no specific model along with locally hosted API URL is provided,
            the system defaults to the available model found using /models API.
        :param api_key:
            API key for the NVIDIA NIM.
        :param api_url:
            Custom API URL for the NVIDIA NIM.
            Format for API URL is http://host:port
        :param prefix:
            A string to add to the beginning of each text.
        :param suffix:
            A string to add to the end of each text.
        :param truncate:
            Specifies how inputs longer that the maximum token length should be truncated.
            If None the behavior is model-dependent, see the official documentation for more information.
        :param backend:
            The backend to use for the component. Currently supported are "nim", "triton-http", and "triton-grpc".
            Default is "nim".
        :param timeout:
            Timeout for the request in seconds. If not set, defaults either to `NVIDIA_TIMEOUT` environment variable
            or 60 seconds.
        :param username:
            Username for HTTP basic authentication.
        :param password:
            Password for HTTP basic authentication.
        :param backend_kwargs:
            Additional keyword arguments to pass to the backend.
        """

        self.api_key = api_key
        self.model = model
        self.api_url = api_url  # url_validation(api_url, _DEFAULT_API_URL, ["v1/embeddings"]) if backend == "nim" else api_url
        self.prefix = prefix
        self.suffix = suffix
        self._backend = backend
        self.timeout = timeout
        self.username = username
        self.password = password
        self.backend_kwargs = backend_kwargs

        if isinstance(truncate, str):
            if self._backend != "nim":
                error_message = "Truncation is only supported with the nim backend."
                raise ValueError(error_message)
            truncate = EmbeddingTruncateMode.from_str(truncate)
        self.truncate = truncate

        self.backend: Optional[Any] = None
        self._initialized = False

        if is_hosted(api_url) and not self.model:  # manually set default model
            self.model = "nvidia/nv-embedqa-e5-v5"

    def default_model(self):
        """Set default model in local NIM mode."""
        valid_models = [
            model.id
            for model in self.backend.models()
            if not model.base_model or model.base_model == model.id
        ]
        name = next(iter(valid_models), None)
        if name:
            warnings.warn(
                f"Default model is set as: {name}. \n"
                "Set model using model parameter. \n"
                "To get available models use available_models property.",
                UserWarning,
                stacklevel=2,
            )
            self.model = self.backend.model = name
        else:
            error_message = "No locally hosted model was found."
            raise ValueError(error_message)

    def warm_up(self):
        """
        Initializes the component.
        """
        if self._initialized:
            return

        if self._backend == "nim":
            model_kwargs = {"input_type": "query"}
            if self.truncate is not None:
                model_kwargs["truncate"] = str(self.truncate)
            self.backend = NimBackend(
                self.model,
                api_url=self.api_url,
                api_key=self.api_key,
                model_kwargs=model_kwargs,
                timeout=self.timeout,
                username=self.username,
                password=self.password,
            )
        else:
            self.backend = TritonBackend(
                model=self.model,
                api_url=self.api_url,
                api_key=self.api_key,
                protocol="http" if self._backend == "triton-http" else "grpc",
                timeout=self.timeout,
                username=self.username,
                password=self.password,
                backend_kwargs=self.backend_kwargs,
            )

        self._initialized = True

        if not self.model:
            self.default_model()

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        return default_to_dict(
            self,
            api_key=self.api_key.to_dict() if self.api_key else None,
            model=self.model,
            api_url=self.api_url,
            prefix=self.prefix,
            suffix=self.suffix,
            truncate=str(self.truncate) if self.truncate is not None else None,
            backend=self._backend,
            timeout=self.timeout,
            username=self.username.to_dict() if self.username else None,
            password=self.password.to_dict() if self.password else None,
            backend_kwargs=self.backend_kwargs,
        )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NvidiaTextEmbedder":
        """
        Deserializes the component from a dictionary.

        :param data:
            The dictionary to deserialize from.
        :returns:
            The deserialized component.
        """
        deserialize_secrets_inplace(
            data["init_parameters"], keys=["api_key", "username", "password"]
        )
        return default_from_dict(cls, data)

    @component.output_types(embedding=List[float], meta=Dict[str, Any])
    def run(self, text: str):
        """
        Embed a string.

        :param text:
            The text to embed.
        :returns:
            A dictionary with the following keys and values:
            - `embedding` - Embeddng of the text.
            - `meta` - Metadata on usage statistics, etc.
        :raises RuntimeError:
            If the component was not initialized.
        :raises TypeError:
            If the input is not a string.
        """
        if not self._initialized:
            msg = "The embedding model has not been loaded. Please call warm_up() before running."
            raise RuntimeError(msg)
        elif not isinstance(text, str):
            msg = (
                "NvidiaTextEmbedder expects a string as an input."
                "In case you want to embed a list of Documents, please use the NvidiaDocumentEmbedder."
            )
            raise TypeError(msg)

        assert self.backend is not None
        text_to_embed = self.prefix + text + self.suffix
        sorted_embeddings, meta = self.backend.embed([text_to_embed])

        return {"embedding": sorted_embeddings[0], "meta": meta}
