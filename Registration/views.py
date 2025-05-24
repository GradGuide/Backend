from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import PyPDF2
from .scraper import fetch_search_results, extract_relevant_fields,extract_text_from_urls
import PyPDF2
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from PyPDF2 import PdfReader
from django.conf import settings
from .qna import QnA as QnAEngine
from django.http import JsonResponse
from .similarity import Similarity, find_common_text
from .serializers import  UserSerializer,GrammarCorrectionHistorySerializer
from .models import   Answer, Question, QnA,SimilarityResult,SimilarityResultURL, User,QnA, Question, Answer,Summarization,GrammarCorrectionHistory
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db.utils import IntegrityError
from django.db import transaction
from .grammar import GrammarCorrector
import fitz 
from io import BytesIO 
qna_engine = QnAEngine()
from rest_framework.permissions import AllowAny,IsAuthenticated
from django.template.loader import render_to_string
from django.conf import settings
from .llm import LLM
import os
from weasyprint import HTML
from langdetect import detect
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("API key not found in environment")

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserSerializer(data=request.data)

        if serializer.is_valid():
            email = serializer.validated_data.get('email')

            if User.objects.filter(email=email).exists():
                return Response({"email": ["This email is already registered."]}, status=status.HTTP_400_BAD_REQUEST)
            try:
                with transaction.atomic():
                    user = serializer.save()

                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)

                    return Response({
                        "message": "User created successfully.",
                        "access": access_token,
                        "refresh": refresh_token,
                        "user": UserSerializer(user).data
                    }, status=status.HTTP_201_CREATED)

            except IntegrityError:
                return Response({"detail": "An error occurred during registration. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class User_account_View(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = []  

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

            user = User.objects.filter(email=email).first()

            if user is None or not user.check_password(password):
                return Response({"detail": "Invalid email or password"}, status=status.HTTP_400_BAD_REQUEST)
            user.save()


            refresh = RefreshToken.for_user(user)
            return Response({
                "access": str(refresh.access_token),
                "refresh": str(refresh),
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



class SimilarityCheckViews(APIView):
    permission_classes = [AllowAny]  

    def post(self, request):
        user = request.user if request.user.is_authenticated else None
        text1 = request.data.get("text1", "")
        text2 = request.data.get("text2", "")
        file1 = request.FILES.get("file1", None)
        file2 = request.FILES.get("file2", None)

        def extract_text_from_pdf(uploaded_file):
            """Extract text from a PDF file if uploaded"""
            file_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))
            with default_storage.open(file_path, "rb") as f:
                pdf_reader = PyPDF2.PdfReader(f)
                return " ".join(page.extract_text() for page in pdf_reader.pages if page.extract_text())

        if file1:
            text1 = extract_text_from_pdf(file1)
        if file2:
            text2 = extract_text_from_pdf(file2)

        if not text1 and not text2:
            return Response({"error": "There is no text for similarity analysis."}, status=status.HTTP_400_BAD_REQUEST)

        similarity = Similarity()
        similarity_results = []

        if text1 and text2:
            sbert_score = similarity.sbert_similarity([text1, text2])[0][1] * 100
            tfidf_score = similarity.tfidf_cosine_similarity([text1, text2])[0][1] * 100
            common_data = find_common_text(text1, text2)
            
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
                "title": "Compare the two texts",
                "sbert_similarity": f"{sbert_score:.2f}%",
                "tfidf_similarity": f"{tfidf_score:.2f}%",
                "common_words": similarity_result.common_words,
                "common_sentences": similarity_result.common_sentences,
                "common_paragraphs": similarity_result.common_paragraphs,
            })
            
            return JsonResponse({"results": similarity_results}, status=200)  

        else:
            text = text1 if text1 else text2

            if not text:
                return JsonResponse({"error": "Please send valid text for comparison"}, status=400)

            search_results = fetch_search_results("http://localhost:8080/search", text)
            extracted_data = extract_relevant_fields(search_results)
            urls = list(extracted_data["results"].values())

            extracted_texts = {}
            if urls:
                extracted_texts = extract_text_from_urls(urls[:3])

            if not extracted_texts:
                return JsonResponse({"error": "No valid texts were found for comparison."}, status=400)

            similarity_result = SimilarityResult.objects.create(
                user=user,
                input_text=text,
                compared_text="",  
                sbert_similarity=0.0,
                tfidf_similarity=0.0,
                common_words="",
                common_sentences="",
                common_paragraphs="",
            )

            similarity_checker = Similarity()
            results = []

            for url, extracted_text in extracted_texts.items():
                if extracted_text:
                    sbert_similarity_score = similarity_checker.sbert_similarity([text, extracted_text])[0][0] * 100
                    tfidf_similarity_score = similarity_checker.tfidf_cosine_similarity([text, extracted_text])[0][0] * 100
                    common_data = find_common_text(text, extracted_text)

                    similarity_result_url = SimilarityResultURL.objects.create(
                        similarity_result=similarity_result,
                        url=url,
                        extracted_text=extracted_text,
                        sbert_similarity=sbert_similarity_score,
                        tfidf_similarity=tfidf_similarity_score,
                        common_words=", ".join(common_data["common_words"]),
                        common_sentences="\n".join(common_data["common_sentences"]),
                        common_paragraphs="\n\n".join(common_data["common_paragraphs"]),
                    )
                    
                    results.append({
                        "title": extracted_data["results"].get(url, "Address not available"),
                        "url": url,
                        "extracted_text":extracted_text,
                        "tfidf": f"{tfidf_similarity_score:.2f}",
                        "sbert": f"{sbert_similarity_score:.2f}",
                        "common_words": similarity_result_url.common_words,
                        "common_sentences": similarity_result_url.common_sentences,
                        "common_paragraphs": similarity_result_url.common_paragraphs,
                    })

            return JsonResponse({"results": results}, status=200)





##################################Grammer correction 

llm=LLM(api_key=api_key)
gc = GrammarCorrector()
class GrammarCorrectionAPIView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        if request.user.is_authenticated:
                histories = GrammarCorrectionHistory.objects.filter(user=request.user)
        else:
                return Response({"error": "You must be logged in to view your history."}, status=status.HTTP_401_UNAUTHORIZED)


        serializer = GrammarCorrectionHistorySerializer(histories, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from uploaded PDF file"""
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
        extracted_text = None

        if pdf_file:
            try:
                extracted_text = self.extract_text_from_pdf(pdf_file)
                text = extracted_text
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        if not text:
            return Response({"error": "No valid text or PDF provided."}, status=400)

        try:
            if len(text.split(" ")) > 20:
                corrected_text = gc.correct(text)
            else:
                corrected_text = llm.grammar_corrector(text)

            similarity = Similarity()
            sbert_score = similarity.sbert_similarity([text, corrected_text])[0][1] * 100
            diff_result = gc.diff(text, corrected_text)

            user = request.user if request.user.is_authenticated else None


            # إنشاء السجل
            grammar_history = GrammarCorrectionHistory.objects.create(
                user=user,
                input_text=text,
                corrected_text=corrected_text,
                sbert_score=sbert_score,
                 diff=diff_result,
            )

            # إنشاء ملف PDF بالنص المصحح
            file_name = f"corrected/pdf/{grammar_history.id}.pdf"
            pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
            pdf_url = os.path.join(settings.MEDIA_URL, file_name)

            html_content = render_to_string(
                "grammer_template.html", {"corrected_text": corrected_text}
            )

            try:
                pdf_data = HTML(string=html_content).write_pdf()
                with open(pdf_path, "wb") as f:
                    f.write(pdf_data)

                # تحديث السجل برابط الملف
                grammar_history.pdf_file = file_name
                grammar_history.save()
            except Exception as e:
                return Response({"error": f"Failed to create PDF: {str(e)}"}, status=500)

            return Response({
                "corrected_text": corrected_text,
                "sbert_score": f"{sbert_score:.2f}",
                "pdf_url": pdf_url,
                "errors": diff_result
            }, status=200)

        except Exception as e:
            return Response({"error": f"An error occurred: {str(e)}"}, status=500)
####################################################



class GenerateQuestionsView(APIView):
    permission_classes = [AllowAny]  

    def post(self, request, *args, **kwargs):
        user = request.user 

        num_questions = int(request.data.get("num_questions", 5))
        uploaded_file = request.FILES.get("file")
        text = request.data.get("text", "")

        if uploaded_file:
            pdf_reader = PdfReader(uploaded_file)
            text = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

        if not text:
            return Response({"error": "No text provided"}, status=status.HTTP_400_BAD_REQUEST)

        if request.user.is_authenticated:
            session = QnA.objects.create(user=request.user, text=text)
        else:
            session = QnA.objects.create(text=text)

        questions = qna_engine.generate_questions(text, num_questions)

        created_questions = []
        for question_text in questions:
            question = Question.objects.create(qna_session=session, text=question_text)
            created_questions.append({"id": question.id, "text": question.text})

        return Response({
            "questions": created_questions
        }, status=status.HTTP_201_CREATED)



class EvaluateAnswersView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        user = request.user
        question_id = request.data.get("question_id")
        user_answer = request.data.get("answer", "").strip()

        if not question_id:
            return Response({"error": "question_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not user_answer:
            return Response({"error": "Answer cannot be empty"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.get(id=question_id)
        except Question.DoesNotExist:
            return Response({"error": "Question not found"}, status=status.HTTP_404_NOT_FOUND)

        evaluation = qna_engine.evaluate_answers([question.text], [user_answer], question.qna_session.text)[0]
        _, score, feedback = evaluation

        is_correct = score > 5

        Answer.objects.create(
            question=question,
            user_answer=user_answer,
            is_correct=is_correct,
            score=score,
            feedback=feedback
        )

        return Response({
            "question": question.text,
            "user_answer": user_answer,
            "is_correct": is_correct,
            "score": score,
            "feedback": feedback
        }, status=status.HTTP_200_OK)




##################################################3##

class SummarizeTextView(APIView):
    permission_classes = [AllowAny]

    def extract_text_from_pdf(self, pdf_file):
        """Extract text from PDF file"""
        text = ""
        try:
            with fitz.open(stream=pdf_file.read(), filetype="pdf") as doc:
                for page in doc:
                    text += page.get_text("text") + "\n"
        except Exception as e:
            raise ValueError(f"Failed to extract text from PDF: {str(e)}")
        return text.strip()

    def post(self, request):
        text = request.data.get("text", "")
        pdf_file = request.FILES.get("file")
        extracted_text = None

        if pdf_file:
            try:
                extracted_text = self.extract_text_from_pdf(pdf_file)
                text = extracted_text
            except ValueError as e:
                return Response({"error": str(e)}, status=400)

        if not text:
            return Response({"error": "No valid text or PDF provided."}, status=400)

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return Response({"error": "API key not found in environment"}, status=500)

        llm = LLM(api_key=api_key)

        detected_language = detect(text)
        language = "Arabic" if detected_language == "ar" else "French" if detected_language == "fr" else "English"
        sbert_score= 0.0

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
                    "sbert_score": summarization.sbert_score,
                },
                status=200,
            )
        summarized_text = llm.summarize(text, language=language).strip()

        if not summarized_text:
            return Response({"error": "Summarization failed or result is empty."}, status=400)



        try:
            similarity = Similarity()
            sbert_score = similarity.sbert_similarity([text, summarized_text])[0][1] * 100
        except Exception as e:
            sbert_score = 0
            print("Error calculating similarity:", e)

        summarization.summary_text = summarized_text
        summarization.sbert_score = sbert_score
        summarization.save()

        file_name = f"summaries/pdf/{summarization.id}.pdf"
        pdf_path = os.path.join(settings.MEDIA_ROOT, file_name)
        pdf_url = os.path.join(settings.MEDIA_URL, file_name)

        html_content = render_to_string(
            "summary_template.html", {"summarized_text": summarized_text}
        )
        try:
            pdf_data = HTML(string=html_content).write_pdf()
            with open(pdf_path, "wb") as f:
                f.write(pdf_data)

            summarization.pdf_file = file_name
            summarization.save()
        except Exception as e:
            return Response({"error": f"Failed to create PDF: {str(e)}"}, status=500)

        return Response(
            {
                "summary_text": summarized_text,
                "summarization_id": summarization.id,
                "pdf_url": pdf_url,
                "sbert_score": f"{sbert_score:.2f}",
            },
            status=200,
    )