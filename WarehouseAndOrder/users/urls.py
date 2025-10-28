# users/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, login_view, login_page, home_page, forget_page, logout_view,
    # Import các view CRUD
    user_list_page, add_user, edit_user, delete_user
)

app_name = 'users' 

router = DefaultRouter()
# 1. ĐỔI ĐƯỜNG DẪN API:
# Đổi 'users' thành 'api/users' để nó không bị trùng với
# đường dẫn 'users/' mà chúng ta muốn dùng cho trang HTML.
router.register(r'api/users', UserViewSet) 

urlpatterns = [
    # URLs để render trang HTML (Template views)
    # 2. ĐƯA CÁC PATH CỤ THỂ LÊN TRƯỚC:
    # Đặt các đường dẫn HTML của bạn LÊN TRÊN include(router.urls)
    # để Django ưu tiên chúng.
    path('login-page/', login_page, name='login_page'),
    path('home-page/', home_page, name='home_page'),      
    path('forget-page/', forget_page, name='forget_page'), 
    path('logout/', logout_view, name='logout'), 
    
    # --- ĐƯỜNG DẪN QUAN TRỌNG CHO TRANG HTML ---
    path('users/', user_list_page, name='user_list_page'), # <--- Đây là trang Quản lý người dùng
    path('users/add/', add_user, name='add_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),

    # URLs cho API
    # 3. ĐƯA ROUTER VÀ CÁC API KHÁC XUỐNG DƯỚI:
    # Đường dẫn API login sẽ là: /api/login/
    # Đường dẫn API user list sẽ là: /api/users/
    path('api/login/', login_view, name='login_api'), 
    path('', include(router.urls)), # Bao gồm các URL của API (ví dụ: /api/users/)
]