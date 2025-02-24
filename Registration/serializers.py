
import string
import random
from rest_framework import serializers
from .models import User
from django.core.mail import send_mail
from django.conf import settings
from django.core.validators import RegexValidator
from phonenumbers import parse, is_valid_number, NumberParseException

class UserSerializer(serializers.ModelSerializer):
    email_validator = RegexValidator(
        regex=r'^[^@]+@[^@]+\.[^@]+$',
        message='Email must be a complex Gmail or Outlook address containing uppercase, lowercase letters, numbers, and special characters.',
        code='invalid_email'
    )
    # phone_validator = RegexValidator(     
    #     regex=r'^\+?[1-9]\d{1,14}$',   #problem 
    #     message='Phone number is not valid.',
    #     code='invalid_phone'
    # )

    # email = serializers.EmailField(validators=[email_validator])
    # phone = serializers.CharField(max_length=15, validators=[phone_validator])



    class Meta():
        model = User
        fields = '__all__'
        extra_kwargs = {
        #     'password': {'write_only': True},
        #     'first_name': {'required': True},
        #     'last_name': {'required': True},
        #     'user_type': {'required': True},
        #     'gender': {'required': True},
            'phone': {'required': True},
            'address': {'required': True},
        #     'is_verified': {'read_only': True},
         }


        def create(self, validated_data):
         user = User.objects.create_user(**validated_data)
         return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance

    def validate_first_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("First name must contain only letters.")
        return value

    def validate_last_name(self, value):
        if any(char.isdigit() for char in value):
            raise serializers.ValidationError("Last name must contain only letters.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value
    
    # def validate_phone(self, value):
    #     try:
    #         phone = parse(value, None)  
    #         if not is_valid_number(phone):
    #             raise serializers.ValidationError("Invalid phone number.")
    #     except NumberParseException as e:
    #         raise serializers.ValidationError(f"Error in phone number: {str(e)}")

        return value

    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            user_type=validated_data.get('user_type'),  
            gender=validated_data.get('gender'),  
            phone=validated_data.get('phone'),  
            address=validated_data['address'],
            is_verified=False,     
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user



class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()
    # verification_code = serializers.CharField(required=False)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        # verification_code = attrs.get('verification_code')
        
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        # if verification_code:
        #     if user.verification_code != verification_code:
        #         raise serializers.ValidationError("Invalid verification code")
            
            user.is_verified = True
            # user.verification_code = ''  
            user.save()

        else:
            # user.verification_code = ''.join(random.choices(string.digits, k=6))
            user.save()

            # send_mail(
            #     'Login Verification Code',
            #     f'Your login verification code is: {user.verification_code}',
            #     settings.DEFAULT_FROM_EMAIL,
            #     [user.email],
            #     fail_silently=False,
            # )

            # raise serializers.ValidationError("Verification code sent. Please enter the code to complete login.")
        
        attrs['user'] = user
        return attrs
    ##################################################################### Research paper 


from rest_framework import serializers

# class ResearchPaperSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ResearchPaper
#         fields = ['id', 'pdf_file', 'uploaded_at']
#         read_only_fields = ['id', 'uploaded_at']
#         from rest_framework import serializers
from .models import Summarization









from rest_framework import serializers
from .models import Summarization

class SummarizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summarization
        fields = ['id', 'text', 'summarized_text', 'keywords']



# class ResearchSimilaritySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ResearchSimilarity
#         fields = ["input_text", "matched_text", "similarity_percentage", "source_link"]

######################################################################################### Similarity
# from .models import Question_LLM
# class QuestionAnswerSerializer(serializers.ModelSerializer):
#     class Meta:
#         model =Question_LLM
#         fields = "__all__"
# from rest_framework import serializers
# from .models import QnA

# class QnASerializer(serializers.ModelSerializer):
#     class Meta:
#         model = QnA
#         fields = '__all__'
from rest_framework import serializers
from .models import QnA, Question, Answer,GrammarCorrectionHistory

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'

class AnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = '__all__'

class QnASerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = QnA
        fields = '__all__'
class GrammarCorrectionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarCorrectionHistory
        fields = '__all__'
from rest_framework import serializers
from .models import SimilarityResult

class SimilarityResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarityResult
        fields = "__all__"
