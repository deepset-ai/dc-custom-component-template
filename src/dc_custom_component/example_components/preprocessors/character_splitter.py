from typing import Dict, List

from haystack import Document, component


@component
class CharacterSplitter:
    """
    A sample component for splitting the text by characters

    ### Usage example

    ```python
    from haystack import Document
    from dc_custom_component.components.preprocessors.character_splitter import CharacterSplitter

    doc = Document(content="Moonlight shimmered softly, wolves howled nearby, night enveloped everything.")

    splitter = CharacterSplitter(split_length=20)
    result = splitter.run(documents=[doc])
    ```
    """

    def __init__(
        self,
        split_length: int = 100,
    ):
        self.split_length = split_length

    @component.output_types(documents=List[Document])
    def run(self, documents: List[Document]) -> Dict[str, List[Document]]:
        """
        Split documents into smaller parts using character lengths.

        :param documents: The documents to split.

        :returns: A dictionary with the following key:
            - `documents`: List of documents with the split texts. Each document includes:
                - A metadata field `source_id` to track the original document.
                - A metadata field `source_offsets` to track the original character offsets.
                - A metadata field `source_part` to track the part number of the split text.
                - All other metadata copied from the original document.
        """
        split_docs = []
        for doc in documents:
            text = doc.content
            for i in range(0, len(text), self.split_length):
                split_text = text[i : i + self.split_length]
                split_doc = Document(
                    content=split_text,
                    meta={
                        "source_id": doc.id,
                        "source_offsets": (i, i + len(split_text)),
                        "source_part": i // self.split_length,
                        **doc.meta,
                    },
                )
                split_docs.append(split_doc)

        return {"documents": split_docs}
