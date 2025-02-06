from typing import Optional
from transformers import pipeline
from difflib import unified_diff
from .utils import process_in_batches

import warnings

warnings.filterwarnings("ignore")


class GrammarCorrector:
    def __init__(self):
        self.model_name = "pszemraj/grammar-synthesis-small"
        self.corrector = pipeline("text2text-generation", self.model_name)

        self.result = None

    @process_in_batches
    def correct(self, text: str) -> str:
        """
        Corrects the grammar of the input text.

        Parameters
        ----------
        text: The text whose grammar is to be corrected.

        """
        result = self.corrector(text)[0]["generated_text"]
        self.result = result

        return result

    def diff(self, original: str, corrected: Optional[str] = None) -> str:
        """
        Generate a unified diff between the original and corrected text, showing the differences.
        Lines with corrections will have '+' (added) or '-' (removed) to indicate changes.

        Parameters
        ----------
        original: Original text before correction.
        corrected: Corrected text after grammar/spelling changes.
        """
        if corrected is None:
            corrected = self.result

        original = original if original.endswith("\n") else original + "\n"
        corrected = corrected if corrected.endswith("\n") else corrected + "\n"

        diff = unified_diff(
            original.splitlines(keepends=True),
            corrected.splitlines(keepends=True),
            fromfile="Original",
            tofile="Corrected",
        )
        return "".join(diff)
