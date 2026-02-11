from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .models import AnonymousUserAccount
app_name = 'account'
urlpatterns = [
    path('anonymous/', views.anonymous_user_view, name='anonymous_user'),
    path('profile/', views.user_profile_view, name='user_profile'),
    path('quick-signup/', views.quick_signup, name='quick_signup'),
    path('login/', views.login_view, name='login'),
    path('journal/new/', views.journal_editor, name='journal_new'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]