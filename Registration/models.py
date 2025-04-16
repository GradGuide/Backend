
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
    def create_superuser(self, email, password=None, **extra_fields):
        """Create and return a superuser with an email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

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
    is_staff = models.BooleanField(default=False) 
    is_superuser = models.BooleanField(default=False) 
    is_active = models.BooleanField(default=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def has_perm(self, perm, obj=None):
        """Check if the user has the specified permission"""
        return self.is_superuser

    def has_module_perms(self, app_label):
        """Check if the user has access permissions to any particular application"""
        return self.is_superuser

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
    sbert_score = models.FloatField(null=True, blank=True)
    tfidf_score = models.FloatField(null=True, blank=True)


    def __str__(self):
        return f"Summary by {self.user.username} - {self.created_at}"
    



class SimilarityResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)
    input_text = models.TextField(default="", blank=True)
    compared_text = models.TextField()
    sbert_similarity = models.FloatField(default=0.0)  
    tfidf_similarity = models.FloatField(default=0.0)
    common_words = models.TextField()
    common_sentences = models.TextField()
    common_paragraphs = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Similarity SBERT: {self.sbert_similarity}% - TF-IDF: {self.tfidf_similarity}% - {self.user.username if self.user else 'Anonymous'}"



from django.db import models
from django.conf import settings

class QnA(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QnA Session ({self.user.username if self.user else 'Guest'}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Question(models.Model):
    qna_session = models.ForeignKey(QnA, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return f"Question: {self.text[:30]}"

class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user_answer = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    score = models.IntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer to {self.question.text[:30]} - Score: {self.score}"


from django.db import models

class GrammarCorrectionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    input_text = models.TextField()
    corrected_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        user_info = self.user.username if self.user else "Anonymous"
        return f"Correction by {user_info} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"