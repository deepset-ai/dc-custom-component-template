from haystack import Document
from dc_custom_component.example_components.rankers.keyword_booster import (
    KeywordBooster,
    SecretKeywordBooster,
)
from haystack.utils import Secret
from typing import Dict, List


class TestKeywordBooster:
    def test_boost_single_keyword(self) -> None:
        doc: Document = Document(content="The quick brown fox", score=0.5)
        booster: KeywordBooster = KeywordBooster(keyword_boosts={"fox": 2.0})

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 1.0  # 0.5 * 2.0

    def test_boost_multiple_keywords(self) -> None:
        doc: Document = Document(content="The quick brown fox jumps", score=0.5)
        booster: KeywordBooster = KeywordBooster(
            keyword_boosts={"fox": 2.0, "jumps": 1.5}
        )

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 1.5  # 0.5 * 2.0 * 1.5

    def test_case_insensitive_boost(self) -> None:
        doc: Document = Document(content="The Quick BROWN Fox", score=0.5)
        booster: KeywordBooster = KeywordBooster(keyword_boosts={"fox": 2.0})

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 1.0

    def test_no_matching_keywords(self) -> None:
        doc: Document = Document(content="The quick brown fox", score=0.5)
        booster: KeywordBooster = KeywordBooster(keyword_boosts={"cat": 2.0})

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 0.5


class TestSecretKeywordBooster:
    def test_boost_with_secret_keyword(self) -> None:
        doc: Document = Document(content="The quick brown fox", score=0.5)
        booster: SecretKeywordBooster = SecretKeywordBooster(
            magic_word=Secret.from_token("fox")
        )

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 50.0  # 0.5 * 100

    def test_case_insensitive_secret_boost(self) -> None:
        doc: Document = Document(content="The Quick BROWN Fox", score=0.5)
        booster: SecretKeywordBooster = SecretKeywordBooster(
            magic_word=Secret.from_token("fox")
        )

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 50.0

    def test_no_matching_secret_keyword(self) -> None:
        doc: Document = Document(content="The quick brown fox", score=0.5)
        booster: SecretKeywordBooster = SecretKeywordBooster(
            magic_word=Secret.from_token("cat")
        )

        result: Dict[str, List[Document]] = booster.run(documents=[doc])

        assert result["documents"][0].score == 0.5

    def test_serialization(self) -> None:
        booster: SecretKeywordBooster = SecretKeywordBooster(
            magic_word=Secret.from_env_var("MY_ENV_VAR")
        )
        serialized: Dict = booster.to_dict()
        deserialized: SecretKeywordBooster = SecretKeywordBooster.from_dict(serialized)

        assert isinstance(deserialized, SecretKeywordBooster)
        assert deserialized.magic_word == Secret.from_env_var("MY_ENV_VAR")

    def test_serialization_from_dict(self) -> None:
        deserialized: SecretKeywordBooster = SecretKeywordBooster.from_dict(
            {
                "type": "dc_custom_component.example_components.rankers.keyword_booster.SecretKeywordBooster",
                "init_parameters": {
                    "magic_word": {
                        "type": "env_var",
                        "env_vars": ["MY_ENV_VAR"],
                        "strict": True,
                    }
                },
            }
        )

        assert isinstance(deserialized, SecretKeywordBooster)
        assert deserialized.magic_word == Secret.from_env_var("MY_ENV_VAR")
