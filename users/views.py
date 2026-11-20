from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, render
from httpcore import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .models  import Survey
from .serializers import LoginSerializer, RegisterSerializer , UserDetailsSerializer, SurveySerializer 
from rest_framework_simplejwt.tokens import RefreshToken

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

import traceback


from .models import UserDetails

from django.http import JsonResponse

def health_check(request):
    return JsonResponse({
        "status": "ok"
    })



# Create your views here.

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access":  str(refresh.access_token),
    }




class LoginView(APIView):
    permission_classes = [AllowAny]  # no auth needed to login

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            data = serializer.validated_data
            return Response(
                {
                    "message": "Login successful",
                    "role":    data["role"],
                    "tokens":  {
                        "access": data["access"],
                        "refresh": data["refresh"],
                    },
                },
                status=status.HTTP_200_OK,
            )

        # If validation fails, return the errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RegisterView(APIView):
    permission_classes = [AllowAny]  # no auth needed to register

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            user   = serializer.save()
            tokens = get_tokens_for_user(user)

            return Response(
                {
                    "message": "Registration successful",
                    "role":    user.role,
                    "tokens":  tokens,
                },
                status=status.HTTP_201_CREATED,
            )

        else:
            # This will show you exactly what failed
            print(serializer.errors)  # Check your terminal/console
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailsView(APIView):


    def get(self,request ,id=None):

        try:

            # user_id is Django's automatically generated field for your ForeignKey or OneToOneField.
            user_details=UserDetails.objects.get(user_id=id)

            serializer=UserDetailsSerializer(user_details)

            return Response(
                serializer.data, 
                status=status.HTTP_200_OK
            )
        except UserDetails.DoesNotExist:
            return Response(
                {"message":"no user found"},
                status=status.HTTP_404_NOT_FOUND
            )
    


    def post(self,request):

        print("DEBUG [1] Incoming request.user:", request.user, "| Authenticated:", request.user.is_authenticated)
        print("DEBUG [2] Incoming request.data:", request.data)

        serializer=UserDetailsSerializer(data=request.data)


        if serializer.is_valid():

                serializer.save(user=request.user)


                return Response(
                    {
                        "message": "Profile saved successfully",
                        "data": serializer.data
                    },
                    status=status.HTTP_201_CREATED 
                )
        print("DEBUG [3] Serializer validation FAILED:", serializer.errors)
        print("DEBUG [3] Serializer validated_data:", serializer.validated_data)

        return Response(
            {
                "message": "Failed to save profile",
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyProfileDetails(request):

    try:
        user_details = UserDetails.objects.get(user=request.user)

        serializer = UserDetailsSerializer(user_details)

        return Response(serializer.data, status=status.HTTP_200_OK)

    except UserDetails.DoesNotExist:
        return Response(
            {"message": "Profile not found"},
            status=status.HTTP_404_NOT_FOUND
        )


class SurveyCreateAPIView(APIView):


    def post(self, request):
        

        try:
            serializer = SurveySerializer(data=request.data, context={"request": request})
            is_valid = serializer.is_valid()
           
            if not is_valid:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


            user = request.user if request.user.is_authenticated else None

            survey = serializer.save(created_by=user)

            response_data = {"data": serializer.data}
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as exc:
         
            # Optional: surface the error in dev while debugging (remove in production)
            return Response(
                {
                    "error": type(exc).__name__,
                    "detail": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def get(self, request, pk=None):
        queryset = (
            Survey.objects.select_related("created_by")
            .prefetch_related("survey_questions")
        )

        # Single survey by ID: GET /api/surveys/<pk>/
        if pk is not None:
            survey = get_object_or_404(queryset, pk=pk)
            serializer = SurveySerializer(survey, context={"request": request})
            return Response({"data": serializer.data}, status=status.HTTP_200_OK)

        # List surveys: GET /api/surveys/ (optional ?status=published|draft|closed)
        status_param = request.query_params.get("status")
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = SurveySerializer(queryset, many=True, context={"request": request})
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)

