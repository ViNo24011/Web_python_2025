
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, login_view, login_page, home_page, forget_page, logout_view,
    user_list_page, add_user, edit_user, delete_user
)

app_name = 'users' 

router = DefaultRouter()
router.register(r'api/users', UserViewSet)

urlpatterns = [
    # --- ĐƯỜNG DẪN CHO TRANG HTML CƠ BẢN ---
    path('login-page/', login_page, name='login_page'),
    path('home-page/', home_page, name='home_page'),      
    path('forget-page/', forget_page, name='forget_page'), 
    path('logout/', logout_view, name='logout'), 
    
    # --- ĐƯỜNG DẪN QUAN TRỌNG CHO TRANG HTML ---
    path('users/', user_list_page, name='user_list_page'), 
    path('users/add/', add_user, name='add_user'),
    path('users/edit/<int:user_id>/', edit_user, name='edit_user'),
    path('users/delete/<int:user_id>/', delete_user, name='delete_user'),

    # --- ĐƯỜNG DẪN CHO API ---
    path('api/login/', login_view, name='login_api'), 
    path('', include(router.urls)),
]