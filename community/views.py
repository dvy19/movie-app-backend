from django.shortcuts import render

from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from .serializers import GroupSerializer
from .models import Group, GroupMember

# Create your views here.

class GroupView(APIView):

    def post(self,request):

        serializer=GroupSerializer(data=request.data)

        if serializer.is_valid():
            group=serializer.save(owner=request.user)

            GroupMember.objects.get_or_create(
                user=request.user,
                group=group,
                defaults={'is_admin': True}
            )
            return Response(
                {
                    "message": "Group created successfully",  
                    "data": serializer.data
                },
                status=status.HTTP_201_CREATED 
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self,request):

        groups=Group.objects.all().order_by('-created_at')

        serializer=GroupSerializer(groups , many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
