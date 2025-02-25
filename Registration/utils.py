from nltk.tokenize import sent_tokenize, word_tokenize


def smart_split(text, n):
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks = []
    current_chunk = []
    current_length = 0

    for paragraph in paragraphs:
        sentences = sent_tokenize(paragraph)
        for sentence in sentences:
            sentence_length = len(word_tokenize(sentence))

            if current_length + sentence_length <= n:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
