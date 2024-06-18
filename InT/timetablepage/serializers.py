from rest_framework import serializers

class MemoryModelSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=100)
    instance = serializers.CharField()  # 클래스 이름을 문자열로 받기 위해 사용
