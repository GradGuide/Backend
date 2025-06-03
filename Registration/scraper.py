from curl_cffi import AsyncSession
from markitdown import MarkItDown
import curl_cffi 
import asyncio
import json
import io

def fetch_search_results(url, query):
    """Send a GET request to the search API and return the response data."""
    response = curl_cffi.get(url, params={"q": query, "format": "json"})
    return response.json()

def extract_relevant_fields(data):
    """Extract all titles and URLs from the API response."""
    return {
        "results": {
            result["title"]: result["url"]
            for result in data.get("results", [])
        }
    }

async def extract_text_from_urls(urls):
    """Asynchronously extract text content from a list of URLs"""
    md = MarkItDown()
    extracted_texts = {}

    async with AsyncSession() as session:
        tasks = []
        for url in urls:
            tasks.append(session.get(url, impersonate="chrome"))

        responses = await asyncio.gather(*tasks)

        for response in responses:
            text = bytes(response.text, 'utf-8')
            extracted = md.convert_stream(io.BytesIO(text))
            extracted_texts[response.url] = extracted.text_content

    return extracted_texts