from django.shortcuts import render
# Nơi viết hàm hoặc class xử lý request từ client
# Create your views here.
from rest_framework import viewsets # tạo các view api dựa trên các model đã có sẵn
from .models import Supplier, Customer
from .serializers import SupplierSerializer, CustomerSerializer

class SupplierViewSet(viewsets.ModelViewSet):  # Bằng cách kế thừa từ ModelViewSet, lớp sẽ tự động được cung cấp một bộ "hành động" (actions) đầy đủ, tương ứng với các thao tác CRUD.
    queryset = Supplier.objects.all() # Truy vấn tất cả các đối tượng Supplier từ cơ sở dữ liệu.
    serializer_class = SupplierSerializer # Xác định lớp serializer sẽ được sử dụng để chuyển đổi dữ liệu giữa các đối tượng Supplier và định dạng JSON.


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
