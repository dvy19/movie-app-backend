
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser , UserDetails,  Survey, SurveyQuestion
from django.db import transaction

class RegisterSerializer(serializers.ModelSerializer):

    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model  = CustomUser
        fields = ["email", "password", "role"]

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email    = validated_data["email"],
            password = validated_data["password"],
            role     = validated_data["role"],
        )
        return user
    

class LoginSerializer(serializers.Serializer):

    email    = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if user is None:
            raise serializers.ValidationError("Invalid credentials")

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return {
            "user": user,
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "role": user.role
        }


class UserDetailsSerializer(serializers.ModelSerializer):

    # UserDetails has a user feild with OneToOne relation with auth, hence user.email is used to get the email
    mail = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model=UserDetails
        feilds=['city' , 'gender' , 'user' , 'profile' , 'name']
        read_only_fields=['user'  , 'email']


class SurveyQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyQuestion
        fields = ['id', 'question_text', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'order']

    def validate(self, attrs):
        choices = [
            attrs.get('choice_1', '').strip(),
            attrs.get('choice_2', '').strip(),
            attrs.get('choice_3', '').strip(),
            attrs.get('choice_4', '').strip(),
        ]
        if any(not c for c in choices):
            raise serializers.ValidationError("All 4 choices are required for each question.")
        if len({c.lower() for c in choices}) < 4:
            raise serializers.ValidationError("All 4 choices in a question must be distinct.")
        return attrs


class SurveySerializer(serializers.ModelSerializer):
    survey_questions = SurveyQuestionSerializer(many=True)

    class Meta:
        model = Survey
        fields = [
            'id', 'title', 'movie', 'rating', 'movie_image',
            'description', 'start_date', 'end_date', 'status',
            'created_by', 'created_at', 'survey_questions'
        ]
        read_only_fields = ['id', 'created_by', 'created_at']

    def validate(self, data):
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        questions = data.get('survey_questions', [])

        if start_date and end_date and start_date >= end_date:
            raise serializers.ValidationError({"end_date": "End date must be after the start date."})

        if len(questions) != 4:
            raise serializers.ValidationError({
                "survey_questions": "A movie survey must contain exactly 4 MCQ questions."
            })

        orders = [q.get('order') for q in questions]
        if len(set(orders)) != len(orders):
            raise serializers.ValidationError({
                "survey_questions": "Duplicate question 'order' values are not allowed."
            })

        return data

    @transaction.atomic
    def create(self, validated_data):
        questions_data = validated_data.pop('survey_questions')
        request = self.context.get('request')

        if 'created_by' not in validated_data and request and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        survey = Survey.objects.create(**validated_data)

        SurveyQuestion.objects.bulk_create([
            SurveyQuestion(survey=survey, **q_data)
            for q_data in questions_data
        ])

        return survey