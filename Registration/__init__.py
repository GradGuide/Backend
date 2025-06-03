from .qna import QnA
from .llm import LLM
from .summary import Summary
from .similarity import Similarity
from .grammar import GrammarCorrector
from typing import List, Optional, Literal, Any, Union
from .ollama import OllamaLLM
from .gemini import GeminiLLM
import os

__all__ = ["LLM", "OllamaLLM", "GeminiLLM"]
__all__ = ["QnA", "LLM", "Summary", "Similarity", "GrammarCorrector"]

class LLM:
    def __init__(
        self,
        provider: Literal["gemini", "ollama"] = "gemini",
        gemini_api_key: Optional[str] = os.environ.get("GEMINI_API_KEY"),
        ollama_default_model: str = "gemma3:1b",
    ):
        self.provider = provider

        if provider == "gemini":
            self.llm = GeminiLLM(api_key=gemini_api_key)
        else:
            self.llm = OllamaLLM(default_model=ollama_default_model)

    def _generate_content(
        self,
        input_text: str,
        system_instruction: str,
        max_tokens: int,
        temperature: float,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
        **kwargs,
    ) -> Union[str, Any]:
        if self.provider == "gemini":
            response = self.llm._generate_content(
                input_text=input_text,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                temperature=temperature,
                additional_instructions=additional_instructions,
                language=language,
                **kwargs,
            )
            return response.text.strip()
        else:
            return self.llm._generate_content(
                input_text=input_text,
                system_instruction=system_instruction,
                max_tokens=max_tokens,
                temperature=temperature,
                additional_instructions=additional_instructions,
                language=language,
                **kwargs,
            )

    def summarize(
        self,
        input_text: str,
        max_tokens: int = 100,
        temperature: float = 0.3,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        return self.llm.summarize(
            input_text=input_text,
            max_tokens=max_tokens,
            temperature=temperature,
            additional_instructions=additional_instructions,
            language=language,
        )

    def answer_question(
        self,
        question: str,
        context: str,
        max_tokens: int = 256,
        temperature: float = 0.3,
        language: Optional[str] = None,
    ) -> str:
        return self.llm.answer_question(
            question=question,
            context=context,
            max_tokens=max_tokens,
            temperature=temperature,
            language=language,
        )

    def grammar_corrector(
        self,
        text: str,
        max_tokens: int = 512,
        temperature: float = 0.1,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        return self.llm.grammar_corrector(
            text=text,
            max_tokens=max_tokens,
            temperature=temperature,
            additional_instructions=additional_instructions,
            language=language,
        )

