from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .models import Supplier, Customer
from .serializers import SupplierSerializer, CustomerSerializer

class SupplierViewSet(viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer


class CustomerViewSet(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
