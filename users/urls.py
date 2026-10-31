from django.urls import path

from .views import  LoginView, RegisterView , UserDetailsView

urlpatterns = [

    path("register/", RegisterView.as_view()),
    path('login/', LoginView.as_view()),

    path('create-user/' , UserDetailsView.as_view()),

    path('get-user-details/<int:id>/' , UserDetailsView.as_view()),

    path('get-self-profile' , UserDetailsView.as_view())
    




]