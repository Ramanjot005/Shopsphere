from django.urls import path
from . import views
from django.shortcuts import redirect
from .views import faq_view, track_order_view, login_view
from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

urlpatterns = [
    path('', views.home, name='home'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('update-cart/<int:product_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('category/<str:category_name>/', views.category_products, name='category_products'),
    path('login/', login_view, name='login'),   
    path('signup/', views.signup, name='signup'),
    path('update-profile/', views.update_profile, name='update_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('orders/', views.order_view, name='orders'),
    path('logout/', views.logout_view, name='logout'),
    path('thank-you/', views.thank_you, name='thank_you'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('clear-cart/', lambda request: (request.session.pop('cart', None), redirect('home'))[1]),
    path('search/', views.search, name='search'),
    path('dashboard/', views.user_dashboard, name='user_dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('wishlist/add/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:product_id>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('orders/delete/<int:order_id>/', views.order_delete, name='order_delete'),
    path('contact/', views.contact_view, name='contact'),
    path('about/', views.about_view, name='about'),
    path('faq/', faq_view, name='faq'),
    path('submit-review/', views.submit_review, name='submit_review'),
    path('review-success/', views.review_success, name='review_success'),
    path('track/<str:order_number>/', track_order_view, name='track_order'),
    
]
