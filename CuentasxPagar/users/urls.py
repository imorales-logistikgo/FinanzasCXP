from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from .views import UserView, signup, test

app_name = 'users'

urlpatterns = [
    path('Login/', auth_views.LoginView.as_view(template_name='login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/Usuario/Login'), name='logout'),
    path('signup/', signup, name='signup'),
    path('', test, name='test')
]
