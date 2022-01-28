
from django.urls import path
# From current dir import views
from . import views

urlpatterns = [
    path('', views.view_bag, name="view_bag")
]
