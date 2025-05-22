from django.contrib import admin
from .models import User, Summarization, SimilarityResult, QnA, Question, Answer, GrammarCorrectionHistory
from django.core.exceptions import PermissionDenied

class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'gender', 'phone', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'gender')
    ordering = ('-date_joined',)
    def has_change_permission(self, request, obj=None):
        if not request.user.is_authenticated:
            raise PermissionDenied("You must be logged in to access this data.")
        return super().has_change_permission(request, obj)


admin.site.register(User, UserAdmin)

class SummarizationAdmin(admin.ModelAdmin):
    list_display = ('user', 'original_text', 'summary_text', 'created_at', 'sbert_score','pdf_file')
    search_fields = ('user__email', 'original_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(Summarization, SummarizationAdmin)

from django.contrib import admin
from .models import SimilarityResult, SimilarityResultURL

class SimilarityResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'sbert_similarity', 'tfidf_similarity','input_text','compared_text','common_words','common_sentences','common_paragraphs', 'created_at')
    search_fields = ('input_text', 'compared_text')
    list_filter = ('created_at', 'user')
    ordering = ('-created_at',)

class SimilarityResultURLAdmin(admin.ModelAdmin):
    list_display = ('similarity_result', 'url', 'sbert_similarity', 'tfidf_similarity','extracted_text','common_words','common_sentences','common_paragraphs', 'created_at')
    search_fields = ('url', 'extracted_text')
    list_filter = ('created_at', 'similarity_result')
    ordering = ('-created_at',)

admin.site.register(SimilarityResult, SimilarityResultAdmin)
admin.site.register(SimilarityResultURL, SimilarityResultURLAdmin)


class QnAAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'created_at')
    search_fields = ('user__email', 'text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)

admin.site.register(QnA, QnAAdmin)

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('qna_session', 'text')
    search_fields = ('qna_session__text', 'text')
    ordering = ('qna_session',)

admin.site.register(Question, QuestionAdmin)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('question_user','question', 'user_answer', 'is_correct', 'score', 'created_at')
    search_fields = ('question__text', 'user_answer')
    list_filter = ('is_correct', 'created_at')
    ordering = ('-created_at',)

admin.site.register(Answer, AnswerAdmin)

class GrammarCorrectionHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'input_text', 'corrected_text', 'created_at','sbert_score')
    search_fields = ('user__email', 'input_text')
    list_filter = ('created_at',)
    ordering = ('-created_at',)
admin.site.register(GrammarCorrectionHistory, GrammarCorrectionHistoryAdmin)
