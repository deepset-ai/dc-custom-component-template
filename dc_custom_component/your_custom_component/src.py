from typing import Dict, List

from haystack import GeneratedAnswer, component

# Example from https://docs.haystack.deepset.ai/docs/custom-components#extended-example

example_pipeline = """
    components:
      splitter:
        init_parameters: {}
        type: dc_custom_component.your_custom_component.src.WhitespaceSplitter
      welcome_text_generator:
        init_parameters: {}
        type: dc_custom_component.your_custom_component.src.WelcomeTextGenerator
    
    connections:
    - receiver: splitter.text
      sender: welcome_text_generator.welcome_text
    
    inputs:  # Define the inputs for your pipeline
      query:  # These components will receive the query as input
      - "welcome_text_generator.name"
    
    outputs:
      answers: "splitter.answers"
    
    max_loops_allowed: 100
    metadata: {}
"""


@component
class WelcomeTextGenerator:
    """
    A component generating personal welcome message and making it upper case
    """

    @component.output_types(welcome_text=str, note=str)
    def run(self, name: str) -> Dict:
        return {
            "welcome_text": (
                "Hello {name}, welcome to Haystack!".format(name=name)
            ).upper(),
            "note": "welcome message is ready",
        }


@component
class WhitespaceSplitter:
    """
    A component for splitting the text by whitespace
    """

    @component.output_types(answers=List[GeneratedAnswer])
    def run(self, text: str) -> Dict:
        return {
            "answers": [
                GeneratedAnswer(
                    data=text,
                    query="Splitting text by whitespace",
                    documents=[],
                    meta={},
                )
            ]
        }
