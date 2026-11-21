from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404, render
from httpcore import request
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
import traceback
from .models  import Survey
from .serializers import LoginSerializer, RegisterSerializer , UserDetailsSerializer, SurveySerializer , UserSurveyResponseSerializer
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
    


   

    def post(self, request):

        try:
            print("\n========== PROFILE POST DEBUG START ==========")

            # 1. Check request user
            print("[DEBUG 1] Request User:", request.user)
            print("[DEBUG 2] Is Authenticated:", request.user.is_authenticated)
            print("[DEBUG 3] User ID:", request.user.id)

            # 2. Check incoming data
            print("[DEBUG 4] Request Data:", request.data)

            # 3. Initialize serializer
            serializer = UserDetailsSerializer(data=request.data)

            print("[DEBUG 5] Serializer Initialized:", serializer)

            # 4. Validate serializer
            is_valid = serializer.is_valid()

            print("[DEBUG 6] Is Serializer Valid:", is_valid)

            if not is_valid:
                print("[DEBUG 7] Serializer Errors:", serializer.errors)
                print("[DEBUG 8] Validation Data:", serializer.validated_data)

                return Response(
                    {
                        "message": "Failed to save profile",
                        "errors": serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # 5. Check validated data
            print("[DEBUG 9] Validated Data:", serializer.validated_data)

            # 6. Save serializer
            print("[DEBUG 10] Saving profile...")

            instance = serializer.save(user=request.user)

            print("[DEBUG 11] Profile Saved Successfully!")
            print("[DEBUG 12] Saved Instance:", instance)
            print("[DEBUG 13] Saved Instance ID:", instance.id)

            # 7. Check serialized response data
            response_data = serializer.data

            print("[DEBUG 14] Response Data:", response_data)

            print("========== PROFILE POST DEBUG END ==========\n")

            return Response(
                {
                    "message": "Profile saved successfully",
                    "data": response_data
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            print("\n========== PROFILE POST EXCEPTION ==========")
            print("[ERROR] Exception Type:", type(e).__name__)
            print("[ERROR] Exception Message:", str(e))
            traceback.print_exc()
            print("========== END EXCEPTION ==========\n")

            return Response(
                {
                    "message": "Internal Server Error",
                    "error": str(e),
                    "type": type(e).__name__
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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


class SubmitSurveyResponsesView(APIView):
    def post(self, request):
        serializer = UserSurveyResponseSerializer(
            data=request.data,
            many=True,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)  # Calls create() once for each of the 4 items
        return Response(serializer.data, status=status.HTTP_201_CREATED)

''' sample post json

[
  { "question": 1, "selected_choice": "choice_1", "has_attended": true },
  { "question": 2, "selected_choice": "choice_3", "has_attended": true },
  { "question": 3, "selected_choice": "choice_2", "has_attended": true },
  { "question": 4, "selected_choice": null, "has_attended": false }
]


'''