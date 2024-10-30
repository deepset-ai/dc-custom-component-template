from typing import Any, Dict, List

from haystack import Document, component, default_from_dict, default_to_dict
from haystack.utils import Secret, deserialize_secrets_inplace


@component
class KeywordBooster:
    """
    A sample component for boosting the score of documents containing specific keywords

    ### Usage example

    ```python
    from haystack import Document
    from dc_custom_component.components.rankers.keyword_booster import KeywordBooster

    doc = Document(content="Moonlight shimmered softly, wolves howled nearby, night enveloped everything.")

    booster = KeywordBooster(keyword_boosts={"moonlight": 1.5, "wolves": 2.0})
    result = booster.run(documents=[doc])
    ```
    """

    def __init__(
        self,
        keyword_boosts: Dict[str, float],
    ):
        self.keyword_boosts = keyword_boosts

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Boost the score of documents containing specific keywords.

        :param documents: The documents to boost.

        :returns: A dictionary with the following key:
            - `documents`: List of documents with the boosted scores.
        """
        for keyword, boost in self.keyword_boosts.items():
            for doc in documents:
                if keyword.lower() in doc.content.lower() and doc.score is not None:
                    doc.score = doc.score * boost

        documents = sorted(documents, key=lambda x: x.score, reverse=True)

        return {"documents": documents}


@component
class SecretKeywordBooster:
    """
    Exactly the same as the KeywordBooster, but with a single keyword that is retrieved
    froma secret and boosted with the value 100.
    """

    def __init__(
        self,
        magic_word: Secret = Secret.from_env_var("MAGIC_WORD"),
    ):
        """
        :param magic_word: A secret keyword to boost documents containing it.
        """
        self.magic_word = magic_word

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Similar to KeywordBooster.run(), but boosts documents containing a single secret keyword.

        :param documents: The documents to boost.

        :returns: A dictionary with the following key:
            - `documents`: List of documents with the boosted scores.
        """
        boost = 100
        keyword = self.magic_word.resolve_value()

        for doc in documents:
            if keyword.lower() in doc.content.lower() and doc.score is not None:
                doc.score = doc.score * boost

        documents = sorted(documents, key=lambda x: x.score, reverse=True)

        return {"documents": documents}

    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the component to a dictionary.

        :returns:
            Dictionary with serialized data.
        """
        serealized_component: Dict[str, Any] = default_to_dict(
            self, magic_word=self.magic_word.to_dict()
        )
        return serealized_component

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecretKeywordBooster":
        """
        Deserializes the component from a dictionary.

        :param data:
            The dictionary to deserialize from.
        :returns:
            The deserialized component.
        """
        deserialize_secrets_inplace(data["init_parameters"], keys=["magic_word"])
        deserialized_component = default_from_dict(cls, data)
        return deserialized_component  # type: ignore
