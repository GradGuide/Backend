from typing import List, Optional, Any
import google.generativeai as genai
import os

from .utils import process_in_batches


class LLM:
    __SUPPORTED_LANGUAGES = ["English", "Arabic", "French"]

    def __init__(self, api_key: Optional[str] = os.environ.get("GEMINI_API_KEY")):
        self.api_key = api_key
        genai.configure(api_key=self.api_key)

    def _create_model(self, system_instruction: str) -> genai.GenerativeModel:
        return genai.GenerativeModel(
            "gemini-1.5-flash", system_instruction=system_instruction
        )

    def _generate_content(
        self,
        input_text: str,
        system_instruction: str,
        max_tokens: int,
        temperature: float,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
        response_mime_type: Optional[str] = None,
        response_schema: Optional[Any] = None,
        *args,
        **kwargs,
    ) -> genai.types.GenerateContentResponse:
        if language and language in self.__SUPPORTED_LANGUAGES:
            system_instruction = f"[Use {language} language] " + system_instruction

        model = self._create_model(system_instruction)
        instructions = [input_text]

        if additional_instructions:
            instructions.extend(additional_instructions)

        generation_config = genai.GenerationConfig(
            max_output_tokens=max_tokens,
            temperature=temperature,
        )

        if response_mime_type:
            generation_config.response_mime_type = response_mime_type

        if response_schema:
            generation_config.response_schema = response_schema

        response = model.generate_content(
            instructions,
            generation_config=generation_config,
            safety_settings={
                "HATE": "BLOCK_NONE",
                "HARASSMENT": "BLOCK_NONE",
                "SEXUAL": "BLOCK_NONE",
                "DANGEROUS": "BLOCK_NONE",
            },
        )

        return response

    @process_in_batches
    def summarize(
        self,
        input_text: str,
        max_tokens: int = 64,
        temperature: float = 0.3,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Generates a summary of the provided input text using the generative AI model.

        Parameters:
        ----------
        input_text : str
            The text that needs to be summarized.
        max_tokens : int, optional
            Maximum number of tokens in the output summary.
        temperature : float, optional
            The creativity level for the response.
        """
        system_instruction = f"You are an AI that provides summaries of the input text only using {max_tokens} words."
        return self._generate_content(
            input_text,
            system_instruction,
            max_tokens,
            temperature,
            additional_instructions,
            language,
        ).text.strip()

    @process_in_batches
    def answer_question(
        self,
        question: str,
        context: str,
        max_tokens: int = 64,
        temperature: float = 0.3,
        language: Optional[str] = None,
    ) -> str:
        """
        Answers a given question based on the provided context.

        Parameters:
        ----------
        question : str
            The question to answer.
        context : str
            The context information to answer the question from.
        max_tokens : int, optional
            Maximum number of tokens for the generated answer.
        temperature : float, optional
            The creativity level for the response.
        """
        system_instruction = (
            "You are an AI assistant that answers questions. Answer the following question based only "
            "on the context provided and nothing more. Keep the answer on point and short."
        )
        return self._generate_content(
            f"Question:\n```{question}\n```",
            system_instruction,
            max_tokens,
            temperature,
            additional_instructions=[f"Context:\n```{context}\n```"],
            language=language,
        ).text.strip()

    @process_in_batches
    def grammar_corrector(
        self,
        text: str,
        max_tokens: int = 64,
        temperature: float = 0.3,
        additional_instructions: Optional[List[str]] = None,
        language: Optional[str] = None,
    ) -> str:
        """
        Correct the grammar and spelling of a given input text.

        Parameters:
        ----------
        text : str
            The text to be corrected.
        max_tokens : int, optional
            Maximum number of tokens.
        temperature : float, optional
            The creativity level for the response.
        """
        system_instruction = (
            "You are an AI assistant that corrects grammar and spelling. Rewrite the text and change "
            "what's necessary with no errors, without any explanation."
        )
        return self._generate_content(
            f"\n```{text}```",
            system_instruction,
            max_tokens,
            temperature,
            additional_instructions,
            language,
        ).text.strip()
