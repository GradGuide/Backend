
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings

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
  
    GENDER_CHOICES = [
        ('male', 'ذكر'),
        ('female', 'أنثى'),
    ]

    email_validator = RegexValidator(
        regex=r'^[^@]+@[^@]+\.[^@]+$',
        message='The email must be a Gmail or Outlook address.',
        code='invalid_email'
    )
    is_staff = models.BooleanField(default=True) 
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
    def __str__(self):
        return self.email


    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, validators=[email_validator])
    password = models.CharField(max_length=128) 
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True)
    phone = PhoneNumberField(unique=True, null=True, blank=False, region='EG')
    address = models.TextField(default="")
    date_joined = models.DateTimeField(auto_now_add=True)
  
    objects = UserManager()

    REQUIRED_FIELDS = ['first_name', 'last_name']



class Summarization(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True)

    original_text = models.TextField(default="")
    summary_text = models.TextField(default="")
    pdf_file = models.FileField(upload_to="summaries/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)
    sbert_score = models.FloatField(default=0.0)

    def __str__(self):
        return f"Summary by {self.user} - {self.created_at}"
    




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
        return f"Similarity SBERT: {self.sbert_similarity} - {self.user if self.user else 'Anonymous'}"


class SimilarityResultURL(models.Model):
    similarity_result = models.ForeignKey(SimilarityResult, related_name="urls", on_delete=models.CASCADE)
    url = models.URLField()
    extracted_text = models.TextField()
    sbert_similarity = models.FloatField(default=0.0)
    tfidf_similarity = models.FloatField(default=0.0)
    common_words = models.TextField()
    common_sentences = models.TextField()
    common_paragraphs = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"URL: {self.url} - Similarity SBERT: {self.sbert_similarity} - TF-IDF: {self.tfidf_similarity}"



class QnA(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"QnA Session ({self.user if self.user else 'Guest'}) - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class Question(models.Model):
    qna_session = models.ForeignKey(QnA, on_delete=models.CASCADE, related_name="questions")
    text = models.TextField()

    def __str__(self):
        return f"Question: {self.text[:30]}"

class Answer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    user_answer = models.TextField()
    is_correct = models.BooleanField(null=True, blank=True)
    score = models.IntegerField()
    feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    question_user = models.ForeignKey(User, related_name='question_user', on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.question and self.question.qna_session and self.question.qna_session.user:
            self.question_user = self.question.qna_session.user
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Answer to {self.question.text[:30]} - Score: {self.score}"




class GrammarCorrectionHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    input_text = models.TextField()
    corrected_text = models.TextField()
    diff = models.TextField(null=True, blank=True)  
    pdf_file = models.FileField(upload_to="corrected/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sbert_score = models.FloatField(null=True, blank=True)

    def __str__(self):
        user_info = self.user if self.user else None
        return f"Correction by {user_info if user_info else 'Guest'} on {self.created_at.strftime('%Y-%m-%d %H:%M')}"