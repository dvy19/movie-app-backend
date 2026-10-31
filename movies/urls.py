from django.urls import path
from .views import PopularMoviesView, SearchMoviesView , MovieView

urlpatterns = [
    path('popular/', PopularMoviesView.as_view()),
    
    path('search/', SearchMoviesView.as_view()),



    # Handles GET (all posts) and POST (create post)
    path('posts/', MovieView.as_view(), name='movie-list-create'),
    
    # Handles GET (single post by ID)
    path('posts/<int:id>/', MovieView.as_view(), name='movie-detail'),

]