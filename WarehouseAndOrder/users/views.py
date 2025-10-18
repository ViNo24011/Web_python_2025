# users/views.py

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db import models
from inventory.models import Product
from partners.models import Customer
from transactions.models import ExportReceipt

# Create your views here.
from rest_framework import viewsets
from .models import User
from .serializers import UserSerializer

# ViewSet tự động hỗ trợ list, retrieve, create, update, delete
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer

# lien ket dang nhap
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data.get('username')
        password = data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'Login successful'})
        else:
            return JsonResponse({'message': 'Invalid credentials'}, status=401)

    return JsonResponse({'error': 'Invalid request'}, status=400)

# Render login page
def login_page(request):
    return render(request, 'login.html')

@login_required
def home_page(request):
    total_products = Product.objects.count()
    total_customers = Customer.objects.count()
    total_orders = ExportReceipt.objects.count()
    low_stock_products = Product.objects.filter(quantity__lte=models.F('min_quantity'))

    context = {
        'total_products': total_products,
        'total_customers': total_customers,
        'total_orders': total_orders,
        'low_stock_products': low_stock_products,
        'products_nearing_out_of_stock': low_stock_products.count()
    }
    return render(request, 'home.html', context)


# Render forget password page
def forget_page(request):
    return render(request, 'forget.html')