# """
# URL configuration for project project.

# The `urlpatterns` list routes URLs to views. For more information please see:
#     https://docs.djangoproject.com/en/5.1/topics/http/urls/
# Examples:
# Function views
#     1. Add an import:  from my_app import views
#     2. Add a URL to urlpatterns:  path('', views.home, name='home')
# Class-based views
#     1. Add an import:  from other_app.views import Home
#     2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
# Including another URLconf
#     1. Import the include() function: from django.urls import include, path
#     2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
# """
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from Registration.views import  RegisterView,SummarizeTextView,User_account_View ,SimilarityCheckViews,EvaluateAnswersView,GenerateQuestionsView,GrammarCorrectionAPIView
# from rest_framework_simplejwt.views import TokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('Registration.urls')),
    path('api/signup/', RegisterView.as_view(), name='signup'),
    path('api/login/', User_account_View.as_view(), name='login'),
    # path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('api/summarize/', SummarizeTextView.as_view(), name='summarize'),
    # path('api/compare-research-papers/', SimilarityCheckView.as_view(), name='check-paper'),
    path('api/check/', SimilarityCheckViews.as_view(), name='check-paper'),
    # path('api/compare-research/', WebSimilarityCheckView.as_view(), name='check-paper'),
    path('api/check-grammer/', GrammarCorrectionAPIView.as_view(), name='check-grammer'),
    path('api/qna/', GenerateQuestionsView.as_view(), name='generate_questions'),
    path('api/eva/', EvaluateAnswersView.as_view(), name='evaluate_answers'),  # ✅ تأكد من التطابق التام
    # path('api/validate-answers/<int:pk>/', ValidateAnswersAPIView.as_view(), name='QNA'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)








    
    
# d9fe41790401b59b85045fb592e60e0fc2b2c866


   
