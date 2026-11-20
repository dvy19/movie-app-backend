from django.urls import path

from .views import  LoginView, RegisterView , UserDetailsView, health_check, getMyProfileDetails, SurveyCreateAPIView

urlpatterns = [

    path("register/", RegisterView.as_view()),
    path('login/', LoginView.as_view()),

    path('create-user/' , UserDetailsView.as_view()),

    path('get-user-details/<int:id>/' , UserDetailsView.as_view()),

    path('get-self-profile' , getMyProfileDetails),

    
    path("health-check/" , health_check),

    path('surveys/create/', SurveyCreateAPIView.as_view(), name='survey-create'),
    path("surveys/<int:pk>/", SurveyCreateAPIView.as_view(), name="survey-detail"),
    




]