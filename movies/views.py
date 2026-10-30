from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny


from .services import get_movies

import requests

import requests

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


class SearchMoviesView(APIView):

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