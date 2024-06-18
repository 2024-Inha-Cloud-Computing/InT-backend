import pickle
from django.core.cache import cache

class MemoryModel:
    def __init__(self):
        pass
    
    @staticmethod
    def save(id, instance):
        serialized_data = cache.get(id)
        if serialized_data is not None: 
            # 인스턴스가 이미 존재하는 경우 업데이트
            existing_instance = pickle.loads(serialized_data)
            # 새로운 인스턴스의 속성을 기존 인스턴스에 병합
            for attr, value in instance.__dict__.items():
                setattr(existing_instance, attr, value)
            # 병합된 인스턴스를 다시 직렬화하여 캐시에 저장
            serialized_data = pickle.dumps(existing_instance)
            cache.set(id, serialized_data, timeout=40000)
        else: # 있는 경우 save
            serialized_data = pickle.dumps(instance)
            cache.set(id, serialized_data, timeout=40000)
    
    @staticmethod
    def get(id):
        serialized_data = cache.get(id)
        if serialized_data is not None:
            instance = pickle.loads(serialized_data)
            return instance
        return None

    @staticmethod
    def delete(id):
        cache.delete(id)