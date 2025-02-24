# qna.py
from typing import List, Tuple
from typing_extensions import TypedDict
import json
from transformers import pipeline
from .llm import LLM


class QuestionList(TypedDict):
    questions: List[str]


class EvaluationResult(TypedDict):
    score: int
    feedback: str


class QnA:
    def __init__(self):
        self.model_name = "deepset/roberta-base-squad2"
        self.oracle = pipeline("question-answering", model=self.model_name)
        self.llm = LLM()

    def generate_questions(
        self,
        text: str,
        num_questions: int = 5,
        language: str = "English",
        max_tokens: int = 256,
        temperature: float = 0.7,
    ) -> List[str]:
        """
        Generates questions with structured JSON output
        """
        system_instruction = (
            f"Generate {num_questions} relevant questions from the text. "
            "Return a JSON object with a 'questions' array containing the questions."
        )

        try:
            response = self.llm._generate_content(
                text,
                system_instruction,
                max_tokens=max_tokens,
                temperature=temperature,
                language=language,
                response_mime_type="application/json",
                response_schema=QuestionList,
            )
            result = json.loads(response.text)
            return result.get("questions", [])
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error parsing questions: {e}")
            return []

    def evaluate_answers(
        self,
        questions: List[str],
        user_answers: List[str],
        context: str,
        language: str = "English",
        max_tokens: int = 128,
        temperature: float = 0.5,
    ) -> List[Tuple[str, int, str]]:
        """
        Evaluates answers with structured JSON output
        """
        results = []
        for question, answer in zip(questions, user_answers):
            evaluation_prompt = f"Question: {question}\nUser Answer: {answer}\nCorrect Context: {context}"

            try:
                response = self.llm._generate_content(
                    evaluation_prompt,
                    "Evaluate answers and return JSON with 'score' (0-10) and 'feedback'",
                    max_tokens=max_tokens,
                    temperature=temperature,
                    language=language,
                    response_mime_type="application/json",
                    response_schema=EvaluationResult,
                )
                evaluation = json.loads(response.text)
                results.append(
                    (
                        question,
                        evaluation.get("score", 0),
                        evaluation.get("feedback", "Evaluation failed"),
                    )
                )
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Error parsing evaluation: {e}")
                results.append((question, 0, "Evaluation error"))

        return results
