from django.urls import path
from .views import PopularMoviesView, SearchMoviesView

urlpatterns = [
    path('popular/', PopularMoviesView.as_view()),
    
    path('search/', SearchMoviesView.as_view()),
]