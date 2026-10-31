
from .models import Group
from rest_framework import serializers

class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model=Group
        fields=['owner' , 'icon' , 'name' , 'description' , 'slug' , 'created_at']
        read_only_fields=['owner' , 'slug' , 'created_at']

