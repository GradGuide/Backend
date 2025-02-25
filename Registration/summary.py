from typing import List, Tuple
import transformers
import spacy
from collections import Counter
import warnings

warnings.filterwarnings("ignore")


class Summary:
    def __init__(self):
        self.summarizer = transformers.pipeline(
            "summarization", model="google-t5/t5-base"
        )
        self.nlp = spacy.load("en_core_web_sm")

    def bart_summarize(
        self,
        text: str,
        min_length: int = 5,
        max_length: int = 64,
        percentage: float = 0.40,
    ) -> List[str]:
        """
        Summarize the input text using BART.
        """
        doc = self.nlp(text)

        tokens = [token.text for token in doc]
        num_tokens = len(tokens)

        if not max_length or max_length > num_tokens:
            max_length = int(num_tokens * percentage)

        min_length = max(5, int(max_length * 0.5))

        return self.summarizer(text, min_length=min_length, max_length=max_length)[0]

    def spacy_extract_keywords(
        self, text: str, num_keywords: int = 10
    ) -> List[Tuple[str, int]]:
        """
        Extract keywords from the input text using spaCy.
        """
        doc = self.nlp(text)
        keywords = [
            token.text for token in doc if (token.is_alpha) and not token.is_stop
        ]
        keyword_freq = Counter(keywords)
        return keyword_freq.most_common(num_keywords)
