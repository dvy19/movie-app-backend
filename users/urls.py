from django.urls import path

from .views import  LoginView, RegisterView , UserDetailsView, health_check, getMyProfileDetails, SurveyCreateAPIView, SubmitSurveyResponsesView , delete_account, test_email

urlpatterns = [

    path("register/", RegisterView.as_view()),
    path('login/', LoginView.as_view()),

    path('create-user/' , UserDetailsView.as_view()),

    path('delete-account/' , delete_account),

    path('get-user-details/<int:id>/' , UserDetailsView.as_view()),

    path('get-self-profile/' , getMyProfileDetails),

    
    path("health-check/" , health_check),

    path('surveys/create/', SurveyCreateAPIView.as_view(), name='survey-create'),
    path("surveys/<int:pk>/", SurveyCreateAPIView.as_view(), name="survey-detail"),

    path("surveys/submit-survey-response/", SubmitSurveyResponsesView.as_view(), name="survey-response"),


    path('test-mail/'  ,test_email )

    




]