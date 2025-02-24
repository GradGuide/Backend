from django.contrib import admin
from .models import User, Summarization, SimilarityResult, QnA, Question, Answer,GrammarCorrectionHistory

admin.site.register(User)
admin.site.register(Summarization)
admin.site.register(SimilarityResult)
admin.site.register(QnA)
admin.site.register(Question)
admin.site.register(Answer)
admin.site.register(GrammarCorrectionHistory)