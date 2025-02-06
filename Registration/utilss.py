import PyPDF2
import requests
from bs4 import BeautifulSoup

def pdf_to_text(pdf_file):
    """تحويل ملف PDF إلى نص"""
    text = ""
    with pdf_file.open("rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() + "\n"
    return text.strip()

def perform_web_scraping(query):
    """تنفيذ Web Scraping لجلب نصوص من الإنترنت بناءً على الاستعلام"""
    search_url = f"https://scholar.google.com/scholar?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}
    
    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for result in soup.select(".gs_ri"):
        title = result.select_one(".gs_rt").text
        abstract = result.select_one(".gs_rs").text if result.select_one(".gs_rs") else ""
        link = result.select_one(".gs_rt a")["href"] if result.select_one(".gs_rt a") else "#"

        results.append(f"{title}. {abstract}. More at: {link}")

    return results[:10]  # إرجاع 10 نتائج فقط
