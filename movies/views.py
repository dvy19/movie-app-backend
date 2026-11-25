from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny

from .serializers import MoviePostSerializer
from .models import MoviePost


import requests

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from .models import MoviePost, Notification
from .serializers import MoviePostSerializer, NotificationSerializer


import requests
from django.conf import settings
from django.http import JsonResponse


from movies.tasks import categorize_post_task


def get_movie_genres(request):

    url = "https://api.themoviedb.org/3/genre/movie/list"

    headers = {
        "Authorization": f"Bearer {settings.TMDB_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "language": "en-US"
    }

    response = requests.get(
        url,
        headers=headers,
        params=params
    )

    return JsonResponse(response.json())

def get_movies_by_genre(request, genre_id):

    page = request.GET.get('page', 1)
    search_query = request.GET.get('query', '').strip()

    url = "https://api.themoviedb.org/3/discover/movie"

    headers = {
        "Authorization": f"Bearer {settings.TMDB_ACCESS_TOKEN}",
        "accept": "application/json"
    }

    params = {
        "with_genres": genre_id,
        "sort_by": "popularity.desc",
        "page": page,
        "include_adult": False
    }

    # Apply movie search if query is provided
    if search_query:
        params["with_text_query"] = search_query

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    movies = data.get("results", [])

    return JsonResponse({
        "genre_id": genre_id,
        "query": search_query,
        "page": data.get("page"),
        "total_pages": data.get("total_pages"),
        "total_results": data.get("total_results"),
        "results": movies[:6]
    })




class PopularMoviesView(APIView):

    permission_classes = [AllowAny]
    def get(self, request):
        try:
            data = get_movies("movie/popular", {
                "language": "en-US",
                "page": request.query_params.get("page", 1)
            })

            return Response(data, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as e:
            print("TMDB ERROR:", e.response.status_code, e.response.text)
            return Response(
                {"error": e.response.text},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            print("ERROR:", repr(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

class MovieDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, movie_id):
        try:
            params = {
                "language": request.query_params.get("language", "en-US"),
            }

            data = get_movies(f"movie/{movie_id}", params)
            return Response(data, status=status.HTTP_200_OK)

        except requests.exceptions.HTTPError as e:
            print("TMDB ERROR:", e.response.status_code, e.response.text)
            return Response(
                {"error": e.response.text},
                status=status.HTTP_502_BAD_GATEWAY
            )

        except Exception as e:
            print("ERROR:", repr(e))
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

'''sample response

[
  {
    "adult": false,
    "backdrop_path": "/9FE5eD92WfVCiivM9Pq9GVSrlWk.jpg",
    "genre_ids": [28, 53, 80],
    "id": 155,
    "title": "The Dark Knight",
    "original_language": "en",
    "original_title": "The Dark Knight",
    "overview": "Batman raises the stakes in his war on crime. With the help of Lt. Jim Gordon and District Attorney Harvey Dent, Batman sets out to dismantle the remaining criminal organizations that plague the streets. The partnership proves to be effective, but they soon find themselves prey to a reign of chaos unleashed by a rising criminal mastermind known to the terrified citizens of Gotham as the Joker.",
    "popularity": 4135.6789,
    "poster_path": "/qJ2tW6WMUDux911r6m7haRef0WH.jpg",
    "release_date": "2008-07-16",
    "softcore": false,
    "video": false,
    "vote_average": 8.539,
    "vote_count": 37141
  },
  {
    "adult": false,
    "backdrop_path": "/sl5NJ1vtyhP9Vr88bB4blULsJYp.jpg",
    "genre_ids": [16, 12, 14],
    "id": 791523,
    "title": "Wildwood",
    "original_language": "en",
    "original_title": "Wildwood",
    "overview": "Prue and her classmate Curtis are drawn into a magical forest filled with enchanted creatures, loyal allies, and formidable adversaries as they embark on a desperate quest to rescue Prue's abducted baby brother from a murder of crows led by a mysterious woman named Alexandra.",
    "popularity": 2183.8371,
    "poster_path": "/8g7q6o54WfKWRmUQ0Ye8OskevUY.jpg",
    "release_date": "2026-10-19",
    "softcore": false,
    "video": false,
    "vote_average": 8.618,
    "vote_count": 114
  },
  {
    "adult": false,
    "backdrop_path": "/qqHFLg90IUSoTmSMpKOOW5RyqN3.jpg",
    "genre_ids": [878, 9648, 28],
    "id": 1058424,
    "title": "Hope",
    "original_language": "ko",
    "original_title": "호프",
    "overview": "In the remote South Korean village of Hope Harbor, police chief Bum-seok and officer Sung-ae are called to investigate a mysterious creature wreaking havoc on the community. But all is not as it seems, and perceptions can be misleading. What begins as ignorance plants the seed of disaster, escalating through human conflict into a tragedy of cosmic proportions.",
    "popularity": 459.5076,
    "poster_path": "/6VY1ZKgpsc8CfGsQcCGiYEgHdH0.jpg",
    "release_date": "2026-07-15",
    "softcore": false,
    "video": false,
    "vote_average": 6.756,
    "vote_count": 408
  }
]
'''


class SearchMoviesView(APIView):
    permission_classes = [AllowAny]


    def get(self, request):

        query = request.query_params.get("query")

        if not query:
            return Response(
                {"error": "Search query required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            data = get_movies("search/movie", {
                "query": query,
                "page": request.query_params.get("page", 1)
            })

            return Response(data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )



class MovieView(APIView):

    def post(self, request):
        serializer = MoviePostSerializer(data=request.data)
        
        if serializer.is_valid():

            post = serializer.save(user=request.user)

            # Trigger background categorization
            categorize_post_task.delay(post.id)

            return Response(
                {
                    "message": "Post created successfully",  
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED 
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, id=None):  

        permission_classes = [AllowAny]

        if id is not None:

            post = get_object_or_404(MoviePost, id=id)
        
            serializer = MoviePostSerializer(post)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            category = request.query_params.get('category')
            
            posts = MoviePost.objects.select_related("user").all()
            
            if category:
                posts = posts.filter(category__iexact=category)
            
            posts = posts.order_by('-id')
            serializer = MoviePostSerializer(posts, many=True)
            return Response(
                {"data": serializer.data}, 
                status=status.HTTP_200_OK
                )

class MyPostsView(APIView):
    #permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get("category")

        posts = request.user.post.select_related("user").all()

        if category:
            posts = posts.filter(category__iexact=category)

        posts = posts.order_by("-id")
        serializer = MoviePostSerializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class NotificationListView(APIView):

    def get(self, request):
        # Get notifications for the currently logged-in user
        notifications = request.user.notifications.all().order_by('-created_at')
        serializer = NotificationSerializer(notifications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MarkNotificationAsReadView(APIView):

    def patch(self, request, pk):
        notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
        notification.is_read = True
        notification.save()
        return Response({"message": "Notification marked as read"}, status=status.HTTP_200_OK)
'''
category__iexact=category is a Django ORM lookup filter that performs a case-insensitive exact match between the database field and your variable value.

i => refers to case insensitivity

we ca also do
category=category

but will be case sensitive

__ => double underscore in django is used to separate the lookup filter from the model name
'''
class FilteredMoviesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        params = {
            "language": request.query_params.get("language", "en-US"),
            "page": request.query_params.get("page", 1),
            "sort_by": request.query_params.get("sort_by", "popularity.desc"),
            "include_adult": request.query_params.get("include_adult", "false").lower(),
        }

        # Filter by country of origin (ISO 3166-1 alpha-2 code, e.g., "IN", "US", or "IN|US")
        origin_country = request.query_params.get("with_origin_country")
        if origin_country:
            params["with_origin_country"] = origin_country.upper()

        # Filter by original audio language (e.g., "hi", "en", or "hi|en")
        original_language = request.query_params.get("with_original_language")
        if original_language:
            params["with_original_language"] = original_language

        # Filter by exact release year (e.g., "2024")
        release_year = request.query_params.get("primary_release_year")
        if release_year:
            params["primary_release_year"] = release_year

        # Filter by release date range (YYYY-MM-DD)
        release_date_gte = request.query_params.get("primary_release_date.gte")
        if release_date_gte:
            params["primary_release_date.gte"] = release_date_gte

        release_date_lte = request.query_params.get("primary_release_date.lte")
        if release_date_lte:
            params["primary_release_date.lte"] = release_date_lte

        try:
            data = get_movies("discover/movie", params)
            return Response(data, status=status.HTTP_200_OK)
        except Exception as exc:
            return Response(
                {"detail": f"Failed to fetch filtered movies: {str(exc)}"},
                status=status.HTTP_502_BAD_GATEWAY,
            )