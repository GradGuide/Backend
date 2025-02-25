

from datetime import timezone
import datetime
import PyPDF2
from arrow import now
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from .similarity import Similarity, find_common_text
from .models import SimilarityResult
from datetime import datetime
# from .scraper import fetch_search_results, extract_relevant_fields, extract_text_from_urls
from .serializers import  UserSerializer
from .models import   Answer, Question, QnA,SimilarityResult, User
from django.core.mail import send_mail
# from rest_framework.authentication import TokenAuthentication
# from rest_framework.authtoken.models import Token
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
# from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import AuthenticationFailed
from django.db.utils import IntegrityError
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .llm import LLM
from .grammar import GrammarCorrector
import os
import fitz 
from io import BytesIO 
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from PyPDF2 import PdfReader
from .models import QnA
from .serializers import QnASerializer
from .qna import QnA as QnAEngine
qna_engine = QnAEngine()
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
import fitz  

class RegisterView(APIView):
    permission_classes = ()

    # authentication_classes = [TokenAuthentication]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            if User.objects.filter(email=email).exists():
                return Response({"email": ["This email is already registered."]}, status=status.HTTP_400_BAD_REQUEST)

            try:
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
# from rest_framework_simplejwt.tokens import RefreshToken

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
        
######################################################################################

# class SimilarityCheckView(APIView):
#     permission_classes = ()

#     def extract_text_from_pdf(self, pdf_file):
#         """استخراج النص من ملف PDF"""
#         from PyPDF2 import PdfReader
#         pdf_reader = PdfReader(pdf_file)
#         text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])
#         return text.strip() if text else None

#     def post(self, request, *args, **kwargs):
#         """استقبال النصوص أو ملفات PDF وحساب التشابه"""
#         text1 = request.data.get("text1", None)
#         text2 = request.data.get("text2", None)
#         pdf1 = request.data.get("file1", None)
#         pdf2 = request.data.get("file2", None)

#         if pdf1:
#             text1 = self.extract_text_from_pdf(pdf1)
#         if pdf2:
#             text2 = self.extract_text_from_pdf(pdf2)

#         if not text1:
#             return JsonResponse({"error": "يرجى إرسال نص أو ملف PDF صالح للمقارنة"}, status=400)

#         similarity_checker = Similarity()
#         results = []

#         if text1 and text2:
#             sbert_similarity_score = similarity_checker.sbert_similarity([text1, text2])[0][0] * 100
#             tfidf_similarity_score = similarity_checker.tfidf_cosine_similarity([text1, text2])[0][0] * 100

#             common_data = find_common_text(text1, text2)

#             results.append({
#                 "title": "مقارنة بين المدخلين",
#                 "tfidf": f"{sbert_similarity_score:.2f}",
#                 "sbert": f"{tfidf_similarity_score:.2f}",
#                 "common_words": common_data["common_words"],
#                 "common_sentences": common_data["common_sentences"],
#                 "common_paragraphs": common_data["common_paragraphs"]
#             })

#             if request.user.is_authenticated:
#                 SimilarityResult.objects.create(
#                     user=request.user,
#                     input_text=text1,
#                     compared_text=text2,
#                     similarity_score=max(sbert_similarity_score, tfidf_similarity_score),
#                     common_words=", ".join(common_data["common_words"]),
#                     common_sentences="\n".join(common_data["common_sentences"]),
#                     common_paragraphs="\n".join(common_data["common_paragraphs"]),
#                     created_at=datetime.now()
#                 )

#         else:
#             text = request.data.get("text", None)

       



#             search_url = "http://localhost:8080/search" 
#             search_results = fetch_search_results(search_url, text)
#             extracted_data = extract_relevant_fields(search_results)

#             if not extracted_data["results"]:
#                 return JsonResponse({"error": "لم يتم العثور على نتائج مشابهة"}, status=404)

#             extracted_texts = extract_text_from_urls(extracted_data["results"].values()[0])

#             for title, url in extracted_data["results"].items():
#                 print(f"{extracted_texts=}")
#                 article_text = extracted_texts.get(url, "")

#                 sbert_similarity_score = similarity_checker.sbert_similarity([text1, article_text])[0][1] 
                
#                 tfidf_similarity_score = similarity_checker.tfidf_cosine_similarity([text1, article_text])[0][1] 

#                 results.append({
#                     "title": title,
#                     "url": url,
#                     "sbert_similarity": f"{sbert_similarity_score:.2f}",
#                     "tfidf_cosine_similarity": f"{tfidf_similarity_score:.2f}"
#                 })

#             results.sort(key=lambda x: max(float(x["sbert_similarity"].replace('%', '')), float(x["tfidf_cosine_similarity"].replace('%', ''))), reverse=True)

#         return JsonResponse({"results": results}, safe=False)







# class WebSimilarityCheckView(APIView):
#     permission_classes = ()

#     def post(self, request, *args, **kwargs):
#         """ استقبال نص والبحث عن محتوى مشابه على الإنترنت """
#         text = request.data.get("text", None)
#         if not text:
#             return JsonResponse({"error": "يرجى إرسال نص صالح للمقارنة"}, status=400)

#         search_results = fetch_search_results("http://localhost:8080/search", text)
#         extracted_data = extract_relevant_fields(search_results)
#         urls = list(extracted_data["results"].values())

#         extracted_texts = extract_text_from_urls(urls[:3])
#         similarity_checker = Similarity()
#         results = []

#         for url, extracted_text in extracted_texts.items():
#             if extracted_text:
#                 sbert_similarity_score = similarity_checker.sbert_similarity([text, extracted_text])[0][0] * 100
#                 tfidf_similarity_score = similarity_checker.tfidf_cosine_similarity([text, extracted_text])[0][0] * 100
#                 common_data = find_common_text(text, extracted_text)
                
#                 results.append({
#                     "title": extracted_data["results"].get(url, "عنوان غير متوفر"),
#                     "url": url,
#                     "tfidf": f"{tfidf_similarity_score:.2f}",
#                     "sbert": f"{sbert_similarity_score:.2f}",
#                     "common_words": common_data["common_words"],
#                     "common_sentences": common_data["common_sentences"],
#                     "common_paragraphs": common_data["common_paragraphs"]
#                 })
        
#         return JsonResponse({"results": results}, status=200)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import PyPDF2
from .models import SimilarityResult
from .serializers import SimilarityResultSerializer
from .similarity import Similarity, find_common_text
from .scraper import fetch_search_results, extract_matching_paragraph

class SimilarityCheckViews(APIView):
    permission_classes = ()

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        text1 = request.data.get("text1", "")
        text2 = request.data.get("text2", "")
        file1 = request.FILES.get("file1", None)
        file2 = request.FILES.get("file2", None)

        def extract_text_from_pdf(uploaded_file):
            """استخراج النص من ملف PDF إذا تم رفعه"""
            file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            with default_storage.open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

        # ✅ استخراج نص من الملفين (إن وجد)
        if file1:
            text1 = extract_text_from_pdf(file1)
        if file2:
            text2 = extract_text_from_pdf(file2)

        # ✅ التأكد من وجود نص لتحليل التشابه
        if not text1 and not text2:
            return Response({"error": "لا يوجد نص لتحليل التشابه"}, status=status.HTTP_400_BAD_REQUEST)

        similarity = Similarity()
        similarity_results = []

        # ✅ إذا كان هناك **نصين**، نحسب التشابه بينهم مباشرة
        if text1 and text2:
            sbert_score = similarity.sbert_similarity([text1, text2])[0][1] * 100
            tfidf_score = similarity.tfidf_cosine_similarity([text1, text2])[0][1] * 100
            common_data = find_common_text(text1, text2)
            
            # ✅ حفظ النتيجة في قاعدة البيانات
            similarity_result = SimilarityResult.objects.create(
                user=user,
                input_text=text1,
                compared_text=text2,
                sbert_similarity=sbert_score,
                tfidf_similarity=tfidf_score,
                common_words=", ".join(common_data["common_words"]),
                common_sentences="\n".join(common_data["common_sentences"]),
                common_paragraphs="\n\n".join(common_data["common_paragraphs"]),
            )
            
            similarity_results.append({
                "title": "مقارنة بين النصين",
                "sbert_similarity": f"{sbert_score:.2f}%",
                "tfidf_similarity": f"{tfidf_score:.2f}%",
                "common_words": similarity_result.common_words,
                "common_sentences": similarity_result.common_sentences,
                "common_paragraphs": similarity_result.common_paragraphs,
            })

        # ✅ إذا كان هناك **نص واحد فقط**، نستخدم Web Scraping
        else:
            search_text = text1 if text1 else text2  # نحدد أي النصوص موجودة
            search_results = fetch_search_results("http://localhost:8080/search", search_text)

            if not search_results:
                return Response({"error": "لم يتم العثور على نتائج"}, status=status.HTTP_404_NOT_FOUND)

            for result in search_results:
                compared_text = extract_matching_paragraph(result["url"], search_text)
                sbert_score = similarity.sbert_similarity([search_text, compared_text])[0][0] * 100
                tfidf_score = similarity.tfidf_cosine_similarity([search_text, compared_text])[0][0] * 100
                
                common_data = find_common_text(search_text, compared_text)

                similarity_results.append({
                    "title": result["title"],
                    "url": result["url"],
                    "sbert_similarity": f"{sbert_score:.2f}%",  
                    "tfidf_similarity": f"{tfidf_score:.2f}%",
                    "common_words": ", ".join(common_data["common_words"]),
                    "common_sentences": "\n".join(common_data["common_sentences"]),
                    "common_paragraphs": "\n\n".join(common_data["common_paragraphs"]),
                })

        return Response(similarity_results, status=status.HTTP_200_OK)



##################################Grammer correction 
from .models import GrammarCorrectionHistory
from .serializers import GrammarCorrectionHistorySerializer
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("مفتاح API غير موجود في البيئة")

llm = LLM(api_key=api_key)
gc = GrammarCorrector()

class GrammarCorrectionAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        # إذا كان المستخدم مسجل دخول، جلب سجلاته فقط، وإلا جلب السجلات العامة
        if request.user.is_authenticated:
            histories = GrammarCorrectionHistory.objects.filter(user=request.user)
        else:
            histories = GrammarCorrectionHistory.objects.filter(user=None)

        serializer = GrammarCorrectionHistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def extract_text_from_pdf(self, pdf_file):
        """استخراج النص من ملف PDF المحمّل"""
        text = ""
        try:
            pdf_bytes = BytesIO(pdf_file.read()) 
            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
            raise ValueError(f"An error occurred while extracting text from PDF.: {str(e)}")
        return text.strip()

    def post(self, request):
        text = request.data.get("text", "")
        pdf_file = request.FILES.get("file")

        if not text and not pdf_file:
            return Response({"error": "You must enter text or upload a PDF file."}, status=status.HTTP_400_BAD_REQUEST)

        if pdf_file:
            try:
                text = self.extract_text_from_pdf(pdf_file)
                if not text:
                    return Response({"error": "No text extracted from PDF file"}, status=status.HTTP_400_BAD_REQUEST)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            if len(text.split(' ')) > 20:
               corrected_text = gc.correct(text)  
            else:
                corrected_text = llm.grammar_corrector(text) 
 
            GrammarCorrectionHistory.objects.create(
                        user=request.user if request.user.is_authenticated else None,
                        input_text=text,
                        corrected_text=corrected_text
                    )
            return Response({"corrected_text": corrected_text}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": f"An error occurred. : {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

####################################################
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader
from .models import QnA, Question, Answer
from django.conf import settings
from .qna import QnA as QnAEngine

qna_engine = QnAEngine()

class GenerateQuestionsView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        num_questions = int(request.data.get("num_questions", 5))
        uploaded_file = request.FILES.get("file")
        text = request.data.get("text", "")

        if uploaded_file:
            pdf_reader = PdfReader(uploaded_file)
            text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        if not text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ إنشاء جلسة جديدة
        session = QnA.objects.create(user=user, text=text)
        questions = qna_engine.generate_questions(text, num_questions)

        created_questions = []
        for question_text in questions:
            question = Question.objects.create(qna_session=session, text=question_text)
            created_questions.append({"id": question.id, "text": question.text})

        return Response({
            "questions": created_questions  # ✅ إرجاع كل سؤال مع الـ ID الخاص به
        }, status=status.HTTP_201_CREATED)



class EvaluateAnswersView(APIView):
    permission_classes = []
    def post(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None

        # ✅ البحث عن أول سؤال لم يتم إجابته في الجلسة
        question = Question.objects.filter(qna_session__user=user).exclude(answers__isnull=False).first()

        if not question:
            return Response({"error": "No active question found"}, status=status.HTTP_400_BAD_REQUEST)

        user_answer = request.data.get("answer", "").strip()
        if not user_answer:
            return Response({"error": "Answer cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        # ✅ تقييم الإجابة
        evaluation = qna_engine.evaluate_answers([question.text], [user_answer], question.qna_session.text)[0]
        _, score, feedback = evaluation

        # ✅ تحديد صحة الإجابة
        is_correct = score > 5

        # ✅ حفظ الإجابة
        Answer.objects.create(
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            score=score,
            feedback=feedback
        )

        # ✅ جلب السؤال التالي في الجلسة
        next_question = Question.objects.filter(qna_session=question.qna_session, id__gt=question.id).first()

        response_data = {
            "question": question.text,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback
        }

        if next_question:
            response_data["next_question"] = next_question.text
        else:
            response_data["message"] = "No more questions in this session"

        return Response(response_data, status=status.HTTP_200_OK)

##################################################3##



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

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return Response({"error": "مفتاح API غير موجود في البيئة"}, status=500)

        llm = LLM(api_key=api_key)

        detected_language = detect(text)
        language = "Arabic" if detected_language == "ar" else "French" if detected_language == "fr" else "English"

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

        summarized_text = llm.summarize(text, language=language).strip()
        
        if not summarized_text:
            return Response({"error": "فشل التلخيص أو النتيجة فارغة."}, status=400)

        summarization.summary_text = summarized_text
        summarization.save()

        file_name = f"summaries/pdf/{summarization.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
        pdf_url = os.path.join(settings.MEDIA_URL, file_name)

        html_content = render_to_string(
            "summary_template.html", {"summarized_text": summarized_text}
        )

        try:
            pdf_file = HTML(string=html_content).write_pdf()
        except Exception as e:
            return Response({"error": f"فشل في إنشاء PDF: {str(e)}"}, status=500)

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
    


    