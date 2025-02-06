import requests
from bs4 import BeautifulSoup
from googlesearch import search
from .similarity import Similarity

class WebScraper:
    def __init__(self):
        self.similarity_model = Similarity()

    def get_scholar_results(self, query, num_results=10):
        """جلب نتائج من Google Scholar"""
        search_url = f"https://scholar.google.com/scholar?q={query}"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            response = requests.get(search_url, headers=headers)
            if response.status_code != 200:
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            results = []
            for entry in soup.select(".gs_r")[:num_results]:
                title_tag = entry.select_one(".gs_rt a")
                snippet_tag = entry.select_one(".gs_rs")
                
                title = title_tag.text if title_tag else "عنوان غير متوفر"
                snippet = snippet_tag.text if snippet_tag else "ملخص غير متوفر"
                link = title_tag["href"] if title_tag else "#"

                results.append({"title": title, "snippet": snippet, "link": link})

            return results

        except Exception as e:
            return []

    def search_and_compare(self, text):
        """البحث عن نص عبر Google Scholar ومقارنته بالمحتوى الموجود في المواقع"""
        results = self.get_scholar_results(text, num_results=10)

        if not results:
            return [{"title": "لم يتم العثور على نتائج", "snippet": "لا يوجد محتوى مشابه", "link": "#", "similarity_percentage": 0.0}]

        for result in results:
            similarity_score = self.similarity_model.bert_similarity([text, result["snippet"]])
            similarity_percentage = similarity_score[0][1] * 100 if len(similarity_score[0]) > 1 else 0
            result["similarity_percentage"] = round(similarity_percentage, 2)

        results.sort(key=lambda x: x["similarity_percentage"], reverse=True)  # ترتيب النتائج حسب نسبة التشابه
        return results
