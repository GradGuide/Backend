import requests
import json
from markitdown import MarkItDown
import io

def fetch_search_results(url, query):
    """Send a GET request to the search API and return the response data."""
    response = requests.get(url, params={"q": query, "format": "json"})
    return response.json()

def extract_relevant_fields(data):
    """Extract all titles and URLs from the API response."""
    return {
        "results": {
            result["title"]: result["url"]
            for result in data.get("results", [])
        }
    }

def extract_text_from_urls(urls):
    """Extract text content from a list of URLs using MarkItDown."""
    md = MarkItDown()
    extracted_texts = {}
    for url in urls:
        text = bytes(requests.get(url).text, 'utf-8')
        extracted = md.convert_stream(io.BytesIO(text))
        extracted_texts[url] = extracted.text_content
    return extracted_texts