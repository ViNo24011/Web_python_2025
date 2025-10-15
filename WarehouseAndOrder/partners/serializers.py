from rest_framework import serializers
from .models import Supplier, Customer

# Chuyển đổi dữ liệu model → JSON (và ngược lại).
# Giúp API giao tiếp với frontend.

class SupplierSerializer(serializers.ModelSerializer): #tự động tạo ra một lớp Serializer dựa trên một lớp Model đã có sẵn.
    class Meta:
        model = Supplier  # liên kết với model Supplier
        fields = '__all__' # bao gồm tất cả các trường trong model Supplier

class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
