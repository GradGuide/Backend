from fastapi import FastAPI, HTTPException
from typing import List, Tuple
from .summary import Summary
from .similarity import Similarity

app = FastAPI()

summary = Summary()
similarity = Similarity()


@app.post("/summary/bart", response_model=List[str])
async def summarize_text(text: str, min_length: int = 5, max_length: int = 20):
    """
    Endpoint to summarize text using BART.
    - text: The text to be summarized.
    - min_length: Minimum length of the summary.
    - max_length: Maximum length of the summary.
    """
    try:
        return summary.bart_summarize(text, min_length, max_length)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/summary/extract_keywords", response_model=List[Tuple[str, int]])
async def extract_keywords(text: str, num_keywords: int = 10):
    """
    Endpoint to extract keywords from text using spaCy.
    - text: The input text.
    - num_keywords: Number of keywords to extract.
    """
    try:
        return summary.spacy_extract_keywords(text, num_keywords)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Similarity routes
@app.post("/similarity/bert", response_model=float)
async def compute_bert_similarity(sentences: List[str]):
    """
    Endpoint to compute similarity between two sentences using BERT.
    - sentences: List containing two sentences.
    """
    if len(sentences) != 2:
        raise HTTPException(
            status_code=400, detail="Please provide exactly two sentences."
        )

    try:
        return similarity.bert_similarity(sentences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similarity/sbert", response_model=List[List[float]])
async def compute_sbert_similarity(paragraphs: List[str]):
    """
    Endpoint to compute similarity for multiple paragraphs using SBERT.
    - paragraphs: List of paragraphs.
    """
    try:
        return similarity.sbert_similarity(paragraphs)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/similarity/tfidf", response_model=List[List[float]])
async def compute_tfidf_similarity(sentences: List[str]):
    """
    Endpoint to compute similarity using TF-IDF. (cosine similarity)
    - sentences: List of sentences.
    """
    try:
        return similarity.tfidf_cosine_similarity(sentences)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
