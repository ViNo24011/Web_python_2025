
from django.urls import path
from . import views

app_name = 'reports' # Define an app namespace

urlpatterns = [
    # URL for the main monthly revenue summary page
    path('revenue/', views.revenue_page, name='revenue_page'),
    path('revenue/<int:year>/<int:month>/', views.revenue_detail_page, name='revenue_detail_page'),
    path(
        'details/<int:year>/<int:month>/warehouse/<int:warehouse_id>/imports/',
        views.warehouse_imports_detail,
        name='warehouse_imports_detail'
    ),
    path(
        'details/<int:year>/<int:month>/warehouse/<int:warehouse_id>/exports/',
        views.warehouse_exports_detail,
        name='warehouse_exports_detail'
    ),
]