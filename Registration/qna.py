from transformers import pipeline
from typing import Dict, Union
from .utils import process_in_batches


class QnA:
    def __init__(self):
        self.model_name = "deepset/roberta-base-squad2"

        self.oracle = pipeline("question-answering", model=self.model_name)

    @process_in_batches
    def simple_question(
        self, question: str, context: str
    ) -> Dict[str, Union[float, int, str]]:
        """
        Answers a question based on the provided context using a pre-trained transformer model.
        Use only for simple one word answer questions.

        Parameters:
            question (str): The question to be answered.
            context (str): The context in which to find the answer.
        """
        return self.oracle(question=question, context=context)
