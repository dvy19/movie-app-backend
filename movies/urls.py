from django.urls import path
from .views import PopularMoviesView, SearchMoviesView , MovieView, NotificationListView , MarkNotificationAsReadView  ,MyPostsView, MovieDetailView
from . import views

urlpatterns = [
    path('popular/', PopularMoviesView.as_view()),
    
    path('search/', SearchMoviesView.as_view()),

    path("movies/<int:movie_id>/", MovieDetailView.as_view()),

    # Handles GET (all posts) and POST (create post)
    path('posts/', MovieView.as_view(), name='movie-list-create'),

    path("posts/me/", MyPostsView.as_view(), name="my-posts"),
    
    # Handles GET (single post by ID)
    path('posts/<int:id>/', MovieView.as_view(), name='movie-detail'),

    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),

    path('get-genre/' , views.get_movie_genres , name='movie-genre'),


    # GET /api/genres/28/movies/?page=1


    
    path('genres/<int:genre_id>/movies/e' , views.get_movies_by_genre, name=''),

    # GET /api/genres/27/search/?query=conjuring&page=1
    path(
        'genres/<int:genre_id>/movies/',
        views.get_movies_by_genre,
        name='genre-movies'
    ),

]