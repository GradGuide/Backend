from typing import List, Optional, Any
import google.generativeai as genai
import os

from .utils import smart_split


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

    def summarize(
        self,
        input_text: str,
        max_tokens: int = 100,
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
        system_instruction = (
            "You are an AI Assistant, Your only job is to provide summary for the text given, you should give no hints that you are an AI. "
            "You do not explain the document/text, you just output the summary."
            "and do not ever interact with the user. For example:\n Text: [very long text]\n[Summary]\n"
            "Can you provide a comprehensive summary of the given text? The "
            "summary should cover all the key points and main ideas presented in the original text, "
            "while also condensing the information into a concise and easy-to-understand format. "
            "Please ensure that the summary includes relevant details and examples that support the main ideas, "
            "while avoiding any unnecessary information or repetition. The length of the summary should be appropriate "
            "for the length and complexity of the original text, providing a clear and "
            "accurate overview without omitting any important information. Use bullet points and headers if needed for clarity."
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
            ).text.strip()
            for chunk in split_texts
        ]

        return " ".join(summaries)

    def answer_question(
        self,
        question: str,
        context: str,
        max_tokens: int = 64,
        temperature: float = 0.3,
        language: Optional[str] = None,
    ) -> str:
        """
        FIXME: DO NOT USE THIS FUNCTION IT DOES NOT WORK, REWRITE TO SUPPORT
        SPLITTING IN CHUNKS.

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

    def grammar_corrector(
        self,
        text: str,
        max_tokens: int = 100,
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
            "I want you to act as an expert in Language arts with advanced experience in proofreading, "
            "editing, spelling, grammar, proper sentence structure, and punctuation. "
            "You have critical thinking skills with the ability to analyze and evaluate information, arguments, "
            "and ideas, and to make logical and well-supported judgments and decisions. "
            "You will be provided content from a professional business to proofread in the form of emails, "
            "texts, and instant messages to make sure they are error-free before sending. "
            "Your approach would be to carefully read through each communication to identify any errors, "
            "inconsistencies, or areas where clarity could be improved. Your overall goal is to ensure "
            "communications are error-free, clear, and effective in achieving their intended purpose. "
            "You will make appropriate updates to increase readability, professionalism, and cohesiveness, "
            "while also ensuring that your intended meaning is conveyed accurately. "
            "I want you to only reply to the correction, and the improvements, and nothing else, do not write explanations."
            "detect the language and correct it in said language."
        )

        split_texts = smart_split(text, max_tokens)

        corrected_texts = [
            self._generate_content(
                chunk,
                system_instruction,
                max_tokens,
                temperature,
                additional_instructions,
                language,
            ).text.strip()
            for chunk in split_texts
        ]

        return " ".join(corrected_texts)
