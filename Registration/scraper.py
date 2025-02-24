import requests
from bs4 import BeautifulSoup
import re

def fetch_search_results(url, query):
    """إرسال طلب GET لاسترجاع أول 3 نتائج بحث بصيغة JSON."""
    try:
        response = requests.get(url, params={"q": query, "format": "json"}, timeout=10)
        response.raise_for_status()
        data = response.json().get("results", [])
        return [{"title": item.get("title", "عنوان غير متوفر"), "url": item.get("url", "")} for item in data[:3]]
    except requests.exceptions.RequestException as e:
        print(f"❌ خطأ أثناء جلب نتائج البحث: {e}")
        return []

def highlight_match(paragraph, query):
    """تلوين الكلمات المتشابهة بين الفقرة ونص البحث باللون الأحمر."""
    words = query.split()
    pattern = re.compile(r'\b(' + '|'.join(re.escape(word) for word in words) + r')\b', re.IGNORECASE)
    highlighted = pattern.sub(r'\033[91m\1\033[0m', paragraph)
    return highlighted

def extract_matching_paragraph(url, query):
    """جلب الفقرة الأكثر تشابهًا مع نص البحث من صفحة الويب."""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        paragraphs = soup.find_all("p")

        best_paragraph = None
        max_matches = 0

        for p in paragraphs:
            text = p.get_text(strip=True)
            matches = sum(1 for word in query.split() if word.lower() in text.lower())

            if matches > max_matches:
                max_matches = matches
                best_paragraph = text
        
        if best_paragraph:
            return highlight_match(best_paragraph, query)
        return "❌ لم يتم العثور على فقرة متطابقة"
    
    except requests.exceptions.RequestException as e:
        print(f"⚠️ خطأ أثناء جلب البيانات من {url}: {e}")
        return "❌ تعذر جلب المحتوى"
