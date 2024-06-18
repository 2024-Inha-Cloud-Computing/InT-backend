# # JWT token
from rest_framework import serializers
from .models import Users

# 회원정보
class UsersSerializer(serializers.ModelSerializer):
    def create(self, instance, validated_data):
        instance.id = validated_data["id"]
        instance.pw = validated_data["pw"]
        instance.name = validated_data["name"]
        instance.birth = validated_data["birth"]
        instance.phone = validated_data["phone"]
        instance.email = validated_data["email"]
        instance.register_day = validated_data["register_day"]
        instance.am_pm = validated_data["am_pm"]
        instance.first_class = validated_data["first_class"]
        instance.space_time = validated_data["space_time"]
        instance.save()
        return instance
    class Meta:
        model = Users
        field = '__all__'