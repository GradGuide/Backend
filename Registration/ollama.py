from typing import List, Optional, Any, Union
import ollama
from .utils import smart_split


class OllamaLLM:
    __SUPPORTED_LANGUAGES = ["English", "Arabic", "French"]

    def __init__(self, default_model: str = "gemma3:1b"):
        self.default_model = default_model

    def _generate_content(
        self,
        input_text: Union[str, List[Any]],
        system_instruction: str,
        max_tokens: int,
        temperature: float,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
        response_format: Optional[str] = None,
        model: Optional[str] = None,
    ) -> str:
        if language and language in self.__SUPPORTED_LANGUAGES:
            system_instruction = f"[Use {language} language] " + system_instruction

        if additional_instructions:
            system_instruction += "\n\n" + "\n".join(additional_instructions)

        messages: list[dict[str, Union[str, list]]] = [
            {"role": "system", "content": system_instruction}
        ]
        messages.append({"role": "user", "content": input_text})

        options: dict[str, Any] = {
            "num_predict": max_tokens,
            "temperature": temperature,
        }

        if response_format:
            options["format"] = response_format

        response = ollama.chat(
            model=model or self.default_model,
            messages=messages,
            options=options,
            stream=False,
        )

        return response["message"]["content"].strip()

    def summarize(
        self,
        input_text: str,
        max_tokens: int = 100,
        temperature: float = 0.3,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        system_instruction = (
            "You are an expert summarizer. Provide a comprehensive summary covering all key points, "
            "using bullet points/headers when helpful."
            "Be concise while maintaining all crucial information. "
            "Only output the summary itself without any introductory text."
        )

        split_texts = smart_split(input_text, max_tokens)
        summaries = [
            self._generate_content(
                chunk,
                system_instruction,
                max_tokens,
                temperature,
                additional_instructions,
                language,
            )
            for chunk in split_texts
        ]

        return "\n".join(summaries)

    def answer_question(
        self,
        question: str,
        context: str,
        max_tokens: int = 256,
        temperature: float = 0.3,
        language: Optional[str] = None,
    ) -> str:
        system_instruction = (
            "Answer the question strictly based on the provided context. "
            "If unsure or if the answer isn't in the context, state that clearly. "
            "Keep responses concise and factual."
        )

        split_contexts = smart_split(context, max_tokens)
        answers = []

        for chunk in split_contexts:
            response = self._generate_content(
                input_text=chunk,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                temperature=temperature,
                additional_instructions=[f"Question: {question}"],
                language=language,
            )
            answers.append(response)

        return " ".join(answers)

    def grammar_corrector(
        self,
        text: str,
        max_tokens: int = 512,
        temperature: float = 0.1,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        system_instruction = (
            "You are a professional proofreader. Correct grammar, spelling, and punctuation errors. "
            "Improve clarity while preserving the original meaning and tone. "
            "Only output the corrected text without explanations."
        )

        split_texts = smart_split(text, max_tokens)
        corrections = [
            self._generate_content(
                chunk,
                system_instruction,
                max_tokens,
                temperature,
                additional_instructions,
                language,
            )
            for chunk in split_texts
        ]

        return " ".join(corrections)