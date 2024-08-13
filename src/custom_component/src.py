from typing import Dict

from haystack import component


@component
class WelcomeTextGenerator:
    """
    A component generating personal welcome message and making it upper case

    Example from https://docs.haystack.deepset.ai/docs/custom-components#extended-example
    """

    @component.output_types(welcome_text=str, note=str)
    def run(self, name: str) -> Dict[str, str]:
        return {
            "welcome_text": (
                "Hello {name}, welcome to Haystack!".format(name=name)
            ).upper(),
            "note": "welcome message is ready",
        }
