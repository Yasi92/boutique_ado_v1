
from django.urls import path
# From current dir import views
from . import views

urlpatterns = [
    path('', views.all_products, name="products")
]
