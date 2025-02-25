from typing import Optional
from transformers import pipeline
from difflib import unified_diff
from .utils import smart_split

import warnings

warnings.filterwarnings("ignore")


class GrammarCorrector:
    def __init__(self):
        self.model_name = "pszemraj/flan-t5-large-grammar-synthesis"
        self.corrector = pipeline("text2text-generation", self.model_name)

        self.result = None

    def correct(self, text: str, max_chunk_size: int = 100) -> str:
        """
        Corrects the grammar of the input text.

        Parameters
        ----------
        text: The text whose grammar is to be corrected.

        """
        split_texts = smart_split(text, max_chunk_size)
        corrected_texts = [
            self.corrector(chunk)[0]["generated_text"] for chunk in split_texts
        ]

        self.result = " ".join(corrected_texts)

        return self.result

    def diff(self, original: str, corrected: Optional[str] = None) -> str:
        return diff(original, corrected if corrected is not None else self.result)


def diff(original: str, corrected: str) -> str:
    """
    Generate a unified diff between the original and corrected text, showing the differences.
    Lines with corrections will have '+' (added) or '-' (removed) to indicate changes.

    Parameters
    ----------
    original: Original text before correction.
    corrected: Corrected text after grammar/spelling changes.
    """
    original = original if original.endswith("\n") else original + "\n"
    corrected = corrected if corrected.endswith("\n") else corrected + "\n"

    diff = unified_diff(
        original.splitlines(keepends=True),
        corrected.splitlines(keepends=True),
        fromfile="Original",
        tofile="Corrected",
    )
    return "".join(diff)
