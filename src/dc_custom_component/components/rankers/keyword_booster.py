from typing import Dict, List

from haystack import Document, component


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
