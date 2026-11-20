from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, render
from httpcore import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
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
        print("[DEBUG] Incoming request.data:", request.data)
        print("[DEBUG] Incoming request.user:", request.user, "| authenticated:", request.user.is_authenticated)

        try:
            serializer = SurveySerializer(data=request.data, context={"request": request})
            is_valid = serializer.is_valid()
            print("[DEBUG] serializer.is_valid():", is_valid)

            if not is_valid:
                print("[DEBUG] serializer.errors:", serializer.errors)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            print("[DEBUG] serializer.validated_data:", serializer.validated_data)

            user = request.user if request.user.is_authenticated else None
            print("[DEBUG] Resolved user for created_by:", user)

            survey = serializer.save(created_by=user)
            print("[DEBUG] Created survey ID:", survey.id)

            response_data = {"data": serializer.data}
            print("[DEBUG] Returning 201 response")
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as exc:
            print("[DEBUG ERROR] Exception type:", type(exc).__name__)
            print("[DEBUG ERROR] Exception message:", str(exc))
            print("[DEBUG TRACEBACK]:\n", traceback.format_exc())

            # Optional: surface the error in dev while debugging (remove in production)
            return Response(
                {
                    "error": type(exc).__name__,
                    "detail": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
    

