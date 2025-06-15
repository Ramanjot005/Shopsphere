from django.urls import path
from .views import MyPasswordChangeView, MyPasswordResetDoneView
from .views import UpdateProfileView
app_name = 'users'

urlpatterns = [
    path('change-password/', MyPasswordChangeView.as_view(), name='change-password'),
    path('password-change-done/', MyPasswordResetDoneView.as_view(), name='password-change-done'),
    path('update-profile/', UpdateProfileView.as_view(), name='update_profile'),
]
