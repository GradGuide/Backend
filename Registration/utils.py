from typing import Callable, List, Union
from functools import wraps


def split_text(text: str, max_length: int) -> List[str]:
    """
    Splits the text into chunks based on a specified maximum length.

    Parameters:
    ----------
    text : str
        The input text to be split.
    max_length : int
        The maximum length for each chunk of text.

    Returns:
    -------
    List[str]
        A list of text chunks, each not exceeding max_length.
    """
    words = text.split()
    chunks = []
    current_chunk: List[str] = []

    for word in words:
        if len(" ".join(current_chunk + [word])) <= max_length:
            current_chunk.append(word)
        else:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_in_batches(func: Callable, max_length: int = 4096) -> Callable:
    """
    Decorator to handle batch processing of long text inputs for specific arguments.
    """

    def _process_chunks(
        value: Union[str, List[str]], process_func
    ) -> Union[str, List[str]]:
        """Splits input into chunks, applies function, and reconstructs output."""
        if isinstance(value, str):
            if len(value) <= max_length:
                return process_func(value)
            chunks = [
                value[i : i + max_length] for i in range(0, len(value), max_length)
            ]
            return "".join(map(process_func, chunks))

        elif isinstance(value, list) and any(len(s) > max_length for s in value):
            chunked_lists = [
                [s[i : i + max_length] for i in range(0, len(s), max_length)]
                for s in value
            ]
            processed_chunks = [
                process_func(chunk) for sublist in chunked_lists for chunk in sublist
            ]
            return [item for sublist in processed_chunks for item in sublist]

        return value

    @wraps(func)
    def wrapper(*args, **kwargs):
        arg_names = func.__code__.co_varnames[: func.__code__.co_argcount]
        args = list(args)

        for arg_name in ["context", "input_text", "text"]:
            if arg_name in kwargs:
                kwargs[arg_name] = _process_chunks(
                    kwargs[arg_name],
                    lambda chunk: func(*args, **{**kwargs, arg_name: chunk}),
                )
            elif arg_name in arg_names:
                idx = arg_names.index(arg_name)
                args[idx] = _process_chunks(
                    args[idx],
                    lambda chunk: func(
                        *args[:idx] + [chunk] + args[idx + 1 :], **kwargs
                    ),
                )

        for arg_name in ["sentences", "paragraphs"]:
            if arg_name in kwargs:
                kwargs[arg_name] = _process_chunks(
                    kwargs[arg_name],
                    lambda chunk: func(*args, **{**kwargs, arg_name: chunk}),
                )
            elif arg_name in arg_names:
                idx = arg_names.index(arg_name)
                args[idx] = _process_chunks(
                    args[idx],
                    lambda chunk: func(
                        *args[:idx] + [chunk] + args[idx + 1 :], **kwargs
                    ),
                )

        return func(*args, **kwargs)

    return wrapper
