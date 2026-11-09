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

    path('/get-genre/' , views.get_movie_genres , name='movie-genre')

]