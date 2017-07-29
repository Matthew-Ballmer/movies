from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

app_name = 'core'
urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(template_name='auth/login.html'), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^signup-fail/$', views.signup_fail, name='signup-fail'),
]
