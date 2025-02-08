

import PyPDF2
from arrow import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


from .serializers import  UserSerializer
from .models import   User
from django.core.mail import send_mail
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.authtoken.models import Token
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.db.utils import IntegrityError
from django.db import transaction

class RegisterView(APIView):
    permission_classes = ()

    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            # تحقق من وجود البريد الإلكتروني مسبقًا
            if User.objects.filter(email=email).exists():
                return Response({"email": ["This email is already registered."]}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # استخدام المعاملة
                with transaction.atomic():
                    user = serializer.save()
                    
                    # إنشاء رمز التحقق
                    # verification_code = ''.join(random.choices(string.digits, k=6))
                    # user.verification_code = verification_code
                    user.save()

                    # إرسال البريد الإلكتروني
                    # send_mail(
                    #     'Verification Code',
                    #     f'Your verification code is: {verification_code}',
                    #     settings.DEFAULT_FROM_EMAIL,
                    #     [user.email],
                    #     fail_silently=False,
                    # )


                return Response({
                    
                    "message": "User created successfully.",
                }, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response({"detail": "An error occurred during registration. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.tokens import RefreshToken

class User_account_View(APIView):
    # authentication_classes = [JWTAuthentication]
    permission_classes = ()

    def put(self, request):
        try:
            user = request.user
            
            serializer = UserSerializer(user, data=request.data, partial=True)  
            if serializer.is_valid():
                if any(serializer.validated_data[key] != getattr(user, key) for key in serializer.validated_data):
                    serializer.save()
                    return Response({
                        "detail": "Updated successfully",  
                        "data": serializer.data
                    }, status=status.HTTP_200_OK)
                return Response({"detail": "No changes detected"}, status=status.HTTP_400_BAD_REQUEST)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        # verification_code = request.data.get('verification_code')
        
        user = User.objects.filter(email=email).first()
        
        if user is None or not user.check_password(password):
            return Response({"detail": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
        user.save()

        # if verification_code:
        #     if user.verification_code != verification_code:
        #         return Response({"detail": "Invalid verification code"}, status=status.HTTP_400_BAD_REQUEST)
        #     user.is_verified = True
        #     user.verification_code = '' 
        #     user.save()
        # else:
        #     user.verification_code = ''.join(random.choices(string.digits, k=6))
          

            # send_mail(
            #     'Login Verification Code',
            #     f'Your login verification code is: {user.verification_code}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            # )

            # return Response({"detail": "Verification code sent. Please enter the code to complete login."}, status=status.HTTP_400_BAD_REQUEST)

        # refresh = RefreshToken.for_user(user)
        return Response({
            # "access": str(refresh.access_token),
            # "refresh": str(refresh),
            "detail": "Login successful"
        }, status=status.HTTP_200_OK)

    def delete(self, request):
        try:
            user = request.user
            
            user.delete()
            return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except AuthenticationFailed as e:
            return Response({"detail": str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        
        



####################################### summary 
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import Summarization  # Model for storing summaries
# from .summary import Summary  # AI summarization logic
# import os
# from io import BytesIO
# from xhtml2pdf import pisa

# class SummarizeTextView(APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         """
#         Summarize the text, generate a well-formatted PDF, and return the PDF link.
#         """
#         text = request.data.get("text", "")
#         min_length = request.data.get("min_length", 10)
#         max_length = request.data.get("max_length", 500)

#         if not text:
#             return Response({"error": "No text provided."}, status=400)

#         # Check if summary already exists
#         summarization, created = Summarization.objects.get_or_create(
#             user=request.user, text=text
#         )

#         if not created:
#             # If summary already exists, return it
#             return Response(
#                 {
#                     "summarized_text": summarization.summarized_text,
#                     "summarization_id": summarization.id,
#                     "pdf_url": summarization.pdf_url,  # Return PDF link
#                 },
#                 status=200,
#             )

#         # AI Summarization
#         summary = Summary()
#         summarized_result = summary.bart_summarize(
#             text, min_length=min_length, max_length=max_length
#         )
#         summarized_text = summarized_result.get("summary_text", "").strip()

#         if not summarized_text:
#             return Response(
#                 {"error": "Summarization failed or returned empty result."}, status=400
#             )

#         summarization.summarized_text = summarized_text
#         summarization.save()

#         # Generate a well-formatted PDF
#         file_name = f"summaries/pdf/{summarization.id}.pdf"
#         pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
#         pdf_url = os.path.join(settings.MEDIA_URL, file_name)

#         # HTML Template for PDF
#         html_content = render_to_string(
#             "summary_template.html", {"summarized_text": summarized_text}
#         )

#         # Convert HTML to PDF
#         result = BytesIO()
#         pdf = pisa.CreatePDF(BytesIO(html_content.encode("UTF-8")), dest=result)

#         if not pdf.err:
#             with open(pdf_path, "wb") as f:
#                 f.write(result.getvalue())

#             summarization.pdf_url = pdf_url
#             summarization.save()

#             return Response(
#                 {
#                     "summarized_text": summarized_text,
#                     "summarization_id": summarization.id,
#                     "pdf_url": pdf_url,
#                 },
#                 status=200,
#             )

#         return Response({"error": "Failed to generate PDF."}, status=500)








#################################################  Similarity
from rest_framework.permissions import IsAuthenticated

import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse
from .models import SimilarityResult
from .similarity import Similarity, find_common_text
from googleapiclient.discovery import build

class SimilarityCheckView(APIView):
    permission_classes = ()


    def extract_text_from_pdf(self, pdf_file):
        """استخراج النصوص من ملف PDF"""
        text = ""
        try:
            doc = fitz.open(pdf_file)
            for page in doc:
                text += page.get_text()
            return text
        except Exception as e:
            return str(e)

    def google_custom_search(self, query):
        """استخدام Google Custom Search API للبحث عن النصوص المشابهة"""
        api_key = "AIzaSyBD8hBPLxe-yObszFAPnGm0xmmZ9D5F5E4"  # استبدلها بـ API Key الخاص بك
        cse_id = "d08c6adb37f3d4c32"  # استبدلها بـ Custom Search Engine ID الخاص بك

        # التحقق من أن النص صالح للبحث
        if not query or len(query.strip()) == 0:
            return []

        # بناء الطلب باستخدام Google API Client
        try:
            service = build("customsearch", "v1", developerKey=api_key)
            res = service.cse().list(q=query, cx=cse_id).execute()

            results = []
            if "items" in res:
                for item in res["items"]:
                    title = item["title"]
                    snippet = item["snippet"]
                    link = item["link"]
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": link
                    })

            return results if results else None  # إرجاع None إذا لم تكن هناك نتائج
        except Exception as e:
            print(f"Error in Google Custom Search API: {e}")
            return None

    def extract_paragraphs_from_url(self, url):
        """استخراج الفقرات من رابط"""
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # استخراج الفقرات من العناصر <p>
            paragraphs = soup.find_all('p')
            text = ' '.join([para.get_text() for para in paragraphs])
            return text
        except Exception as e:
            print(f"Error extracting paragraphs: {e}")
            return ""

    def post(self, request, *args, **kwargs):
        """استقبال النصوص أو ملفات PDF، البحث في الإنترنت عند الحاجة، وحساب التشابه"""
        text1 = request.data.get("text1", None)
        text2 = request.data.get("text2", None)
        pdf1 = request.data.get("file1", None)
        pdf2 = request.data.get("file2", None)

        # استخراج النصوص من PDF إذا تم إرسال ملفات
        if pdf1:
            text1 = self.extract_text_from_pdf(pdf1)
        if pdf2:
            text2 = self.extract_text_from_pdf(pdf2)

        # التحقق من أن هناك على الأقل إدخالًا واحدًا صحيحًا
        if not text1:
            return JsonResponse({"error": "يرجى إرسال نص أو ملف PDF صالح للمقارنة"}, status=400)

        similarity_checker = Similarity()
        results = []

        if text1 and text2:
            # مقارنة بين ملفين PDF أو بين نص و PDF
            similarity_score = similarity_checker.bert_similarity([text1, text2])[0][1] * 100
            common_data = find_common_text(text1, text2)

            results.append({
                "title": "مقارنة بين المدخلين",
                "url": "N/A",
                "similarity_score": f"{similarity_score:.2f}%",
                "common_words": common_data["common_words"],
                "common_sentences": common_data["common_sentences"],
                "common_paragraphs": common_data["common_paragraphs"]
            })

        else:
            # إذا كان هناك إدخال واحد فقط (PDF أو نص)، يتم البحث عن مقالات مشابهة من الإنترنت
            search_results = self.google_custom_search(text1)

            if not search_results:  # التحقق من أن النتائج ليست None أو فارغة
                return JsonResponse({"error": "لم يتم العثور على نتائج مشابهة"}, status=404)

            for result in search_results:
                # استخراج النص الكامل من الرابط
                compared_text = self.extract_paragraphs_from_url(result["url"])
                similarity_score = similarity_checker.tfidf_cosine_similarity([text1, compared_text])[0][1] * 100
                common_data = find_common_text(text1, compared_text)

                results.append({
                    "title": result["title"],
                    "url": result["url"],
                    "similarity_score": f"{similarity_score:.2f}%",
                    "common_words": common_data["common_words"],
                    "common_sentences": common_data["common_sentences"],
                    "common_paragraphs": common_data["common_paragraphs"]
                })

        # حفظ جميع النتائج في قاعدة البيانات
        for result in results:
            SimilarityResult.objects.create(
                user=request.user,
                input_text=text1,
                compared_text=result["title"],
                similarity_score=float(result["similarity_score"].replace("%", "")),
                common_words=", ".join(result["common_words"]),
                common_sentences="\n".join(result["common_sentences"]),
                common_paragraphs="\n".join(result["common_paragraphs"]),
                created_at=now()
            )

        return JsonResponse({"results": results}, safe=False)




##################################Grammer correction 

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .llm import LLM
import os

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("مفتاح API غير موجود في البيئة")

llm = LLM(api_key=api_key)

class GrammarCorrectionAPIView(APIView):
    permission_classes = ()

    def post(self, request):
        text = request.data.get("text", "")

        # التأكد من وجود النص في البيانات
        if not text:
            return Response({"error": "يجب إدخال النص"}, status=status.HTTP_400_BAD_REQUEST)

        # تهيئة الكلاس LLM مع المفتاح الكامل من البيئة
        api_key = os.getenv("GEMINI_API_KEY")  # استخدام المفتاح من ملف .env
        if not api_key:
            return Response({"error": "مفتاح API غير موجود في البيئة"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        llm = LLM(api_key=api_key)  # تمرير المفتاح للـ LLM

        # استخدام الكلاس للحصول على الإجابة
        try:
            corrected_text = llm.grammar_corrector(text)  # تصحيح النص

            return Response({"corrected_text": corrected_text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"حدث خطأ: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

#####################################QNA
from .qna import QnA


class QnAView(APIView):
    permission_classes = ()

    """
    API View to handle question answering.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.qna_service = QnA()  # Initialize the QnA class

    def post(self, request, *args, **kwargs):
        """
        Handle POST requests to process question-answering.
        """
        question = request.data.get("question", "")
        context = request.data.get("context", "")

        # Validate the inputs
        if not question or not context:
            return Response(
                {"error": "Both 'question' and 'context' fields are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Process the question-answering
            result = self.qna_service.simple_question(question, context)

            return Response(result, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
############################################################# summary
# from rest_framework.permissions import AllowAny
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from django.template.loader import render_to_string
# from django.conf import settings
# from .models import Summarization  # Model for storing summaries
# from .llm import LLM  # AI summarization logic using LLM API
# import os
# from io import BytesIO
# from weasyprint import HTML
# from langdetect import detect
# import fitz  # مكتبة PyMuPDF لاستخراج النص من PDF

# class SummarizeTextView(APIView):
#     permission_classes = [AllowAny]  # يمكنك تغييرها لاحقًا إلى [IsAuthenticated]

#     def extract_text_from_pdf(self, pdf_file):
#         """استخراج النص من ملف PDF"""
#         text = ""
#         with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
#             for page in doc:
#                 text += page.get_text("text") + "\n"
#         return text.strip()

#     def post(self, request):
#         """
#         تلخيص النص سواء كان نصًا مكتوبًا أو مستخرجًا من ملف PDF.
#         """
#         text = request.data.get("text", "")
#         pdf_file = request.FILES.get("file")  # استلام ملف PDF إذا كان مرفوعًا

#         if pdf_file:
#             text = self.extract_text_from_pdf(pdf_file)
        
#         if not text:
#             return Response({"error": "لم يتم توفير نص أو PDF صالح."}, status=400)

#         # استدعاء API Key من المتغيرات البيئية
#         api_key = os.getenv("GEMINI_API_KEY")
#         if not api_key:
#             raise ValueError("مفتاح API غير موجود في البيئة")

#         llm = LLM(api_key=api_key)  # تمرير API Key إلى LLM

#         # تحديد لغة النص
#         detected_language = detect(text)
#         language = "Arabic" if detected_language == "ar" else "French" if detected_language == "fr" else "English"

#         # تحقق مما إذا كان الملخص موجودًا بالفعل
#         summarization, created = Summarization.objects.get_or_create(
#             user=request.user if request.user.is_authenticated else None,
#             original_text=text
#         )

#         if not created:
#             return Response(
#                 {
#                     "summary_text": summarization.summary_text,
#                     "summarization_id": summarization.id,
#                     "pdf_url": summarization.pdf_file.url if summarization.pdf_file else None,
#                 },
#                 status=200,
#             )

#         # تلخيص النص باستخدام LLM مع اللغة المكتشفة
#         summarized_text = llm.summarize(text, language=language).strip()
        
#         if not summarized_text:
#             return Response({"error": "فشل التلخيص أو النتيجة فارغة."}, status=400)

#         summarization.summary_text = summarized_text
#         summarization.save()

#         # إنشاء PDF من النص الملخص
#         file_name = f"summaries/pdf/{summarization.id}.pdf"
#         pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
#         pdf_url = os.path.join(settings.MEDIA_URL, file_name)
        
#         # تحميل قالب HTML وإنشاء PDF
#         html_content = render_to_string(
#             "summary_template.html", {"summarized_text": summarized_text}
#         )

#         # إنشاء PDF باستخدام WeasyPrint
#         pdf_file = HTML(string=html_content).write_pdf()

#         # حفظ الـ PDF في الملف
#         with open(pdf_path, "wb") as f:
#             f.write(pdf_file)
        
#         summarization.pdf_file = file_name  # حفظ رابط الـ PDF
#         summarization.save()
        
#         return Response(
#             {
#                 "summary_text": summarized_text,
#                 "summarization_id": summarization.id,
#                 "pdf_url": pdf_url,
#             },
#             status=200,
#         )

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from django.template.loader import render_to_string
from django.conf import settings
from .models import Summarization
from .llm import LLM
import os
from io import BytesIO
from weasyprint import HTML
from langdetect import detect
import fitz  # PyMuPDF لاستخراج النص من PDF

class SummarizeTextView(APIView):
    permission_classes = [AllowAny]

    def extract_text_from_pdf(self, pdf_file):
        """استخراج النص من ملف PDF"""
        text = ""
        try:
            with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
            raise ValueError(f"فشل في استخراج النص من PDF: {str(e)}")
        return text.strip()

    def post(self, request):
        """
        تلخيص النص سواء كان نصًا مكتوبًا أو مستخرجًا من ملف PDF.
        """
        text = request.data.get("text", "")
        pdf_file = request.FILES.get("file")

        if pdf_file:
            try:
                text = self.extract_text_from_pdf(pdf_file)
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        if not text:
            return Response({"error": "لم يتم توفير نص أو PDF صالح."}, status=400)

        # استدعاء API Key من المتغيرات البيئية
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return Response({"error": "مفتاح API غير موجود في البيئة"}, status=500)

        llm = LLM(api_key=api_key)

        # تحديد لغة النص
        detected_language = detect(text)
        language = "Arabic" if detected_language == "ar" else "French" if detected_language == "fr" else "English"

        # تحقق مما إذا كان الملخص موجودًا بالفعل
        summarization, created = Summarization.objects.get_or_create(
            user=request.user if request.user.is_authenticated else None,
            original_text=text
        )

        if not created:
            return Response(
                {
                    "summary_text": summarization.summary_text,
                    "summarization_id": summarization.id,
                    "pdf_url": summarization.pdf_file.url if summarization.pdf_file else None,
                },
                status=200,
            )

        # تلخيص النص باستخدام LLM مع اللغة المكتشفة
        summarized_text = llm.summarize(text, language=language).strip()
        
        if not summarized_text:
            return Response({"error": "فشل التلخيص أو النتيجة فارغة."}, status=400)

        summarization.summary_text = summarized_text
        summarization.save()

        # إنشاء PDF من النص الملخص
        file_name = f"summaries/pdf/{summarization.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
        pdf_url = os.path.join(settings.MEDIA_URL, file_name)

        # تحميل قالب HTML وإنشاء PDF
        html_content = render_to_string(
            "summary_template.html", {"summarized_text": summarized_text}
        )

        try:
            pdf_file = HTML(string=html_content).write_pdf()
        except Exception as e:
            return Response({"error": f"فشل في إنشاء PDF: {str(e)}"}, status=500)

        # حفظ الـ PDF في الملف
        with open(pdf_path, "wb") as f:
            f.write(pdf_file)

        summarization.pdf_file = file_name
        summarization.save()

        return Response(
            {
                "summary_text": summarized_text,
                "summarization_id": summarization.id,
                "pdf_url": pdf_url,
            },
            status=200,
        )        ##################################################################