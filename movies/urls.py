from django.urls import path
from .views import PopularMoviesView, SearchMoviesView , MovieView, NotificationListView , MarkNotificationAsReadView 
from . import views

urlpatterns = [
    path('popular/', PopularMoviesView.as_view()),
    
    path('search/', SearchMoviesView.as_view()),

    # Handles GET (all posts) and POST (create post)
    path('posts/', MovieView.as_view(), name='movie-list-create'),
    
    # Handles GET (single post by ID)
    path('posts/<int:id>/', MovieView.as_view(), name='movie-detail'),

    path('notifications/', NotificationListView.as_view(), name='notification-list'),
    
    path('notifications/<int:pk>/read/', MarkNotificationAsReadView.as_view(), name='notification-mark-read'),

    path('get-genre/' , views.get_movie_genres , name='movie-genre'),


    # GET /api/genres/28/movies/?page=1

    '''
    There is one optimization worth considering: TMDB returns 20 movies per page, so our backend currently fetches 20 and sends only 6.
    '''
    path('genres/<int:genre_id>/movies/e' , views.get_movie_by_genre, name=''),

    # GET /api/genres/27/search/?query=conjuring&page=1
    path(
        'genres/<int:genre_id>/movies/',
        views.get_movies_by_genre,
        name='genre-movies'
    ),

]