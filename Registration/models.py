
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator

# Registration ##############################################################
class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        """Create and return a regular user with an email and password."""     
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class User(AbstractBaseUser):
    USER_TYPE_CHOICES = [
        ('researcher', 'باحث'),
        ('jury member', 'لجنة تحكيم'),
    ]

    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]
    
    email_validator = RegexValidator(
        regex=r'^[^@]+@[^@]+\.[^@]+$',
        message='The email must be a Gmail or Outlook address.',
        code='invalid_email'
    )

    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, validators=[email_validator])
    password = models.CharField(max_length=128) 
    user_type = models.CharField(max_length=50, choices=USER_TYPE_CHOICES, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    phone = models.CharField(max_length=15, unique=True, null=True)
    address = models.TextField(default="")
    date_joined = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)  
    # verification_code = models.CharField(max_length=6, blank=True, null=True)
  
    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
########################################################## Research paper and summary
from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings


# class Summary(models.Model):
#     research_paper = models.OneToOneField(ResearchPaper, on_delete=models.CASCADE, related_name='summary')  # ارتباط مع الورقة البحثية
#     summarized_text = models.TextField(blank=True, null=True)  # النص الملخص
#     summary_file = models.FileField(upload_to='summaries/', blank=True, null=True)  # ملف النص الملخص

#     def __str__(self):
#         return f"Summary for {self.research_paper.id}"

# ########################################################## Similarity

# from django.db import models

# class ResearchSimilarity(models.Model):
#     input_text = models.TextField()
#     matched_text = models.TextField()
#     similarity_percentage = models.FloatField()
#     source_link = models.URLField()

#     def __str__(self):
#         return f"{self.input_text[:50]} - {self.similarity_percentage}%"
from django.utils.timezone import now

    # original_text = models.TextField(default="", blank=True)
    # summarized_text = models.TextField(default="")  # النص الملخص
   


from django.db import models
from django.conf import settings

class Summarization(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    original_text = models.TextField(default="")
    summary_text = models.TextField(default="")
    pdf_file = models.FileField(upload_to="summaries/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)


    def __str__(self):
        return f"Summary by {self.user.username} - {self.created_at}"
    



class SimilarityResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    input_text = models.TextField(default="", blank=True)
    compared_text = models.TextField()
    similarity_score = models.FloatField()
    common_words = models.TextField()
    common_sentences = models.TextField()
    common_paragraphs = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Similarity {self.similarity_score} - {self.user.username if self.user else 'Anonymous'}"

class Question_LLM(models.Model):
    text = models.TextField(null=True, blank=True)  # النص الأصلي (إذا كان المستخدم أدخل نصًا)
    pdf_file = models.FileField(upload_to="pdfs/", null=True, blank=True)  # رفع PDF
    questions = models.JSONField(default=list)  # تخزين الأسئلة المولدة
    user_answers = models.JSONField(default=list)  # إجابات المستخدم
    validation_results = models.JSONField(default=dict)  # نتيجة التحقق من صحة الإجابة
    created_at = models.DateTimeField(auto_now_add=True)