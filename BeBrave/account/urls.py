from django.urls import path, include
from . import views

app_name = 'account'
urlpatterns = [
    path('anonymous/', views.anonymous_user_view, name='anonymous_user'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('quick-signup/', views.quick_signup, name='quick_signup'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
]