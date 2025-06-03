
from rest_framework import serializers
from django.core.validators import RegexValidator
from phonenumber_field.serializerfields import PhoneNumberField as PhoneNumberSerializerField
from .models import User, QnA, Question, Answer,GrammarCorrectionHistory,Summarization,SimilarityResult

class UserSerializer(serializers.ModelSerializer):
    email_validator = RegexValidator(
        regex=r'^[^@]+@[^@]+\.[^@]+$',
        message='Email must be a complex Gmail or Outlook address containing uppercase, lowercase letters, numbers, and special characters.',
        code='invalid_email'
    )
    phone = PhoneNumberSerializerField(region='EG')

    class Meta():
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'gender': {'required': True},
            'phone': {'required': True},
            'address': {'required': True},
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
    


    def create(self, validated_data):
        user = User(
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            gender=validated_data.get('gender'),  
            phone=validated_data.get('phone'),  
            address=validated_data['address'],
        )
        
        user.set_password(validated_data['password'])
        user.save()

        return user

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        user = User.objects.filter(email=email).first()
        if user is None or not user.check_password(password):
            raise serializers.ValidationError("Invalid email or password")

        else:
            user.save()
        
        attrs['user'] = user
        return attrs





class SummarizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Summarization
        fields = ['id', 'text', 'summarized_text', 'keywords']



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
import json
class GrammarCorrectionHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = GrammarCorrectionHistory
        fields = '__all__'

        errors = serializers.SerializerMethodField()

  
        def get_errors(self, obj):
            if obj.diff:
                try:
                    return json.loads(obj.diff)
                except Exception:
                    return []
            return []

class SimilarityResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = SimilarityResult
        fields = "__all__"
