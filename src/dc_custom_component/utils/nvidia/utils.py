import os
from dataclasses import dataclass, field
from typing import List, Optional
from urllib.parse import urlparse

REQUEST_TIMEOUT = float(os.environ.get("NVIDIA_TIMEOUT", 60.0))


def is_hosted(api_url: str):
    """"""
    return urlparse(api_url).netloc in [
        "integrate.api.nvidia.com",
        "ai.api.nvidia.com",
    ]


@dataclass
class Model:
    """
    Model information.

    id: unique identifier for the model, passed as model parameter for requests
    aliases: list of aliases for the model
    base_model: root model for the model
    All aliases are deprecated and will trigger a warning when used.
    """

    id: str
    aliases: Optional[List[str]] = field(default_factory=list)
    base_model: Optional[str] = None
