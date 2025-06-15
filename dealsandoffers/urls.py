from django.urls import path
from . import views
from store import views as store_views

app_name = 'dealsandoffers'

urlpatterns = [
    path('', views.deals_list, name='deals_list'),
    path('add-to-cart/', store_views.add_to_cart, name='add_to_cart'),
    path('add-to-wishlist/', store_views.add_to_wishlist, name='add_to_wishlist'),
]
