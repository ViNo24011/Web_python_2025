# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, login_page, home_page, forget_page, logout_view

app_name = 'users' # Thêm dòng này để sử dụng namespace cho URL

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    path('', include(router.urls)),
    
    # URLs cho API
    path('login/', login_view, name='login_api'), # Đổi tên để tránh nhầm lẫn

    # URLs để render trang HTML
    path('login-page/', login_page, name='login_page'),
    path('home-page/', home_page, name='home_page'),      
    path('forget-page/', forget_page, name='forget_page'), 
    path('logout/', logout_view, name='logout'), # URL cho đăng xuất
]