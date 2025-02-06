from typing import List
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer
import torch
import warnings

warnings.filterwarnings("ignore")


class Similarity:
    def __init__(self):
        self.bert_tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")
        self.bert_model = BertModel.from_pretrained("bert-base-uncased")

        self.sbert_model_name = "all-mpnet-base-v2"
        self.sbert_model = SentenceTransformer(self.sbert_model_name)

    def _tokenize_sentences(self, sentences: List[str]):
        tokens = self.bert_tokenizer(
            sentences,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=512,
        )
        return tokens["input_ids"], tokens["attention_mask"]

    def bert_similarity(self, sentences: List[str]) -> float:
        """
        Compute similarity using BERT embeddings for two sentences.
        """
        input_ids, attention_mask = self._tokenize_sentences(sentences)

        with torch.no_grad():
            outputs = self.bert_model(input_ids, attention_mask=attention_mask)
            sentence_embeddings = outputs.last_hidden_state[:, 0, :].numpy()

        similarity = cosine_similarity([sentence_embeddings[0], sentence_embeddings[1]])
        return similarity[0][1]

    def sbert_similarity(self, paragraphs: List[str]) -> List[List[float]]:
        """
        Compute similarity using SBERT embeddings for multiple paragraphs.
        """
        embeddings = self.sbert_model.encode(paragraphs)
        similarities = cosine_similarity(embeddings)
        return similarities

    def tfidf_cosine_similarity(self, sentences: List[str]) -> List[List[float]]:
        """
        Compute similarity using TF-IDF vectorization and cosine similarity for multiple sentences.
        """
        vectorizer = TfidfVectorizer().fit_transform(sentences)
        vectors = vectorizer.toarray()
        cosine_sim = cosine_similarity(vectors)
        return cosine_sim
